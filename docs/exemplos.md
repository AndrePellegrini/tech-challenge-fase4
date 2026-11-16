# Exemplos de perguntas e respostas

Execuções reais do pipeline completo (índice de 42.687 avaliações, E5-small + ChromaDB, Qwen2.5-1.5B-Instruct em CPU), realizadas em 15/11/2026 com a configuração `v3-adaptativo-p311`. Nada foi editado à mão: respostas, afirmações e trechos foram transcritos de [`reports/exemplos_respostas.json`](../reports/exemplos_respostas.json), gerado por:

```powershell
.\.venv\Scripts\python.exe scripts/gerar_exemplos.py
```

As perguntas seguem os exemplos do enunciado (páginas 4, 5, 8 e 9), incluindo o desafio adicional de metadados (filtro por nota) e casos de limite. A coluna **Nota** mostra a nota (1 a 5) da avaliação citada. Cada exemplo termina com uma **análise crítica** da fidelidade da resposta às evidências.

## Resumo

| # | Tipo | Pergunta | Filtro | Status | Avaliação |
|---|---|---|---|---|---|
| [E01](#e01--investigação-de-reclamações) | Reclamações | Principais problemas relatados | — | respondida | Parcial: 2 afirmações em inglês; 1 fonte positiva |
| [E02](#e02--investigação-de-um-tema-específico) | Tema específico | Problemas relacionados à entrega | — | respondida | Fiel |
| [E03](#e03--busca-por-experiências-positivas) | Experiências positivas | Aspectos mais elogiados | — | respondida | Fiel |
| [E04](#e04--exploração-baseada-em-evidências) | Evidências | Avaliações que sustentam problemas de prazo | — | respondida | Bom; 1 fonte com polaridade oposta |
| [E05](#e05--qualidade-dos-produtos) | Qualidade | Padrões sobre qualidade dos produtos | — | respondida | Falha de recuperação |
| [E06](#e06--investigação-de-insatisfação-filtro-por-nota) | Insatisfação | Padrões de clientes insatisfeitos | nota ≤ 2 | respondida | Fontes corretas; 2 afirmações sem suporte |
| [E07](#e07--metadados-nota-baixa-filtro-por-nota) | Metadados | Principais problemas | nota ≤ 1 | respondida | Majoritariamente fiel |
| [E08](#e08--metadados-nota-alta-filtro-por-nota) | Metadados | O que mais elogiam na entrega | nota ≥ 5 | respondida | Fiel |
| [E09](#e09--evidências-insuficientes) | Sem evidências | Quantos clientes moram em Curitiba | — | evidencias_insuficientes | Recusa correta |
| [E10](#e10--fora-do-escopo-regra-de-escopo) | Fora do escopo | Receita de bolo | — | fora_do_escopo | Recusa correta (sem busca) |
| [E11](#e11--pergunta-externa-sem-regra-de-escopo) | Fora do escopo | Previsão do tempo | — | evidencias_insuficientes | Recusa correta; status ideal seria fora_do_escopo |

**Leitura geral:** nenhuma resposta inventou fontes ou trechos (todos são literais e verificáveis) e as três perguntas sem resposta possível foram recusadas. Os erros observados vêm de duas origens: **recuperação**, quando a similaridade vetorial traz textos do mesmo vocabulário com intenção oposta ou lateral (E04, E05), e **síntese do modelo de 1,5B**, com citações em excesso, extrapolações e deriva de idioma (E01, E06). O filtro por nota (E06–E08) melhora visivelmente a precisão das fontes.

---

## E01 — Investigação de reclamações

> **Pergunta:** Quais são os principais problemas relatados pelos clientes em suas avaliações?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Quais são os principais problemas relatados pelos clientes em suas avaliações?"
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 146.7 s

**Resposta:**

> De acordo com as avaliações dos clientes, alguns dos principais problemas relatados incluem demora na entrega, falta de informações claras sobre o status do pedido, falta de resolução eficaz dos problemas reportados, e falta de atendimento personalizado.

**Afirmações e fontes:**

- Demora na entrega é um problema frequentemente relatado. — F1, F5, F6
- Lack of clear information about the order status is also mentioned by customers. — F1, F2, F8
- Ineffective resolution to reported problems is highlighted in several reviews. — F1, F2, F3, F4
- Insufficient personalized customer service is noted. — F7

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F1 | `olist_review_row_000949` | 5 | Comentario: Atenciosos,ligam para dar acompanhamento. Bom prazo de validade. Demorou de chegar. Agora é verificar a qualidade do produto. |
| F5 | `olist_review_row_002345` | 1 | Titulo: Informação\preocupada Comentario: Minha avaliação ta sendo esta pq aqui aparece q recebi o produto e ainda não chegou em casa.Por favor, queria saber o q está acontecendo ??? Atenciosamente, Juliana |
| F6 | `olist_review_row_037364` | 1 | Comentario: Solicitei cancelamento e estou aguardando o retorno. Não entendi porque estão me enviando essa avaliação... |
| F2 | `olist_review_row_090071` | 3 | Comentario: Sou cliente e essa é a primeira vez que houve problemas, até o momento não recebi a mercadoria. Aguardo retorno urgente!! |
| F8 | `olist_review_row_028468` | 1 | Comentario: Gostaria de saber a quem e como reclamar para receber o produto correto. Grata. |
| F3 | `olist_review_row_013810` | 1 | Comentario: Estou há mais de 01 mês esperando a solução do problema conforme atendimento aberto . Quanto tempo mais terei que aguardar ? Tenho que buscar ajuda no procon ou juizados de pequenas causas ?? |
| F4 | `olist_review_row_088507` | 1 | Comentario: Só posso fazer avaliação depois que receber o meu produto!!! No momento todas as respostas são negativa |
| F7 | `olist_review_row_016802` | 1 | Comentario: Total falta de respeito com o consumidor. Além de não realizar a entrega que tinha um prazo enorme, ao longo do período, pedi mais detalhes do status para acompanhar o processo e nunca ligaram. |

**Análise:** **Parcialmente fiel.** Os temas (demora, falta de informação, problemas não resolvidos, atendimento) aparecem de fato nas fontes, quase todas de nota 1. Dois problemas: duas das quatro afirmações saíram em inglês, uma deriva de idioma do modelo de 1,5B; e F1 é uma avaliação nota 5, majoritariamente positiva ("atenciosos, ligam para dar acompanhamento"), citada como evidência de problema. A pergunta é ampla: a busca vetorial privilegia avaliações que falam de "avaliação" e "problema", por isso pedidos não entregues dominam o contexto.

---

## E02 — Investigação de um tema específico

> **Pergunta:** O que os clientes relatam sobre problemas relacionados à entrega?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "O que os clientes relatam sobre problemas relacionados à entrega?"
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 146.3 s

**Resposta:**

> Os clientes relatam problemas de entrega, incluindo atrasos, falta de informações sobre o status e problemas na entrega dos produtos.

**Afirmações e fontes:**

- Comentários de clientes indicam atrasos na entrega. — F2, F3, F4, F5, F6, F7, F8
- Clientes relatam falta de informações sobre o status da entrega. — F2, F3, F4, F5, F6, F7, F8
- Alguns clientes relatam problemas específicos durante a entrega. — F2, F3, F4, F5, F6, F7, F8

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F2 | `olist_review_row_012144` | 1 | Comentario: Atraso na entrega |
| F3 | `olist_review_row_081354` | 3 | Comentario: Foi falado que houve problemas na entrega mas não falava o que e nem como seria resolvido. Me causou uma preocupação e frustração desnecessária já que o mesmo chegou antes do prazo estipulado. |
| F4 | `olist_review_row_007572` | 1 | Comentario: demora na entrega |
| F5 | `olist_review_row_049598` | 1 | Comentario: Tive problemas com a entrega. E ainda não mandaram todos os produtos! |
| F6 | `olist_review_row_065820` | 1 | Comentario: Primeiro marcaram uma data e nao cumpriram depois disseram ter dificuldade na entrega quando recebemos pelo menos 50 encomendas por dia |
| F7 | `olist_review_row_091805` | 1 | Comentario: TERRIVEL ESTE PROBLEMA DA ENTREGA |
| F8 | `olist_review_row_044788` | 1 | Titulo: produto nao entregue Comentario: recebi um email das lannister informando que haviam problemas na distribuicao, e agora outro perguntando se recebi a compra o que ate o momento nao aconteceu, nao sei o que aconteceu ou a que atribu |

**Análise:** **Fiel.** As sete fontes tratam de problemas de entrega (atraso, entrega parcial, falta de informação), e a síntese não acrescenta nada que não esteja nelas. A ressalva é a seletividade: cada afirmação cita as sete fontes, quando bastariam duas ou três por afirmação.

---

## E03 — Busca por experiências positivas

> **Pergunta:** Quais aspectos da experiência de compra são mais elogiados pelos clientes?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Quais aspectos da experiência de compra são mais elogiados pelos clientes?"
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 151.7 s

**Resposta:**

> Os clientes elogiam principalmente a qualidade dos produtos, a rapidez da entrega, a eficiência do atendimento e a confiabilidade das lojas.

**Afirmações e fontes:**

- Os clientes elogiam a qualidade dos produtos. — F1, F3, F7
- Os clientes elogiam a rapidez da entrega. — F1, F2, F5, F6
- Os clientes elogiam a eficiência do atendimento. — F1, F2, F3, F4, F5, F6, F7
- Os clientes elogiam a confiabilidade das lojas. — F1, F2, F3, F4, F5, F6, F7

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F1 | `olist_review_row_028879` | 5 | Comentario: excelente experiência de compra. Obrigado |
| F3 | `olist_review_row_026046` | 5 | Comentario: Lojas ótimas e de confiança. Recomendo sim. Compro a anos e é de confiança. Obrigada pelo atendimentos e a atenção. |
| F7 | `olist_review_row_092448` | 5 | Comentario: Adorei a compra. Farei mais compras futuramente. Com certeza. |
| F2 | `olist_review_row_080308` | 5 | Comentario: Fiquei muito feliz pela compra / atendimento e a entrega q foi bem antes do previsto tanto q no mesmo dia incentivei minha mãe tbm comprar com vcs. Estão de parabéns ! Ganharam fiéis clientes ! |
| F5 | `olist_review_row_092003` | 5 | Comentario: Com relação à compra e entrega, só tenho a elogiar. Muito obrigada! |
| F6 | `olist_review_row_016833` | 5 | Comentario: É impressionante o respeito, consideração, tratamento e agilidade pela entrega da mercadoria ao consumidor dado pelo stark, só me resta agradecer e reconhecer estes valores. Obrigado. |
| F4 | `olist_review_row_058615` | 5 | Comentario: Foi maravilhosa minha experiência com a loja! Chegou bem antes da data prevista, não teria como ficar mais contente. Muito obrigada 😁👍🏻 |

**Análise:** **Fiel.** Todas as fontes são avaliações nota 5 e sustentam os temas apontados: experiência geral, entrega antes do prazo, atendimento e confiança na loja. "Qualidade dos produtos" é a afirmação mais fraca: F1 e F7 elogiam a compra, não o produto em si.

---

## E04 — Exploração baseada em evidências

> **Pergunta:** Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?"
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 138.1 s

**Resposta:**

> De acordo com as evidências fornecidas, há avaliações que indicam problemas recorrentes relacionados ao prazo de entrega. As avaliações com notas baixas (F2, F6) e aquelas que mencionam dificuldades para cumprir o prazo (F1, F3, F7) sugerem que existem problemas consistentes em relação à entrega dentro dos prazos estabelecidos.

**Afirmações e fontes:**

- Existem avaliações com notas baixas referentes ao prazo de entrega. — F2, F6
- Há avaliações que mencionam dificuldades para cumprir o prazo de entrega. — F1, F3, F7

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F2 | `olist_review_row_075527` | 1 | Comentario: Ñ compriu seu prazo de entrega |
| F6 | `olist_review_row_099061` | 1 | Comentario: Esperava que eles cumprisse o prazo da entrega |
| F1 | `olist_review_row_023217` | 4 | Comentario: o que mata é o prazo da entrega! |
| F3 | `olist_review_row_077102` | 4 | Comentario: Achei vwue o prazo de entrega nåo foi respeitado. |
| F7 | `olist_review_row_052263` | 5 | Comentario: O produto chegou entes do prazo de entrega. Recomendo. |

**Análise:** **Bom, com um erro de polaridade.** A afirmação de que F2 e F6 têm nota baixa está correta (ambas nota 1; a nota faz parte do contexto enviado ao modelo). F1, F2, F3 e F6 sustentam a conclusão. **F7 contradiz a conclusão:** "O produto chegou antes do prazo de entrega. Recomendo." (nota 5). É o caso típico de similaridade sem intenção: o texto fala de "prazo de entrega" com polaridade oposta. O filtro por nota (E06/E07) é a mitigação disponível.

---

## E05 — Qualidade dos produtos

> **Pergunta:** Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?"
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 140.9 s

**Resposta:**

> Sim, existem padrões recorrentes nas avaliações da Olist referentes à qualidade dos produtos. As avaliações mais frequentes incluem reclamações sobre entrega tardia, falta de informações sobre o produto antes da compra, e comentários negativos em relação à qualidade do produto. Algumas avaliações também indicam que alguns clientes esperavam mais do produto e estão satisfeitos com a entrega, embora ainda estejam pendentes de testes para avaliar sua qualidade.

**Afirmações e fontes:**

- Há padrões recorrentes nas avaliações da Olist sobre a qualidade dos produtos. — F1, F2, F3, F4, F5, F6, F7, F8

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F1 | `olist_review_row_079731` | 3 | Comentario: Produto nao foi entregue ainda. Por isso nao é possivel fazer uma avaliaçao adequada |
| F2 | `olist_review_row_069660` | 3 | Comentario: A avaliação geral foi regular porque ainda não testei o produto. Avaliei a compra/entrega. |
| F3 | `olist_review_row_088507` | 1 | Comentario: Só posso fazer avaliação depois que receber o meu produto!!! No momento todas as respostas são negativa |
| F4 | `olist_review_row_080952` | 3 | Comentario: O produto foi entregue no prazo Ainda não posso avaliar a qualidade do produto Por não usei ainda |
| F5 | `olist_review_row_070041` | 1 | Titulo: ainda recomendo Comentario: Se o produto não chegou, como pode ser obrigatório o preenchimento da avaliação geral ou se eu recomendo a loja?! Piada né?! |
| F6 | `olist_review_row_036894` | 2 | Comentario: Não estou entendendo?! Por q desta avaliação?? Cadê meu produto?? |
| F7 | `olist_review_row_083087` | 5 | Titulo: Produto de qualidade! Comentario: Compromisso com o cliente e qualidade no produto resumem essa compra. |
| F8 | `olist_review_row_008942` | 5 | Comentario: Quanto a loja, perfeito. Entregue no prazo e tudo OK com o produto. Com relação ao produto, não testei ainda, mas parece de boa qualidade. |

**Análise:** **Falha de recuperação.** A busca por "qualidade dos produtos" trouxe principalmente avaliações que *ainda não puderam* avaliar a qualidade ("ainda não testei", "não recebi"). A síntese mistura temas e menciona "entrega tardia" e "falta de informações" que não respondem à pergunta. É a mesma limitação registrada em D011/D012, em que consultas sobre qualidade melhoram com reformulação ou reranking.

---

## E06 — Investigação de insatisfação (filtro por nota)

> **Pergunta:** Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?" --nota-max 2
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 164.8 s

**Resposta:**

> As avaliações de clientes insatisfeitos mostram padrões consistentes de reclamações e frustração. Pode-se notar que muitos clientes estão questionando a entrega, a eficácia dos serviços de atendimento ao cliente e a qualidade do produto. Há também preocupações com a segurança da informação e a falta de transparência na comunicação entre a empresa e os clientes.

**Afirmações e fontes:**

- Muitos clientes estão questionando a entrega. — F1, F2, F3, F4, F5, F6, F7, F8
- Há preocupações com a eficácia dos serviços de atendimento ao cliente. — F3, F4, F5, F6, F7, F8
- Existem preocupações com a qualidade do produto. — F3, F4, F5, F6, F7, F8
- Há preocupações com a segurança da informação. — F7, F8
- Há preocupações com a falta de transparência na comunicação. — F3, F4, F5, F6, F7, F8

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F1 | `olist_review_row_094502` | 1 | Titulo: insatisfeita Comentario: Preciso saber a data que será entregue |
| F2 | `olist_review_row_027722` | 1 | Comentario: COMO VOU AVALIAR UM PRODUTO QUE NÃO RECEBI |
| F3 | `olist_review_row_096185` | 1 | Titulo: Insatisfação Comentario: Fiz uma compra q foi cancelada por vcs. Tentei por diversas vezes falar com vcs contudo não fui atendido. Não sei pq minha compra foi cancelada? Ninguém entrou em contato e não consigo ser atendido |
| F4 | `olist_review_row_008799` | 1 | Comentario: nao sei como posso avaliar se nao recebi a mercadoria |
| F5 | `olist_review_row_086041` | 1 | Comentario: Nao posso avalia um produto que ainda nao recebi se fosse para avalia eu daria 0 |
| F6 | `olist_review_row_088507` | 1 | Comentario: Só posso fazer avaliação depois que receber o meu produto!!! No momento todas as respostas são negativa |
| F7 | `olist_review_row_005509` | 1 | Comentario: Mandei um email até agora não obtive resposta. Meu produto não chegou... |
| F8 | `olist_review_row_002467` | 1 | Comentario: o produto nao poder ser avaliado ainda nao recebi |

**Análise:** **Filtro funcionando; síntese com afirmações sem suporte.** O filtro `--nota-max 2` funcionou: as oito fontes são avaliações nota 1, todas de insatisfação. O padrão dominante, produto não recebido e falta de resposta, está bem sustentado. Porém "segurança da informação" e "qualidade do produto" não aparecem em nenhuma fonte; são extrapolações do modelo. A validação de citações garante que as fontes existem, não que cada afirmação é sustentada por elas (limitação documentada).

---

## E07 — Metadados: nota baixa (filtro por nota)

> **Pergunta:** Quais são os principais problemas relatados nas avaliações?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Quais são os principais problemas relatados nas avaliações?" --nota-max 1
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 178.1 s

**Resposta:**

> De acordo com as avaliações dos clientes, alguns dos principais problemas incluem:
> - Espera indefinida de entrega.
> - Problemas de atendimento ao cliente.
> - Falta de informação sobre o estado do pedido.
> - Problemas financeiros, como bloqueio de cartão de crédito.
> - Problemas de entrega, como produtos não chegarem ou passarem do prazo de entrega.
> - Inconsistências entre informações fornecidas pela empresa e o que os clientes esperavam.
> - Demora excessiva para resolver problemas já registrados.
> - Falta de feedback ou acompanhamento após a compra.

**Afirmações e fontes:**

- Problemas de entrega e falta de informação são frequentemente mencionados. — F1, F2, F3, F4, F5, F6, F7, F8
- Falta de atendimento eficiente e demora para resolver problemas também são pontos críticos. — F1, F2, F3, F4, F5, F6, F7, F8
- Problemas financeiros, como bloqueio de cartão de crédito, são mencionados frequentemente. — F6, F7
- Inconsistência entre informações fornecidas pela empresa e o que os clientes esperavam é outra preocupação. — F1, F2, F3, F4, F5, F6, F7, F8

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F1 | `olist_review_row_037364` | 1 | Comentario: Solicitei cancelamento e estou aguardando o retorno. Não entendi porque estão me enviando essa avaliação... |
| F2 | `olist_review_row_087991` | 1 | Comentario: A dias esperando e ainda nao chegou. Como resolvemos? |
| F3 | `olist_review_row_002345` | 1 | Titulo: Informação\preocupada Comentario: Minha avaliação ta sendo esta pq aqui aparece q recebi o produto e ainda não chegou em casa.Por favor, queria saber o q está acontecendo ??? Atenciosamente, Juliana |
| F4 | `olist_review_row_088507` | 1 | Comentario: Só posso fazer avaliação depois que receber o meu produto!!! No momento todas as respostas são negativa |
| F5 | `olist_review_row_013810` | 1 | Comentario: Estou há mais de 01 mês esperando a solução do problema conforme atendimento aberto . Quanto tempo mais terei que aguardar ? Tenho que buscar ajuda no procon ou juizados de pequenas causas ?? |
| F6 | `olist_review_row_079769` | 1 | Comentario: ja tive problemas com a lannister 2 vez o meu produto nao foi entregue e nem estornaram meu cartao quero saber como vai ficar |
| F7 | `olist_review_row_000689` | 1 | Comentario: Produto mais que passou do prazo de entregar, tento resolver o problema com a empresa e não consigo falar com ninguém. Tudo que fazem é me passar para reclamar num sistema que não funciona. |
| F8 | `olist_review_row_005509` | 1 | Comentario: Mandei um email até agora não obtive resposta. Meu produto não chegou... |

**Análise:** **Majoritariamente fiel.** Com `--nota-max 1`, todas as fontes são nota 1. Não entrega, falta de retorno e demora para resolver estão nas fontes. "Bloqueio de cartão" distorce F6, que fala de estorno não realizado, e "frequentemente" é uma generalização que o Top-K não permite.

---

## E08 — Metadados: nota alta (filtro por nota)

> **Pergunta:** O que os clientes mais elogiam na entrega?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "O que os clientes mais elogiam na entrega?" --nota-min 5
```

**Status:** `respondida` · recuperados: 50 · no contexto: 8 · tempo: 113.1 s

**Resposta:**

> Os clientes mais elogiaram a eficiência e rapidez da entrega.

**Afirmações e fontes:**

- Comentários de alta nota referentes à entrega rápida e eficaz. — F1, F2, F3, F4, F5, F6, F7, F8

**Evidências citadas:**

| Marcador | Documento | Nota | Trecho literal |
|---|---|---:|---|
| F1 | `olist_review_row_054806` | 5 | Comentario: Amei a loja cumprem a entrega |
| F2 | `olist_review_row_054192` | 5 | Comentario: Ótima loja entrega é excelente |
| F3 | `olist_review_row_016833` | 5 | Comentario: É impressionante o respeito, consideração, tratamento e agilidade pela entrega da mercadoria ao consumidor dado pelo stark, só me resta agradecer e reconhecer estes valores. Obrigado. |
| F4 | `olist_review_row_023049` | 5 | Comentario: Ótima loja entrega no prazo |
| F5 | `olist_review_row_012068` | 5 | Comentario: Agilidade na entrega! |
| F6 | `olist_review_row_051344` | 5 | Comentario: Eficiente do pedido a entrega |
| F7 | `olist_review_row_025688` | 5 | Comentario: Espetacular o tempo de entrega! Parabéns |
| F8 | `olist_review_row_076286` | 5 | Comentario: otima loja entrega super rapida |

**Análise:** **Fiel.** Com `--nota-min 5`, as oito fontes são elogios nota 5 à entrega (rapidez, prazo, eficiência), e a resposta curta reflete exatamente isso. Exemplo de como o metadado melhora a precisão da recuperação.

---

## E09 — Evidências insuficientes

> **Pergunta:** Quantos clientes moram na cidade de Curitiba?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Quantos clientes moram na cidade de Curitiba?"
```

**Status:** `evidencias_insuficientes` · recuperados: 50 · no contexto: 8 · tempo: 105.1 s

**Resposta:**

> Não há informações específicas sobre quantos clientes moram na cidade de Curitiba presente nas evidências fornecidas.

**Análise:** **Recusa correta.** A pergunta busca um dado demográfico que não existe nas avaliações. O sistema recuperou documentos, mas o modelo reconheceu que nenhum sustentava a resposta e não inventou um número.

---

## E10 — Fora do escopo (regra de escopo)

> **Pergunta:** Me ensine uma receita de bolo de cenoura.

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Me ensine uma receita de bolo de cenoura."
```

**Status:** `fora_do_escopo` · recuperados: 0 · no contexto: 0 · tempo: 0.0 s

**Resposta:**

> Esta solicitacao esta fora do escopo de analise das avaliacoes da Olist.

**Análise:** **Recusa correta, sem custo.** A regra de escopo identifica o pedido culinário e devolve `fora_do_escopo` sem consultar o índice nem chamar o modelo (0 s).

---

## E11 — Pergunta externa sem regra de escopo

> **Pergunta:** Qual a previsão do tempo em São Paulo amanhã?

```powershell
.\.venv\Scripts\python.exe -m src.app --pergunta "Qual a previsão do tempo em São Paulo amanhã?"
```

**Status:** `evidencias_insuficientes` · recuperados: 50 · no contexto: 8 · tempo: 180.3 s

**Resposta:**

> Não há informações específicas sobre a previsão do tempo em São Paulo amanhã presente nas evidências fornecidas.

**Análise:** **Recusa correta, com o status de insuficiência.** Previsão do tempo não está coberta pelas regras de escopo, então a pergunta seguiu para o RAG. O modelo não inventou uma previsão e recusou por falta de evidências. O resultado é seguro, mas o status ideal seria `fora_do_escopo`: as regras são conservadoras de propósito (D025), e o modelo prefere `evidencias_insuficientes` quando há documentos no contexto.

---
