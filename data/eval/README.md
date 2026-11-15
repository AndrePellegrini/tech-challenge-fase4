# Casos de exemplo

`casos_exemplo.jsonl` é um conjunto ilustrativo de 6 perguntas para testar
rapidamente o fluxo pergunta -> busca -> contexto -> LLM -> resposta.

Ele **não substitui** o benchmark oficial da frente de dados (P1), que está
versionado em [`evaluation/`](../../evaluation/README.md): 30 casos (20
respondíveis, 4 de insuficiência, 3 fora do escopo e 3 adversariais),
divididos em 18 de desenvolvimento e 12 reservados para a avaliação final.

Para os exemplos usados na documentação, ver
[`scripts/gerar_exemplos.py`](../../scripts/gerar_exemplos.py) e
[`docs/exemplos.md`](../../docs/exemplos.md).
