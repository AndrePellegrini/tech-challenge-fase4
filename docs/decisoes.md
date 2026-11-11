# Registro de decisoes tecnicas

## D001 - Comecar pela analise dos textos (02/11/2026)

**Decisao:** usar `olist_order_reviews_dataset.csv` como base do primeiro experimento; adiar juncao com pedidos/produtos ate validar texto disponivel.

**Motivo:** comentarios sao foco obrigatorio; joins podem multiplicar linhas se feitos antes de entender granularidade.

**Alternativas:** carregar todos os CSVs na etapa inicial; descartada pela complexidade desnecessaria antes do perfil.

**Conferencia futura:** decidir se metadados de entregas e notas agregam valor real.

## D002 - Preservar texto e identificadores (02/11/2026)

**Decisao:** juntar titulo e comentario quando disponiveis, sem remover palavras comuns, acentos ou pontuacao nesta etapa. Manter `review_id`, `order_id` e um identificador tecnico unico por linha.

**Motivo:** negacoes como 'nao recebi' podem perder sentido se eliminarmos stopwords; IDs naturais podem se repetir.

**Conferencia futura:** auditoria de duplicatas antes de qualquer deduplicacao.

## D003 - API e banco vetorial ainda nao escolhidos

**Decisao:** avaliar opcoes gratuitas/locais primeiro; selecionar depois de medir o volume de documentos e testar recuperacao em portugues.

## D004 - Selecionar avaliacoes com texto para a base de conhecimento (02/11/2026)

**Decisao:** considerar inicialmente os 42.687 registros da Olist que possuem titulo e/ou comentario textual para construir a base de conhecimento do RAG. Excluir apenas da indexacao semantica os 56.537 registros sem texto, mantendo intacto o dataset original. Preservar inicialmente os 1.737 registros que possuem somente titulo, identificando essa condicao nos metadados. Nao eliminar automaticamente registros que compartilham `review_id` ou `order_id`; cada linha aproveitada deve manter um identificador tecnico unico e os IDs originais para rastreabilidade.

**Motivo:** o foco do Tech Challenge e recuperar evidencias presentes nas avaliacoes escritas. Registros sem texto nao fornecem conteudo semantico para embeddings; titulos isolados ainda podem registrar elogios ou reclamacoes. A base original possui 99.224 avaliacoes, das quais 42.687 (aproximadamente 43,02%) contem texto. A exclusao automatica de IDs repetidos pode apagar avaliacoes distintas.

**Alternativas:** indexar todas as avaliacoes, inclusive as sem texto; descartada porque nao acrescenta evidencia textual. Descartar os registros com somente titulo ou deduplicar por identificador; alternativas adiadas ate avaliacao da qualidade e auditoria dos dados.

**Limitacoes:** os documentos textuais nao devem ser tratados automaticamente como uma amostra representativa das 99.224 avaliacoes. Recuperar alguns comentarios semanticamente semelhantes nao demonstra, por si so, a frequencia de um problema em toda a base.

**Conferencia futura:** comparar a distribuicao das notas entre a base completa e os registros com texto; auditar duplicatas; verificar a utilidade dos titulos isolados; validar a quantidade de documentos gerados na Etapa 2 e avaliar a estrategia de chunking antes da indexacao vetorial.


## D005 - Manter uma avaliacao por documento, sem chunking (02/11/2026)

**Decisao:** utilizar inicialmente um documento para cada avaliacao textual, sem dividir os comentarios em chunks menores. Os 42.687 documentos serao mantidos como unidades independentes de recuperacao semantica.

**Motivo:** o perfil documental apresentou mediana de 10 palavras (P50), percentil 95 de 34 palavras (P95) e comprimento maximo de 50 palavras. Esses valores indicam textos curtos, para os quais a fragmentacao pode separar informacoes relacionadas e prejudicar a interpretacao da experiencia relatada pelo cliente.

**Alternativas:** utilizar chunking de tamanho fixo, chunking recursivo ou agrupar diversas avaliacoes em um unico documento. Essas alternativas nao serao adotadas inicialmente porque os comentarios ja possuem granularidade adequada para uma primeira estrategia de recuperacao.

**Limitacoes:** a ausencia de chunking nao garante, por si so, melhor qualidade de recuperacao. Documentos extremamente curtos podem apresentar pouco contexto semantico. A estrategia devera ser avaliada por testes praticos.

**Conferencia futura:** medir a relevancia das avaliacoes recuperadas, especialmente para consultas sobre entrega, qualidade de produtos, atendimento e satisfacao. Reavaliar a estrategia caso sejam identificados problemas de recuperacao.

## D006 - Preservar repeticoes e explicitar o recorte textual (02/11/2026)

**Decisao:** preservar inicialmente os 5.975 registros classificados como textos repetidos e os 5.778 documentos com ate 3 palavras. Nao aplicar deduplicacao ou exclusao por comprimento nesta etapa. Documentar que os resultados do RAG representam as avaliacoes com conteudo textual, e nao necessariamente todas as avaliacoes da Olist.

**Motivo:** comentarios identicos podem representar experiencias distintas. A exclusao automatica poderia reduzir indevidamente a quantidade de relatos e alterar futuras analises. Alem disso, a distribuicao das notas difere entre a base completa e a base textual.

**Evidencias:** a base textual possui 42.687 documentos, dos quais 5.975 correspondem a ocorrencias adicionais de textos repetidos (14,00%) e 5.778 possuem ate 3 palavras (13,54%). As notas 1 e 2 representam 25,75% da base textual, contra 14,69% da base completa. As notas 4 e 5 representam 65,71% da base textual, contra 77,07% da base completa.

**Alternativas:** excluir textos repetidos, remover comentarios muito curtos ou considerar somente avaliacoes negativas. Essas alternativas foram adiadas porque podem introduzir vieses e prejudicar a rastreabilidade.

