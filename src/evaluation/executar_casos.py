
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


def carregar_casos(caminho) -> list[dict]:
    casos = []
    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            linha = linha.strip()
            if not linha:
                continue

            caso = json.loads(linha)
            if "case_id" not in caso or "pergunta" not in caso:
                raise ValueError(f"Caso invalido na linha {numero_linha}: faltam case_id/pergunta")

            casos.append(caso)

    return casos


def executar(casos: list[dict], recuperador: Recuperador, gerador: GeradorQwenLocal) -> list[dict]:
    predicoes = []

    for caso in casos:
        # time.monotonic() em vez de time.time(): nao sofre com ajustes
        # de relogio do sistema, ideal para medir duracao de um unico
        # caso (usado so para registrar o tempo no trace, nao como
        # cronometro entre maquinas).
        inicio = time.monotonic()
        resultado = processar_pergunta(caso["pergunta"], recuperador, gerador)
        duracao = time.monotonic() - inicio

        predicoes.append({
            "case_id": caso["case_id"],
            "status": resultado["status"],
            "resposta": resultado["resposta"],
            "retrieved_ids": resultado["retrieved_ids"],
            "context_ids": resultado["context_ids"],
            # "citacoes" no contrato do PDF corresponde as "fontes" do
            # nosso schema interno (marcador + document_id + trecho).
            "citacoes": resultado["fontes"],
            "trace": {
                "consulta": caso["pergunta"],
                "modelo_embeddings": config.MODELO_EMBEDDINGS,
                "colecao": config.COLECAO_CHROMA,
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


def main():
    parser = argparse.ArgumentParser(
        description="Executa casos de desenvolvimento contra o pipeline RAG"
    )
    parser.add_argument("--casos", required=True, help="Arquivo JSONL com os casos (case_id, pergunta)")
    parser.add_argument("--saida", required=True, help="Arquivo JSONL de predicoes a gerar")
    argumentos = parser.parse_args()

    casos = carregar_casos(argumentos.casos)
    print(f"Casos carregados: {len(casos)}")

    # Recuperador e gerador sao criados uma unica vez e reutilizados em
    # todos os casos (o modelo de embeddings, o indice e o LLM so sao
    # carregados na primeira chamada, dentro de processar_pergunta).
    recuperador = Recuperador()
    gerador = GeradorQwenLocal()

    predicoes = executar(casos, recuperador, gerador)
    salvar_predicoes(predicoes, argumentos.saida)

    print(f"Predicoes salvas em: {argumentos.saida}")


if __name__ == "__main__":
    main()
