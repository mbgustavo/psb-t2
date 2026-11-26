# Instruções do repositório

## Organização do trabalho

- Consulte `README.md` antes de alterar a organização ou o fluxo de execução do projeto.
- O enunciado oficial de cada item está em `PDS_Homework202xB.pdf`. Antes de implementar ou resolver um item, localize e leia no PDF o enunciado correspondente, incluindo observações relevantes.
- Para resolver um item `X`, coloque as funções específicas em `item_x/`, seguindo o padrão já usado no projeto. Chame essas funções a partir de `main.py` e salve os arquivos gerados dentro da mesma pasta `item_x/`.
- Mantenha em `main.py` o fluxo principal que carrega os dados, chama as funções dos itens e coordena os resultados.
- Atualize `requirements.txt` se a implementação introduzir novas dependências.
- Atualize `README.md` quando a organização, a configuração ou o modo de execução do projeto mudar.

## Documentação do código

- Toda função criada deve ter uma docstring que descreva seu propósito e os parâmetros recebidos. Documente também o valor retornado quando houver retorno.
- Use nomes de funções, variáveis e comentários em português, seguindo o padrão existente no projeto.
- Mantenha em português toda a documentação do repositório, incluindo README, relatório, comentários e textos explicativos de notebooks.

## Relatório

- Toda implementação ou alteração funcional deve ser registrada em `RELATORIO.md`.
- Siga a estrutura atual do relatório: mantenha o enunciado geral do item 1 e documente cada item em sua própria seção, organizando a metodologia, os resultados e sua análise em subseções correspondentes.
- Consulte o enunciado no PDF e descreva com precisão a metodologia aplicada, os resultados obtidos e sua análise. Registre limitações ou partes do enunciado ainda não atendidas; não apresente como concluído o que não foi realizado.
- Descreva no relatório a metodologia e os detalhes de implementação necessários para que os procedimentos sejam compreensíveis e reproduzíveis, incluindo bibliotecas utilizadas, parâmetros, filtros, critérios de seleção e etapas de cálculo. Apresente esses detalhes em prosa, sem citar arquivos de código ou dados, nomes de funções e variáveis, nem chamadas entre arquivos. Organize cada item em metodologia, resultados e análise; atualize essas seções quando houver mudanças relevantes.
- Ao criar ou alterar documentação do repositório, registre a mudança em uma seção apropriada do `RELATORIO.md`, sem apagar nem contradizer o histórico dos itens.

## Google Colab

- A skill local para converter o projeto em notebook está em `.agents/skills/python-to-colab-notebook/SKILL.md`. Consulte-a quando a tarefa pedir uma versão Google Colab, mantendo um bloco de funções e outro de execução para cada item e exibindo gráficos no notebook sem salvá-los em arquivos.
- A skill local para sincronizar alterações funcionais de um notebook de volta ao projeto Python está em `.agents/skills/update-python-from-notebook/SKILL.md`. Preserve diferenças próprias do Colab, como instalação no runtime, upload, estado entre células e exibição inline de gráficos.