**Limitacoes:** o indicador de textos repetidos nao demonstra que os registros sejam duplicatas reais. A distribuicao das notas evidencia diferencas entre os recortes, mas nao identifica suas causas. A recuperacao semantica isolada tambem nao permite medir a frequencia de problemas em toda a base.

**Conferencia futura:** avaliar a influencia das repeticoes e dos textos curtos nos resultados da busca vetorial, investigar a relevancia dos documentos recuperados e distinguir conclusoes sobre a base textual de conclusoes sobre todas as avaliacoes.


## D007 - Selecionar o multilingual-e5-small para o primeiro prototipo RAG (02/11/2026)

**Decisao:** adotar provisoriamente o modelo `intfloat/multilingual-e5-small` para a primeira implementacao de recuperacao semantica. Manter sua avaliacao em aberto antes de considera-lo a escolha definitiva.

**Motivo:** o modelo permite gerar embeddings localmente, sem depender de uma API paga. O experimento com 1.000 documentos da Olist foi executado com sucesso, produzindo vetores de 384 dimensoes e recuperando comentarios semanticamente relacionados a perguntas em portugues.

**Configuracao:** utilizar o prefixo `passage:` para documentos e `query:` para perguntas. Normalizar os embeddings e utilizar similaridade de cosseno.

**Resultados:** foram realizadas tres consultas sobre atrasos de entrega, problemas de qualidade e elogios. A inspecao inicial identificou 14 resultados aparentemente relevantes entre 15 recuperados, considerando os trechos exibidos. Esse resultado e exploratorio e nao constitui uma metrica geral de desempenho.

**Limitacoes:** foi recuperado o comentario positivo "Produto com qualidade" para uma pergunta sobre problemas de qualidade. Tambem foram encontradas reclamacoes com notas positivas. Portanto, similaridade semantica e nota da avaliacao nao garantem a identificacao correta da intencao do texto.

**Alternativas:** avaliar outros modelos de embeddings multilíngues ou adicionar mecanismos de reranking. Essas alternativas permanecem disponiveis caso os testes de recuperacao indiquem necessidade.

**Conferencia futura:** ampliar a avaliacao com perguntas e documentos rotulados, verificar a relevancia dos resultados, testar consultas fora do escopo e avaliar estrategias para reduzir recuperacoes incoerentes com a intencao da pergunta.


## D008 - Adotar ChromaDB como banco vetorial local (02/11/2026)

**Decisao:** utilizar o ChromaDB como banco vetorial na primeira versao do RAG, com armazenamento persistente em disco, similaridade de cosseno e embeddings gerados pelo modelo `intfloat/multilingual-e5-small`.

**Motivo:** o ChromaDB permite armazenar textos, vetores e metadados em uma colecao persistente. Sua utilizacao local evita a dependencia inicial de servicos pagos e facilita a reproducao do projeto.

**Configuracao:** utilizar `PersistentClient`, colecao vetorial com metrica `cosine`, embeddings normalizados de 384 dimensoes e identificadores tecnicos unicos por documento.

**Experimento realizado:** foram indexados 1.000 documentos da Olist, em lotes de 100 registros. Tres perguntas recuperaram cinco avaliacoes cada, totalizando 15 resultados.

**Validacao:** os resultados do ChromaDB coincidiram com os resultados do experimento anterior utilizando NumPy, incluindo a ordem dos documentos e as similaridades apresentadas. Uma segunda execucao confirmou a reutilizacao da colecao armazenada, sem recalcular os embeddings dos documentos.

**Alternativas:** utilizar FAISS, outros bancos vetoriais locais ou solucoes gerenciadas em nuvem. O ChromaDB foi selecionado inicialmente pela simplicidade de integracao, persistencia local e suporte a metadados.

**Limitacoes:** o experimento utilizou somente 1.000 dos 42.687 documentos textuais. A qualidade da recuperacao ainda precisa ser avaliada formalmente. A persistencia foi confirmada no ambiente local, mas o indice completo ainda nao foi construido.

**Conferencia futura:** indexar os 42.687 documentos, validar a contagem e a persistencia, testar consultas representativas e avaliar o comportamento da recuperacao semantica na base completa.


## D009 - Indexar integralmente a base textual com processamento incremental (02/11/2026)

**Decisao:** utilizar o ChromaDB com o modelo `intfloat/multilingual-e5-small` para indexar os 42.687 documentos da base textual da Olist. Manter uma colecao separada do experimento piloto, com processamento em lotes e capacidade de retomada.

**Motivo:** a indexacao completa permite recuperar evidencias de todo o conjunto textual selecionado, eliminando a limitacao da amostra inicial de 1.000 documentos. O processamento incremental evita recalcular embeddings de registros ja armazenados.

**Configuracao:**
- Colecao: `olist_e5_full_42687_v1`.
- Modelo de embeddings: `intfloat/multilingual-e5-small`.
- Dimensionalidade: 384.
- Similaridade: cosseno.
- Lotes de indexacao: 128 documentos.
- Lotes de inferencia: 32 textos.
- Prefixos: `passage:` e `query:`.
- Armazenamento local persistente.
- Validacao de identificadores e assinatura SHA-256 da origem.

**Resultado:** foram carregados e indexados 42.687 documentos. A verificacao final confirmou a contagem esperada e a presenca dos identificadores.

**Observacoes sobre a recuperacao:** as consultas sobre atrasos e elogios apresentaram resultados pertinentes. Entretanto, a pergunta sobre problemas de qualidade recuperou comentarios positivos e relatos que nao comprovam defeitos nos produtos.

**Limitacoes:** a busca por similaridade de cosseno nao garante que os resultados correspondam a intencao da pergunta. O aumento da base disponibiliza mais documentos candidatos, mas nao assegura maior precisao. A relevancia da recuperacao ainda precisa de avaliacao sistematica.

