
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

def plotar_sinal_ecg(
    tempo_inicio, tempo_fim, frequencia, dados_originais, dados_interpolados, arquivo
):
    """Plota os sinais original e interpolado em subplots separados por canal.

    Args:
        tempo_inicio: Início do intervalo a plotar, em segundos.
        tempo_fim: Fim do intervalo a plotar, em segundos.
        frequencia: Frequência de amostragem do sinal, em amostras por segundo;
            é exibida no título e identifica a frequência do sinal interpolado.
        dados_originais: DataFrame com ``SamplingInterval`` e os canais originais.
        dados_interpolados: DataFrame com ``SamplingInterval`` e os canais
            interpolados.
        arquivo: Caminho do arquivo PNG onde o gráfico será salvo.
    """
    tempo_original = dados_originais["SamplingInterval"].to_numpy()
    tempo_interpolado = dados_interpolados["SamplingInterval"].to_numpy()
    mascara_original = (tempo_original >= tempo_inicio) & (tempo_original <= tempo_fim)
    mascara_interpolado = (tempo_interpolado >= tempo_inicio) & (tempo_interpolado <= tempo_fim)
    canais = [coluna for coluna in dados_interpolados.columns if coluna != "SamplingInterval"]
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
            tempo_original[mascara_original],
            dados_originais.loc[mascara_original, canal],
            color=cores[indice * 2],
            linestyle="None",
            marker="o",
            markersize=2,
            label="Original (1000 amostras/s)",
        )
        eixo.plot(
            tempo_interpolado[mascara_interpolado],
            dados_interpolados.loc[mascara_interpolado, canal],
            color=cores[indice * 2 + 1],
            linewidth=0.7,
            label=f"Interpolado ({frequencia} amostras/s)",
        )
        eixo.set_title(canal, loc="left", fontsize=10)
        eixo.set_ylabel("Amplitude")
        eixo.grid(True, alpha=0.3)
        eixo.legend(loc="upper right", fontsize=8)

    ticks = np.arange(np.ceil(tempo_inicio), np.floor(tempo_fim) + 1, 1)
    eixos[-1].set_xticks(ticks)
    eixos[-1].set_xticklabels([f"{int(t // 60)}:{int(t % 60):02d}" for t in ticks])
    eixos[-1].set_xlim(tempo_inicio, tempo_fim)
    eixos[-1].set_xlabel("Tempo (min:s)")
    fig.suptitle(
        f"Sinais de ECG original e interpolado · {int(tempo_inicio // 60)}:"
        f"{int(tempo_inicio % 60):02d}–{int(tempo_fim // 60)}:"
        f"{int(tempo_fim % 60):02d} ({frequencia} amostras/s)"
    )
    fig.savefig(arquivo, format="png", dpi=220)
    plt.close(fig)
    print(f"Gráfico PNG salvo em: {arquivo}")
