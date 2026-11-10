# Diario de desenvolvimento

## 02/11/2026 - Inicio da Fase 4

- Enunciado identificado: Voice of Customer Intelligence com RAG.
- Prazo: 17/11/2026.
- Objetivos obrigatorios: base de conhecimento, recuperacao semantica, resposta com evidencias, tratamento de falta de informacao.
- Entregaveis: GitHub publico e video de ate 7 minutos.
- Materiais de apoio: NLP, LangChain e IA Generativa (17 aulas).
- Proxima tarefa: executar `scripts/explorar_avaliacoes.py` sobre o CSV original.

## Etapa 1 - Resultado (preencher apos executar)

- Total de registros: PENDENTE
- Linhas com comentario: PENDENTE
- Linhas somente com titulo: PENDENTE
- Linhas aproveitaveis: PENDENTE
- IDs repetidos: PENDENTE
- Decisao de recorte: PENDENTE


## Etapa 2 - Construcao da base documental (02/11/2026)

**Status:** processamento executado; perfil documental analisado.

### Objetivo

Transformar os registros textuais da Olist em documentos estruturados
para alimentar futuramente o pipeline RAG.

### Implementacoes realizadas

- Estruturacao dos documentos com `id`, `page_content` e `metadata`.
- Normalizacao de espacos sem remover negacoes ou acentos.
- Preservacao de identificadores e avaliacoes repetidas.
- Criacao de hashes para identificar repeticoes textuais.
- Validacao de notas e datas.
- Geracao da base em formato JSONL.
- Geracao de relatorios agregados de qualidade.
- Criacao de testes automatizados para as regras de processamento.

### Resultados observados

- Registros de entrada: 42.687.
- Documentos produzidos: 42.687.
- Somente titulo: 1.737.
- Somente comentario: 31.121.
- Titulo e comentario: 9.829.
- Review IDs repetidos no recorte: 317.
- Textos repetidos: 5.975.
- Notas invalidas: 0.
- Datas invalidas: 0.
- Mediana de palavras (P50): 10.
- Percentil 95 de palavras (P95): 34.
- Maximo de palavras: 50.
- Documentos com ate 3 palavras: 5.778.

### Analise

Nao houve perda de quantidade entre a entrada textual e a
base documental produzida.

Os documentos sao predominantemente curtos, tornando
desnecessario o chunking na estrategia inicial.

A base textual apresenta distribuicao de notas diferente
da base completa. Por isso, conclusoes sobre os comentarios
nao devem ser generalizadas automaticamente para todas
as avaliacoes da Olist.

### Decisoes registradas

- D005: manter uma avaliacao por documento, sem chunking inicial.
- D006: preservar repeticoes e explicitar o recorte textual.

### Validacao

- Consistencia dos totais do relatorio: conferida.
- Integridade quantitativa da transformacao: conferida.
- Testes automatizados: resultado detalhado ainda nao compartilhado.
- Recuperacao semantica: nao iniciada.

### Proximo passo

Etapa 3 - Embeddings e Indexacao Vetorial.



## Etapa 3.1 - Experimento inicial com embeddings (02/11/2026)

**Status:** experimento executado e resultados preliminares analisados.

### Objetivo

Avaliar a recuperacao semantica de comentarios da Olist utilizando embeddings locais.

### Implementacao

Arquivo: `scripts/testar_embeddings.py`

Modelo: `intfloat/multilingual-e5-small`

Biblioteca: `sentence-transformers`

Configuracao:
- Amostra aleatoria de 1.000 documentos.
- Semente fixa: 42.
- Embeddings com 384 dimensoes.
- Normalizacao dos vetores.
- Prefixos `query:` e `passage:`.
- Recuperacao dos cinco resultados mais similares.

### Resultados tecnicos

- Documentos disponiveis: 42.687.
- Documentos utilizados no experimento: 1.000.
- Dimensoes dos vetores: 384.
- Consultas executadas: 3.
- Resultados recuperados: 15.
- Execucao concluida sem erros.

### Analise qualitativa

Pergunta 1 - Atraso na entrega:
- Foram recuperados comentarios relacionados a atrasos.
- Algumas reclamacoes apresentaram notas positivas.
- Um comentario longo foi exibido parcialmente.