**Alternativas:** complementar a recuperacao vetorial com reformulacao de consultas, busca lexical, busca hibrida, filtros de metadados ou reranking.

**Conferencia futura:** confirmar a persistencia da colecao completa, avaliar candidatos recuperados em diferentes consultas, comparar estrategias de recuperacao e estabelecer criterios para evitar respostas sem evidencias suficientes.


## D010 - Priorizar evidencias, qualidade da recuperacao e requisitos obrigatorios (04/11/2026)

**Status:** estrategia de desenvolvimento definida; melhorias tecnicas sujeitas a validacao experimental.

**Decisao:** manter a base original de 42.687 documentos e a indexacao existente com multilingual-e5-small e ChromaDB. Priorizar a melhoria da recuperacao, a geracao de respostas fundamentadas, a rastreabilidade das evidencias e o tratamento de perguntas sem informacoes suficientes antes de implementar os recursos opcionais do Tech Challenge.

**Motivo:** a indexacao completa foi concluida, mas a consulta sobre problemas de qualidade recuperou comentarios positivos e evidencias sem relacao com defeitos nos produtos. A busca vetorial isolada apresentou limitacoes relacionadas a intencao da pergunta. A FIAP exige que as respostas sejam coerentes com os dados recuperados e que a solucao reconheca ausencia de evidencias suficientes.

**Verificacao dos embeddings:** os scripts desenvolvidos utilizam os prefixos `passage:` para documentos e `query:` para perguntas, conforme a especificacao do modelo E5. Nao foi identificada necessidade de reindexacao por ausencia de prefixos.

**Estrategia planejada:**
- Avaliar a recuperacao atual como baseline.
- Testar reformulacao de consultas.
- Experimentar reranking multilingual sobre candidatos recuperados.
- Considerar busca hibrida se os testes justificarem.
- Preservar os registros originais e controlar repeticoes na recuperacao.
- Implementar verificacao de escopo e suficiencia das evidencias.
- Construir respostas com identificadores de fontes rastreaveis.
- Avaliar separadamente perguntas que exigem contagem de frequencias.
- Priorizar a implementacao do pipeline RAG completo e seus testes.
- Deixar o enriquecimento contextual com metadados adicionais como evolucao opcional.

**Alternativas:** reindexar documentos sem evidencias de problemas na criacao dos embeddings; agrupar permanentemente registros por texto unico; utilizar apenas um limiar de similaridade para decidir se o sistema deve responder; implementar todos os recursos adicionais antes do RAG basico. Essas alternativas nao foram selecionadas neste momento.

**Limitacoes:** o reranking ainda nao foi testado, e sua eficacia nao pode ser presumida. Scores de similaridade ou relevancia nao devem ser tratados automaticamente como probabilidades de acerto. A classificacao de temas devera ser validada antes de sustentar conclusoes quantitativas.

**Conferencia futura:** comparar as estrategias de recuperacao com perguntas e evidencias avaliadas manualmente; verificar a relevancia e diversidade dos documentos; testar casos fora do escopo; avaliar fidelidade das respostas; registrar a escolha final dos componentes apos os resultados experimentais.


## D011 - Avaliar reformulacao de consultas para melhorar a recuperacao (04/11/2026)

**Status:** experimento validado; estrategia definitiva de recuperacao pendente.

**Decisao:** manter o indice vetorial existente e considerar a reformulacao de consultas como uma estrategia candidata para melhorar a relevancia das evidencias. Antes de adota-la definitivamente, comparar a recuperacao vetorial com alternativas que utilizem reranking.

**Motivo:** a consulta original sobre problemas de qualidade recuperou elogios e comentarios sobre outros problemas. A reformulacao da pergunta, incluindo termos relacionados a defeitos e danos, apresentou resultados mais coerentes com a intencao da busca.

**Ambiente do experimento:**
- Base textual: 42.687 documentos.
- Modelo: `intfloat/multilingual-e5-small`.
- Banco vetorial: ChromaDB.
- Colecao: `olist_e5_full_42687_v1`.
- Quantidade recuperada: 15 documentos por consulta.
- Metrica de busca: similaridade de cosseno.

**Consulta original:** Quais problemas de qualidade dos produtos foram relatados?

**Consulta reformulada:** Quais avaliacoes relatam produtos defeituosos, quebrados, danificados ou de ma qualidade?

**Criterio de relevancia:** considerar relevante apenas uma avaliacao que apresente evidencia explicita de defeito, dano ou ma qualidade do produto. Comentarios sobre atraso de entrega, elogios ou produto errado sem defeito declarado nao foram considerados relevantes nesse criterio estrito.

**Resultados:**
- Consulta original: 4 de 15 resultados relevantes (Precision@15 exploratoria de 26,7%).
- Consulta reformulada: 14 de 15 resultados relevantes (Precision@15 exploratoria de 93,3%).
- Consulta original: 11 textos distintos entre os 15 resultados.
- Consulta reformulada: 15 textos distintos entre os 15 resultados.

**Limitacoes:** a avaliacao utilizou apenas duas formulacoes de uma mesma necessidade de informacao e classificacao manual dos resultados apresentados. A reformulacao favoreceu problemas de quebra e danos, podendo deixar de recuperar outras dimensoes da qualidade, como durabilidade, acabamento e desempenho. Os resultados nao demonstram desempenho geral do modelo.

**Alternativas:** manter apenas a busca vetorial original; utilizar reformulacao automatica de consultas; ampliar a recuperacao e aplicar reranking; introduzir recuperacao hibrida combinando embeddings e busca lexical.

