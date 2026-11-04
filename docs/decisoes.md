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
