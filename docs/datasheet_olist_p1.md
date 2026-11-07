# Datasheet - base Olist para Voice of Customer

Versão da entrega P1: 1.0.0, 07/11/2026. Responsável pela frente: Pedro.
Fonte: Brazilian E-Commerce Public Dataset by Olist, obtido no Kaggle.
URL: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data
Uso pretendido: recuperar avaliações escritas e produzir sínteses rastreáveis.
Não é uma base de estoque atual nem uma amostra aleatória de todos os consumidores.

## Origem e linhagem

ZIP obtido na fonte oficial em 03/11/2026; o download completo não é versionado.
Arquivo extraído sem alterações: `../data/raw/olist_order_reviews_dataset.csv`.
Fluxo: CSV original -> `explorar_avaliacoes.py` -> `reviews_preparadas.csv` ->
`construir_base.py` e `documentos.py` -> `reviews_documentos.jsonl`.
O CSV tem 99.224 linhas e sete colunas. Datas de criação de avaliações observadas:
02/10/2016 a 31/08/2018. Essas datas não são datas de compra nem de entrega.

Checkpoint da preparação: `1363122f6dcc00be6119b20404a04c1b6ce43a27` do André.
Execução local reproduzida em 04/11/2026: Python 3.12.14, Pandas 3.0.1.
O requirements do checkpoint pede Pandas 2.3.3; instalação limpa de toda a stack
continua pendente. Essa diferença não alterou o perfil documental reproduzido.

SHA-256 do CSV: `012b61c7593e34f51fa614efdf802b9c7056ce6aae5307ddb93236e7cfc797d7`.
SHA-256 do JSONL: `3519b8a9653c35c386d43959663beb4a9ee804f425a4568b7aac082c458043ce`.
JSONL: 22.432.974 bytes, UTF-8, 42.687 objetos, um por linha, sem cabeçalho.

## Seleção e tratamento

| Indicador | Quantidade |
|---|---:|
| Avaliações originais | 99.224 |
| Sem título nem comentário | 56.537 |
| Documentos com texto | 42.687 |
| Somente título | 1.737 |
| Somente comentário | 31.121 |
| Título e comentário | 9.829 |
| Textos distintos pelo hash atual | 36.712 |
| Ocorrências adicionais de textos repetidos | 5.975 |
| Grupos repetidos | 1.203 |
| Maior número de ocorrências do mesmo texto | 351 |

Valores ausentes de título e comentário viram texto vazio para seleção. Uma linha
sem ambos é excluída somente do recorte textual, preservando o arquivo original.
Espaços consecutivos são normalizados. Acentos, pontuação e negações são mantidos.
Não foram aplicados stemming, tradução, remoção de stopwords ou correção automática
das falas. Título e comentário recebem rótulos e são unidos por quebra de linha.

Uma avaliação por documento, sem fragmentação: mediana de 10 palavras, P95 de 34
e máximo de 50 no indicador existente. Atenção: esse indicador inclui os rótulos.
Há 5.778 documentos de até três palavras incluindo rótulos e 8.503 excluindo-os.
Não usar esse indicador como contagem de tokens do modelo.

IDs naturais repetidos foram preservados: 814 ocorrências adicionais de review_id
na base completa e 317 no recorte textual. Isso não prova duplicação indevida.
Textos iguais podem pertencer a avaliações diferentes. Não apagar automaticamente.
No contexto do RAG, agrupar cópias por hash e manter associação aos IDs de origem.

## Dicionário de dados entregue

| Campo | Tipo e regra |
|---|---|
| `id` | string única `olist_review_row_XXXXXX`, posição de linha do CSV original |
| `page_content` | título e/ou comentário não vazio, com rótulos |
| `metadata.document_id` | igual ao ID técnico |
| `metadata.review_id` | ID original; string ou null; pode repetir |
| `metadata.order_id` | ID do pedido; string ou null |
| `metadata.review_score` | inteiro de 1 a 5; null se inválido |
| `metadata.review_creation_date` | data da avaliação em AAAA-MM-DD; null se inválida |
| `metadata.tipo_texto` | `ambos`, `somente_titulo`, `somente_comentario` |
| `metadata.fonte` | nome do CSV de avaliações |
| `metadata.n_palavras` | split por espaços, incluindo rótulos |
| `metadata.hash_texto` | SHA-256 de page_content.casefold() em UTF-8 |

Não ordenar ou filtrar o CSV antes da atribuição do ID técnico. O ID depende da
ordem e do arquivo de origem. Não renomear campos sem versionar o contrato.
ChromaDB: omitir metadados null no momento da inserção. E5: adicionar `passage: `
ao indexar e `query: ` ao consultar, sem inserir esses prefixos no JSONL canônico.

## Representatividade e limites

| Nota | Base completa | Base textual |
|---|---:|---:|
| 1 | 11.424 | 8.829 |
| 2 | 3.151 | 2.165 |
| 3 | 8.179 | 3.643 |
| 4 | 19.142 | 6.274 |
| 5 | 57.328 | 21.776 |

O recorte textual contém cerca de 43% dos registros. As notas 1 e 2 correspondem
a aproximadamente 14,69% da base completa e 25,75% da textual. Não generalizar
distribuições ou temas do recorte para todos os pedidos ou consumidores.
Notas não substituem interpretação: há elogios com ressalvas e notas altas com
reclamações. Alegações do cliente são relatos, não diagnósticos técnicos comprovados.
Um ranking Top-K não mede frequência global de problemas. Não inferir percentuais,
causas, transportadora ou solução de um problema sem suporte explícito.

## Qualidade, acesso e reprodução

Todos os 42.687 documentos foram conferidos contra o CSV original quanto a texto,
IDs, nota, data, fonte e hash. O perfil é igual ao checkpoint. Os testes originais
de preparação passaram. Não houve execução local de E5, Chroma ou gerador nesta
entrega P1; o relatório do colega sobre indexação não substitui essa reprodução.

Dados brutos e JSONL completo permanecem locais. O benchmark versiona somente
os trechos selecionados necessários aos casos e suas fixtures de teste.
O fato de o dataset ser público não dispensa conferir possíveis dados pessoais em
texto livre. Não foi feita anonimização completa nem certificação de ausência de PII.
Na aplicação, minimizar conteúdo enviado ao provedor e exposto em logs.
Material teórico personalizado da FIAP não deve ser copiado para o repositório público.

Evidências: [auditoria do corpus](../reports/validacao_local_dados.json),
[perfil original](../reports/perfil_olist.json), [perfil textual](../reports/perfil_documentos.json),
[guia de integração](tech_challenge_fase4_entrega_p1.pdf).

Reproduzir da raiz do projeto com o Python do ambiente:

```powershell
python scripts/explorar_avaliacoes.py
python scripts/construir_base.py
python scripts/validar_entrega_dados.py
python scripts/preparar_avaliacao_p1.py
python scripts/auditar_avaliacao_p1.py
```

O manifesto congelado do benchmark impede alterações silenciosas em conteúdo e
divisão. Uma revisão do gabarito ou do corpus exige versão explícita e registro.
