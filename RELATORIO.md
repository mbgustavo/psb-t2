# Relatório do trabalho

[`PDS_Homework202xB.pdf`](PDS_Homework202xB.pdf)

A partir do [sinal de ECG de três canais, X, Y e Z simultâneos](<ECG_XYZ.txt(fs=1000Hz)>), dado em aula com cinco (5) minutos de duração e amostrado a 1000 amostras/seg., desenvolva os algoritmos e faça as implementações para realizar as seguintes operações:

## Item a

> Interpole o sinal original para 4000 amostras/s. Fazer o gráfico para ambos os sinais no intervalo de 3:00 a 3:10 minutos (marcando as amostras).

### Dados de entrada

Foi utilizado o arquivo [`ECG_XYZ.txt(fs=1000Hz)`](<ECG_XYZ.txt(fs=1000Hz)>), que contém as amostras do ECG original e a coluna `SamplingInterval`, com o tempo em segundos. A frequência original indicada no arquivo é 1000 amostras/s.

### O que foi implementado

O código principal em [`main.py`](main.py) carrega o arquivo de entrada, chama as funções do item a e coordena a gravação dos resultados. As funções de interpolação e plotagem estão em [`item_a/utils.py`](item_a/utils.py).

A função `interpolar_dados` cria uma nova grade temporal com intervalo de 1/4000 s e interpola cada canal usando `numpy.interp`. O resultado é salvo em [`item_a/ECG_XYZ_4000Hz.csv`](item_a/ECG_XYZ_4000Hz.csv).

A função `plotar_sinal_ecg` gera, no intervalo de 180 a 190 segundos (3:00 a 3:10), um subplot por canal com o sinal original e o interpolado sobrepostos. Os sinais de cada canal compartilham uma cor; marcadores circulares maiores mostram as amostras originais, e a linha contínua mostra o sinal interpolado. A legenda indica a frequência de cada sinal. O gráfico é salvo como PNG a 220 dpi em [`item_a/ECG_03-00_a_03-10.png`](item_a/ECG_03-00_a_03-10.png).

#### Gráfico gerado

![Comparação dos canais originais e interpolados de ECG entre 3:00 e 3:10](item_a/ECG_03-00_a_03-10.png)

## Item b

> Desenvolva um algoritmo para detectar cada batimento, enquadrar, alinhar e promediar o complexo PQRST; apresentando o sinal promediado, número de complexos incluídos na promediação, número de rejeitados, estimativa do ruído residual, calcular o vetor magnitude utilizando as seguintes frequências passa-alta em 25, 40 e 80 Hz.

### Dados de entrada

O sinal de entrada do item b é o resultado interpolado do item a, [`item_a/ECG_XYZ_4000Hz.csv`](item_a/ECG_XYZ_4000Hz.csv), com frequência de amostragem definida explicitamente como 4000 Hz em [`main.py`](main.py). Os canais ortogonais considerados são `ChXGain5000`, `ChYGain5000` e `ChZGain5000`; a coluna `RefChXGain1000Inverted` é uma referência e não entra no cálculo do vetor magnitude.

### Método implementado

As funções do item estão em [`item_b/utils.py`](item_b/utils.py), e o encadeamento da análise e a gravação das saídas são feitos diretamente por [`main.py`](main.py). Para localizar os batimentos, o canal Y recebe um filtro Butterworth passa-banda com fase nula. A ordem dos filtros passa-banda e passa-alta é parametrizável e tem valor padrão 3. Na detecção, os cortes do passa-banda (5 e 25 Hz), o intervalo mínimo entre picos (400 ms) e o fator de proeminência (2 desvios-padrão) também são parâmetros com esses valores como padrão.

Cada batimento é enquadrado de 250 ms antes a 550 ms depois do pico R. Como os recortes são centrados no máximo R do sinal filtrado, ficam temporalmente alinhados. Os batimentos sem janela completa são rejeitados. Para a rejeição morfológica, cada janela multicanal é centralizada, normalizada e correlacionada com o molde mediano; são aceitas correlações de pelo menos 0,90 e acima do limite inferior de Tukey. O limite mínimo de correlação é parametrizável, com valor padrão 0,90. O complexo promediado é a média amostral dos complexos aceitos.

