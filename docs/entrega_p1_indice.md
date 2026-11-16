# Entrega P1 - dados e avaliação

Pacote de dados e avaliação para continuidade da implementação.

| Entrega | Artefato | Situação |
|---|---|---|
| 1. Trinta casos e evidências | `evaluation/definicoes_casos.json`, `definicoes_limites.json` e gabaritos por split | Preparados; conferência estrutural concluída; revisão humana pendente |
| 2. Desenvolvimento/teste | `evaluation/manifesto_congelado.json` | 18/12, hashes fixados e zero texto de evidência idêntico entre splits |
| 3. Documentação dos dados | `docs/datasheet_olist_p1.md` | Consolidada, com linhagem, campos e limites |
| 4. Revisão P2/P3 | `docs/revisao_p2_p3_p1.md`, verificador e ficha humana | Revisão do código disponível concluída; avaliação de respostas reais e revisão conjunta pendentes da integração |

Leia [instruções de avaliação](../evaluation/README.md),
[datasheet](datasheet_olist_p1.md) e [passagem P2/P3](revisao_p2_p3_p1.md).
O resumo em PDF está em [guia de continuidade](tech_challenge_fase4_entrega_p1.pdf).

Para regenerar o PDF: instalar `requirements-pdf.txt` e executar
`python scripts/gerar_resumo_p1_pdf.py`. A saída padrão fica em `docs/`.

Validações executadas: corpus original preservado; trechos do gabarito literais;
composição de 30 casos correta; fixture maliciosa isolada; cinco testes de preparação
e nove testes do verificador aprovados. Não foram executados modelos de geração ou
embeddings. Não atribuir métricas ao RAG com base nesses testes.
