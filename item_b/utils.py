"""Detecção, alinhamento e promediação de complexos PQRST."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, find_peaks, sosfiltfilt


def obter_canais_ecg(dados):
    """Obtém os três canais ortogonais X, Y e Z do DataFrame de ECG.

    Args:
        dados: Dados com a coluna temporal ``SamplingInterval`` e os canais.

    Returns:
        Lista com os nomes das colunas correspondentes aos canais X, Y e Z.

    Raises:
        ValueError: Se algum dos três canais esperados não estiver presente.
    """
    canais = ["ChXGain5000", "ChYGain5000", "ChZGain5000"]
    ausentes = [canal for canal in canais if canal not in dados.columns]
    if ausentes:
        raise ValueError(f"Canais de ECG ausentes: {', '.join(ausentes)}")
    return canais


def filtrar_passa_banda(
    sinal,
    frequencia_amostragem,
    frequencia_inferior,
    frequencia_superior,
    ordem=3,
):
    """Aplica filtro Butterworth passa-banda com fase nula a um sinal.

    Args:
        sinal: Vetor do sinal a filtrar.
        frequencia_amostragem: Frequência de amostragem do sinal, em hertz.
        frequencia_inferior: Frequência de corte inferior, em hertz.
        frequencia_superior: Frequência de corte superior, em hertz.
        ordem: Ordem do filtro Butterworth.

    Returns:
        Vetor filtrado, com o mesmo tamanho de ``sinal``.
    """
    filtro = butter(
        ordem,
        [frequencia_inferior, frequencia_superior],
        btype="bandpass",
        fs=frequencia_amostragem,
        output="sos",
    )
    return sosfiltfilt(filtro, sinal)


def filtrar_passa_alta(sinal, frequencia_amostragem, frequencia_corte, ordem=3):
    """Aplica filtro Butterworth passa-alta com fase nula a um sinal.

    Args:
        sinal: Vetor do sinal a filtrar.
        frequencia_amostragem: Frequência de amostragem do sinal, em hertz.
        frequencia_corte: Frequência de corte do passa-alta, em hertz.
        ordem: Ordem do filtro Butterworth.

    Returns:
        Vetor filtrado, com o mesmo tamanho de ``sinal``.
    """
    filtro = butter(
        ordem,
        frequencia_corte,
        btype="highpass",
        fs=frequencia_amostragem,
        output="sos",
    )
    return sosfiltfilt(filtro, sinal)


def detectar_picos_r(
    sinal,
    frequencia_amostragem,
    frequencia_inferior=5,
    frequencia_superior=25,
    intervalo_minimo=0.4,
    fator_proeminencia=2,
):
    """Detecta picos R em um canal de ECG previamente selecionado.

    Por padrão, um passa-banda de 5 a 25 Hz privilegia a energia do QRS. Os
    picos são separados por no mínimo 400 ms e precisam ter proeminência de
    duas vezes o desvio-padrão do sinal filtrado.

    Args:
        sinal: Vetor do canal usado para a detecção.
        frequencia_amostragem: Frequência de amostragem, em hertz.
        frequencia_inferior: Corte inferior do passa-banda, em hertz.
        frequencia_superior: Corte superior do passa-banda, em hertz.
        intervalo_minimo: Separação mínima entre picos R, em segundos.
        fator_proeminencia: Multiplicador do desvio-padrão usado como
            proeminência mínima.

    Returns:
        Índices inteiros dos picos R detectados no sinal original.
    """
    sinal_qrs = filtrar_passa_banda(
        sinal,
        frequencia_amostragem,
        frequencia_inferior,
        frequencia_superior,
    )
    distancia_minima = int(round(intervalo_minimo * frequencia_amostragem))
    proeminencia = fator_proeminencia * np.std(sinal_qrs)
    picos, _ = find_peaks(
        sinal_qrs,
        distance=distancia_minima,
        prominence=proeminencia,
    )
    return picos


def extrair_janelas(sinais, picos_r, amostras_antes, amostras_depois):
    """Extrai janelas centradas nos picos R para todos os canais.

    Args:
        sinais: Matriz bidimensional no formato amostras por canais.
        picos_r: Índices dos picos R candidatos.
        amostras_antes: Número de amostras antes do pico R.
        amostras_depois: Número de amostras após o pico R.

    Returns:
        Tupla com matriz de batimentos, índices de picos aproveitáveis e
        quantidade de picos descartados por não caberem no registro.
    """
    quantidade_amostras = sinais.shape[0]
    comprimento = amostras_antes + amostras_depois + 1
    janelas = []
    picos_validos = []
    for pico in picos_r:
        inicio = pico - amostras_antes
        fim = pico + amostras_depois + 1
        if inicio < 0 or fim > quantidade_amostras:
            continue
        janelas.append(sinais[inicio:fim])
        picos_validos.append(pico)
    matriz = np.asarray(janelas, dtype=float)
    if matriz.size == 0:
        matriz = np.empty((0, comprimento, sinais.shape[1]))
    return matriz, np.asarray(picos_validos, dtype=int), len(picos_r) - len(picos_validos)


def selecionar_batimentos(matriz_batimentos, limite_correlacao=0.9):
    """Rejeita batimentos morfologicamente discrepantes da mediana.

    Cada batimento é centralizado, normalizado pela norma Euclidiana e
    comparado, por correlação, ao molde mediano. O limiar é o limite inferior
    de Tukey das correlações; também são rejeitados valores abaixo do limite
    de correlação informado (0,90 por padrão).

    Args:
        matriz_batimentos: Matriz no formato batimentos por amostras por canais.
        limite_correlacao: Correlação mínima aceita para um batimento.

    Returns:
        Máscara booleana que indica os batimentos incluídos na promediação.
    """
    if len(matriz_batimentos) == 0:
        return np.empty(0, dtype=bool)

    vetores = matriz_batimentos.reshape(len(matriz_batimentos), -1)
    vetores = vetores - vetores.mean(axis=1, keepdims=True)
    normas = np.linalg.norm(vetores, axis=1)
    vetores_normalizados = vetores / np.maximum(normas[:, None], np.finfo(float).eps)
    molde = np.median(vetores_normalizados, axis=0)
    molde /= max(np.linalg.norm(molde), np.finfo(float).eps)
    correlacoes = vetores_normalizados @ molde
    primeiro_quartil, terceiro_quartil = np.quantile(correlacoes, [0.25, 0.75])
    limite_tukey = primeiro_quartil - 1.5 * (terceiro_quartil - primeiro_quartil)
    limite = max(limite_correlacao, limite_tukey)
    return correlacoes >= limite


def calcular_ruido_residual(batimentos, sinal_medio):
    """Calcula o RMS dos resíduos entre batimentos aceitos e o sinal médio.

    Args:
        batimentos: Matriz de batimentos aceitos.
        sinal_medio: Matriz do complexo médio, no formato amostras por canais.

    Returns:
        Vetor com o RMS residual estimado para cada canal.
    """
    residuos = batimentos - sinal_medio[None, :, :]
    return np.sqrt(np.mean(residuos**2, axis=(0, 1)))


def calcular_vetores_magnitude(
    sinais,
    picos_aceitos,
    frequencia_amostragem,
    amostras_antes,
    amostras_depois,
    frequencias_corte=(25, 40, 80),
):
    """Calcula vetores magnitude médios após filtros passa-altas definidos.

    Args:
        sinais: Matriz dos canais X, Y e Z, no formato amostras por canais.
        picos_aceitos: Índices R dos batimentos usados na promediação.
        frequencia_amostragem: Frequência de amostragem, em hertz.
        amostras_antes: Número de amostras antes do pico R.
        amostras_depois: Número de amostras após o pico R.
        frequencias_corte: Frequências de corte dos filtros passa-alta, em
            hertz.

    Returns:
        Dicionário que associa cada frequência de corte ao vetor magnitude
        médio do complexo correspondente.
    """
    vetores = {}
    for frequencia_corte in frequencias_corte:
        filtrado = np.column_stack(
            [
                filtrar_passa_alta(sinais[:, indice], frequencia_amostragem, frequencia_corte)
                for indice in range(sinais.shape[1])
            ]
        )
        janelas, _, _ = extrair_janelas(
            filtrado,
            picos_aceitos,
            amostras_antes,
            amostras_depois,
        )
        sinal_medio = np.mean(janelas, axis=0)
        vetores[frequencia_corte] = np.sqrt(np.sum(sinal_medio**2, axis=1))
    return vetores


def plotar_complexo_medio(tempo_relativo, sinal_medio, canais, quantidade_incluida, quantidade_rejeitada, ruido_residual, arquivo):
    """Salva o gráfico dos três canais do complexo PQRST médio.

    Args:
        tempo_relativo: Tempo relativo ao pico R, em segundos.
        sinal_medio: Matriz do complexo médio, no formato amostras por canais.
        canais: Nomes dos canais na mesma ordem das colunas de ``sinal_medio``.
        quantidade_incluida: Número de complexos incluídos na média.
        quantidade_rejeitada: Número total de complexos rejeitados.
        ruido_residual: RMS residual estimado por canal.
        arquivo: Caminho do PNG a ser gravado.
    """
    fig, eixos = plt.subplots(3, 1, figsize=(11, 8), sharex=True, constrained_layout=True)
    for indice, eixo in enumerate(eixos):
        eixo.plot(tempo_relativo * 1000, sinal_medio[:, indice], linewidth=1.1)
        eixo.axvline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
        eixo.set_ylabel("Amplitude")
        eixo.set_title(f"{canais[indice]} | RMS residual: {ruido_residual[indice]:.4f}", loc="left", fontsize=10)
        eixo.grid(True, alpha=0.3)
    eixos[-1].set_xlabel("Tempo relativo ao pico R (ms)")
    fig.suptitle(
        "Complexo PQRST promediado "
        f"({quantidade_incluida} incluídos; {quantidade_rejeitada} rejeitados)"
    )
    fig.savefig(arquivo, dpi=220)
    plt.close(fig)


def plotar_vetores_magnitude(tempo_relativo, vetores_magnitude, arquivo):
    """Salva o gráfico dos vetores magnitude para os três passa-altas.

    Args:
        tempo_relativo: Tempo relativo ao pico R, em segundos.
        vetores_magnitude: Dicionário de frequência de corte para vetor magnitude.
        arquivo: Caminho do PNG a ser gravado.
    """
    fig, eixo = plt.subplots(figsize=(11, 4.8), constrained_layout=True)
    for frequencia_corte, vetor in vetores_magnitude.items():
        eixo.plot(tempo_relativo * 1000, vetor, label=f"Passa-alta {frequencia_corte} Hz")
    eixo.axvline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6, label="Pico R")
    eixo.set_xlabel("Tempo relativo ao pico R (ms)")
    eixo.set_ylabel("Magnitude")
    eixo.set_title("Vetor magnitude médio dos complexos aceitos")
    eixo.grid(True, alpha=0.3)
    eixo.legend()
    fig.savefig(arquivo, dpi=220)
    plt.close(fig)


