---
name: python-to-colab-notebook
description: Converta um projeto ou trabalho Python existente em um notebook Google Colab, organizado por item e com gráficos exibidos no próprio notebook.
---

# Converter um projeto para Google Colab

Use esta skill quando o usuário pedir para transferir, adaptar ou organizar código Python existente em um notebook Google Colab. Preserve o objetivo da implementação atual e os requisitos do trabalho.

## Fluxo

1. Consulte as instruções e a documentação do repositório. Leia o código-fonte, os dados e o enunciado relevante, quando houver. Identifique as funções de cada item, o fluxo de execução, as dependências, os arquivos de entrada e os resultados gerados.
2. Crie ou atualize um notebook `.ipynb` no local solicitado pelo usuário. Se ele não indicar um local, use uma pasta `notebooks/` no projeto e um nome de arquivo descritivo. Preserve os demais arquivos do projeto, a menos que o usuário peça para movê-los ou substituí-los.
3. Inclua uma célula inicial concisa de configuração quando for necessário instalar dependências. Mantenha nela os imports e a configuração compartilhada; agrupe as funções específicas junto ao item correspondente.
4. Organize cada item no mesmo formato:
   - Um título Markdown com o nome do item.
   - Uma subseção e uma célula de código com as funções usadas pelo item. Inclua docstrings descritivas nas funções.
   - Uma subseção e uma célula de código que carregue ou prepare os dados do item, chame as funções e apresente os resultados.
   - Em seguida, comece o próximo item repetindo esse formato.
5. Preserve a ordem dos itens do trabalho. Use o PDF como fonte dos enunciados; não deduza requisitos apenas pelo código. Mantenha explícitas no notebook as limitações conhecidas.
6. Adapte o acesso a arquivos para o Colab. Mantenha claros os nomes dos arquivos de entrada e ofereça uma forma prática de disponibilizá-los no ambiente de execução. Não presuma que o Google Drive esteja montado; só inclua a montagem quando for solicitada ou quando o projeto depender claramente dela.
7. Exiba os gráficos diretamente no notebook. Substitua a gravação de gráficos em arquivo por `plt.show()` ou mecanismo equivalente e não use `savefig` para os gráficos. Feche as figuras depois de exibi-las, se necessário. Mantenha outros arquivos de saída, como CSV, somente quando forem exigidos pelo trabalho ou pelo fluxo existente.
8. Garanta que as células de execução chamem as funções do item na ordem correta e usem as variáveis atuais do notebook. Evite importar módulos do projeto que o notebook deva substituir por células com as definições das funções.
9. Siga as instruções do repositório para dependências e documentação. A conversão do código existente para o notebook, por si só, não exige atualização do `RELATORIO.md`; esse relatório deve ser atualizado quando houver implementação ou alteração funcional no código Python. Atualize o `README.md` se o ponto de entrada ou as instruções de execução do projeto mudarem.

## Qualidade do notebook

- Escreva em português o Markdown, os títulos e os textos explicativos do notebook, seguindo o idioma da documentação do repositório.
- Use títulos claros e explicações curtas para separar a definição das funções de sua execução.
- Mantenha cada item suficientemente autocontido para que as funções possam ser entendidas antes da célula de execução.
- Use a exibição nativa do notebook para gráficos e resumos de dados. Não deixe referências a arquivos de imagem que o notebook não gera.
- Preserve rótulos, unidades, legendas e o intervalo de tempo pedidos em cada gráfico.
- Não afirme que o notebook foi verificado sem executar as células na ordem ou validar seu funcionamento de outra forma. Se o Colab não estiver disponível, informe o que não pôde ser verificado.
