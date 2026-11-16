
"""Orquestracao do fluxo RAG: pergunta -> busca -> contexto -> LLM -> resposta.

Execucao por CLI:
    python -m src.app --pergunta "Quais relatos descrevem atraso na entrega?"
    python -m src.app --pergunta "Quais problemas aparecem?" --nota-max 2

Carrega o modelo de embeddings, o indice vetorial e o LLM uma unica vez
por processo (nao recarrega a cada pergunta).
"""

import argparse
import json
import sys

from src import config
from src.escopo import claramente_fora_do_escopo
from src.generation.modelo import GeradorQwenLocal
from src.generation.resposta import gerar_resposta
from src.retrieval.contexto import montar_contexto
from src.retrieval.recuperador import Recuperador


def _resposta_erro(mensagem: str) -> dict:
    # Formato minimo de erro_operacional, usado sempre que uma etapa do
    # pipeline falha por motivo tecnico (nao por falta de evidencias).
    # retrieved_ids/context_ids ficam vazios porque nenhuma busca ou
    # selecao de contexto foi concluida com sucesso neste caminho.
    return {
        "status": "erro_operacional",
        "resposta": mensagem,
        "afirmacoes": [],
        "fontes": [],
        "retrieved_ids": [],
        "context_ids": [],
    }


def processar_pergunta(
    pergunta: str,
    recuperador: Recuperador,
    gerador: GeradorQwenLocal,
    nota_min: int | None = None,
    nota_max: int | None = None,
) -> dict:
    """Executa o fluxo completo para uma pergunta e devolve o contrato de saida.

    Erros operacionais (falha na recuperacao, timeout, excecao do modelo)
    sempre viram status erro_operacional, nunca evidencias_insuficientes.

    nota_min/nota_max sao opcionais e restringem a recuperacao pela nota
    da avaliacao (D027). Quando ambos sao None, o fluxo e identico ao
    avaliado nos casos de desenvolvimento da P1.
    """
    # Passo 1 do fluxo do PDF de entrega P1: validar a entrada antes de
    # gastar tempo com embeddings, busca ou geracao.
    pergunta = (pergunta or "").strip()
    if not pergunta:
        return _resposta_erro("Pergunta vazia.")

    # Passo 2: gerar o embedding da pergunta (feito dentro do Recuperador,
    # que ja aplica o prefixo "query:" do modelo E5) e consultar o indice.
    # Qualquer excecao aqui (indice ausente, timeout, erro do ChromaDB)
    # e tratada como falha operacional, nunca como "sem evidencias" --
    # a ausencia de evidencias so pode ser concluida quando a busca
    # realmente rodou e nao encontrou nada.

    # P3.3B - Triagem conservadora antes da busca vetorial.
    # Somente perguntas inequivocamente externas sao
    # recusadas aqui. Casos ambiguos seguem para o RAG.
    if claramente_fora_do_escopo(pergunta):
        return {
            "status": "fora_do_escopo",
            "resposta": (
                "Esta solicitacao esta fora do escopo de "
                "analise das avaliacoes da Olist."
            ),
            "afirmacoes": [],
            "fontes": [],
            "retrieved_ids": [],
            "context_ids": [],
        }

    # Os filtros so sao repassados quando informados, preservando a
    # chamada original buscar(pergunta, k=...) para o fluxo sem filtro.
    filtros = {
        chave: valor
        for chave, valor in (("nota_min", nota_min), ("nota_max", nota_max))
        if valor is not None
    }

    try:
        candidatos = recuperador.buscar(pergunta, k=config.TOP_K_CANDIDATOS, **filtros)
    except Exception as erro:
        return _resposta_erro(f"Falha operacional na recuperacao: {erro}")

    # Passo 3-4: selecionar evidencias distintas e dentro do orcamento de
    # contexto. Tambem protegido por try/except: um bug na selecao (por
    # exemplo, metadado inesperado) deve virar erro_operacional e nao
    # derrubar o processo com uma excecao nao tratada.
    try:
        evidencias = montar_contexto(
            candidatos,
            max_documentos=config.MAX_DOCUMENTOS_CONTEXTO,
            max_caracteres=config.MAX_CARACTERES_CONTEXTO,
        )
    except Exception as erro:
        return _resposta_erro(f"Falha operacional na montagem do contexto: {erro}")

    # Passos 5-6: gerar a resposta restrita ao contexto (ou recusa) e
    # validar a saida do LLM. gerar_resposta() ja devolve um status
    # coerente (respondida/evidencias_insuficientes/fora_do_escopo/
    # erro_operacional) para falhas de parse ou de citacao; o try/except
    # aqui cobre apenas excecoes inesperadas do proprio modelo (timeout,
    # falha de hardware, etc.), que tambem viram erro_operacional.
    try:
        resposta = gerar_resposta(pergunta, evidencias, gerador)
    except Exception as erro:
        resultado = _resposta_erro(f"Falha operacional na geracao: {erro}")
    else:
        resultado = resposta.model_dump()

    # retrieved_ids guarda TODOS os candidatos recuperados (para auditoria
    # de recall); context_ids guarda apenas os que foram efetivamente
    # enviados ao LLM (para conferir se os IDs citados na resposta
    # realmente vieram do contexto enviado, conforme exigido pelo PDF).
    resultado["retrieved_ids"] = [candidato.id for candidato in candidatos]
    resultado["context_ids"] = [evidencia.document_id for evidencia in evidencias]
    if filtros:
        # Registra no proprio resultado qual recorte de notas foi usado,
        # para que a resposta nao seja lida como valida para toda a base.
        resultado["filtros"] = filtros
        # Metadados de cada evidencia enviada ao LLM: permitem conferir,
        # na saida, que todas as fontes respeitam o filtro de nota.
        resultado["evidencias_contexto"] = [
            {
                "marcador": evidencia.marcador,
                "document_id": evidencia.document_id,
                "review_score": evidencia.review_score,
                "similaridade": (
                    round(evidencia.similaridade, 4)
                    if evidencia.similaridade is not None
                    else None
                ),
            }
            for evidencia in evidencias
        ]
    return resultado


