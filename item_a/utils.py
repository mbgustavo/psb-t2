
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def interpolar_dados(dados, arquivo, frequencia):
    """Interpola os canais do arquivo de ECG para uma nova frequência de amostragem.

    Args:
        dados: DataFrame de origem (mantido por compatibilidade; os dados são
            carregados de ``arquivo`` dentro desta função).
        arquivo: Caminho do arquivo tabulado com ``SamplingInterval`` e os
            canais do ECG.
        frequencia: Frequência de amostragem desejada, em amostras por segundo.

    Returns:
        DataFrame com a coluna de tempo e os canais interpolados pela função
        ``numpy.interp``.
    """
    dados = pd.read_csv(arquivo, sep="\t")
    tempo_original = dados["SamplingInterval"].to_numpy()
    passo_novo = 1 / frequencia
    tempo_novo = np.arange(
        tempo_original[0],
        tempo_original[-1] + passo_novo / 2,
        passo_novo,
    )

    resultado = {"SamplingInterval": tempo_novo}
    for coluna in dados.columns[1:]:
        resultado[coluna] = np.interp(
            tempo_novo,
            tempo_original,
            dados[coluna].to_numpy(),
        )

    return pd.DataFrame(resultado)

def plotar_sinal_ecg(tempo_inicio, tempo_fim, frequencia, dados, arquivo):
    """Plota cada canal do ECG em um subplot, usando uma cor diferente.

    Args:
        tempo_inicio: Início do intervalo a plotar, em segundos.
        tempo_fim: Fim do intervalo a plotar, em segundos.
        frequencia: Frequência de amostragem do sinal, em amostras por segundo;
            é exibida no título do gráfico.
        dados: DataFrame com ``SamplingInterval`` e os canais interpolados.
        arquivo: Caminho do arquivo SVG onde o gráfico será salvo.
    """
    tempo = dados["SamplingInterval"].to_numpy()
    mascara = (tempo >= tempo_inicio) & (tempo <= tempo_fim)
    canais = [coluna for coluna in dados.columns if coluna != "SamplingInterval"]
    cores = plt.get_cmap("tab10").colors

    fig, eixos = plt.subplots(
        nrows=len(canais),
        ncols=1,
        figsize=(12, 9),
        sharex=True,
        constrained_layout=True,
    )
    if len(canais) == 1:
        eixos = [eixos]

    for indice, canal in enumerate(canais):
        eixo = eixos[indice]
        eixo.plot(
            tempo[mascara],
            dados.loc[mascara, canal],
            color=cores[indice % len(cores)],
            linewidth=0.8,
        )
        eixo.set_title(canal, loc="left", fontsize=10)
        eixo.set_ylabel("Amplitude")
        eixo.grid(True, alpha=0.3)

    ticks = np.arange(np.ceil(tempo_inicio), np.floor(tempo_fim) + 1, 1)
    eixos[-1].set_xticks(ticks)
    eixos[-1].set_xticklabels([f"{int(t // 60)}:{int(t % 60):02d}" for t in ticks])
    eixos[-1].set_xlabel("Tempo (min:s)")
    fig.suptitle(
        f"Sinal de ECG interpolado · {int(tempo_inicio // 60)}:"
        f"{int(tempo_inicio % 60):02d}–{int(tempo_fim // 60)}:"
        f"{int(tempo_fim % 60):02d} ({frequencia} amostras/s)"
    )
    fig.savefig(arquivo, format="svg")
    plt.close(fig)
    print(f"Gráfico SVG salvo em: {arquivo}")
