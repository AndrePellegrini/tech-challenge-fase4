
"""Executa a Etapa 2 a partir da raiz do projeto."""

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.preprocessing.documentos import construir_documentos, salvar_resultados

ENTRADA = RAIZ / "data" / "processed" / "reviews_preparadas.csv"
SAIDA_DOCUMENTOS = RAIZ / "data" / "processed" / "reviews_documentos.jsonl"
SAIDA_MD = RAIZ / "reports" / "perfil_documentos.md"
SAIDA_JSON = RAIZ / "reports" / "perfil_documentos.json"


def main():
    if not ENTRADA.is_file():
        raise SystemExit("CSV ausente. Execute a Etapa 1 para gerar reviews_preparadas.csv")

    dados = pd.read_csv(
        ENTRADA, dtype={"document_id": "string", "review_id": "string", "order_id": "string"},
        low_memory=False,
    )
    documentos, relatorio = construir_documentos(dados)
    salvar_resultados(documentos, relatorio, SAIDA_DOCUMENTOS, SAIDA_MD, SAIDA_JSON)

    print("ETAPA 2 CONCLUIDA")
    print(f"Linhas de entrada: {relatorio['linhas_entrada']}")
    print(f"Documentos gerados: {relatorio['documentos_saida']}")
    print(f"Relatorio: {SAIDA_MD}")
    print(f"Documentos: {SAIDA_DOCUMENTOS}")


if __name__ == "__main__":
    main()
