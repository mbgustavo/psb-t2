"""Delineação dos intervalos QT e da duração do QRS em ECGs."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import label
from scipy.signal import butter, sosfiltfilt


def filtrar_ecg_para_delineacao(sinal, frequencia_amostragem, ordem=3):
    """Remove deriva de linha de base e ruído de alta frequência do ECG.

    Args:
        sinal: Vetor unidimensional de amplitudes do ECG.
        frequencia_amostragem: Frequência de amostragem do sinal, em hertz.
        ordem: Ordem do filtro Butterworth.

    Returns:
        Sinal filtrado por passa-banda de 0,5 a 40 Hz, sem atraso de fase.
    """
    filtro = butter(
        ordem,
        [0.5, 40],
        btype="bandpass",
        fs=frequencia_amostragem,
        output="sos",
    )
    return sosfiltfilt(filtro, np.asarray(sinal, dtype=float))


def _desvio_padrao_robusto(valores):
    """Estima o desvio-padrão a partir do desvio absoluto mediano.

    Args:
        valores: Valores usados para a estimativa robusta.

    Returns:
        Estimativa não negativa do desvio-padrão.
    """
    valores = np.asarray(valores, dtype=float)
    mediana = np.median(valores)
    return 1.4826 * np.median(np.abs(valores - mediana))


def _janela(indice_inicial, indice_final, quantidade_amostras):
    """Limita uma janela de índices aos limites válidos do sinal.

    Args:
        indice_inicial: Primeiro índice desejado.
        indice_final: Índice final exclusivo desejado.
        quantidade_amostras: Comprimento do sinal.

    Returns:
        Objeto ``slice`` correspondente à parte válida da janela.
    """
    return slice(max(0, indice_inicial), min(quantidade_amostras, indice_final))


def _suavizar_media_movel(sinal, amostras_janela):
    """Suaviza um vetor por média móvel centrada.

    Args:
        sinal: Vetor a suavizar.
        amostras_janela: Comprimento ímpar ou par da janela, em amostras.

    Returns:
        Vetor suavizado com o mesmo comprimento de ``sinal``.
    """
    tamanho = max(1, int(amostras_janela))
    nucleo = np.ones(tamanho, dtype=float) / tamanho
    return np.convolve(sinal, nucleo, mode="same")


def detectar_limites_qrs(sinal_filtrado, pico_r, frequencia_amostragem, atividade=None):
    """Delimita o início e o fim do QRS por limiar da derivada suavizada.

    A atividade do QRS é a magnitude da derivada, suavizada em 10 ms. O
    limiar combina o ruído observado antes do complexo com uma fração do pico
    de atividade na janela de busca. O componente de atividade mais próximo
    do pico R é adotado como QRS.

    Args:
        sinal_filtrado: ECG já filtrado para delineação.
        pico_r: Índice do pico R previamente detectado.
        frequencia_amostragem: Frequência de amostragem, em hertz.
        atividade: Magnitude da derivada já suavizada. Quando omitida, ela é
            calculada a partir de ``sinal_filtrado``.

    Returns:
        Tupla ``(inicio_qrs, fim_qrs)``; ambos os valores são ``None`` quando
        não é possível delimitar o complexo.
    """
    quantidade = len(sinal_filtrado)
    if atividade is None:
        derivada = np.gradient(sinal_filtrado) * frequencia_amostragem
        atividade = _suavizar_media_movel(
            np.abs(derivada), round(0.010 * frequencia_amostragem)
        )
    janela_ruido = _janela(
        pico_r - round(0.250 * frequencia_amostragem),
        pico_r - round(0.120 * frequencia_amostragem),
        quantidade,
    )
    ruido = atividade[janela_ruido]
    if len(ruido) < 5:
        return None, None

    inicio_busca = max(0, pico_r - round(0.120 * frequencia_amostragem))
    fim_busca = min(quantidade, pico_r + round(0.160 * frequencia_amostragem))
    atividade_local = atividade[inicio_busca:fim_busca]
    if len(atividade_local) == 0:
        return None, None

    limiar_ruido = np.median(ruido) + 4 * _desvio_padrao_robusto(ruido)
    limiar_pico = 0.08 * np.max(atividade_local)
    limiar = max(limiar_ruido, limiar_pico)
    mascara = atividade_local >= limiar
    mascara = _suavizar_media_movel(
        mascara.astype(float), round(0.012 * frequencia_amostragem)
    ) > 0
    rotulos, quantidade_componentes = label(mascara)
    if quantidade_componentes == 0:
        return None, None

    indice_local_r = int(np.clip(pico_r - inicio_busca, 0, len(mascara) - 1))
    componentes = []
    for componente in range(1, quantidade_componentes + 1):
        indices = np.flatnonzero(rotulos == componente)
        distancia_r = 0 if indice_local_r in indices else np.min(np.abs(indices - indice_local_r))
        componentes.append((distancia_r, indices[0], indices[-1]))
    _, inicio_local, fim_local = min(componentes, key=lambda componente: componente[0])
    return inicio_busca + inicio_local, inicio_busca + fim_local


def detectar_fim_onda_t_por_derivada(
    sinal_filtrado,
    pico_r,
    fim_qrs,
    proximo_pico_r,
    frequencia_amostragem,
    derivada_suave=None,
):
    """Detecta o fim da onda T pelo retorno da derivada ao limiar de ruído.

    A polaridade da onda T é obtida pelo maior desvio absoluto em relação à
    linha de base após o QRS. Após o máximo da onda T, procura-se o primeiro
    trecho de 20 ms em que a derivada orientada para a descida permanece abaixo
    do limiar, estimado a partir do ruído pré-QRS. Assim, o marcador é definido
    por limiar da derivada, e não por limiar de amplitude.

    Args:
        sinal_filtrado: ECG já filtrado para delineação.
        pico_r: Índice do pico R do batimento.
        fim_qrs: Índice do fim do QRS do batimento.
        proximo_pico_r: Índice do próximo pico R, ou ``None`` no último batimento.
        frequencia_amostragem: Frequência de amostragem, em hertz.
        derivada_suave: Derivada já suavizada do sinal. Quando omitida, ela é
            calculada a partir de ``sinal_filtrado``.

    Returns:
        Índice do fim da onda T ou ``None`` se não houver evidência suficiente.
    """
    quantidade = len(sinal_filtrado)
    inicio_base = max(0, pico_r - round(0.250 * frequencia_amostragem))
    fim_base = max(inicio_base + 1, pico_r - round(0.120 * frequencia_amostragem))
    linha_base = np.median(sinal_filtrado[inicio_base:fim_base])
    if derivada_suave is None:
        derivada = np.gradient(sinal_filtrado) * frequencia_amostragem
        derivada_suave = _suavizar_media_movel(
            derivada, round(0.008 * frequencia_amostragem)
        )
    ruido_derivada = derivada_suave[inicio_base:fim_base]
    if len(ruido_derivada) < 5:
        return None

    inicio_t = min(quantidade - 1, fim_qrs + round(0.040 * frequencia_amostragem))
    fim_t = min(quantidade, pico_r + round(0.600 * frequencia_amostragem))
    if proximo_pico_r is not None:
        fim_t = min(fim_t, proximo_pico_r - round(0.100 * frequencia_amostragem))
    if fim_t - inicio_t < round(0.080 * frequencia_amostragem):
        return None

    trecho_t = sinal_filtrado[inicio_t:fim_t] - linha_base
    indice_pico_t = inicio_t + int(np.argmax(np.abs(trecho_t)))
    amplitude_t = sinal_filtrado[indice_pico_t] - linha_base
    if np.abs(amplitude_t) < 4 * _desvio_padrao_robusto(sinal_filtrado[inicio_base:fim_base]):
        return None

    polaridade = np.sign(amplitude_t)
    descida = -polaridade * derivada_suave
    inicio_procura = indice_pico_t + round(0.015 * frequencia_amostragem)
    if inicio_procura >= fim_t:
        return None
    pico_descida = inicio_procura + int(np.argmax(descida[inicio_procura:fim_t]))
    limiar_ruido = np.median(np.abs(ruido_derivada)) + 3 * _desvio_padrao_robusto(ruido_derivada)
    limiar = max(limiar_ruido, 0.05 * descida[pico_descida])
    persistencia = max(1, round(0.020 * frequencia_amostragem))
    candidatos = descida[pico_descida + 1:fim_t] <= limiar
    if len(candidatos) < persistencia:
        return None
    consecutivos = np.convolve(candidatos.astype(int), np.ones(persistencia, dtype=int), mode="valid")
    encontrados = np.flatnonzero(consecutivos == persistencia)
    if len(encontrados) == 0:
        return None
    return pico_descida + 1 + int(encontrados[0])


def calcular_qtc(qt_ms, rr_ms):
    """Calcula QTc pelos métodos de Bazett, Fridericia e Framingham.

    Args:
        qt_ms: Intervalos QT em milissegundos.
        rr_ms: Intervalos RR precedentes em milissegundos.

    Returns:
        DataFrame com as três correções de QT, em milissegundos.
    """
    qt_ms = np.asarray(qt_ms, dtype=float)
    rr_ms = np.asarray(rr_ms, dtype=float)
    rr_s = rr_ms / 1000
    with np.errstate(invalid="ignore", divide="ignore"):
        bazett = qt_ms / np.sqrt(rr_s)
        fridericia = qt_ms / np.cbrt(rr_s)
        framingham = qt_ms + 154 * (1 - rr_s)
    invalidos = ~np.isfinite(qt_ms) | ~np.isfinite(rr_s) | (rr_s <= 0)
    bazett[invalidos] = np.nan
    fridericia[invalidos] = np.nan
    framingham[invalidos] = np.nan
    return pd.DataFrame(
        {
            "QTcBazett_ms": bazett,
            "QTcFridericia_ms": fridericia,
            "QTcFramingham_ms": framingham,
        }
    )


def medir_intervalos_qt(sinais, canais, picos_r, frequencia_amostragem):
    """Mede QRS, QT e QTc em cada batimento e canal de ECG.

    Os picos R são comuns aos três canais e os limites são estimados
    independentemente em cada canal. O RR precedente é usado nas correções de
    QT, portanto o primeiro batimento não recebe valor de QTc. Delineações
    com QRS fora de 40--200 ms são marcadas como ausentes para impedir que um
    limiar incorretamente acionado contamine os resumos.

    Args:
        sinais: Matriz no formato amostras por canais.
        canais: Nomes dos canais na mesma ordem das colunas de ``sinais``.
        picos_r: Índices crescentes dos picos R previamente detectados.
        frequencia_amostragem: Frequência de amostragem, em hertz.

    Returns:
        DataFrame longo contendo os marcadores, intervalos e correções por
        batimento e canal.
    """
    picos_r = np.asarray(picos_r, dtype=int)
    sinais = np.asarray(sinais, dtype=float)
    filtrados = [
        filtrar_ecg_para_delineacao(sinais[:, indice], frequencia_amostragem)
        for indice in range(sinais.shape[1])
    ]
    derivadas_suaves = [
        _suavizar_media_movel(
            np.gradient(filtrado) * frequencia_amostragem,
            round(0.008 * frequencia_amostragem),
        )
        for filtrado in filtrados
    ]
    atividades_qrs = [
        _suavizar_media_movel(
            np.abs(np.gradient(filtrado) * frequencia_amostragem),
            round(0.010 * frequencia_amostragem),
        )
        for filtrado in filtrados
    ]
    registros = []
    for indice_batimento, pico_r in enumerate(picos_r):
        rr_ms = np.nan if indice_batimento == 0 else (pico_r - picos_r[indice_batimento - 1]) * 1000 / frequencia_amostragem
        proximo_pico = picos_r[indice_batimento + 1] if indice_batimento + 1 < len(picos_r) else None
        for indice_canal, canal in enumerate(canais):
            inicio_qrs, fim_qrs = detectar_limites_qrs(
                filtrados[indice_canal],
                pico_r,
                frequencia_amostragem,
                atividades_qrs[indice_canal],
            )
            fim_t = None
            if inicio_qrs is not None and fim_qrs is not None:
                fim_t = detectar_fim_onda_t_por_derivada(
                    filtrados[indice_canal],
                    pico_r,
                    fim_qrs,
                    proximo_pico,
                    frequencia_amostragem,
                    derivadas_suaves[indice_canal],
                )
            qrs_ms = np.nan if inicio_qrs is None or fim_qrs is None else (fim_qrs - inicio_qrs) * 1000 / frequencia_amostragem
            qt_ms = np.nan if inicio_qrs is None or fim_t is None else (fim_t - inicio_qrs) * 1000 / frequencia_amostragem
            if not np.isnan(qrs_ms) and not 40 <= qrs_ms <= 200:
                qrs_ms = np.nan
                qt_ms = np.nan
            registros.append(
                {
                    "Batimento": indice_batimento + 1,
                    "Canal": canal,
                    "PicoR_Amostra": pico_r,
                    "InicioQRS_Amostra": inicio_qrs,
                    "FimQRS_Amostra": fim_qrs,
                    "FimT_Amostra": fim_t,
                    "RRPrecedente_ms": rr_ms,
                    "QRS_ms": qrs_ms,
                    "QT_ms": qt_ms,
                }
            )
    medidas = pd.DataFrame(registros)
    correcoes = calcular_qtc(medidas["QT_ms"].to_numpy(), medidas["RRPrecedente_ms"].to_numpy())
    return pd.concat([medidas.reset_index(drop=True), correcoes], axis=1)


def medir_intervalos_no_complexo_medio(sinal_medio, canais, frequencia_amostragem, amostras_antes):
    """Mede QRS e QT no complexo médio alinhado ao pico R.

    Args:
        sinal_medio: Matriz do PQRST médio, no formato amostras por canais.
        canais: Nomes dos canais na mesma ordem de ``sinal_medio``.
        frequencia_amostragem: Frequência de amostragem, em hertz.
        amostras_antes: Quantidade de amostras entre o início da janela e R.

    Returns:
        DataFrame com os marcadores e intervalos do complexo médio por canal.
    """
    pico_r = int(amostras_antes)
    registros = []
    for indice, canal in enumerate(canais):
        filtrado = filtrar_ecg_para_delineacao(sinal_medio[:, indice], frequencia_amostragem)
        inicio_qrs, fim_qrs = detectar_limites_qrs(filtrado, pico_r, frequencia_amostragem)
        fim_t = None
        if inicio_qrs is not None and fim_qrs is not None:
            fim_t = detectar_fim_onda_t_por_derivada(
                filtrado, pico_r, fim_qrs, None, frequencia_amostragem
            )
        registros.append(
            {
                "Canal": canal,
                "InicioQRS_ms": np.nan if inicio_qrs is None else (inicio_qrs - pico_r) * 1000 / frequencia_amostragem,
                "FimQRS_ms": np.nan if fim_qrs is None else (fim_qrs - pico_r) * 1000 / frequencia_amostragem,
                "FimT_ms": np.nan if fim_t is None else (fim_t - pico_r) * 1000 / frequencia_amostragem,
                "QRS_ms": np.nan if inicio_qrs is None or fim_qrs is None else (fim_qrs - inicio_qrs) * 1000 / frequencia_amostragem,
                "QT_ms": np.nan if inicio_qrs is None or fim_t is None else (fim_t - inicio_qrs) * 1000 / frequencia_amostragem,
            }
        )
    return pd.DataFrame(registros)


def resumir_medidas_qt(medidas):
    """Resume as medidas válidas de QRS, QT e QTc por canal.

    Args:
        medidas: DataFrame detalhado produzido por ``medir_intervalos_qt``.

    Returns:
        DataFrame com quantidade válida, médias e desvios-padrão por canal.
    """
    colunas = ["QRS_ms", "QT_ms", "QTcBazett_ms", "QTcFridericia_ms", "QTcFramingham_ms"]
    resumo = medidas.groupby("Canal")[colunas].agg(["count", "mean", "std"])
    resumo.columns = [f"{medida}_{estatistica}" for medida, estatistica in resumo.columns]
    return resumo.reset_index()


def plotar_qt_por_tempo(medidas, arquivo):
    """Salva gráfico dos QT e QTc de Bazett válidos por batimento e canal.

    Args:
        medidas: DataFrame detalhado produzido por ``medir_intervalos_qt``.
        arquivo: Caminho do PNG a ser gravado.
    """
    canais = medidas["Canal"].unique()
    fig, eixos = plt.subplots(len(canais), 1, figsize=(11, 8), sharex=True, constrained_layout=True)
    if len(canais) == 1:
        eixos = [eixos]
    for eixo, canal in zip(eixos, canais):
        dados = medidas.loc[medidas["Canal"] == canal]
        eixo.plot(dados["Batimento"], dados["QT_ms"], marker=".", linestyle="none", label="QT")
        eixo.plot(dados["Batimento"], dados["QTcBazett_ms"], marker=".", linestyle="none", label="QTc Bazett")
        eixo.set_ylabel("Duração (ms)")
        eixo.set_title(canal, loc="left", fontsize=10)
        eixo.grid(True, alpha=0.3)
        eixo.legend()
    eixos[-1].set_xlabel("Batimento")
    fig.suptitle("Intervalos QT e QTc de Bazett por batimento")
    fig.savefig(arquivo, dpi=220)
    plt.close(fig)
