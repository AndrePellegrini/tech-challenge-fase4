# Revisão disponível e passagem para P2/P3

Data: 07/11/2026. Frente revisora: P1, curadoria assistida por IA.
Repositório de André consultado novamente nesta entrega:
`1363122f6dcc00be6119b20404a04c1b6ce43a27`. A consulta não encontrou novos commits.

## Resultado da revisão do disponível

| Verificação | Resultado | Evidência e próximo responsável |
|---|---|---|
| Integridade da base de entrada | Validada localmente; 42.687 documentos | `reports/validacao_local_dados.json`; P1 |
| Exatidão das fontes de referência | Conferida contra o corpus, sem texto de evidência idêntico entre splits | `reports/auditoria_benchmark_p1.json`; P1/P4 revisam rótulos |
| E5 com query/passage e normalização | Encontrado no código existente, sem mudança de estratégia necessária | `scripts/indexar_base_completa.py`; P2 reproduz índice |
| Relevância da recuperação | Evidências exploratórias do colega mostram confusão entre elogio e reclamação; não houve nova execução local | `docs/decisoes.md`, D011/D012; P2 mede baseline com os 18 casos |
| Geração com evidências | Não implementada no checkpoint | diretório generation contém apenas arquivo inicial vazio no remoto; P3 integra |
| Respostas reais e fidelidade | Não avaliáveis nesta entrega | `reports/revisao_rag_desenvolvimento.json` e `revisao_rag_reservado.json` registram 0 resultados recebidos |
| Revisão conjunta P2/P3 | Não realizada; nenhum integrante foi contatado | Artefatos e protocolo disponíveis para o time |

O runtime desta sessão não tem sentence-transformers ou ChromaDB instalados.
Isso não é um defeito comprovado do requirements. O gerador tampouco está presente
na aplicação. Não foi instalada ou implementada toda a frente de P2/P3 só para
produzir um resultado artificial. A conclusão da revisão semântica depende de
predições reais do fluxo integrado e de revisão dos responsáveis.

## Entrega pronta para os colegas

P2 recebe corpus, IDs, contrato e perguntas de desenvolvimento. Deve registrar
retrieved_ids e context_ids reais. Referências são exemplos não exaustivos, então
documentos alternativos relevantes precisam ser avaliados, não marcados como erro
automaticamente. Priorizar a distinção de negações, reclamação/elogio e diversidade.

P3 recebe contextos controlados, regras de resposta e esquema de predições.
Deve demonstrar fontes verificáveis e recusa sem inferências externas. Toda afirmação
substantiva precisa de suporte, não apenas um rodapé com uma fonte existente.

O verificador `scripts/revisar_resultados_rag.py` e a ficha de revisão estão prontos.
Os nove testes desse verificador passaram com fixtures sintéticas, além dos cinco
testes originais de dados. Isso valida o apoio à revisão, não a qualidade do RAG.

## Onde a próxima etapa deve parar

Até 10/11: fluxo básico com E5 -> Chroma -> contexto -> LLM -> resposta com fontes,
ou status explícito de insuficiência/fora de escopo. Deve rodar pela CLI ou interface
mínima e produzir o arquivo de predições/trace de desenvolvimento. Usar fixtures
controladas para casos de limite e perguntas abertas para o fluxo completo.

Parar quando houver execução reproduzível, contrato estável, nenhuma fonte inventada
nos casos de conferência, negações preservadas e erros operacionais tratados.
Não usar o teste reservado para escolher prompt/Top-K. Não adicionar joins, agentes,
multimodalidade ou dashboard elaborado nessa etapa.

## Etapa 3: validação e fechamento do desenvolvimento

De 11 a 13/11: P2 compara baseline e candidato BM25/RRF nos casos de desenvolvimento;
P3 corrige geração/recusa; P1/P4 rotulam resultados e revisam suporte por afirmação.
Escolher configuração, registrar resultados e congelar. Depois executar os 12 casos
reservados e registrar falhas sem esconder limitações. Reprodução limpa e documentação
devem ser concluídas. Se o reservado orientar correção, registrar e renovar o teste.

Fechar desenvolvimento em 13/11. Dias 14 e 15: vídeo de até sete minutos e conferência
do pacote; 16 e 17: reserva e envio. Prazo final confirmado: 17/11/2026.
