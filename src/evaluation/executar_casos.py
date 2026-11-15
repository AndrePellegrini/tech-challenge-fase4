
"""Executa casos de desenvolvimento contra o pipeline RAG e salva predicoes.

Contrato de saida por linha (JSONL), conforme o PDF de entrega P1:
case_id, status, resposta, retrieved_ids, context_ids, citacoes e um
trace de execucao (configuracao, consulta, tempos, erros).

Uso:
    python -m src.evaluation.executar_casos \
        --casos data/eval/casos_exemplo.jsonl \
        --saida reports/predicoes_dev.jsonl
"""

import argparse
import json
import time
from pathlib import Path

from src import config
from src.app import processar_pergunta
from src.generation.modelo import GeradorQwenLocal
from src.retrieval.recuperador import Recuperador
from src.generation.resposta import gerar_resposta
from src.retrieval.tipos import Evidencia


def carregar_casos(caminho) -> list[dict]:
    casos = []
    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha:
                continue

            caso = json.loads(linha)

            # Compatibilidade P1/P2: a P1 usa "id" e a P2,
            # "case_id". Preservamos os demais campos,
            # especialmente o "modo" da avaliacao.
            identificador = caso.get("case_id") or caso.get("id")

            if (
                not isinstance(identificador, str)
                or not identificador.strip()
                or not isinstance(caso.get("pergunta"), str)
                or not caso["pergunta"].strip()
            ):
                raise ValueError(
                    f"Caso invalido na linha {numero_linha}: "
                    "faltam identificador ou pergunta"
                )

            if (
                caso.get("id") is not None
                and caso.get("case_id") is not None
                and caso["id"] != caso["case_id"]
            ):
                raise ValueError(
                    f"Identificadores divergentes na linha {numero_linha}"
                )

            caso["case_id"] = identificador
            casos.append(caso)


    return casos

def _executar_contexto_controlado(
    caso: dict,
    gerador,
    fixtures: list[dict],
) -> dict:
    """Executa geracao apenas com as evidencias fixas da P1.

    Nao consulta ChromaDB e nao altera o texto das fixtures.
    """
    case_id = caso["case_id"]

    documentos = [
        documento
        for documento in fixtures
        if documento["case_id"] == case_id
    ]

    # Contexto vazio so e valido quando declarado
    # explicitamente no benchmark.
    if not documentos and caso.get("tema") != "contexto_vazio":
        return {
            "status": "erro_operacional",
            "resposta": (
                f"Fixture obrigatoria ausente para o caso {case_id}."
            ),
            "afirmacoes": [],
            "fontes": [],
            "retrieved_ids": [],
            "context_ids": [],
        }


    # Caso controlado intencionalmente sem evidencias.
    # Nao houve busca vetorial; portanto, nao devemos
    # informar que a recuperacao deixou de encontrar documentos.
    if not documentos:
        return {
            "status": "evidencias_insuficientes",
            "resposta": (
                "Nao ha evidencias no contexto fornecido "
                "para responder a pergunta."
            ),
            "afirmacoes": [],
            "fontes": [],
            "retrieved_ids": [],
            "context_ids": [],
        }


    evidencias = [
        Evidencia(
            marcador=f"F{indice}",
            document_id=documento["document_id"],
            review_id=None,
            review_score=None,
            trecho=documento["page_content"],
            similaridade=None,
        )
        for indice, documento in enumerate(documentos, start=1)
    ]

    try:
        resposta = gerar_resposta(
            caso["pergunta"],
            evidencias,
            gerador,
        )

        resultado = resposta.model_dump()

    except Exception as erro:
        resultado = {
            "status": "erro_operacional",
            "resposta": (
                "Falha operacional no contexto controlado: "
                f"{erro}"
            ),
            "afirmacoes": [],
            "fontes": [],
        }

    resultado["retrieved_ids"] = []
    resultado["context_ids"] = [
        evidencia.document_id
        for evidencia in evidencias
    ]

    return resultado


def executar(
    casos: list[dict],
    recuperador: Recuperador,
    gerador: GeradorQwenLocal,
    fixtures: list[dict] | None = None,
) -> list[dict]:
    """Executa casos P1/P2 respeitando o modo de avaliacao."""

    predicoes = []
    fixtures = fixtures if fixtures is not None else []

    for caso in casos:
        inicio = time.monotonic()

        modo = caso.get(
            "modo",
            "recuperacao_e_geracao",
        )

        if modo == "contexto_controlado":
            resultado = _executar_contexto_controlado(
                caso,
                gerador,
                fixtures,
            )

        elif modo == "recuperacao_e_geracao":
            resultado = processar_pergunta(
                caso["pergunta"],
                recuperador,
                gerador,
            )

        else:
            raise ValueError(
                f"Modo de avaliacao desconhecido: {modo}"
            )

        duracao = time.monotonic() - inicio

        predicoes.append({
            "case_id": caso["case_id"],
            "status": resultado["status"],
            "resposta": resultado["resposta"],
            "retrieved_ids": resultado["retrieved_ids"],
            "context_ids": resultado["context_ids"],
            "citacoes": resultado["fontes"],
            "trace": {
                "consulta": caso["pergunta"],
                "modo": modo,
                "modelo_embeddings": (
                    config.MODELO_EMBEDDINGS
                    if modo == "recuperacao_e_geracao"
                    else None
                ),
                "colecao": (
                    config.COLECAO_CHROMA
                    if modo == "recuperacao_e_geracao"
                    else None
                ),
                "modelo_gerador": config.MODELO_GERADOR,
                "versao_prompt": config.VERSAO_PROMPT,
                "tempo_segundos": round(duracao, 3),
            },
        })

    return predicoes


