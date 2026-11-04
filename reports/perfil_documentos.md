# Perfil da base documental - Etapa 2

Fonte: `data/processed/reviews_preparadas.csv`.

| Indicador | Valor |
|---|---:|
| linhas_entrada | 42.687 |
| documentos_saida | 42.687 |
| somente_titulo | 1.737 |
| somente_comentario | 31.121 |
| titulo_e_comentario | 9.829 |
| review_ids_repetidos_no_recorte | 317 |
| textos_repetidos | 5.975 |
| notas_invalidas | 0 |
| datas_invalidas | 0 |
| palavras_p50 | 10 |
| palavras_p95 | 34 |
| palavras_max | 50 |
| documentos_ate_3_palavras | 5.778 |

## Notas na base textual

| Nota | Quantidade |
|---|---:|
| 1 | 8829 |
| 2 | 2165 |
| 3 | 3643 |
| 4 | 6274 |
| 5 | 21776 |

## Limites da interpretacao

- Uma linha textual origina um documento; IDs naturais podem se repetir.
- Textos curtos e repetidos foram mantidos.
- Nao foram criados embeddings nesta etapa.
- Frequencia de temas nao pode ser inferida so da busca semantica.
- O arquivo JSONL contem comentarios e deve permanecer fora do GitHub.
