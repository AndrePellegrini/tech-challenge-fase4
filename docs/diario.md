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


## Etapa 2 da integracao - RAG basico (07/11/2026)

**Status:** codigo implementado e testado com dependencias falsas;
reproducao local em andamento (dataset baixado, base reconstruida,
indice completo em construcao).

### Objetivo

Implementar o RAG basico pedido na Etapa 2 do PDF de entrega P1:
recuperador reutilizavel, montagem de contexto, integracao de um LLM,
resposta com citacoes verificaveis e execucao por CLI.

### Implementacoes realizadas

- `src/config.py`: caminhos, modelos e parametros centralizados.
- `src/retrieval/tipos.py`: `Candidato` e `Evidencia` (tipos
  compartilhados entre recuperacao e geracao).
- `src/retrieval/recuperador.py`: `Recuperador.buscar` reaproveita o
  modelo E5 e a colecao do ChromaDB ja existentes, com carregamento
  tardio e suporte a injecao de dependencia para testes (D014).
- `src/retrieval/contexto.py`: `montar_contexto` deduplica por
  `hash_texto`, respeita um orcamento de documentos/caracteres e nunca
  preenche o contexto com copias (D015).
- `src/generation/modelo.py`: `GeradorQwenLocal`, adaptador do
  Qwen2.5-1.5B-Instruct local via `transformers` (D016).
- `src/generation/resposta.py`: prompt-base, parse com correcao
  limitada, schema Pydantic (`RespostaRAG`) e verificacao de citacoes
  (marcador, document_id e trecho literal) (D016).
- `src/app.py`: `processar_pergunta` orquestra o fluxo completo, com
  tratamento de erro operacional em cada etapa; `python -m src.app
  --pergunta "..."` como CLI.
- `src/evaluation/executar_casos.py`: executa um lote de casos e salva
  predicoes em JSONL, no contrato definido pelo PDF.
- `data/eval/casos_exemplo.jsonl`: 6 perguntas ilustrativas (nao o
  benchmark oficial de 30 casos da frente de dados, que nao foi
  incluido no repositorio).
- Testes automatizados novos: `tests/test_contexto.py`,
  `tests/test_recuperador.py`, `tests/test_resposta.py`,
  `tests/test_app.py` -- todos com modelo/colecao/gerador falsos, sem
  depender do indice real nem do download do LLM.

### Reproducao local executada nesta sessao

- Dataset baixado via `kagglehub` (`olistbr/brazilian-ecommerce`) e
  `olist_order_reviews_dataset.csv` copiado para `data/raw/`.
- `.venv` criado; `requirements.txt` atualizado com as versoes
  realmente instaladas (`pydantic==2.14.3`, `transformers==5.22.2`,
  `torch==2.15.0`, resolvidas via `sentence-transformers`/`chromadb`).
- `scripts/explorar_avaliacoes.py`: reproduziu exatamente os numeros
  documentados (42.687 documentos aproveitaveis, 56.537 sem texto).
- `scripts/construir_base.py`: 42.687 linhas de entrada, 42.687
  documentos gerados.
- `python -m unittest discover -s tests -v`: **29 testes executados,
  29 aprovados** (21 novos da integracao + 8 das Etapas 1-2).
- `scripts/indexar_base_completa.py`: assinatura SHA-256 da base
  (`3519b8a9...`) identica a registrada em D009, confirmando que os
  dados reconstruidos localmente batem com os da sessao original.

### Correcao feita durante a revisao

- `src/app.py` nao tinha tratamento de excecao ao redor de
  `montar_contexto`; um erro ali derrubaria o processo em vez de
  devolver `erro_operacional`. Corrigido com um segundo bloco
  try/except.
- `tests/test_recuperador.py` usava uma lista Python simples como
  retorno falso de `encode(...)`, mas o codigo de producao chama
  `.tolist()` no vetor (presumindo `numpy.ndarray`, como o
  `SentenceTransformer` real devolve). Corrigido para o teste devolver
  `numpy.array(...)`, validando o mesmo caminho que o codigo real usa.

### Validacao end-to-end concluida nesta sessao

- Indexacao completa validada: 42.687/42.687 documentos no ChromaDB
  (mesmo SHA-256 da base de D009).
- `python -m src.app --pergunta "Quais relatos descrevem atraso na
  entrega?"` executado com sucesso contra o indice real: `status:
  "respondida"`, 50 candidatos recuperados, 8 selecionados para o
  contexto, afirmacoes citando corretamente os marcadores F1-F8.
- Dois bugs reais encontrados e corrigidos durante a validacao (ver
  D017): excecao nao tratada em `montar_contexto` dentro de
  `src/app.py`; saida da CLI corrompida ao redirecionar no Windows por
  falta de `sys.stdout.reconfigure(encoding="utf-8")`.
- `src/evaluation/executar_casos.py` executado com os 6 casos de
  exemplo (`data/eval/casos_exemplo.jsonl`), em CPU:

| case_id | status obtido | tipo esperado | tempo (s) |
|---|---|---|---:|
| exemplo_001 | erro_operacional | respondivel | 359,8 |
| exemplo_002 | respondida | respondivel | 295,5 |
| exemplo_003 | erro_operacional | respondivel | 458,6 |
| exemplo_004 | respondida | evidencias_insuficientes | 183,0 |
| exemplo_005 | evidencias_insuficientes | fora_do_escopo | 201,3 |
| exemplo_006 | respondida | fora_do_escopo (adversarial) | 152,1 |

### Analise dos resultados do lote

Os dois `erro_operacional` (exemplo_001, exemplo_003) vieram de JSON
malformado gerado pelo Qwen2.5-1.5B ("Expecting value" / "Expecting
',' delimiter"), consistente com a saida sendo cortada no limite de
`MAX_TOKENS_SAIDA = 600` antes de fechar o objeto JSON -- o
comportamento esperado do schema (rejeitar e marcar como falha, nunca
aceitar JSON invalido) funcionou corretamente, mas o limite de tokens
provavelmente precisa subir.

Os demais quatro casos nao bateram com o `tipo_esperado` ilustrativo
(exemplo_004, exemplo_005, exemplo_006): o modelo respondeu quando o
esperado era abster-se ou recusar por escopo. Isso e esperado de um
modelo de 1.5B sem ajuste fino nessas categorias, e e exatamente o
tipo de lacuna que a Etapa 3 (validacao sistematica com os casos
reais da frente de dados) deve medir e corrigir -- `tipo_esperado` em
`casos_exemplo.jsonl` e apenas ilustrativo, nao um gabarito validado.

Tempo de geracao em CPU: entre 150s e 460s por pergunta nesta maquina
(sem GPU). Isso e alto para uma demonstracao ao vivo e deve ser
medido/otimizado antes do video final (ver D016 e Prioridade 2 do
README).

### Pendente

- Investigar se aumentar `MAX_TOKENS_SAIDA` reduz os `erro_operacional`
  por truncamento de JSON.
- Medir e, se necessario, melhorar o tempo de geracao em CPU.
- Reforcar o prompt ou pos-processar para reduzir casos onde o modelo
  responde quando deveria abster-se ou recusar por escopo.
- Obter e rodar o benchmark oficial de 18+12 casos da frente de dados.
