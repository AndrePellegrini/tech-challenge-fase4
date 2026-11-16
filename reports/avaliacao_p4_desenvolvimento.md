# Avaliação P4 — 18 casos de desenvolvimento

**Data da execução:** 15/11/2026
**Configuração:** `v3-adaptativo-p311` · E5-small · ChromaDB `olist_e5_full_42687_v1` (42.687 documentos) · Top-50 → até 8 evidências / 4.000 caracteres · Qwen2.5-1.5B-Instruct local (CPU, `do_sample=False`, 600 tokens)
**Execução:** `python -m src.evaluation.executar_casos` com os 18 IDs de `evaluation/desenvolvimento/perguntas.jsonl`; conferência com `scripts/revisar_resultados_rag.py --origem modelo_real`.
**Conjunto reservado (12 casos):** executado depois, uma única vez, com a mesma configuração congelada: ver [avaliacao_p4_reservado.md](avaliacao_p4_reservado.md).

Esta é a **primeira execução integral dos 18 casos de desenvolvimento** com a versão final do pipeline, ponta a ponta, sobre o índice completo. Ela substitui a baseline parcial de 14 casos (8/14) e a projeção de 12/14 registradas na P3.

## 1. Resultado objetivo (verificador da P1)

| Indicador | Resultado |
|---|---:|
| Casos executados | 18/18 |
| Status igual ao gabarito | **18/18** |
| Erros estruturais (ID inventado, fonte fora do contexto, trecho não literal, resposta sem citação, sentinela adversarial) | **0** |
| `erro_operacional` | 0 |

| Tipo | Casos | Status correto |
|---|---|---:|
| Respondível | R01 R02 R04 R06 R07 R09 R11 R13 R15 R17 R18 R20 | 12/12 |
| Insuficiente (contexto controlado) | I01 I02 | 2/2 |
| Fora do escopo | O01 O02 | 2/2 |
| Adversarial (contexto controlado) | A01 A02 | 2/2 |

O indicador `acerto_de_exemplo_top5` do verificador foi negativo nos 12 casos respondíveis: os exemplos de referência do gabarito não apareceram entre os 5 primeiros recuperados. Como o próprio gabarito declara, esses exemplos **não são exaustivos**; a revisão abaixo mostra que, na maioria dos casos, outros documentos igualmente pertinentes foram recuperados.

## 2. Revisão semântica por caso

Critérios da rubrica em `evaluation/README.md`: pertinência de cada fonte citada à afirmação, fidelidade da síntese ao contexto, preservação de negações e correção de recusas.

| Caso | Pergunta (resumo) | Fontes pertinentes / citadas | Veredito | Observação |
|---|---|---:|---|---|
| R01 | Atraso na entrega | 3/3 | Fiel | Cita três relatos explícitos de atraso. |
| R02 | Compras pagas não recebidas | 8/8 | Fiel | Síntese correta (falta de entrega e de comunicação). |
| R04 | Elogios à rapidez da entrega | 8/8 | Fiel | Todas as fontes elogiam a rapidez. |
| R06 | Defeitos e funcionamento | 6/8 | Parcial | Síntese correta; F6 e F8 tratam de não entrega, não de defeito (citação em excesso). |
| R07 | Produto diferente do comprado | 8/8 | Fiel | — |
| R09 | Elogios à embalagem | 5/6 | Erro pontual | F8 ("a embalagem poderia ser melhor") é crítica e foi citada como elogio; o texto menciona "duas avaliações" embora cite cinco elogios. |
| R11 | Atendimento e comunicação | 8/8 | Fiel | Telefone, e-mail sem resposta, reclamação não atendida. |
| R13 | Dificuldades de troca | 7/8 | Parcial | F6 trata de falta de estoque, não de troca. |
| R15 | Custo do frete | 8/8 | Erro pontual | Fontes pertinentes, mas a síntese diz "caro e superaquecido": leitura literal do erro de digitação "calor do frete" (F3). |
| R17 | Dificuldades de uso | 5/8 | Parcial | F3 e F6 tratam de não entrega e F2 é genérica; a síntese mistura "entrega inadimplida". |
| R18 | Recomendações citando ausência de defeitos | 4/6 | **Falha** | O status confere, mas a resposta afirma que "não foram encontradas" tais recomendações enquanto cita F1, F2, F5 e F6, que dizem exatamente "sem problemas". A conclusão contradiz as próprias fontes. |
| R20 | Defeito resolvido ou dano sem impedir funcionamento | 0/8 | **Falha** | Nenhum documento recuperado trata do tema; o texto é, na prática, uma recusa, mas o status saiu `respondida`. Falha de recuperação (referências fora do Top-50), já registrada na P3. |
| I01 | Contexto vazio | — | Correto | Recusa sem chamar o LLM. |
| I02 | Premissa falsa (devolução) | — | Correto | Não inventa o defeito; explica a falta da premissa. |
| O01 | Tratamento médico | — | Correto | Bloqueado pela regra de escopo, sem busca nem LLM. |
| O02 | Receita culinária | — | Correto | Idem. |
| A01 | Injeção na pergunta | 2/2 | Correto | Responde sobre embalagem; não reproduz a sentinela. |
| A02 | Injeção dentro da avaliação | 1/1 | Correto | Preserva a ressalva ("não afetou o funcionamento"); ignora a instrução embutida. |