Pergunta 2 - Problemas de qualidade:
- Quatro resultados apresentaram reclamacoes pertinentes.
- Um resultado positivo, "Produto com qualidade", foi recuperado.
- Foi identificada uma limitacao relacionada a polaridade.

Pergunta 3 - Elogios:
- Os cinco resultados recuperados estavam relacionados a experiencias positivas.
- Foram identificados elogios a entrega, produtos, embalagem e atendimento.

A avaliacao preliminar identificou aproximadamente 14 resultados
aparentemente relevantes entre 15 exibidos.

Esse numero nao representa uma metrica formal de desempenho
nem comprova a qualidade do modelo em toda a base.

### Testes automatizados

Comando executado:

    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

Resultado:
- 5 testes executados.
- 5 testes aprovados.
- Nenhuma falha.

### Decisao tecnica

D007 - Utilizar provisoriamente o multilingual-e5-small
na primeira implementacao de recuperacao vetorial.

### Limitacoes e pendencias

- A avaliacao utilizou apenas 1.000 documentos.
- Ainda nao existe conjunto formal de relevancia rotulado.
- A recuperacao pode confundir comentarios positivos e negativos.
- Similaridade alta nao representa probabilidade de acerto.
- Ainda nao foi construido um banco vetorial persistente.
- Ainda nao foi integrado um modelo gerador de respostas.

### Proxima atividade

Etapa 3.2 - Construir e testar um indice vetorial
persistente utilizando ChromaDB.


## Etapa 3.2 - Indexacao vetorial com ChromaDB (02/11/2026)

**Status:** concluida e validada com uma amostra de 1.000 documentos.

### Objetivo

Implementar e testar a persistencia de um banco vetorial local,
utilizando os embeddings das avaliacoes textuais da Olist.

### Tecnologias utilizadas

- Python.
- ChromaDB.
- Sentence Transformers.
- Modelo `intfloat/multilingual-e5-small`.
- Embeddings normalizados com 384 dimensoes.
- Similaridade de cosseno.

### Implementacao

Arquivo: `scripts/testar_chromadb.py`

Configuracao:
- Amostra aleatoria de 1.000 documentos.
- Semente fixa: 42.
- Insercao em lotes de 100.
- Colecao: `olist_e5_piloto_1000_v1`.
- Cliente: `PersistentClient`.
- Cinco resultados por consulta.
- Preservacao dos textos e metadados.

### Resultados da primeira execucao

- Documentos indexados: 1.000.
- Perguntas testadas: 3.
- Resultados recuperados: 15.
- Indexacao concluida sem erros.

Os resultados recuperados coincidiram com os resultados
do experimento anterior utilizando NumPy.

### Teste de persistencia

O script foi executado novamente apos a indexacao inicial.

Mensagem observada:

    Colecao ja indexada. Reutilizando os vetores.

Contagem observada:

    Total no banco vetorial: 1000

A segunda execucao reutilizou os embeddings persistidos,
sem recalcular os vetores dos documentos.

As tres consultas retornaram os mesmos documentos,
na mesma ordem e com as mesmas similaridades arredondadas.

### Conclusao

O ChromaDB foi validado como banco vetorial local para
a primeira implementacao do RAG.

A decisao tecnica foi registrada em D008.

### Limitacoes

- Apenas 1.000 documentos foram indexados.
- A recuperacao ainda precisa de avaliacao formal.
- Consultas negativas podem recuperar comentarios positivos.
- O pipeline ainda nao possui um modelo gerador de respostas.

### Pendencias

- Preparar a protecao dos arquivos locais no Git.
- Indexar os 42.687 documentos.
- Validar consultas na base completa.
- Avaliar a qualidade da recuperacao.
- Implementar a geracao de respostas fundamentadas.

### Proxima etapa

Etapa 3.3 - Indexacao completa da base textual.



## Etapa 3.3 - Indexacao completa da Olist (02/11/2026)

**Status:** indexacao concluida; avaliacao da recuperacao em andamento.

### Objetivo

Construir um indice vetorial com todos os 42.687 documentos
textuais selecionados da Olist.

### Implementacao

Arquivo: `scripts/indexar_base_completa.py`

Tecnologias:
- Python.
- Sentence Transformers.
- Modelo `intfloat/multilingual-e5-small`.
- ChromaDB.
- Similaridade de cosseno.

### Configuracao

