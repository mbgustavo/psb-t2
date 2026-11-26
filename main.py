"""Processamento do sinal de ECG para o trabalho."""

from pathlib import Path

import numpy as np
import pandas as pd
from item_a import utils as utils_a
from item_b import utils as utils_b

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
