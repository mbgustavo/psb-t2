# Trabalho de Processamento Digital de Sinais

Este repositório contém o trabalho cujos enunciados estão no arquivo **`PDS_Homework202xB.pdf`**. O arquivo **`ECG_XYZ.txt(fs=1000Hz)`** é o dado de entrada utilizado para o processamento do sinal de ECG.

## Organização do projeto

- `main.py`: código principal do trabalho. Ao ser executado, carrega os dados e chama as funções correspondentes a cada item.
- `item_X/`: pasta destinada às funções específicas e aos arquivos gerados para o item `X`.
- `requirements.txt`: dependências Python do projeto.
- `PDS_Homework202xB.pdf`: enunciados do trabalho.
- `ECG_XYZ.txt(fs=1000Hz)`: dados originais do sinal de ECG.
- `RELATORIO.md`: Relatório do que foi feito no trabalho.

À medida que novos itens forem implementados, suas funções e arquivos de resultado devem ficar em pastas próprias, seguindo o padrão `item_X/`.

## Interface gráfica

Como etapa futura, o projeto deverá possuir uma interface gráfica para facilitar a interação com as funcionalidades do trabalho.

## Configuração e execução

Crie e ative um ambiente virtual, instale as dependências e execute o código principal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Os arquivos de saída são gravados na pasta do item correspondente.
