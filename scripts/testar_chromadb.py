
"""Etapa 3.2: indexacao vetorial persistente com ChromaDB."""

import json
from pathlib import Path
import random

import chromadb
from sentence_transformers import SentenceTransformer

RAIZ = Path(__file__).resolve().parents[1]

ARQUIVO_DOCUMENTOS = (
    RAIZ / "data" / "processed" / "reviews_documentos.jsonl"
)

PASTA_BANCO = RAIZ / "data" / "vectorstore" / "chroma_e5_piloto"

NOME_COLECAO = "olist_e5_piloto_1000_v1"
NOME_MODELO = "intfloat/multilingual-e5-small"

TAMANHO_AMOSTRA = 1000
SEMENTE = 42
TAMANHO_LOTE = 100
TOP_K = 5

PERGUNTAS = [
    "Quais clientes reclamaram de atraso na entrega?",
    "Quais problemas de qualidade dos produtos foram relatados?",
    "O que os clientes elogiaram sobre suas compras?",
]


def carregar_amostra():
    documentos = []

    with ARQUIVO_DOCUMENTOS.open(
        "r", encoding="utf-8"
    ) as arquivo:
        for linha in arquivo:
            if linha.strip():
                documentos.append(json.loads(linha))

    if len(documentos) < TAMANHO_AMOSTRA:
        raise ValueError("Quantidade insuficiente de documentos.")

    sorteador = random.Random(SEMENTE)
    return sorteador.sample(documentos, TAMANHO_AMOSTRA)


def preparar_metadados(documento):
    """Remove valores ausentes e conserva os metadados principais."""
    origem = documento["metadata"]

    campos = [
        "document_id",
        "review_id",
        "order_id",
        "review_score",
        "tipo_texto",
        "review_creation_date",
    ]

    return {
        campo: origem[campo]
        for campo in campos
        if campo in origem and origem[campo] is not None
    }


def main():
    print("Iniciando o banco vetorial...")

    amostra = carregar_amostra()

    modelo = SentenceTransformer(NOME_MODELO)

    cliente = chromadb.PersistentClient(
        path=str(PASTA_BANCO)
    )

    colecao = cliente.get_or_create_collection(
        name=NOME_COLECAO,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
        embedding_function=None,
    )

    quantidade_atual = colecao.count()

    if quantidade_atual == 0:
        print("Gerando embeddings para indexacao...")

        textos = [
            documento["page_content"]
            for documento in amostra
        ]

        vetores = modelo.encode(
            ["passage: " + texto for texto in textos],
            batch_size=32,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        for inicio in range(0, len(amostra), TAMANHO_LOTE):
            fim = inicio + TAMANHO_LOTE

            lote = amostra[inicio:fim]

            colecao.add(
                ids=[doc["id"] for doc in lote],
                documents=[
                    doc["page_content"] for doc in lote
                ],
                metadatas=[
                    preparar_metadados(doc) for doc in lote
                ],
                embeddings=vetores[inicio:fim].tolist(),
            )

            print(
                f"Documentos indexados: {colecao.count()}"
            )

    elif quantidade_atual == TAMANHO_AMOSTRA:
        print("Colecao ja indexada. Reutilizando os vetores.")

    else:
        raise RuntimeError(
            "Colecao parcialmente preenchida. "
            "Interrompendo para evitar inconsistencias. "
            f"Quantidade atual: {quantidade_atual}"
        )

    print(f"\nTotal no banco vetorial: {colecao.count()}")

    if colecao.count() != TAMANHO_AMOSTRA:
        raise RuntimeError("Quantidade indexada incorreta.")

    for pergunta in PERGUNTAS:
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

        print("\n" + "=" * 65)
        print(f"PERGUNTA: {pergunta}")

        for posicao, (
            identificador, texto, metadados, distancia
        ) in enumerate(
            zip(
                resultados["ids"][0],
                resultados["documents"][0],
                resultados["metadatas"][0],
                resultados["distances"][0],
            ),
            start=1,
        ):
            similaridade = 1 - distancia

            print(f"\n{posicao}. Similaridade: {similaridade:.4f}")
            print(f"   document_id: {identificador}")
            print(f"   review_id: {metadados.get('review_id')}")
            print(f"   nota: {metadados.get('review_score')}")
            print(f"   texto: {texto[:400]}")

    print("\nTeste do ChromaDB concluido.")


if __name__ == "__main__":
    main()
