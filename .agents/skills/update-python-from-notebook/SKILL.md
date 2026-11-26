---
name: update-python-from-notebook
description: Compare um notebook Colab com o código Python do repositório e sincronize mudanças funcionais, preservando diferenças exclusivas do notebook.
---

# Sincronizar notebook com Python

Use esta skill quando o usuário pedir para verificar ou trazer para o projeto mudanças feitas em um notebook Google Colab. O notebook é a fonte das alterações funcionais a sincronizar; o código Python do repositório mantém a organização e os comportamentos próprios do projeto.

## Fluxo

1. Leia `AGENTS.md`, `README.md` e `RELATORIO.md`. Localize o notebook relevante e os arquivos Python associados. Se houver mais de um notebook plausível e não for possível identificar o atualizado, peça ao usuário que indique qual usar.
2. Quando o trabalho for dividido em itens, consulte no PDF o enunciado de cada item afetado. Use a organização das células do notebook: para cada item, uma seção com as funções e outra seção com a execução; em seguida começa o item seguinte no mesmo formato.
3. Compare as definições funcionais do notebook com os módulos Python em `item_x/` e com as chamadas de `main.py`. Identifique alterações de algoritmos, parâmetros, tratamentos de dados, cálculos, resultados e rótulos técnicos que representem comportamento do item.
4. Sincronize no Python as mudanças funcionais que estejam no notebook e ainda não estejam refletidas no projeto. Integre-as à estrutura existente, preserve funções de item em `item_x/`, as chamadas em `main.py` e os caminhos de saída próprios do projeto. Não substitua arquivos inteiros por blocos do notebook se isso remover comportamento Python ainda necessário.
5. Ignore diferenças que existam apenas para adaptar o notebook ao Colab, incluindo:
   - Células Markdown, títulos e explicações de apresentação do notebook.
   - Instalação de pacotes no runtime, imports exclusivos do Colab, upload de arquivos e montagem de Google Drive.
   - Ordem ou divisão de células, variáveis temporárias de execução e estado mantido entre células.
   - Exibir figuras inline com `plt.show()` em vez de salvar gráficos com `savefig` nos scripts Python.
   - Remoção de gravação de resultados em arquivo quando ela tiver sido feita apenas para evitar arquivos no notebook, sem mudar o cálculo solicitado.
6. Preserve nos arquivos Python as diferenças que são parte do produto do repositório: função principal executável, leitura dos arquivos de entrada, geração de arquivos requeridos pelo fluxo atual e gráficos salvos na pasta do item quando o projeto assim define. Não transplante instruções de interface do Colab para módulos Python.
7. Documente toda função nova com docstring em português. Mantenha a documentação em português e não altere requisitos de dependências com base apenas em comandos de instalação específicos do Colab.
8. Atualize a subseção correspondente de `RELATORIO.md` em português. Descreva apenas as mudanças funcionais sincronizadas no projeto Python e atualize referências a código e resultados gerados. Não descreva diferenças exclusivas de apresentação ou execução do notebook como mudanças do projeto.
9. Se a diferença não puder ser classificada com confiança como funcional ou exclusiva do notebook, compare-a com o enunciado e o uso no projeto. Integre mudanças funcionais reversíveis quando possível; se uma alteração puder remover comportamento importante e a intenção continuar ambígua, pare antes de sobrescrevê-la e esclareça a divergência.

## Validação

- Verifique os arquivos modificados e confirme que `main.py` chama as funções atualizadas com os argumentos corretos.
- Execute o fluxo quando isso for possível e apropriado para regenerar resultados que mudaram. Não afirme que o código foi executado se a validação não ocorreu.
- Informe quais diferenças funcionais foram sincronizadas e quais foram ignoradas por serem próprias do notebook.