A estimativa de ruído residual é o valor RMS da diferença entre cada complexo aceito e o complexo médio, calculada separadamente para X, Y e Z. Para cada corte de 25, 40 e 80 Hz, os três canais recebem um passa-alta Butterworth de ordem 3 com fase nula; os complexos aceitos são novamente promediados e o vetor magnitude é calculado como `sqrt(X² + Y² + Z²)` em cada amostra.

### Resultados gerados

A execução atual, sobre os dados interpolados a 4000 Hz, detectou 293 complexos, dos quais 281 foram incluídos na promediação e 12 rejeitados (1 por borda e 11 por morfologia). Os RMS residuais foram 0,1059 no canal X, 0,2142 no canal Y e 0,1058 no canal Z. Esses valores e as contagens completas estão em [`item_b/resumo_item_b.csv`](item_b/resumo_item_b.csv).

- [`item_b/complexo_pqrst_promediado.csv`](item_b/complexo_pqrst_promediado.csv): sinal médio dos canais X, Y e Z, com o tempo relativo ao pico R.
- [`item_b/vetores_magnitude.csv`](item_b/vetores_magnitude.csv): vetores magnitude médios para os passa-altas de 25, 40 e 80 Hz.
- [`item_b/complexo_pqrst_promediado.png`](item_b/complexo_pqrst_promediado.png): gráfico dos complexos PQRST médios e respectivos RMS residuais.
- [`item_b/vetores_magnitude_passa_alta.png`](item_b/vetores_magnitude_passa_alta.png): comparação gráfica dos três vetores magnitude.

#### Gráficos gerados

![Complexos PQRST promediados](item_b/complexo_pqrst_promediado.png)

![Vetores magnitude com filtros passa-alta](item_b/vetores_magnitude_passa_alta.png)

### Dependência adicionada

Foi adicionada a dependência `scipy` em [`requirements.txt`](requirements.txt) para os filtros digitais Butterworth e a detecção de picos.

## Item c

> Determine em milissegundos todos os intervalos RR consecutivos do registro e faça o gráfico RR x Tempo.

### Dados de entrada

Foram utilizados os picos R detectados no item b a partir do sinal interpolado a 4000 Hz. Os instantes dos picos são obtidos na coluna `SamplingInterval` de `dados_interpolados` em [`main.py`](main.py).

### O que foi implementado

As funções específicas estão em [`item_c/utils.py`](item_c/utils.py). A função `calcular_intervalos_rr` calcula a diferença entre cada par consecutivo de picos R e converte o resultado para milissegundos. Cada intervalo é associado ao ponto médio temporal entre seus dois picos delimitadores, o que é usado no gráfico RR x Tempo produzido por `plotar_intervalos_rr`.

### Resultados gerados

Foram calculados 292 intervalos RR a partir dos 293 picos detectados no item b. Os valores variam de 705,25 ms a 1294,75 ms.

- [`item_c/intervalos_rr.csv`](item_c/intervalos_rr.csv): tempos inicial, final e médio de cada par de picos, além do intervalo RR em milissegundos.
- [`item_c/RR_x_Tempo.png`](item_c/RR_x_Tempo.png): gráfico de todos os intervalos RR consecutivos em função do tempo.

#### Gráfico gerado

![Intervalos RR consecutivos em função do tempo](item_c/RR_x_Tempo.png)

## Item d

## Item e

## Item f

## Item g

## Padrões do repositório

As instruções para organização do código, documentação das funções e atualização deste relatório estão registradas em [`AGENTS.md`](AGENTS.md).

A skill [`python-to-colab-notebook`](.agents/skills/python-to-colab-notebook/SKILL.md) orienta a conversão do código para um notebook do Google Colab, com as funções de cada item separadas das células de execução e os gráficos exibidos diretamente no notebook.

A skill [`update-python-from-notebook`](.agents/skills/update-python-from-notebook/SKILL.md) orienta a sincronização das mudanças funcionais do notebook de volta aos módulos Python, ignorando adaptações exclusivas do Colab.

A documentação do projeto, incluindo os textos explicativos dos notebooks, deve ser mantida em português.