def main():
    # No Windows, print() para um arquivo/pipe redirecionado usa a
    # codificacao padrao do console (ex.: cp1252), nao UTF-8 -- o que
    # corrompe acentos mesmo com json.dumps(..., ensure_ascii=False).
    # Forcar UTF-8 aqui garante saida consistente entre plataformas.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Voice of Customer com RAG sobre avaliacoes da Olist"
    )
    parser.add_argument("--pergunta", required=True, help="Pergunta em portugues")
    parser.add_argument(
        "--nota-min", type=int, choices=range(1, 6), default=None,
        help="Considerar apenas avaliacoes com nota >= este valor (1 a 5)",
    )
    parser.add_argument(
        "--nota-max", type=int, choices=range(1, 6), default=None,
        help="Considerar apenas avaliacoes com nota <= este valor (1 a 5)",
    )
    argumentos = parser.parse_args()
    if (
        argumentos.nota_min is not None
        and argumentos.nota_max is not None
        and argumentos.nota_min > argumentos.nota_max
    ):
        parser.error("--nota-min nao pode ser maior que --nota-max")

    # Instanciados uma vez por execucao do processo: o modelo de
    # embeddings, a colecao do ChromaDB e o LLM so sao carregados de
    # fato na primeira propriedade acessada (inicializacao tardia),
    # evitando baixar/carregar tudo quando so se quer, por exemplo,
    # rodar os testes.
    recuperador = Recuperador()
    gerador = GeradorQwenLocal()

    resultado = processar_pergunta(
        argumentos.pergunta,
        recuperador,
        gerador,
        nota_min=argumentos.nota_min,
        nota_max=argumentos.nota_max,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