**Conferencia futura:** comparar a estrategia original, a reformulada e o reranking utilizando o mesmo banco de documentos, registrar criterios de relevancia, avaliar perguntas diversificadas e selecionar a estrategia que melhor sustente as respostas finais do RAG.


## D012 - Avaliar reranking e controlar a diversidade das evidencias (04/11/2026)

**Status:** experimento concluido; reranker nao adotado como padrao definitivo.

**Decisao:** manter o multilingual-e5-small e o ChromaDB como componentes principais da recuperacao. Preservar a possibilidade de utilizar reranking como estrategia opcional, mas nao aplica-lo indiscriminadamente antes de ampliar a avaliacao. Implementar controle de textos repetidos na selecao das evidencias, sem excluir registros da base original.

**Motivo:** o reranker melhorou a relevancia dos resultados da pergunta original sobre problemas de qualidade, mas reduziu a precisao observada na pergunta reformulada. Portanto, nao existe evidencia suficiente de que sua utilizacao universal aumentara a qualidade do RAG.

**Modelos utilizados:**
- Embeddings: `intfloat/multilingual-e5-small`.
- Reranking: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.
- Armazenamento: ChromaDB.
- Base: 42.687 documentos.
- Recuperacao inicial: Top-50.
- Comparacao final: Top-8.

**Criterio de relevancia:** considerar relevante apenas comentario que apresente evidencia explicita de defeito, dano ou ma qualidade fisica do produto.

**Resultados exploratorios:**

| Consulta | E5 | E5 + reranker |
|---|---:|---:|
| Original | 1/8 (12,5%) | 6/8 (75,0%) |
| Reformulada | 8/8 (100,0%) | 7/8 (87,5%) |

**Diversidade:**
- Consulta original com E5: 5 textos distintos no Top-8.
- Consulta original com reranker: 7 textos distintos no Top-8.
- Consulta reformulada: 8 textos distintos em ambas as estrategias.

**Falhas identificadas:** o reranker colocou comentarios sobre atraso de entrega nas primeiras posicoes da pergunta original. Na pergunta reformulada, incluiu um elogio aos produtos acompanhado de reclamacao sobre frete.

**Interpretacao:** o reranking apresentou ganhos em uma formulacao, mas nao resolveu completamente o problema de relevancia. Seus scores brutos nao devem ser tratados como probabilidades ou utilizados com limiares arbitrarios.

**Alternativas:** utilizar somente a recuperacao E5, aplicar reranking opcional, combinar buscas reformuladas ou experimentar recuperacao hibrida.

**Limitacoes:** o experimento utilizou duas formulacoes de uma unica necessidade de informacao. A Precision@8 calculada e exploratoria, nao uma estimativa do desempenho geral.

**Conferencia futura:** construir um conjunto de avaliacao com aproximadamente 25 a 30 perguntas, incluindo consultas fora do escopo e casos sem evidencias. Comparar relevancia, diversidade, fidelidade das respostas e capacidade de abstencao antes de definir a estrategia final.


## D013 - Publicar checkpoint inicial do projeto no GitHub (04/11/2026)

**Status:** decisao aprovada; primeira publicacao pendente de verificacao.

**Decisao:** publicar uma primeira versao do projeto apos
a conclusao da infraestrutura de preparacao, embeddings,
indexacao e experimentos de recuperacao semantica.

**Versao inicial:** v0.1.0 - Base de Conhecimento e Recuperacao Semantica.

**Objetivo:** permitir que o grupo acompanhe o desenvolvimento,
revise o codigo, compreenda a arquitetura e colabore nas
proximas implementacoes.

**Artefatos versionados:**
- Codigo-fonte.
- Scripts experimentais.
- Testes automatizados.
- README.
- Documento de arquitetura.
- Decisoes tecnicas e diario.
- Relatorios agregados de qualidade.

**Artefatos excluidos do versionamento:**
- Dataset bruto.
- Arquivos intermediarios com dados textuais.
- Documentos JSONL contendo comentarios individuais.
- Banco vetorial persistente.
- Ambiente virtual Python.
- Credenciais e arquivos de configuracao sensiveis.

**Estrategia de colaboracao:** utilizar a branch `main` como
referencia de integracao e desenvolver novas funcionalidades
em branches especificas, preferencialmente com Pull Requests.

**Justificativa:** a publicacao incremental permite revisao
antecipada pelo grupo e reduz o risco de concentrar toda a
integracao e documentacao no periodo final do desafio.

**Limitacoes:** a versao v0.1.0 nao representa um RAG completo.
A geracao de respostas com LLM, o tratamento de ausencia de
evidencias e a avaliacao final ainda estao pendentes.

**Conferencia futura:** verificar o push inicial, o acesso dos
colaboradores, a ausencia de dados indevidos no repositorio
e a reproducibilidade da instalacao e dos scripts.

**Repositorio remoto:** registrar o endereco apos a publicacao.


## D014 - Transformar a busca dos scripts em modulos reutilizaveis (07/11/2026)

**Status:** implementado; validacao end-to-end pendente do indice completo.

**Decisao:** criar `src/config.py`, `src/retrieval/recuperador.py` e
`src/retrieval/contexto.py` para reutilizar a logica ja validada dos
scripts experimentais (`testar_embeddings.py`, `testar_chromadb.py`,
`indexar_base_completa.py`, `auditar_recuperacao.py`), sem reescrever o
modelo de embeddings nem o indice ja construidos.

**Motivo:** o PDF de entrega P1 pede explicitamente um "recuperador
reutilizavel", preservando prefixos do E5, IDs e metadados. Os scripts
da Etapa 3 eram experimentos de linha de comando, nao um componente que
o pipeline RAG pudesse chamar por pergunta.

