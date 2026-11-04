
"""Experimento inicial de recuperacao semantica com comentarios da Olist."""

import json
from pathlib import Path
import random
import sys

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data" / "processed" / "reviews_documentos.jsonl"

MODELO = "intfloat/multilingual-e5-small"
TAMANHO_AMOSTRA = 1000
SEMENTE = 42
TOP_K = 5

PERGUNTAS = [
    "Quais clientes reclamaram de atraso na entrega?",
    "Quais problemas de qualidade dos produtos foram relatados?",
    "O que os clientes elogiaram sobre suas compras?",
]


def carregar_documentos(caminho):
    documentos = []

    with caminho.open("r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue

            documento = json.loads(linha)

            if (
                not isinstance(documento, dict)
                or not isinstance(documento.get("page_content"), str)
            ):
                raise ValueError(
                    f"Documento invalido na linha {numero_linha}"
                )

            if not documento["page_content"].strip():
                raise ValueError(
                    f"Texto vazio na linha {numero_linha}"
                )

            if "id" not in documento or "metadata" not in documento:
                raise ValueError(
                    f"ID ou metadados ausentes na linha {numero_linha}"
                )

            documentos.append(documento)

    return documentos


def main():
    if not ENTRADA.is_file():
        sys.exit(f"Arquivo nao encontrado: {ENTRADA}")

    documentos = carregar_documentos(ENTRADA)

    if not documentos:
        sys.exit("Nenhum documento encontrado.")

    sorteador = random.Random(SEMENTE)

    amostra = sorteador.sample(
        documentos,
        min(TAMANHO_AMOSTRA, len(documentos))
    )

    from sentence_transformers import SentenceTransformer

    print(f"Carregando modelo: {MODELO}", flush=True)
    modelo = SentenceTransformer(MODELO)

    textos = [
        "passage: " + doc["page_content"]
        for doc in amostra
    ]

    vetores_documentos = modelo.encode(
        textos,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    if vetores_documentos.shape != (len(amostra), 384):
        raise ValueError(
            f"Formato inesperado: {vetores_documentos.shape}"
        )

    print(f"Documentos totais no JSONL: {len(documentos)}")
    print(f"Documentos no experimento: {len(amostra)}")
    print(f"Dimensoes por vetor: {vetores_documentos.shape[1]}")

    for pergunta in PERGUNTAS:
        vetor_pergunta = modelo.encode(
            ["query: " + pergunta],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]

        similaridades = vetores_documentos @ vetor_pergunta
        indices = np.argsort(-similaridades)[:TOP_K]

        print("\n" + "=" * 72)
        print(f"PERGUNTA: {pergunta}")

        for posicao, indice in enumerate(indices, start=1):
            doc = amostra[int(indice)]
            meta = doc["metadata"]

            print(
                f"\n{posicao}. Similaridade: "
                f"{similaridades[indice]:.4f}"
            )
            print(f"   document_id: {doc['id']}")
            print(f"   review_id: {meta.get('review_id')}")
            print(f"   nota: {meta.get('review_score')}")
            print(f"   texto: {doc['page_content'][:400]}")

    print(
        "\nExperimento finalizado. "
        "Resultados requerem avaliacao humana."
    )


if __name__ == "__main__":
    main()
