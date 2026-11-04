
"""Etapa 3.4: auditar a relevancia da busca semantica."""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


RAIZ = Path(__file__).resolve().parents[1]

PASTA_BANCO = (
    RAIZ / "data" / "vectorstore" / "chroma_e5_completo"
)

COLECAO = "olist_e5_full_42687_v1"
MODELO = "intfloat/multilingual-e5-small"

TOP_K = 15

PERGUNTAS = {
    "Original": (
        "Quais problemas de qualidade dos produtos foram relatados?"
    ),
    "Reformulada": (
        "Quais avaliacoes relatam produtos defeituosos, "
        "quebrados, danificados ou de ma qualidade?"
    ),
}


def main():
    if not PASTA_BANCO.exists():
        raise FileNotFoundError(
            f"Banco vetorial nao encontrado: {PASTA_BANCO}"
        )

    cliente = chromadb.PersistentClient(
        path=str(PASTA_BANCO)
    )

    colecao = cliente.get_collection(
        name=COLECAO,
        embedding_function=None,
    )

    quantidade = colecao.count()

    print(f"Documentos disponiveis: {quantidade}")

    if quantidade != 42687:
        raise ValueError(
            "A colecao nao possui a quantidade esperada."
        )

    modelo = SentenceTransformer(MODELO)

    for nome, pergunta in PERGUNTAS.items():

        vetor_pergunta = modelo.encode(
            ["query: " + pergunta],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        resultados = colecao.query(
            query_embeddings=[vetor_pergunta.tolist()],
            n_results=TOP_K,
            include=["documents", "metadatas", "distances"],
        )

        textos = resultados["documents"][0]
        identificadores = resultados["ids"][0]
        metadados = resultados["metadatas"][0]
        distancias = resultados["distances"][0]

        print("\n" + "=" * 70)
        print(f"CONSULTA: {nome}")
        print(f"PERGUNTA: {pergunta}")
        print("=" * 70)

        textos_distintos = len({
            texto.casefold().strip()
            for texto in textos
        })

        print(f"Resultados: {len(textos)}")
        print(f"Textos distintos: {textos_distintos}")

        for posicao, (
            identificador, texto, metadata, distancia
        ) in enumerate(
            zip(
                identificadores,
                textos,
                metadados,
                distancias,
            ),
            start=1,
        ):
            print(f"\nResultado {posicao}")
            print(f"Similaridade: {1 - distancia:.4f}")
            print(f"Document ID: {identificador}")
            print(f"Nota: {metadata.get('review_score')}")
            print(f"Texto: {texto}")

    print("\nAuditoria exploratoria concluida.")


if __name__ == "__main__":
    main()