**Configuracao:** `Recuperador` carrega o `SentenceTransformer` e a
colecao do ChromaDB uma unica vez por processo (propriedades com
inicializacao tardia) e aceita injecao de dependencia para testes, sem
exigir o indice real. `buscar(pergunta, k)` devolve candidatos com id,
texto, metadata e score de similaridade (1 - distancia de cosseno).

**Alternativas:** manter a busca apenas nos scripts experimentais e
duplicar a logica dentro do `app.py`. Descartada porque dificultaria
testes automatizados e a reutilizacao pelo modulo de avaliacao.

**Limitacoes:** a classe ainda nao foi exercitada contra o indice
completo de 42.687 documentos neste commit; os testes automatizados
usam modelo e colecao falsos.

**Conferencia futura:** validar `Recuperador.buscar` contra o indice
real apos reconstruir a base localmente, comparando os resultados com
os scripts de auditoria.


## D015 - Selecao de contexto com deduplicacao e orcamento de caracteres (07/11/2026)

**Status:** implementado; limites numericos ainda experimentais.

**Decisao:** implementar `montar_contexto` para agrupar candidatos com o
mesmo `hash_texto` (ou o mesmo texto normalizado, se o hash faltar),
selecionando ate 8 documentos distintos e ate 4.000 caracteres. O
primeiro candidato sempre entra, mesmo se sozinho ultrapassar o
orcamento, para nunca gerar um contexto vazio quando ha pelo menos um
candidato.

**Motivo:** o PDF de entrega P1 define como ponto de partida
experimental recuperar ate 50 candidatos e selecionar ate 8 textos
distintos, alertando para nao preencher o contexto com copias quando ha
poucos textos distintos. Isso e coerente com D006 e D012, que ja haviam
identificado textos repetidos na base e preservado os registros
originais sem deduplicacao automatica no indice.

**Configuracao:** `max_documentos=8`, `max_caracteres=4000`, definidos
em `src/config.py`. Esses numeros nao foram validados com os 18 casos
de desenvolvimento e deverao ser ajustados na Etapa 3.

**Alternativas:** deduplicar also por order_id ou review_id; descartada
porque review_id pode repetir por outros motivos (D004) e nao implica
texto identico. Limitar o contexto apenas por numero de documentos, sem
orcamento de caracteres; descartada porque poderia estourar o limite de
entrada do gerador escolhido.

**Limitacoes:** o orcamento em caracteres e uma aproximacao do
orcamento real de tokens do gerador; o modulo de geracao usa o
tokenizador do Qwen para medir tokens, mas a selecao de contexto em si
nao tokeniza.

**Conferencia futura:** comparar o numero de textos distintos
efetivamente selecionados por pergunta nos 18 casos de desenvolvimento
e ajustar `max_documentos`/`max_caracteres` se necessario.


## D016 - Qwen2.5-1.5B-Instruct local como gerador, com saida validada por schema (07/11/2026)

**Status:** implementado; qualidade e tempo de geracao ainda nao
medidos na maquina local.

**Decisao:** adotar `Qwen/Qwen2.5-1.5B-Instruct`, carregado localmente
via `transformers`, como gerador de respostas, com decodificacao
gulosa (`do_sample=False`). Validar toda saida do modelo com um schema
Pydantic (`RespostaRAG`) e rejeitar citacoes cujo marcador, document_id
ou trecho nao existam literalmente no contexto enviado.

**Motivo:** o guia de implementacao do PDF de entrega P1 recomenda
testar o Qwen2.5-1.5B-Instruct localmente antes de considerar um
provedor de API, para nao depender de credenciais nem GPU. O contrato
de saida exige que "cada ID citado deve existir no contexto" e "cada
trecho deve ocorrer literalmente na fonte", o que so pode ser garantido
com verificacao programatica apos o parse.

**Configuracao:**
- Gerador: `Qwen/Qwen2.5-1.5B-Instruct`, `transformers.AutoModelForCausalLM`.
- Decodificacao: gulosa, ate 600 tokens de saida.
- Parse: `json.loads` direto; se falhar, tenta isolar o maior bloco
  entre a primeira `{` e a ultima `}` (correcao limitada).
- Validacao estrutural: Pydantic (`status`, `resposta`, `afirmacoes`,
  `fontes`).
- Validacao de citacoes: marcador deve existir nas evidencias
  enviadas; `document_id` da fonte deve coincidir com o da evidencia;
  `trecho` deve ocorrer (case-insensitive) dentro do texto da
  evidencia.
- Falha de parse ou de citacao: sempre vira `erro_operacional`, nunca
  uma saida aceita sem validacao.

**Alternativas:** usar um provedor de API (OpenAI, Anthropic ou outro)
com credencial por variavel de ambiente, conforme o guia tambem
permite. Adiada porque o modelo local evita depender de uma chave que
o time ainda nao definiu, e porque o Qwen2.5-1.5B e pequeno o
suficiente para rodar em CPU.

**Limitacoes:** o tempo de geracao e a qualidade das respostas em CPU
ainda nao foram medidos com os casos de desenvolvimento reais. A
verificacao estrutural das citacoes nao comprova que a afirmacao
realmente decorre do trecho citado (suporte semantico), apenas que o
trecho existe literalmente na fonte.

**Conferencia futura:** medir tempo de geracao e qualidade com os 18
casos de desenvolvimento; decidir se o modelo local e viavel ou se e
necessario migrar para um provedor de API; revisar manualmente se as
afirmacoes realmente decorrem dos trechos citados.


## D017 - Validacao end-to-end local: dois achados corrigidos, uma limitacao documentada (07/11/2026)

**Status:** pipeline validado contra o indice completo (42.687
documentos) e o Qwen2.5-1.5B-Instruct local, em uma maquina Windows.

**Decisao:** manter a implementacao de D014-D016, com duas correcoes
aplicadas apos a reproducao local, e documentar uma limitacao de
qualidade do gerador observada na primeira execucao real.

