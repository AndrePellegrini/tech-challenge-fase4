
"""Etapa 3.3: indexacao completa e incremental da Olist no ChromaDB."""

import hashlib
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# 1. Caminhos e configuracoes

RAIZ = Path(__file__).resolve().parents[1]

ARQUIVO_DOCUMENTOS = (
    RAIZ / "data" / "processed" / "reviews_documentos.jsonl"
)

PASTA_BANCO = (
    RAIZ / "data" / "vectorstore" / "chroma_e5_completo"
)

MODELO = "intfloat/multilingual-e5-small"
COLECAO = "olist_e5_full_42687_v1"

TOTAL_ESPERADO = 42687
DIMENSOES = 384
TAMANHO_LOTE = 128
BATCH_EMBEDDINGS = 32
TOP_K = 5

PERGUNTAS = [
    "Quais clientes reclamaram de atraso na entrega?",
    "Quais problemas de qualidade dos produtos foram relatados?",
    "O que os clientes elogiaram sobre suas compras?",
]


# 2. Leitura e validacao da base documental

def carregar_documentos():
    if not ARQUIVO_DOCUMENTOS.is_file():
        raise FileNotFoundError(
            f"Base documental nao encontrada: {ARQUIVO_DOCUMENTOS}"
        )

    documentos = []
    identificadores = set()
    assinatura = hashlib.sha256()

    with ARQUIVO_DOCUMENTOS.open("rb") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            assinatura.update(linha)

            if not linha.strip():
                continue

            documento = json.loads(linha)
            identificador = documento.get("id")
            texto = documento.get("page_content")
            metadados = documento.get("metadata")

            if not isinstance(identificador, str) or not identificador:
                raise ValueError(
                    f"ID invalido na linha {numero_linha}"
                )

            if identificador in identificadores:
                raise ValueError(
                    f"ID duplicado: {identificador}"
                )

            if not isinstance(texto, str) or not texto.strip():
                raise ValueError(
                    f"Texto invalido na linha {numero_linha}"
                )

            if not isinstance(metadados, dict):
                raise ValueError(
                    f"Metadados invalidos na linha {numero_linha}"
                )

            identificadores.add(identificador)
            documentos.append(documento)

    if len(documentos) != TOTAL_ESPERADO:
        raise ValueError(
            f"Esperados {TOTAL_ESPERADO} documentos, "
            f"mas encontrados {len(documentos)}"
        )

    return documentos, assinatura.hexdigest()


# 3. Preparacao dos metadados para o ChromaDB

def preparar_metadados(documento):
    origem = documento["metadata"]

    campos = [
        "document_id",
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "tipo_texto",
        "fonte",
        "n_palavras",
        "hash_texto",
    ]

    metadados = {}

    for campo in campos:
        valor = origem.get(campo)

        if valor is not None and isinstance(
            valor, (str, int, float, bool)
        ):
            metadados[campo] = valor

    return metadados


# 4. Criacao ou reutilizacao do banco vetorial

def obter_colecao(assinatura):
    PASTA_BANCO.mkdir(parents=True, exist_ok=True)

    cliente = chromadb.PersistentClient(
        path=str(PASTA_BANCO)
    )

    configuracao_origem = {
        "modelo": MODELO,
        "assinatura_jsonl": assinatura,
        "total_esperado": TOTAL_ESPERADO,
        "dimensoes": DIMENSOES,
        "prefixo_documento": "passage:",
    }

    colecao = cliente.get_or_create_collection(
        name=COLECAO,
        metadata=configuracao_origem,
        configuration={
            "hnsw": {
                "space": "cosine"
            }
        },
        embedding_function=None,
    )

    metadados_colecao = colecao.metadata or {}

    for chave, valor in configuracao_origem.items():
        if metadados_colecao.get(chave) != valor:
            raise RuntimeError(
                "Colecao existente incompatível com os dados "
                f"ou modelo configurado: {chave}. "
                "Nao reutilize este indice sem investigar."
            )

    return colecao


# 5. Indexacao incremental

def indexar_documentos(colecao, documentos, modelo):
    total = len(documentos)

    print(f"Documentos esperados: {total}")
    print(f"Documentos ja armazenados: {colecao.count()}")

    for inicio in range(0, total, TAMANHO_LOTE):
        lote = documentos[inicio:inicio + TAMANHO_LOTE]

        ids_lote = [doc["id"] for doc in lote]

        consulta = colecao.get(
            ids=ids_lote,
            include=[],
        )

        ids_existentes = set(consulta["ids"])

        faltantes = [
            doc for doc in lote
            if doc["id"] not in ids_existentes
        ]

        if faltantes:
            textos = [
                "passage: " + doc["page_content"]
                for doc in faltantes
            ]

            vetores = modelo.encode(
                textos,
                batch_size=BATCH_EMBEDDINGS,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            if vetores.shape != (len(faltantes), DIMENSOES):
                raise ValueError(
                    f"Dimensoes inesperadas: {vetores.shape}"
                )

            colecao.add(
                ids=[doc["id"] for doc in faltantes],
                documents=[
                    doc["page_content"] for doc in faltantes
                ],
                metadatas=[
                    preparar_metadados(doc)
                    for doc in faltantes
                ],
                embeddings=vetores.tolist(),
            )

        processados = min(inicio + TAMANHO_LOTE, total)

        if processados % 1024 == 0 or processados == total:
            print(
                f"Verificados: {processados}/{total} | "
                f"Armazenados: {colecao.count()}",
                flush=True,
            )

    if colecao.count() != TOTAL_ESPERADO:
        raise RuntimeError(
            f"Indice incompleto: {colecao.count()} documentos"
        )

    # Verificacao final dos identificadores, mesmo em retomadas.
    for inicio in range(0, total, TAMANHO_LOTE):
        ids = [
            doc["id"]
            for doc in documentos[inicio:inicio + TAMANHO_LOTE]
        ]

        encontrados = set(
            colecao.get(ids=ids, include=[])["ids"]
        )

        if encontrados != set(ids):
            raise RuntimeError(
                f"Falha de integridade no lote iniciado em {inicio}"
            )

    print("\nINDEXACAO COMPLETA VALIDADA")
    print(f"Total no ChromaDB: {colecao.count()}")


# 6. Consultas de verificacao

def testar_consultas(colecao, modelo):
    for pergunta in PERGUNTAS:
        vetor = modelo.encode(
            ["query: " + pergunta],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]

        resultados = colecao.query(
            query_embeddings=[vetor.tolist()],
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
            print(
                f"\n{posicao}. Similaridade: {1 - distancia:.4f}"
            )
            print(f"   document_id: {identificador}")
            print(f"   review_id: {metadados.get('review_id')}")
            print(f"   nota: {metadados.get('review_score')}")
            print(f"   texto: {texto[:400]}")


# 7. Execucao principal

def main():
    print("ETAPA 3.3 - INDEXACAO COMPLETA DA OLIST")

    documentos, assinatura = carregar_documentos()

    print(f"Documentos carregados: {len(documentos)}")
    print(f"SHA-256 da base: {assinatura}")

    colecao = obter_colecao(assinatura)

    print(f"Modelo: {MODELO}")
    modelo = SentenceTransformer(MODELO)

    indexar_documentos(colecao, documentos, modelo)

    testar_consultas(colecao, modelo)

    print("\nEtapa 3.3 executada com sucesso.")


if __name__ == "__main__":
    main()
