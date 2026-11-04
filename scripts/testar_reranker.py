
"""Etapa 3.5 - Comparacao de recuperacao com e sem reranking."""

from pathlib import Path

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder


RAIZ = Path(__file__).resolve().parents[1]

PASTA_BANCO = RAIZ / "data" / "vectorstore" / "chroma_e5_completo"

COLECAO = "olist_e5_full_42687_v1"

MODELO_E5 = "intfloat/multilingual-e5-small"

MODELO_RERANKER = (
    "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
)

TOP_CANDIDATOS = 50
TOP_FINAL = 8

PERGUNTAS = {
    "Original": (
        "Quais problemas de qualidade dos produtos foram relatados?"
    ),
    "Reformulada": (
        "Quais avaliacoes relatam produtos defeituosos, "
        "quebrados, danificados ou de ma qualidade?"
    ),
}


def exibir_resultados(titulo, candidatos, tipo_score):
    print("\n" + "-" * 65)
    print(titulo)
    print("-" * 65)

    for posicao, doc in enumerate(candidatos[:TOP_FINAL], start=1):
        print(f"\nResultado {posicao}")
        print(f"Document ID: {doc['id']}")
        print(f"Nota: {doc['metadata'].get('review_score')}")
        print(f"Score {tipo_score}: {doc[tipo_score]:.4f}")
        print(f"Texto: {doc['texto']}")


def main():
    cliente = chromadb.PersistentClient(
        path=str(PASTA_BANCO)
    )

    colecao = cliente.get_collection(
        name=COLECAO,
        embedding_function=None,
    )

    if colecao.count() != 42687:
        raise ValueError("Colecao incompleta.")

    print("Carregando modelo de embeddings...")
    modelo_e5 = SentenceTransformer(MODELO_E5)

    print("Carregando modelo de reranking...")
    reranker = CrossEncoder(MODELO_RERANKER)

    for nome, pergunta in PERGUNTAS.items():
        vetor = modelo_e5.encode(
            ["query: " + pergunta],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        resultados = colecao.query(
            query_embeddings=[vetor.tolist()],
            n_results=TOP_CANDIDATOS,
            include=["documents", "metadatas", "distances"],
        )

        candidatos = []

        for identificador, texto, metadata, distancia in zip(
            resultados["ids"][0],
            resultados["documents"][0],
            resultados["metadatas"][0],
            resultados["distances"][0],
        ):
            candidatos.append({
                "id": identificador,
                "texto": texto,
                "metadata": metadata,
                "similaridade": 1 - distancia,
            })

        pares = [
            (pergunta, doc["texto"])
            for doc in candidatos
        ]

        scores = np.asarray(
            reranker.predict(
                pares,
                batch_size=8,
                show_progress_bar=True,
            )
        ).reshape(-1)

        if len(scores) != len(candidatos):
            raise RuntimeError("Quantidade de scores inesperada.")

        for doc, score in zip(candidatos, scores):
            doc["reranker"] = float(score)

        reordenados = sorted(
            candidatos,
            key=lambda doc: doc["reranker"],
            reverse=True,
        )

        print("\n" + "=" * 65)
        print(f"CONSULTA: {nome}")
        print(f"PERGUNTA: {pergunta}")

        exibir_resultados(
            "BASELINE - E5 + CHROMADB",
            candidatos,
            "similaridade",
        )

        exibir_resultados(
            "EXPERIMENTO - E5 + RERANKER",
            reordenados,
            "reranker",
        )

        print("\nTextos distintos no Top-8:")
        print(
            "Baseline:",
            len({d["texto"].casefold().strip()
                 for d in candidatos[:TOP_FINAL]}),
        )
        print(
            "Reranker:",
            len({d["texto"].casefold().strip()
                 for d in reordenados[:TOP_FINAL]}),
        )

    print("\nExperimento de reranking concluido.")


if __name__ == "__main__":
    main()