**Achado 1 - excecao nao tratada em `src/app.py`:** a chamada a
`montar_contexto` nao estava dentro de um bloco try/except, entao um
erro ali derrubaria o processo com uma excecao nao tratada, em vez de
devolver `erro_operacional` como as demais etapas do fluxo. Corrigido
com um segundo try/except ao redor da montagem de contexto.

**Achado 2 - saida corrompida ao redirecionar a CLI no Windows:** com
`print(json.dumps(..., ensure_ascii=False))`, a codificacao usada para
escrever em um arquivo/pipe redirecionado no Windows seguia o locale
do sistema (`cp1252` nesta maquina), nao UTF-8 -- acentos como "a" e "o"
viravam bytes cp1252 validos, mas invalidos como UTF-8 para quem le o
arquivo esperando essa codificacao. Corrigido com
`sys.stdout.reconfigure(encoding="utf-8")` no inicio de `main()`.
Verificado lendo os bytes brutos do arquivo de saida antes e depois da
correcao (antes: `\xe1` solto; depois: `\xc3\xa1`, UTF-8 correto para
"a" acentuado).

**Observacao de qualidade (nao e um bug de codigo):** na primeira
pergunta real testada ("Quais relatos descrevem atraso na entrega?"),
o Qwen2.5-1.5B-Instruct local devolveu `status: "respondida"` com
`afirmacoes` citando corretamente os marcadores F1-F8, mas com o campo
`fontes` vazio (o modelo nao preencheu a lista de
marcador/document_id/trecho pedida no schema, apesar de instruido a
faze-lo). A verificacao de citacoes nao falhou porque
`validar_citacoes` confere os marcadores citados contra as evidencias
realmente enviadas (nao contra o campo `fontes` da propria resposta),
entao o resultado continuou coerente -- mas a riqueza da citacao
(document_id e trecho explicitos por fonte) ficou incompleta nesta
execucao.

**Configuracao da execucao de validacao:**
- Dataset baixado via `kagglehub` nesta sessao; CSV identico ao
  usado nas Etapas 1-3 anteriores (mesmo SHA-256 da base: D009).
- `requirements.txt` atualizado para as versoes realmente resolvidas
  pelo pip nesta maquina: `pydantic==2.14.3`, `transformers==5.22.2`,
  `torch==2.15.0` (via dependencias de `sentence-transformers` e
  `chromadb`, sem pin explicito anterior).
- 29 testes automatizados aprovados (`python -m unittest discover -s
  tests -v`).
- Indexacao completa validada: 42.687/42.687 documentos no ChromaDB.
- CLI executada com sucesso contra o indice real e o LLM local.

**Alternativas:** aceitar a saida sem forcar UTF-8, deixando a
responsabilidade para quem consome a CLI configurar o proprio
ambiente. Descartada porque o contrato de saida da aplicacao deve ser
UTF-8 de forma consistente entre plataformas, independente do locale
de quem executa.

**Limitacoes:** a observacao sobre `fontes` vazio vem de uma unica
pergunta; nao prova um padrao geral do modelo. A correcao de
codificacao foi validada no Windows desta maquina; nao foi testada em
Linux/macOS (onde o locale padrao costuma ser UTF-8 e o problema
provavelmente nao ocorreria, mas a correcao e inofensiva nesses casos).

**Conferencia futura:** medir, nos 18 casos de desenvolvimento reais,
com que frequencia o campo `fontes` fica incompleto e decidir se vale
a pena reforcar o prompt, pedir uma segunda tentativa de geracao, ou
preencher `fontes` automaticamente a partir das `afirmacoes` e das
evidencias quando o modelo citar marcadores validos mas esquecer de
listar as fontes correspondentes.


## D018 - Fortalecer o contrato de citacoes da geracao (10/11/2026)

**Status:** implementada e validada por testes automatizados em 10/11/2026.

**Responsavel:** P3 - Geracao.

**Decisao:** exigir que respostas com status `respondida`
possuam afirmacoes estruturadas e evidencias rastreaveis.
Quando o modelo citar marcadores validos nas afirmacoes,
mas omitir a lista de fontes, permitir sua reconstrucao
deterministica a partir do contexto efetivamente enviado.

**Motivo:** a implementacao P2 pode aceitar respostas sem
afirmacoes nem fontes. O Qwen tambem apresentou omissoes
na lista de fontes, mesmo quando citou marcadores validos.

**Regras planejadas:**
- Rejeitar respostas substantivas sem afirmacoes fundamentadas.
- Validar os marcadores citados contra o contexto.
- Nao criar fontes inexistentes.
- Reutilizar document_id e trecho da evidencia original.
- Rejeitar citacoes divergentes ou inventadas.
- Manter falhas de contrato distintas de ausencia de evidencias.

**Limitacao:** a validacao estrutural nao comprova que
uma afirmacao seja semanticamente sustentada pelo trecho.
Essa verificacao sera tratada separadamente.

**Criterio de aceite:** os testes de regressao devem
demonstrar rejeicao de respostas sem evidencias e
reconstrucao correta de fontes omitidas pelo LLM.

**Conferencia futura:** executar toda a suite de testes,
verificar os casos de desenvolvimento da P1 e registrar
os resultados antes do merge.


**Resultado da implementacao (10/11/2026):**

- Antes da correcao: 13 testes de geracao executados,
  sendo 11 aprovados e 2 falhas esperadas.
- Falha 1: resposta sem afirmacoes e fontes era aceita.
- Falha 2: fontes omitidas pelo LLM nao eram reconstruidas.
- Depois da correcao: 13 de 13 testes de geracao aprovados.
- Suite completa: 31 de 31 testes aprovados.

**Arquivos modificados:**
- `src/generation/resposta.py`
- `tests/test_resposta.py`

