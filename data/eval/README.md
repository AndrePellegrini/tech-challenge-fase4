# Casos de avaliacao

`casos_exemplo.jsonl` e um conjunto ilustrativo de 6 perguntas para testar
o fluxo pergunta -> busca -> contexto -> LLM -> resposta de ponta a ponta.

Ele **nao substitui** o benchmark oficial de 30 casos (20 respondiveis, 4
de insuficiencia, 3 fora do escopo e 3 adversariais) preparado pela frente
de dados (P1), que e um artefato local e nao foi incluido neste
repositorio. Usar o pacote `evaluation/` do P1 assim que estiver
disponivel, preservando os 12 casos reservados para a avaliacao final.
