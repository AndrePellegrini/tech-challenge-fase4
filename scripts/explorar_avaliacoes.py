"""Etapa 1: perfil das avaliacoes da Olist, preservando textos e IDs.

Execute a partir da raiz do repositorio:
    .\\.venv\\Scripts\\python.exe scripts/explorar_avaliacoes.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "olist_order_reviews_dataset.csv"
OUTPUT_CSV = ROOT / "data" / "processed" / "reviews_preparadas.csv"
OUTPUT_JSON = ROOT / "reports" / "perfil_olist.json"
OUTPUT_MD = ROOT / "reports" / "perfil_olist.md"

EXPECTED = [
    "review_id", "order_id", "review_score", "review_comment_title",
    "review_comment_message", "review_creation_date"
]


def limpar_espacos(valor: object) -> str:
    """Normaliza so espacos; NAO remove acentos, pontuacao, nem negacoes."""
    if pd.isna(valor):
        return ""
    return re.sub(r"\s+", " ", str(valor)).strip()


def preparar_avaliacoes(df: pd.DataFrame) -> pd.DataFrame:
    """Gera um documento por linha que tenha titulo ou comentario valido."""
    faltantes = [c for c in EXPECTED if c not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas ausentes no CSV: {faltantes}")

    work = df.copy()
    # ID tecnico por posicao, independente da repeticao de review_id
    work["document_id"] = [f"olist_review_row_{i:06d}" for i in range(1, len(work) + 1)]
    work["titulo_limpo"] = work["review_comment_title"].map(limpar_espacos)
    work["comentario_limpo"] = work["review_comment_message"].map(limpar_espacos)
    work["texto"] = work.apply(
        lambda row: "\n".join(
            (["Titulo: " + row["titulo_limpo"]] if row["titulo_limpo"] else [])
            + (["Comentario: " + row["comentario_limpo"]] if row["comentario_limpo"] else [])
        ),
        axis=1,
    )
    return work[work["texto"].str.strip().ne("")].copy()


def criar_perfil(df: pd.DataFrame, validos: pd.DataFrame) -> dict:
    titulo = df["review_comment_title"].map(limpar_espacos).ne("")
    comentario = df["review_comment_message"].map(limpar_espacos).ne("")
    score_counts = df["review_score"].value_counts(dropna=False).sort_index()
    return {
        "total_avaliacoes": int(len(df)),
        "com_comentario": int(comentario.sum()),
        "com_titulo": int(titulo.sum()),
        "titulo_e_comentario": int((titulo & comentario).sum()),
        "somente_titulo": int((titulo & ~comentario).sum()),
        "somente_comentario": int((~titulo & comentario).sum()),
        "sem_texto": int((~titulo & ~comentario).sum()),
        "documentos_aproveitaveis": int(len(validos)),
        "review_id_repetidos": int(df["review_id"].duplicated().sum()),
        "order_id_repetidos": int(df["order_id"].duplicated().sum()),
        "notas": {str(k): int(v) for k, v in score_counts.items()},
        "mediana_caracteres_texto": float(validos["texto"].str.len().median()) if len(validos) else 0,
        "fonte": str(INPUT.name),
    }


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "Arquivo nao encontrado: " + str(INPUT)
            + "\nBaixe a Olist no Kaggle e salve 'olist_order_reviews_dataset.csv' em data/raw/."
        )
    df = pd.read_csv(INPUT, low_memory=False)
    validos = preparar_avaliacoes(df)
    perfil = criar_perfil(df, validos)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    validos.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    OUTPUT_JSON.write_text(json.dumps(perfil, indent=2, ensure_ascii=False), encoding="utf-8")
    linhas = [
        "# Perfil inicial da base Olist", "",
        "Fonte: `olist_order_reviews_dataset.csv` (dataset oficial Olist).", "",
        "| Indicador | Total |", "|---|---:|",
    ]
    for chave in ["total_avaliacoes", "com_comentario", "com_titulo", "somente_titulo",
                  "somente_comentario", "titulo_e_comentario", "sem_texto",
                  "documentos_aproveitaveis", "review_id_repetidos", "order_id_repetidos"]:
        linhas.append(f"| {chave.replace('_', ' ')} | {perfil[chave]:,} |".replace(",", "."))
    linhas += ["", "## Distribuicao das notas", "", "| Nota | Quantidade |", "|---|---:|"]
    linhas += [f"| {nota} | {qtd} |" for nota, qtd in perfil["notas"].items()]
    linhas += [
        "", "## Cuidados", "",
        "- IDs naturais repetidos foram CONTADOS, mas nao removidos automaticamente.",
        "- Textos sem titulo e sem comentario foram excluidos APENAS da base textual processada.",
        "- Este perfil nao prova frequencia de reclamacoes; isso exige analise posterior.",
        "- Manter os dados brutos como foram baixados e fora do repositorio publico.",
    ]
    OUTPUT_MD.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\nETAPA 1 - PERFIL DOS REVIEWS OLIST")
    for k, v in perfil.items():
        if isinstance(v, (int, float)):
            print(f"  {k}: {v}")
    print(f"\nRelatorio: {OUTPUT_MD}")
    print(f"JSON:      {OUTPUT_JSON}")
    print(f"CSV:       {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
