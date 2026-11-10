# Matriz de rastreabilidade - Fase 4

Fonte primaria: `[IAST] - Tech Challenge - Fase 4.pdf`, paginas 4 a 10.

| ID | Exigencia no enunciado | Etapa | Materiais FIAP | Evidencia futura | Estado |
|---|---|---|---|---|---|
| R01 | Selecao dos dados e conteudos textuais | 1 | NLP aulas 1-2 | Perfil e recorte justificado | Concluido |
| R02 | Limpeza, preparacao e valores ausentes | 1-2 | NLP aula 2 | Codigo e contagens antes/depois | Concluido |
| R03 | Organizacao dos documentos | 2 | NLP aulas 2-4 | Documentos com IDs e metadata | Concluido |
| R04 | Criacao de embeddings | 3 | NLP aula 4; LangChain aula 3 | Modelo, dimensao e teste | Concluido |
| R05 | Armazenamento e indexacao | 3 | LangChain aula 3 | Indice reproduzivel | Concluido |
| R06 | Processamento/transformacao da pergunta | 4 | IA Generativa aula 3 | Consulta e log | Concluido (`Recuperador.buscar`) |
| R07 | Recuperacao semantica e selecao de comentarios | 3-4 | LangChain aula 3; GenAI aula 2 | Top-K com ids/scores | Concluido (`recuperador.py`, `contexto.py`) |
| R08 | Contexto e geracao de resposta | 4 | LangChain aulas 1-2 | RAG funcionando | Implementado; validacao end-to-end pendente |
| R09 | Resposta com evidencias rastreaveis | 4-5 | GenAI aulas 2-3 | ID, trecho e fonte | Implementado (`resposta.py`, validacao de citacoes) |
| R10 | Faltam evidencias ou fora do escopo | 5 | GenAI aulas 3 e 6 | Testes de nao resposta | Implementado; validacao sistematica pendente |
| R11 | Repositorio publico, README, instalacao e reproducao | 1-6 | Engenharia de software | GitHub e documentacao | Em andamento |
| R12 | Video <= 7 minutos com demonstracao e decisoes | 7 | Entregaveis | Link do video | A fazer |
| E01 | Metadados adicionais: nota, entrega, categorias, periodo | Opcional | LangChain aula 3 | Filtros e comparacoes | Nao iniciado |

## Criterios de avaliacao interpretados do enunciado

- Recuperacao relevante
- Contexto pertinente
- Fidelidade aos comentarios
- Evitar afirmacoes inventadas
- Evidencias identificaveis
- Ausencia de evidencias tratada explicitamente

Observacao: nao ha modelo de embeddings, LLM ou interface especificos impostos pelo PDF.


## Acompanhamento - Construcao da Base de Conhecimento

### Requisito 1 - Construcao da base de conhecimento

**Status:** preparacao documental, embeddings e indexacao concluidos.

| Elemento exigido pela FIAP | Situacao | Evidencia |
|---|---|---|
| Selecao dos dados | Concluido | `reports/perfil_olist.md` |
| Limpeza e preparacao textual | Concluido | `src/preprocessing/documentos.py` |
| Tratamento de valores ausentes | Concluido para o recorte textual | `reports/perfil_olist.md` |
| Organizacao dos documentos | Concluido | `data/processed/reviews_documentos.jsonl` |
| Justificativa de chunking | Concluido inicialmente | `docs/decisoes.md` - D005 |
| Criacao dos embeddings | Concluido | `docs/decisoes.md` - D007, D009 |
| Armazenamento e indexacao vetorial | Concluido | `docs/decisoes.md` - D008, D009 |

### Requisito 2 - RAG basico integrado (recuperacao, contexto e geracao)

**Status:** implementado; validacao end-to-end contra o indice completo
e o benchmark oficial da frente de dados (P1) ainda pendente.

| Elemento exigido pela FIAP | Situacao | Evidencia |
|---|---|---|
| Recuperador reutilizavel | Concluido | `src/retrieval/recuperador.py`, D014 |
| Selecao de contexto sem copias desnecessarias | Concluido | `src/retrieval/contexto.py`, D015 |
| Escolha e integracao do LLM | Concluido (Qwen2.5-1.5B local) | `src/generation/modelo.py`, D016 |
| Resposta restrita as evidencias, com citacoes verificaveis | Concluido | `src/generation/resposta.py`, D016 |
| Reconhecimento de evidencias insuficientes | Concluido | `src/app.py` |
| Reconhecimento de perguntas fora do escopo | Concluido (via prompt-base do LLM) | `src/generation/resposta.py` |
| Execucao por CLI | Concluido | `src/app.py` |
| Predicoes salvas com case_id, status, ids e citacoes | Concluido | `src/evaluation/executar_casos.py` |
| Validacao contra o indice completo e casos reais | Pendente | Requer dataset local e benchmark da P1 |

### Evidencias da Etapa 2

A base documental foi construida a partir de 42.687 registros
textuais da Olist, produzindo 42.687 documentos estruturados.

A estrategia inicial preserva uma avaliacao por documento,
sem fragmentacao em chunks.

Os metadados mantem informacoes para rastrear as fontes.

As principais decisoes estao registradas em:

- D001: analise inicial dos textos.
- D002: preservacao de texto e identificadores.
- D003: selecao futura de API e banco vetorial.
- D004: selecao dos registros textuais.
- D005: ausencia de chunking inicial.
- D006: preservacao de repeticoes e limites do recorte textual.

### Pendencias dos requisitos

O Requisito 1 esta implementado e documentado (D007-D009); a qualidade
da recuperacao continua em avaliacao experimental (D010-D012).

O Requisito 2 (RAG basico integrado) esta implementado, mas ainda
precisa de:

1. Validacao contra o indice vetorial completo nesta maquina.
2. Execucao dos 18 casos de desenvolvimento reais da frente de dados (P1).
3. Medicao de tempo e qualidade do Qwen2.5-1.5B-Instruct local.
4. Comparacao sistematica de estrategias de recuperacao antes da Etapa 3
   (E5 puro vs. BM25 + RRF, conforme o PDF de entrega P1).
5. Congelamento de configuracao, prompt e modelo antes dos 12 casos
   reservados para a avaliacao final.
