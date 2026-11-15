# Matriz de rastreabilidade — Fase 4

Fonte primária: `[IAST] - Tech Challenge - Fase 4.pdf`, páginas 4 a 10.
Situação revisada em 16/11/2026 (entrega final).

## 1. Requisitos obrigatórios

| ID | Exigência do enunciado | Estado | Evidência |
|---|---|---|---|
| R01 | Seleção dos dados textuais | Concluído | `reports/perfil_olist.md`; D001, D004 |
| R02 | Limpeza, preparação e valores ausentes | Concluído | `src/preprocessing/documentos.py`; `reports/perfil_documentos.md`; D002, D006 |
| R03 | Organização dos documentos | Concluído | JSONL com `id`, `page_content`, `metadata`; D005; hash conferido em `evaluation/manifesto_congelado.json` |
| R04 | Criação dos embeddings | Concluído | E5-small, `passage:`/`query:`, 384 dim.; D007 |
| R05 | Armazenamento e indexação | Concluído | ChromaDB persistente, 42.687 documentos; D008, D009 |
| R06 | Transformação da pergunta | Concluído | Prefixo `query:` e normalização (`Recuperador.buscar`); remoção de comandos de sobrescrita (`extrair_tarefa_legitima`); D024 |
| R07 | Recuperação semântica e seleção | Concluído | `src/retrieval/recuperador.py` (Top-50), `src/retrieval/contexto.py` (deduplicação, 8 textos / 4.000 caracteres); D014, D015 |
| R08 | Construção do contexto e geração | Concluído | `construir_prompt` + Qwen2.5-1.5B local; D016, D026; 18 casos executados ponta a ponta |
| R09 | Respostas com evidências rastreáveis | Concluído | Afirmações→marcadores→`document_id`/trecho literal; validação de citações; 0 erros estruturais em 18 casos |
| R10 | Evidências insuficientes / fora do escopo | Concluído | `src/escopo.py`, status `evidencias_insuficientes`/`fora_do_escopo`; I01, I02, O01, O02 corretos; D023, D025 |
| R11 | Repositório público, README, instalação e reprodução | Concluído | `README.md`, `docs/`, reprodução validada em máquina limpa (hash idêntico da base) |
| R12 | Vídeo de até 7 minutos | Em preparação | Etapa seguinte à entrega do repositório |
| E01 | Desafio adicional: metadados | Concluído (nota) | Filtro `--nota-min`/`--nota-max` (D027); exemplos E06–E08 em `docs/exemplos.md` |

## 2. Entregáveis do repositório (página 9)

| Item exigido | Onde está |
|---|---|
| Código-fonte | `src/`, `scripts/` |
| Instruções de instalação e execução | `README.md`, seções "Como executar" |
| README explicando o projeto | `README.md` |
| Descrição da arquitetura | `docs/arquitetura.md` e diagrama no README |
| Tecnologias e bibliotecas | README, seção "Tecnologias"; `requirements.txt` |
| Estratégia do pipeline RAG | README e `docs/arquitetura.md`, seção 4 |
| Preparação da base | README e `docs/arquitetura.md`, seção 3; `docs/etapa2_guia.md`; `docs/datasheet_olist_p1.md` |
| Justificativa das decisões técnicas | `docs/decisoes.md` (D001–D027) |
| Exemplos de perguntas e respostas | `docs/exemplos.md` (execuções reais) |
| Informações para reproduzir | README, seção "Como executar"; `evaluation/manifesto_congelado.json` |

## 3. Critérios esperados (página 10)

| Critério | Como é atendido | Evidência |
|---|---|---|
| Recuperar conteúdos relevantes | E5 + ChromaDB, deduplicação, filtro por nota | 80,5% das citações pertinentes nos 12 casos respondíveis |
| Construir contexto adequado | Orçamento de 8 textos / 4.000 caracteres, evidências em JSON | `src/retrieval/contexto.py` |
| Gerar respostas coerentes com as evidências | Prompt restrito ao contexto, até 3 afirmações | 11/18 fiéis, 3 parciais, 2 com erro pontual, 2 falhas |
| Evitar informações não fundamentadas | Validação literal de trechos e IDs | 0 erros estruturais |
| Rastreabilidade dos insights | Afirmação→marcador→documento→review/pedido | Contrato de saída em `docs/arquitetura.md` |
| Reconhecer falta de informação | Regras de escopo + status de recusa | I01, I02, O01, O02 corretos |

Detalhes da avaliação: [`reports/avaliacao_p4_desenvolvimento.md`](../reports/avaliacao_p4_desenvolvimento.md).
