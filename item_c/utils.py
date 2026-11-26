"""Cálculo e visualização dos intervalos RR consecutivos."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter


def calcular_intervalos_rr(tempos_picos):
    """Calcula todos os intervalos RR consecutivos a partir dos picos R.

    O instante associado a cada intervalo é o ponto médio entre os dois picos
    R que o delimitam.

    Args:
        tempos_picos: Vetor crescente dos instantes dos picos R, em segundos.

    Returns:
        DataFrame com os tempos inicial, final e médio em segundos, além do
        intervalo RR correspondente em milissegundos.

    Raises:
        ValueError: Se houver menos de dois picos R.
    """
    tempos_picos = np.asarray(tempos_picos, dtype=float)
    if len(tempos_picos) < 2:
        raise ValueError("São necessários ao menos dois picos R para calcular RR.")
    return pd.DataFrame(
        {
            "TempoInicio_s": tempos_picos[:-1],
            "TempoFim_s": tempos_picos[1:],
            "TempoMedio_s": (tempos_picos[:-1] + tempos_picos[1:]) / 2,
            "IntervaloRR_ms": np.diff(tempos_picos) * 1000,
        }
    )


def formatar_minutos_segundos(valor, _):
    """Formata um tempo em segundos no padrão minutos:segundos.

    Args:
        valor: Tempo em segundos.
        _: Posição do marcador no eixo, fornecida pelo Matplotlib.

    Returns:
        Tempo formatado como ``min:seg``.
    """
    minutos, segundos = divmod(int(round(valor)), 60)
    return f"{minutos}:{segundos:02d}"


def plotar_intervalos_rr(intervalos_rr, arquivo):
    """Gera o gráfico dos intervalos RR em função do tempo.

    Args:
        intervalos_rr: DataFrame retornado por ``calcular_intervalos_rr``.
        arquivo: Caminho do PNG a ser gravado.
    """
    fig, eixo = plt.subplots(figsize=(11, 5), constrained_layout=True)
    eixo.plot(
        intervalos_rr["TempoMedio_s"],
        intervalos_rr["IntervaloRR_ms"],
        marker="o",
        markersize=2.8,
        linewidth=0.8,
    )
    eixo.set_xlabel("Tempo (min:s)")
    eixo.set_ylabel("Intervalo RR (ms)")
    eixo.set_title("Intervalos RR consecutivos")
    eixo.xaxis.set_major_formatter(FuncFormatter(formatar_minutos_segundos))
    eixo.grid(True, alpha=0.3)
    fig.savefig(arquivo, dpi=220)
    plt.close(fig)
