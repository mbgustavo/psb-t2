"""Processamento do sinal de ECG para o trabalho."""

import pandas as pd
from item_a import utils as utils_a

# Item a do trabalho: interpolar o sinal de ECG de 1000 para 4000 amostras/s e plotar o gráfico.
arquivo_entrada = "ECG_XYZ.txt(fs=1000Hz)"
arquivo_saida = "item_a/ECG_XYZ_4000Hz.csv"
frequencia_nova = 4000  # amostras por segundo

dados = pd.read_csv(arquivo_entrada, sep="\t")
dados_interpolados = utils_a.interpolar_dados(dados, arquivo_entrada, frequencia_nova)
dados_interpolados.to_csv(arquivo_saida, index=False)
print(f"Sinal interpolado salvo em: {arquivo_saida}")

arquivo_grafico = "item_a/ECG_03-00_a_03-10.svg"
inicio_grafico = 180  # segundos (3:00)
fim_grafico = 190  # segundos (3:10)
utils_a.plotar_sinal_ecg(inicio_grafico, fim_grafico, frequencia_nova, dados_interpolados, arquivo_grafico)
