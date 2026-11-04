# Matriz de rastreabilidade - Fase 4

Fonte primaria: `[IAST] - Tech Challenge - Fase 4.pdf`, paginas 4 a 10.

| ID | Exigencia no enunciado | Etapa | Materiais FIAP | Evidencia futura | Estado |
|---|---|---|---|---|---|
| R01 | Selecao dos dados e conteudos textuais | 1 | NLP aulas 1-2 | Perfil e recorte justificado | A fazer |
| R02 | Limpeza, preparacao e valores ausentes | 1-2 | NLP aula 2 | Codigo e contagens antes/depois | A fazer |
| R03 | Organizacao dos documentos | 2 | NLP aulas 2-4 | Documentos com IDs e metadata | A fazer |
| R04 | Criacao de embeddings | 3 | NLP aula 4; LangChain aula 3 | Modelo, dimensao e teste | A fazer |
| R05 | Armazenamento e indexacao | 3 | LangChain aula 3 | Indice reproduzivel | A fazer |
| R06 | Processamento/transformacao da pergunta | 4 | IA Generativa aula 3 | Consulta e log | A fazer |
| R07 | Recuperacao semantica e selecao de comentarios | 3-4 | LangChain aula 3; GenAI aula 2 | Top-K com ids/scores | A fazer |
| R08 | Contexto e geracao de resposta | 4 | LangChain aulas 1-2 | RAG funcionando | A fazer |
| R09 | Resposta com evidencias rastreaveis | 4-5 | GenAI aulas 2-3 | ID, trecho e fonte | A fazer |
| R10 | Faltam evidencias ou fora do escopo | 5 | GenAI aulas 3 e 6 | Testes de nao resposta | A fazer |
| R11 | Repositorio publico, README, instalacao e reproducao | 1-6 | Engenharia de software | GitHub e documentacao | A fazer |
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

**Status:** preparacao documental concluida; embeddings e indexacao pendentes.

| Elemento exigido pela FIAP | Situacao | Evidencia |
|---|---|---|
| Selecao dos dados | Concluido | `reports/perfil_olist.md` |
| Limpeza e preparacao textual | Concluido | `src/preprocessing/documentos.py` |
| Tratamento de valores ausentes | Concluido para o recorte textual | `reports/perfil_olist.md` |
| Organizacao dos documentos | Concluido | `data/processed/reviews_documentos.jsonl` |
| Justificativa de chunking | Concluido inicialmente | `docs/decisoes.md` - D005 |
| Criacao dos embeddings | Pendente | Etapa 3 |
| Armazenamento e indexacao vetorial | Pendente | Etapa 3 |

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

### Pendencias do requisito

A construcao da base de conhecimento ainda precisa de:

1. Selecao justificada do modelo de embeddings.
2. Geracao dos vetores dos documentos.
3. Criacao do indice vetorial.
4. Testes da qualidade da recuperacao.
5. Documentacao das tecnologias escolhidas.

O Requisito 1 somente sera considerado integralmente concluido
apos a implementacao e validacao desses componentes.