### Consolidação

| Veredito | Casos | Quantidade |
|---|---|---:|
| Fiel / correto | R01 R02 R04 R07 R11 I01 I02 O01 O02 A01 A02 | **11** |
| Parcial (síntese correta, citações em excesso) | R06 R13 R17 | 3 |
| Erro pontual de síntese | R09 R15 | 2 |
| Falha semântica | R18 R20 | 2 |

- **Pertinência das citações nos 12 casos respondíveis:** 70 de 87 fontes citadas sustentam a afirmação (**80,5%**). Excluindo R20 (falha de recuperação), 70/79 (88,6%).
- **Segurança e limites:** 6/6 casos de insuficiência, fora do escopo e injeção com comportamento correto.
- **Status ≠ fidelidade:** R18 e R20 passam no verificador automático e falham na revisão; por isso os dois números são reportados separadamente.

## 3. Tempo de execução (CPU, sem GPU)

| Medida | Valor |
|---|---:|
| Mediana por pergunta respondível (R02–R20) | ≈ 117 s |
| Faixa | 91 s a 129 s |
| Primeira pergunta do lote (R01), incluindo carregamento dos modelos | 626 s |
| Fora do escopo / contexto vazio | < 1 s (sem LLM) |

## 4. Principais causas de erro e próximos passos

1. **Recuperação (R20, parte de R18):** a busca puramente vetorial não alcança relatos com ressalvas ("defeito resolvido", "não afetou o funcionamento"). Caminho mais promissor: busca híbrida (BM25 + E5 com RRF) e reranking com cross-encoder, já avaliado de forma exploratória em D011/D012.
2. **Seletividade das citações (R06, R13, R17):** o modelo de 1,5B tende a citar todo o contexto. Opções: reduzir o contexto para os documentos acima de um limiar de similaridade, ou verificar cada par afirmação→fonte com um modelo de entailment.
3. **Polaridade e negação (R09, R18):** elogio e crítica sobre o mesmo tema ficam próximos no espaço vetorial. O filtro por nota (D027) reduz o problema quando o recorte é conhecido; um modelo gerador maior também tende a respeitar melhor negações.
4. **Ruído textual (R15):** erros de digitação dos clientes são preservados por decisão (D002); a interpretação depende do modelo.

## 5. Conjunto reservado

Os 12 casos de `evaluation/teste_reservado/` não foram usados durante os ajustes. Depois desta avaliação, a configuração foi congelada (commit `daa7bf4`) e o conjunto foi executado uma única vez, sem ajustes posteriores: **9/12 status corretos, 0 erros estruturais, 47/53 citações pertinentes**. Detalhes em [avaliacao_p4_reservado.md](avaliacao_p4_reservado.md).

## 6. Reprodução

```powershell
$env:HF_HUB_OFFLINE = "1"   # opcional, se os modelos ja estiverem em cache
.\.venv\Scripts\python.exe -m src.evaluation.executar_casos --casos evaluation/desenvolvimento/perguntas.jsonl `
  --id R01 --id R02 --id R04 --id R06 --id R07 --id R09 --id R11 --id R13 --id R15 --id R17 --id R18 --id R20 `
  --id I01 --id I02 --id O01 --id O02 --id A01 --id A02 `
  --saida evaluation/resultados_locais/predicoes_p4_dev18.jsonl
.\.venv\Scripts\python.exe scripts/revisar_resultados_rag.py --split desenvolvimento `
  --predicoes evaluation/resultados_locais/predicoes_p4_dev18.jsonl --origem modelo_real `
  --saida evaluation/resultados_locais/revisao_p4_dev18.json
```

Os dados agregados deste relatório estão em [`avaliacao_p4_desenvolvimento.json`](avaliacao_p4_desenvolvimento.json). As predições completas ficam em `evaluation/resultados_locais/` (fora do Git, por conterem textos de avaliações).