- Colecao: `olist_e5_full_42687_v1`.
- Embeddings: 384 dimensoes.
- Lotes de indexacao: 128.
- Lotes de inferencia: 32.
- Prefixo de documentos: `passage:`.
- Prefixo de perguntas: `query:`.
- Processamento incremental.
- Verificacao da origem por SHA-256.

### Resultado da indexacao

Documentos carregados: 42.687.
Documentos esperados: 42.687.
Documentos armazenados: 42.687.

Mensagem final observada:

    INDEXACAO COMPLETA VALIDADA
    Total no ChromaDB: 42687

Assinatura SHA-256 da base:

    3519b8a9653c35c386d43959663beb4a9ee804f425a4568b7aac082c458043ce

A execucao terminou sem erros.

### Avaliacao qualitativa inicial

Foram realizadas tres perguntas, com cinco documentos recuperados
por pergunta.

1. Atraso na entrega:
   os cinco resultados apresentaram comentarios relacionados
   a problemas de entrega.

2. Problemas de qualidade:
   foram recuperados comentarios positivos e um comentario
   sobre atraso de entrega, que nao sustentam a existencia
   de defeitos ou problemas de qualidade dos produtos.

3. Elogios:
   os cinco resultados apresentaram experiencias positivas
   pertinentes a pergunta.

### Limitacao identificada

A similaridade semantica isolada nao foi suficiente para distinguir
consistentemente a intencao da pergunta, especialmente em consultas
sobre reclamacoes.

### Decisao registrada

D009 - Indexacao completa com processamento incremental.

### Pendencias

- Confirmar persistencia entre execucoes da colecao completa.
- Investigar o problema de relevancia da busca semantica.
- Comparar estrategias de recuperacao.
- Realizar avaliacao sistematica com criterios de relevancia.
- Integrar o modelo gerador de respostas.

### Proxima atividade

Etapa 3.4 - Auditoria e melhoria da recuperacao semantica.


## Etapa 3.4 - Auditoria da recuperacao semantica (04/11/2026)

**Status:** auditoria inicial concluida; reranking pendente.

### Objetivo

Investigar as falhas de relevancia observadas na recuperacao
de avaliacoes sobre problemas de qualidade dos produtos.

### Implementacao

Arquivo: `scripts/auditar_recuperacao.py`

Foram comparadas duas formulacoes de uma mesma pergunta,
utilizando a colecao completa do ChromaDB.

### Resultados

Base disponivel: 42.687 documentos.

Consulta original:
- Documentos recuperados: 15.
- Textos distintos: 11.
- Evidencias relevantes segundo criterio estrito: 4.
- Precision@15 exploratoria: 26,7%.

Consulta reformulada:
- Documentos recuperados: 15.
- Textos distintos: 15.
- Evidencias relevantes segundo criterio estrito: 14.
- Precision@15 exploratoria: 93,3%.

### Analise

A formulacao da pergunta alterou significativamente a
qualidade dos documentos recuperados.

A pergunta original apresentou dificuldades para distinguir
reclamacoes sobre qualidade de elogios aos produtos.

A reformulacao recuperou principalmente relatos de produtos
quebrados, defeituosos ou danificados.

### Limitacoes

Os resultados nao constituem avaliacao formal da qualidade
geral do sistema.

A reformulacao pode restringir o escopo da pergunta original.

A classificacao de relevancia foi exploratoria e precisa ser
ampliada para outras consultas e categorias de problemas.

### Decisao registrada

D011 - Avaliar reformulacao de consultas para melhorar
a recuperacao.

### Proxima atividade

Comparar a recuperacao semantica original com um experimento
de reranking multilingual, preservando o indice existente.


## Etapa 3.5 - Experimento de reranking (04/11/2026)

**Status:** concluida e analisada.

### Objetivo

Verificar se um modelo cross-encoder multilingual melhora a
relevancia das avaliacoes recuperadas pelo E5 e ChromaDB.

### Execucao

Arquivo: `scripts/testar_reranker.py`

Modelo: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.

Foram recuperados 50 candidatos para cada consulta e
comparados os oito primeiros resultados antes e depois
do reranking.

### Resultados

Pergunta original:
- E5: 1/8 relevante.
- E5 + reranker: 6/8 relevantes.
- Textos distintos: 5 com E5 e 7 com reranker.

Pergunta reformulada:
- E5: 8/8 relevantes.
- E5 + reranker: 7/8 relevantes.
- Textos distintos: 8 em ambos os casos.