def salvar_predicoes(predicoes: list[dict], caminho_saida):
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    # JSONL (um objeto por linha), mesmo formato usado pela base
    # documental (reviews_documentos.jsonl), para manter consistencia
    # no projeto e facilitar leitura linha a linha de arquivos grandes.
    with Path(caminho_saida).open("w", encoding="utf-8") as arquivo:
        for predicao in predicoes:
            arquivo.write(json.dumps(predicao, ensure_ascii=False) + "\n")


def carregar_fixtures(caminho) -> list[dict]:
    """Le as evidencias fixas do benchmark P1."""

    fixtures = []

    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue

            documento = json.loads(linha)

            for campo in ("case_id", "document_id", "page_content"):
                if (
                    not isinstance(documento.get(campo), str)
                    or not documento[campo].strip()
                ):
                    raise ValueError(
                        f"Fixture invalida na linha {numero_linha}: "
                        f"campo {campo}"
                    )

            fixtures.append(documento)

    return fixtures



def main():
    parser = argparse.ArgumentParser(
        description="Executa casos de avaliacao do RAG"
    )

    parser.add_argument(
        "--casos",
        required=True,
        help="Arquivo JSONL com as perguntas",
    )

    parser.add_argument(
        "--saida",
        required=True,
        help="Arquivo JSONL para salvar as predicoes",
    )

    parser.add_argument(
        "--id",
        dest="ids",
        action="append",
        help="ID do caso. Repita --id para selecionar varios.",
    )

    parser.add_argument(
        "--fixtures",
        default="evaluation/fixtures/contextos.jsonl",
        help="Arquivo JSONL de contextos controlados",
    )

    argumentos = parser.parse_args()

    # O conjunto reservado nao deve ser usado durante os ajustes.
    if "teste_reservado" in Path(argumentos.casos).parts:
        parser.error(
            "O conjunto reservado nao deve ser executado "
            "durante o desenvolvimento."
        )

    casos = carregar_casos(argumentos.casos)

    if argumentos.ids:
        selecionados = set(argumentos.ids)
        disponiveis = {caso["case_id"] for caso in casos}

        desconhecidos = selecionados - disponiveis

        if desconhecidos:
            parser.error(
                "IDs nao encontrados: "
                + ", ".join(sorted(desconhecidos))
            )

        casos = [
            caso
            for caso in casos
            if caso["case_id"] in selecionados
        ]

    elif any("modo" in caso for caso in casos):
        # Protecao temporaria: evita executar o benchmark
        # completo por acidente durante a integracao.
        parser.error(
            "Para o benchmark P1, selecione pelo menos "
            "um caso com --id. A execucao completa "
            "sera habilitada apos a validacao."
        )

    print(f"Casos selecionados: {len(casos)}")
    print(
        "IDs: "
        + ", ".join(caso["case_id"] for caso in casos)
    )

    precisa_fixtures = any(
        caso.get("modo") == "contexto_controlado"
        for caso in casos
    )

    if precisa_fixtures:
        caminho_fixtures = Path(argumentos.fixtures)

        if not caminho_fixtures.is_file():
            parser.error(
                f"Arquivo de fixtures nao encontrado: "
                f"{caminho_fixtures}"
            )

        fixtures = carregar_fixtures(caminho_fixtures)
        print(f"Registros de fixtures carregados: {len(fixtures)}")

    else:
        fixtures = []

    # Ambos possuem inicializacao tardia.
    # I01 nao deve carregar embeddings nem Qwen.
    recuperador = Recuperador()
    gerador = GeradorQwenLocal()

    predicoes = executar(
        casos=casos,
        recuperador=recuperador,
        gerador=gerador,
        fixtures=fixtures,
    )

    salvar_predicoes(
        predicoes,
        argumentos.saida,
    )

    print(f"Predicoes salvas em: {argumentos.saida}")

    for predicao in predicoes:
        print(
            f"{predicao['case_id']}: "
            f"{predicao['status']}"
        )


if __name__ == "__main__":
    main()