**Correcao aplicada:**
- Exigir afirmacoes e fontes rastreaveis para respostas.
- Validar marcadores contra as evidencias reais.
- Reconstruir fontes omitidas a partir do contexto.
- Rejeitar IDs ou trechos de citacao invalidos.
- Exigir correspondencia literal dos trechos citados.

**Limitacao remanescente:**
Os testes confirmam a consistencia estrutural,
mas nao comprovam a fidelidade semantica de todas
as afirmacoes geradas pelo LLM.

**Proxima atividade:** P3.2 - diagnosticar e reduzir
falhas de geracao de JSON no Qwen2.5-1.5B.


## D019 - Diagnosticar o encerramento da geracao do LLM (10/11/2026)

**Status:** implementada e validada por testes automatizados simulados.

**Responsavel:** P3 - Geracao.

**Problema:**
A entrega P2 identificou dois casos em que o Qwen2.5-1.5B
produziu JSON invalido. Uma das hipoteses e o truncamento
da resposta pelo limite de 600 tokens.

A implementacao anterior retornava apenas o texto gerado,
sem registrar a quantidade de tokens ou o motivo da parada.

**Decisao:**
Adicionar o atributo `ultimo_diagnostico` ao adaptador
GeradorQwenLocal, preservando o contrato publico de `gerar()`.

**Informacoes registradas:**
- motivo_parada: eos, limite_tokens ou outro.
- tokens_gerados: quantidade de tokens produzidos.
- max_tokens_saida: limite configurado para a geracao.

**Regras:**
- A ocorrencia de EOS tem prioridade sobre o limite.
- Uma geracao que atinge o limite sem EOS e classificada
  como limite_tokens.
- O diagnostico anterior e limpo antes de uma nova geracao.

**Arquivos modificados:**
- src/generation/modelo.py
- tests/test_modelo.py

**Validacao:**
- 2 de 2 testes especificos aprovados.
- 33 de 33 testes da suite completa aprovados.
- git diff --check sem problemas.

**Limitacoes:**
- Os testes utilizam modelos e tokenizadores simulados.
- Ainda nao foi realizada nova medicao com o Qwen real.
- Atingir o limite nao comprova que o JSON foi truncado.
- O diagnostico ainda nao foi integrado ao tratamento
  de erros de parse ou ao trace de avaliacao.

**Proxima atividade:**
Conectar o diagnostico aos erros de interpretacao do JSON
e verificar o comportamento em execucoes reais.


**Complemento P3.2B - Diagnostico de erros JSON (10/11/2026)**

Foi integrada a leitura de `ultimo_diagnostico`
ao tratamento de falhas de interpretacao do JSON.

A resposta continua utilizando `erro_operacional`
quando o JSON ou schema nao pode ser validado.

O diagnostico passa a distinguir:
- Geracao interrompida no limite de tokens.
- Geracao encerrada com EOS.
- Ausencia de diagnostico no adaptador.

A correcao nao modifica o texto gerado, nao completa
JSON incompleto e nao transforma falhas operacionais
em ausencia de evidencias.

**Validacao:** registrar o resultado dos testes
de regressao e da suite completa apos a execucao.

**Pendente:** avaliar o Qwen real e determinar
se o limite de tokens explica as falhas observadas.


### Complemento - P3.2B: diagnostico de erros JSON

**Data:** 10/11/2026

**Status:** implementado e validado por testes automatizados.

Foi integrada a leitura de `ultimo_diagnostico` ao
tratamento de erros de interpretacao do JSON em
`src/generation/resposta.py`.

Quando ocorre uma falha de interpretacao, o sistema
continua retornando `erro_operacional`, mas agora
inclui as informacoes disponiveis sobre a geracao:

- motivo_parada
- tokens_gerados
- max_tokens_saida

O tratamento permite diferenciar geracoes encerradas
por EOS de geracoes que atingiram o limite de tokens
sem encerramento reconhecido.

**Validacao executada:**
- 15 de 15 testes de resposta aprovados.
- 35 de 35 testes da suite completa aprovados.
- git diff --check sem problemas na verificacao final.

**Arquivos modificados:**
- src/generation/resposta.py
- tests/test_resposta.py

**Limitacoes:**
- Os testes desta atividade utilizam geradores simulados.
- O diagnostico ainda nao foi validado em nova execucao
  com o Qwen real.
- A implementacao nao repara automaticamente JSON invalido.
- A causa dos erros observados no lote P2 ainda precisa
  ser confirmada com execucoes reais.

**Proximo passo:** avaliar qualidade de geracao,
com foco em escopo, abstencao e fidelidade das respostas.


## D020 - Validar citacoes em todos os estados de resposta (10/11/2026)

**Status:** implementada e validada por testes automatizados.

**Responsavel:** P3 - Geracao.

### Problema identificado

A implementacao anterior validava citacoes apenas quando
o status da resposta era `respondida`.

Uma resposta classificada como `evidencias_insuficientes`
ou `fora_do_escopo` poderia apresentar marcadores ou
documentos inexistentes sem ser rejeitada.

### Decisao

Aplicar a validacao de citacoes estruturadas tambem
aos estados de recusa.

Manter a possibilidade de recusar uma pergunta sem
apresentar fontes, desde que nenhuma citacao invalida
seja fornecida.

### Implementacao

Arquivo alterado: `src/generation/resposta.py`.

- Respostas com status `respondida` continuam utilizando
  as validacoes implementadas na D018.
- Respostas com outros status tambem passam pela
  verificacao de citacoes.
- Marcadores inexistentes, IDs divergentes e trechos
  invalidos resultam em `erro_operacional`.
- Recusas legitimas sem fontes continuam permitidas.

### Testes de regressao

Arquivo alterado: `tests/test_resposta.py`.

Foram adicionados tres testes:

