
# Etapa 2 - Construcao da Base de Conhecimento

## 1. Objetivo

Transformar as avaliacoes textuais do dataset Brazilian E-Commerce
Public Dataset by Olist em documentos estruturados para uso posterior
em um pipeline Retrieval-Augmented Generation (RAG).

Esta etapa atende ao requisito de construcao da base de conhecimento
do Tech Challenge da Fase 4.

## 2. Referencias academicas

- NLP - Aula 2: Pre-processamento de Textos.
- NLP - Aula 4: Embeddings e Representacoes Semanticas.
- LangChain - Aula 3: Vector Databases and Memory Management.
- IA Generativa - Aula 2: Retrieval-Augmented Generation (RAG).

## 3. Dados de entrada

Arquivo: `data/processed/reviews_preparadas.csv`

Origem: `olist_order_reviews_dataset.csv`, preparado na Etapa 1.

### Perfil inicial da Olist

| Indicador | Quantidade |
|---|---:|
| Total de avaliacoes | 99.224 |
| Avaliacoes com texto aproveitavel | 42.687 |
| Avaliacoes sem texto | 56.537 |
| Somente titulo | 1.737 |
| Somente comentario | 31.121 |
| Titulo e comentario | 9.829 |

Foram selecionados inicialmente os registros que possuem titulo
e/ou comentario textual.

O dataset original permanece preservado.

## 4. Estrategia de processamento

O processamento foi implementado nos arquivos:

- `src/preprocessing/documentos.py`
- `scripts/construir_base.py`

As principais transformacoes sao:

1. Verificar a existencia das colunas obrigatorias.
2. Validar a unicidade do identificador tecnico.
3. Normalizar espacos nos titulos e comentarios.
4. Preservar palavras, acentos, pontuacao e negacoes.
5. Combinar titulo e comentario quando ambos estiverem presentes.
6. Gerar um documento por avaliacao textual.
7. Preservar os identificadores originais como metadados.
8. Padronizar notas e datas.
9. Gerar hashes para identificar textos repetidos.
10. Calcular estatisticas de qualidade e comprimento.
11. Salvar os documentos no formato JSONL.

Nao foram aplicados stemming, lematizacao, remocao de stopwords,
deduplicacao automatica ou chunking.

## 5. Estrutura dos documentos

Cada documento possui tres componentes principais:

- `id`: identificador tecnico unico.
- `page_content`: texto da avaliacao para recuperacao semantica.
- `metadata`: informacoes para rastreabilidade e analise.

Os metadados incluem:

- `document_id`
- `review_id`
- `order_id`
- `review_score`
- `review_creation_date`
- `tipo_texto`
- `fonte`
- `n_palavras`
- `hash_texto`

A estrutura foi organizada para permitir a futura conversao
dos registros em documentos utilizados pelo pipeline RAG.

## 6. Resultados obtidos

A execucao da Etapa 2 produziu o seguinte perfil:

| Indicador | Valor |
|---|---:|
| Linhas de entrada | 42.687 |
| Documentos gerados | 42.687 |
| Somente titulo | 1.737 |
| Somente comentario | 31.121 |
| Titulo e comentario | 9.829 |
| Review IDs repetidos no recorte | 317 |
| Textos repetidos | 5.975 |
| Notas invalidas | 0 |
| Datas invalidas | 0 |
| Palavras P50 | 10 |
| Palavras P95 | 34 |
| Maximo de palavras | 50 |
| Documentos com ate 3 palavras | 5.778 |

### Interpretacao

O numero de documentos gerados corresponde exatamente ao numero de
registros de entrada: 42.687.

Nao houve perda de quantidade durante a construcao documental.

Foram identificadas 5.975 ocorrencias adicionais de textos
repetidos, equivalentes a aproximadamente 14,00% dos documentos.

Foram identificados 5.778 documentos com ate 3 palavras,
equivalentes a aproximadamente 13,54% da base textual.

Esses registros foram mantidos.

Os indicadores de repeticao textual nao comprovam a existencia
de registros integralmente duplicados.

## 7. Distribuicao das notas na base textual

| Nota | Quantidade |
|---|---:|
| 1 | 8.829 |
| 2 | 2.165 |
| 3 | 3.643 |
| 4 | 6.274 |
| 5 | 21.776 |
| Total | 42.687 |

As notas 1 e 2 representam aproximadamente 25,75% da base
textual, enquanto representam 14,69% da base completa.

As notas 4 e 5 representam aproximadamente 65,71% da base
textual, enquanto representam 77,07% da base completa.

Portanto, a distribuicao das notas e diferente entre os dois
recortes. Os resultados obtidos com comentarios textuais nao
devem ser automaticamente generalizados para todas as avaliacoes.

## 8. Estrategia de chunking

Decisao inicial: nao utilizar chunking.

Justificativa:

- Mediana de 10 palavras por documento.
- Percentil 95 de 34 palavras.
- Maior documento com 50 palavras.
- Uma avaliacao ja representa uma unidade logica de experiencia.

Dividir comentarios curtos poderia fragmentar o contexto
necessario para compreender corretamente os relatos.

A decisao sera reavaliada durante os testes de recuperacao.

Referencia: `docs/decisoes.md`, decisao D005.

## 9. Tratamento de repeticoes e textos curtos

Textos repetidos e comentarios curtos foram preservados.

A exclusao automatica poderia remover relatos distintos
e distorcer analises posteriores.

O sistema RAG devera preservar a rastreabilidade das fontes
e considerar que a busca semantica nao corresponde a uma
contagem estatistica de temas na base.

Referencia: `docs/decisoes.md`, decisao D006.

## 10. Arquivos gerados

- `data/processed/reviews_documentos.jsonl`
- `reports/perfil_documentos.md`
- `reports/perfil_documentos.json`

O arquivo JSONL contem textos de avaliacoes e deve permanecer
fora do repositorio publico.

Os relatorios agregados podem ser usados para documentar
a qualidade da base.

## 11. Como reproduzir

Na raiz do projeto, executar:

    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

Em seguida:

    .\.venv\Scripts\python.exe scripts/construir_base.py

A execucao do script gerou os resultados apresentados neste
documento.

O resultado detalhado dos testes automatizados deve ser
registrado e conferido separadamente.

## 12. Limitacoes

- A base textual e um recorte das avaliacoes originais.
- Existem textos repetidos e documentos muito curtos.
- IDs naturais repetidos nao foram excluidos automaticamente.
- Nenhum embedding foi criado nesta etapa.
- Nenhum banco vetorial foi construido nesta etapa.
- A qualidade da recuperacao semantica ainda nao foi avaliada.
- A frequencia de temas nao pode ser inferida somente dos
  documentos mais similares recuperados por um RAG.

## 13. Conclusao

A Etapa 2 produziu 42.687 documentos estruturados,
preservando todos os registros textuais de entrada.

A base esta preparada para iniciar os experimentos com
embeddings e recuperacao vetorial.

## 14. Proxima etapa

Etapa 3 - Embeddings e Indexacao Vetorial.

Atividades previstas:

1. Avaliar modelos de embeddings adequados ao portugues.
2. Selecionar uma estrategia inicial de indexacao.
3. Gerar vetores para os documentos.
4. Construir o indice vetorial.
5. Testar consultas semanticas.
6. Avaliar a relevancia dos resultados recuperados.
7. Documentar as escolhas e limitacoes.