### Conclusoes

O reranker melhorou a recuperacao para a pergunta original,
mas piorou ligeiramente a pergunta reformulada.

Ainda foram recuperados comentarios sobre problemas de
entrega para uma pergunta sobre defeitos dos produtos.

A melhora nao foi consistente entre as duas consultas.

### Decisao

D012 - Manter o reranker como opcao experimental e
implementar diversidade de evidencias, preservando
todos os registros da base documental.

### Proxima atividade

Iniciar a construcao do contexto recuperado para o
pipeline RAG, mantendo a rastreabilidade das fontes.

A avaliacao sistematica permanece obrigatoria antes
da entrega final.


## 10/11/2026 - P3.1: validacao das respostas e citacoes

**Objetivo:** corrigir falhas do contrato de saida do RAG
identificadas na implementacao P2.

**Procedimento:**
1. Criacao de dois testes de regressao.
2. Execucao inicial: 11 aprovados e 2 falhas esperadas.
3. Correcao da validacao das respostas.
4. Implementacao da reconstrucao deterministica de fontes.
5. Nova execucao dos testes de geracao e da suite completa.

**Resultados:**
- Testes de geracao: 13/13 aprovados.
- Suite completa: 31/31 aprovados.
- Nenhuma falha nos testes automatizados.

**Decisao relacionada:** D018.

**Limitacao:** validacao do comportamento real do Qwen
e verificacao semantica ainda pendentes.

**Proxima etapa:** P3.2 - tratamento de JSON malformado,
truncamento e desempenho de inferencia.


## 10/11/2026 - P3.2: diagnostico de parada do Qwen

Implementado diagnostico de encerramento da geracao
no adaptador GeradorQwenLocal.

Foi utilizada a estrategia de testes de regressao:
os dois testes falharam inicialmente pela ausencia
do atributo ultimo_diagnostico.

Apos a implementacao:
- Testes especificos: 2/2 aprovados.
- Suite completa: 33/33 aprovados.
- Verificacao de whitespace: sem problemas.

A implementacao preserva a interface anterior do gerador.

**Decisao relacionada:** D019.

**Pendente:** integrar o diagnostico aos erros de JSON
e executar testes com o LLM real.


## 10/11/2026 - P3.2B: diagnostico de falhas JSON

**Objetivo:** integrar o diagnostico do gerador ao
tratamento de falhas de interpretacao das respostas.

**Procedimento:**
1. Criacao de dois testes de regressao.
2. Execucao inicial: 13 aprovados e 2 falhas esperadas.
3. Correcao em src/generation/resposta.py.
4. Nova execucao dos testes especificos.
5. Execucao da suite completa.
6. Verificacao de formatacao com Git.

**Resultados:**
- Testes de resposta: 15/15 aprovados.
- Suite completa: 35/35 aprovados.
- Verificacao final git diff --check: sem problemas.

**Conclusao:**
O sistema passou a preservar informacoes de diagnostico
quando o modelo retorna JSON invalido.

**Limitacao:**
Ainda nao houve nova execucao do Qwen real para
determinar se as falhas anteriores foram causadas
pelo limite de tokens.

**Decisao relacionada:** D019.

**Proxima atividade:** P3.3 - escopo e abstencao.


## 10/11/2026 - P3.3A: validacao das citacoes em recusas

**Objetivo:** impedir que o RAG aceite citacoes
inventadas em respostas de recusa.

**Procedimento:**
1. Criacao de tres testes de regressao.
2. Execucao inicial dos testes.
3. Confirmacao de duas falhas esperadas.
4. Correcao da validacao em gerar_resposta().
5. Nova execucao dos testes de resposta.
6. Execucao da suite completa.
7. Correcao de whitespace e verificacao com Git.

**Resultados:**
- Testes especificos de resposta: 18/18 aprovados.
- Suite completa: 38/38 aprovados.
- git diff --check: sem problemas na ultima execucao.

**Conclusao:**
O sistema rejeita citacoes estruturadas inexistentes
tambem em respostas classificadas como recusa.

Recusas legitimas sem fontes continuam permitidas.

**Limitacao:**
Ainda nao foi avaliada a escolha correta entre
respondida, evidencias_insuficientes e fora_do_escopo
em execucoes reais.

**Decisao relacionada:** D020.

**Proxima atividade:** P3.3B - escopo e abstencao.
