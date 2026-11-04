# Perfil inicial da base Olist

Fonte: `olist_order_reviews_dataset.csv` (dataset oficial Olist).

| Indicador | Total |
|---|---:|
| total avaliacoes | 99.224 |
| com comentario | 40.950 |
| com titulo | 11.566 |
| somente titulo | 1.737 |
| somente comentario | 31.121 |
| titulo e comentario | 9.829 |
| sem texto | 56.537 |
| documentos aproveitaveis | 42.687 |
| review id repetidos | 814 |
| order id repetidos | 551 |

## Distribuicao das notas

| Nota | Quantidade |
|---|---:|
| 1 | 11424 |
| 2 | 3151 |
| 3 | 8179 |
| 4 | 19142 |
| 5 | 57328 |

## Cuidados

- IDs naturais repetidos foram CONTADOS, mas nao removidos automaticamente.
- Textos sem titulo e sem comentario foram excluidos APENAS da base textual processada.
- Este perfil nao prova frequencia de reclamacoes; isso exige analise posterior.
- Manter os dados brutos como foram baixados e fora do repositorio publico.