1. Insuficiencia de evidencias com fonte inventada.
2. Fora do escopo com fonte inventada.
3. Recusa legitima sem fontes.

### Resultados

Antes da correcao:
- 18 testes de resposta executados.
- 16 aprovados.
- 2 falhas esperadas.

Apos a correcao:
- 18/18 testes de resposta aprovados.
- 38/38 testes da suite completa aprovados.
- `git diff --check` sem problemas na verificacao final.

### Limitacoes

A validacao confirma consistencia estrutural das citacoes,
mas nao comprova fidelidade semantica.

Marcadores presentes exclusivamente no texto livre da
resposta ainda nao sao verificados por esta alteracao.

O comportamento com o Qwen real e os casos de avaliacao
da P1 ainda precisa ser validado.

### Proxima atividade

P3.3B - Tratamento de perguntas fora do escopo
e de evidencias insuficientes.


## D021 - Triagem conservadora de perguntas fora do escopo (10/11/2026)

**Status:** implementada e validada por testes automatizados.

**Responsavel:** P3 - Geracao.

### Problema identificado

A implementacao P2 encaminhava todas as perguntas nao vazias
diretamente ao recuperador vetorial.

Mesmo perguntas claramente externas ao dominio, como
questoes de geografia e instrucoes culinarias, acionavam
a recuperacao semantica.

Como a busca vetorial pode retornar documentos para
perguntas irrelevantes, o LLM poderia tentar responder
utilizando conhecimento externo as avaliacoes da Olist.

### Decisao

Implementar uma triagem preliminar e conservadora
de intencoes fora do escopo, antes da recuperacao.

O filtro deve bloquear somente padroes externos
reconhecidos com alta confianca.

Perguntas ambiguas ou relacionadas a avaliacoes
devem continuar no fluxo RAG.

### Implementacao

Arquivos:
- src/escopo.py
- src/app.py
- tests/test_app.py

Foi criada a funcao `claramente_fora_do_escopo()`.

A funcao:
- Normaliza texto e acentos.
- Reconhece alguns padroes externos predefinidos.
- Preserva perguntas com referencias explicitas
  ao dominio de avaliacoes e consumidores.
- Evita recuperar documentos em casos bloqueados.
- Retorna fora_do_escopo com listas de fontes e IDs vazias.

### Validacao

Antes da implementacao:
- 7 testes executados.
- 5 aprovados.
- 2 falhas esperadas.

Depois da implementacao:
- 7/7 testes de aplicacao aprovados.
- 41/41 testes da suite completa aprovados.
- git diff --check sem problemas.

Cenarios verificados:
- Pergunta geografica claramente externa.
- Pedido de instrucao culinaria.
- Pergunta legitima sobre avaliacoes de livros de receitas.
- Preservacao dos comportamentos anteriores da aplicacao.

### Limitacoes

O filtro nao constitui um classificador geral de escopo.

Perguntas externas com outras formulacoes podem
seguir para a recuperacao e depender do LLM.

Perguntas ambiguas nao devem ser bloqueadas
automaticamente por palavras isoladas.

Ainda nao foi implementada uma verificacao completa
de suficiencia semantica das evidencias.

Os testes utilizaram componentes simulados.
A qualidade do comportamento com o Qwen real
ainda precisa ser avaliada.

### Proxima atividade

Validar abstencao por evidencias insuficientes,
testar perguntas adversariais e integrar os
casos de desenvolvimento preparados pela P1.

## D022 - Integracao P1/P2/P3 para avaliacao controlada (10/11/2026)

**Decisao:** integrar o conjunto de desenvolvimento da P1 ao executor RAG da P2/P3, preservando a separacao entre recuperacao_e_geracao e contexto_controlado.

**Motivo:** os casos controlados devem receber exclusivamente as evidencias fixadas pela P1. Executar recuperacao vetorial nesses casos alteraria as condicoes do teste e comprometeria a comparabilidade dos resultados.

**Implementacao:**
- O carregador aceita os identificadores `id` (P1) e `case_id` (P2).
- O modo `recuperacao_e_geracao` preserva o fluxo normal do RAG.
- O modo `contexto_controlado` fornece as fixtures diretamente ao gerador, sem consultar o ChromaDB.
- Contextos obrigatorios ausentes produzem `erro_operacional`.
- Contextos declarados intencionalmente vazios produzem `evidencias_insuficientes`, sem consultar o recuperador ou o gerador.
- A CLI aceita `--id` e `--fixtures`, permitindo executar casos individuais.
- Os resultados locais sao ignorados pelo Git.
- Somente o conjunto de desenvolvimento da P1 foi incorporado. O conjunto reservado permanece fora dos ajustes.

**Validacao:**
- 56 testes automatizados aprovados.
- `git diff --check` sem erros.
- Caso I01 executado pelo executor integrado.
- I01 retornou `evidencias_insuficientes`, com `retrieved_ids`, `context_ids` e `citacoes` vazios.
- A mensagem foi ajustada para informar ausencia de evidencias no contexto fornecido, sem afirmar que houve busca vetorial.
- O verificador P1 aceitou a primeira predicao I01: status correspondente ao gabarito e nenhum erro estrutural.

**Limitacoes:** I01 foi uma execucao deterministica, sem inferencia do Qwen. A origem `fixture_sintetica` utilizada na revisao nao deve ser interpretada como geracao sintetica da resposta ou execucao do modelo. Os testes automatizados e a revisao estrutural nao comprovam a fidelidade semantica de respostas produzidas pelo Qwen.

**Conferencia futura:** executar I02 com modelo real; avaliar A01/A02 quanto a prompt injection; avaliar os casos com recuperacao; revisar evidencias, citacoes, latencia e falhas operacionais. Manter os casos reservados separados da etapa de ajustes.
