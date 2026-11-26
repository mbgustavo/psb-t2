"""Processamento do sinal de ECG para o trabalho."""

from pathlib import Path

import numpy as np
import pandas as pd
from item_a import utils as utils_a
from item_b import utils as utils_b
from item_c import utils as utils_c
from item_d import utils as utils_d

# Item a do trabalho: interpolar o sinal de ECG de 1000 para 4000 amostras/s e plotar o gráfico.
arquivo_entrada = "ECG_XYZ.txt(fs=1000Hz)"
arquivo_saida = "item_a/ECG_XYZ_4000Hz.csv"
frequencia_nova = 4000  # amostras por segundo

dados = pd.read_csv(arquivo_entrada, sep="\t")
dados_interpolados = utils_a.interpolar_dados(dados, arquivo_entrada, frequencia_nova)
dados_interpolados.to_csv(arquivo_saida, index=False)
print(f"Sinal interpolado salvo em: {arquivo_saida}")

arquivo_grafico = "item_a/ECG_03-00_a_03-10.png"
inicio_grafico = 180  # segundos (3:00)
fim_grafico = 190  # segundos (3:10)
utils_a.plotar_sinal_ecg(
    inicio_grafico,
    fim_grafico,
    frequencia_nova,
    dados,
    dados_interpolados,
    arquivo_grafico,
)

# Item b do trabalho: detectar, alinhar e promediar os complexos PQRST.
diretorio_item_b = Path("item_b")
diretorio_item_b.mkdir(parents=True, exist_ok=True)
canais_item_b = utils_b.obter_canais_ecg(dados_interpolados)
sinais_item_b = dados_interpolados[canais_item_b].to_numpy(dtype=float)
picos_detectados = utils_b.detectar_picos_r(sinais_item_b[:, 1], frequencia_nova)
amostras_antes = int(round(0.25 * frequencia_nova))
amostras_depois = int(round(0.55 * frequencia_nova))
janelas, picos_validos, rejeitados_borda = utils_b.extrair_janelas(
    sinais_item_b,
    picos_detectados,
    amostras_antes,
    amostras_depois,
)
mascara_aceitos = utils_b.selecionar_batimentos(janelas)
batimentos_aceitos = janelas[mascara_aceitos]
picos_aceitos = picos_validos[mascara_aceitos]
if len(batimentos_aceitos) == 0:
    raise ValueError("Nenhum batimento foi aceito para a promediação do item b.")

sinal_medio = np.mean(batimentos_aceitos, axis=0)
ruido_residual = utils_b.calcular_ruido_residual(batimentos_aceitos, sinal_medio)
tempo_relativo = np.arange(-amostras_antes, amostras_depois + 1) / frequencia_nova
frequencias_corte_magnitude = (25, 40, 80)
vetores_magnitude = utils_b.calcular_vetores_magnitude(
    sinais_item_b,
    picos_aceitos,
    frequencia_nova,
    amostras_antes,
    amostras_depois,
    frequencias_corte_magnitude,
)

tabela_pqrst = pd.DataFrame({"TempoRelativo_s": tempo_relativo})
for indice, canal in enumerate(canais_item_b):
    tabela_pqrst[canal] = sinal_medio[:, indice]
tabela_pqrst.to_csv(diretorio_item_b / "complexo_pqrst_promediado.csv", index=False)

tabela_magnitude = pd.DataFrame({"TempoRelativo_s": tempo_relativo})
for frequencia_corte, vetor in vetores_magnitude.items():
    tabela_magnitude[f"Magnitude_passa_alta_{frequencia_corte}Hz"] = vetor
tabela_magnitude.to_csv(diretorio_item_b / "vetores_magnitude.csv", index=False)

quantidade_rejeitada = rejeitados_borda + int((~mascara_aceitos).sum())
resumo_item_b = pd.DataFrame(
    [
        {
            "FrequenciaAmostragem_Hz": frequencia_nova,
            "ComplexosDetectados": len(picos_detectados),
            "ComplexosIncluidos": len(batimentos_aceitos),
            "ComplexosRejeitados": quantidade_rejeitada,
            "RejeitadosPorBorda": rejeitados_borda,
            "RejeitadosPorMorfologia": int((~mascara_aceitos).sum()),
            "RMSResidual_X": ruido_residual[0],
            "RMSResidual_Y": ruido_residual[1],
            "RMSResidual_Z": ruido_residual[2],
        }
    ]
)
resumo_item_b.to_csv(diretorio_item_b / "resumo_item_b.csv", index=False)

utils_b.plotar_complexo_medio(
    tempo_relativo,
    sinal_medio,
    canais_item_b,
    len(batimentos_aceitos),
    quantidade_rejeitada,
    ruido_residual,
    diretorio_item_b / "complexo_pqrst_promediado.png",
)
utils_b.plotar_vetores_magnitude(
    tempo_relativo,
    vetores_magnitude,
    diretorio_item_b / "vetores_magnitude_passa_alta.png",
)
print(
    "Item b concluído: "
    f"{len(batimentos_aceitos)} complexos incluídos e "
    f"{quantidade_rejeitada} rejeitados."
)

# Item c do trabalho: calcular e plotar os intervalos RR dos picos do item b.
diretorio_item_c = Path("item_c")
diretorio_item_c.mkdir(parents=True, exist_ok=True)
tempos_picos_r = dados_interpolados.loc[picos_detectados, "SamplingInterval"].to_numpy()
intervalos_rr = utils_c.calcular_intervalos_rr(tempos_picos_r)
intervalos_rr.to_csv(diretorio_item_c / "intervalos_rr.csv", index=False)
utils_c.plotar_intervalos_rr(intervalos_rr, diretorio_item_c / "RR_x_Tempo.png")
print(f"Item c concluído: {len(intervalos_rr)} intervalos RR calculados.")

# Item d: medir QRS, QT e QTc nos três canais e no complexo PQRST médio.
diretorio_item_d = Path("item_d")
diretorio_item_d.mkdir(parents=True, exist_ok=True)
medidas_qt = utils_d.medir_intervalos_qt(
    sinais_item_b,
    canais_item_b,
    picos_detectados,
    frequencia_nova,
)
medidas_qt.to_csv(diretorio_item_d / "intervalos_qt_por_batimento.csv", index=False)
resumo_qt = utils_d.resumir_medidas_qt(medidas_qt)
resumo_qt.to_csv(diretorio_item_d / "resumo_intervalos_qt.csv", index=False)

medidas_complexo_medio = utils_d.medir_intervalos_no_complexo_medio(
    sinal_medio,
    canais_item_b,
    frequencia_nova,
    amostras_antes,
)
rr_medio_ms = np.mean(np.diff(picos_detectados)) * 1000 / frequencia_nova
qtcs_complexo_medio = utils_d.calcular_qtc(
    medidas_complexo_medio["QT_ms"].to_numpy(),
    np.full(len(medidas_complexo_medio), rr_medio_ms),
)
medidas_complexo_medio = pd.concat(
    [medidas_complexo_medio, qtcs_complexo_medio], axis=1
)
medidas_complexo_medio.insert(1, "RRMedio_ms", rr_medio_ms)
medidas_complexo_medio.to_csv(
    diretorio_item_d / "intervalos_qt_complexo_medio.csv", index=False
)
utils_d.plotar_qt_por_tempo(medidas_qt, diretorio_item_d / "QT_e_QTc_por_batimento.png")
print(
    "Item d concluído: "
    f"{medidas_qt['QT_ms'].notna().sum()} medidas QT válidas de "
    f"{len(medidas_qt)} tentativas nos três canais."
)
