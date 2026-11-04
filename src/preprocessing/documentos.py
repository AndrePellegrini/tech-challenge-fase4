
"""Etapa 2: transforma avaliacoes da Olist em documentos para o futuro RAG."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

COLUNAS = [
    "document_id", "review_id", "order_id", "review_score",
    "review_comment_title", "review_comment_message", "review_creation_date",
]


def normalizar_texto(valor):
    """Remove apenas espacos excedentes; mantem palavras, acentos e negacoes."""
    if pd.isna(valor):
        return ""
    return re.sub(r"\s+", " ", str(valor)).strip()


def valor_opcional(valor):
    texto = normalizar_texto(valor)
    return texto if texto else None


def converter_nota(valor):
    """Devolve uma nota inteira de 1 a 5, ou None se for invalida."""
    try:
        nota = float(valor)
    except (ValueError, TypeError):
        return None
    if pd.isna(nota) or not nota.is_integer() or not 1 <= nota <= 5:
        return None
    return int(nota)


def converter_data(valor):
    """Converte a data para AAAA-MM-DD, sem inventar valores ausentes."""
    texto = normalizar_texto(valor)
    if not texto:
        return None
    data = pd.to_datetime(texto, errors="coerce")
    return None if pd.isna(data) else data.strftime("%Y-%m-%d")


def construir_documentos(df):
    """Gera um documento por linha com texto e estatisticas da conversao."""
    ausentes = [coluna for coluna in COLUNAS if coluna not in df.columns]
    if ausentes:
        raise ValueError(f"Colunas ausentes: {ausentes}")
    if df["document_id"].isna().any() or df["document_id"].astype(str).duplicated().any():
        raise ValueError("document_id deve ser preenchido e unico")

    documentos = []
    tipos = Counter()
    notas = Counter()
    hashes = Counter()
    tamanhos = []
    notas_invalidas = 0
    datas_invalidas = 0

    for registro in df.to_dict(orient="records"):
        titulo = normalizar_texto(registro["review_comment_title"])
        comentario = normalizar_texto(registro["review_comment_message"])
        if not titulo and not comentario:
            raise ValueError("O CSV preparado possui uma linha sem texto")

        partes = []
        if titulo:
            partes.append(f"Titulo: {titulo}")
        if comentario:
            partes.append(f"Comentario: {comentario}")
        conteudo = "\n".join(partes)
        tipo = "ambos" if titulo and comentario else ("somente_titulo" if titulo else "somente_comentario")
        identificador = str(registro["document_id"])
        nota = converter_nota(registro["review_score"])
        data = converter_data(registro["review_creation_date"])
        hash_texto = hashlib.sha256(conteudo.casefold().encode("utf-8")).hexdigest()
        numero_palavras = len(conteudo.split())

        notas_invalidas += nota is None
        datas_invalidas += data is None and bool(normalizar_texto(registro["review_creation_date"]))
        tipos[tipo] += 1
        if nota is not None:
            notas[nota] += 1
        hashes[hash_texto] += 1
        tamanhos.append(numero_palavras)

        documentos.append({
            "id": identificador,
            "page_content": conteudo,
            "metadata": {
                "document_id": identificador,
                "review_id": valor_opcional(registro["review_id"]),
                "order_id": valor_opcional(registro["order_id"]),
                "review_score": nota,
                "review_creation_date": data,
                "tipo_texto": tipo,
                "fonte": "olist_order_reviews_dataset.csv",
                "n_palavras": numero_palavras,
                "hash_texto": hash_texto,
            },
        })

    if not documentos:
        raise ValueError("Nenhum documento valido foi gerado")

    relatorio = {
        "linhas_entrada": len(df),
        "documentos_saida": len(documentos),
        "somente_titulo": tipos["somente_titulo"],
        "somente_comentario": tipos["somente_comentario"],
        "titulo_e_comentario": tipos["ambos"],
        "review_ids_repetidos_no_recorte": int(df["review_id"].duplicated().sum()),
        "textos_repetidos": sum(qtd - 1 for qtd in hashes.values() if qtd > 1),
        "notas_invalidas": notas_invalidas,
        "datas_invalidas": datas_invalidas,
        "palavras_p50": int(pd.Series(tamanhos).median()),
        "palavras_p95": int(pd.Series(tamanhos).quantile(0.95)),
        "palavras_max": max(tamanhos),
        "documentos_ate_3_palavras": sum(t <= 3 for t in tamanhos),
        "notas_base_textual": {str(n): notas[n] for n in range(1, 6)},
    }
    return documentos, relatorio


def salvar_resultados(documentos, relatorio, caminho_jsonl, caminho_md, caminho_json):
    """Salva documentos locais e relatorios agregados, sem expor comentarios."""
    for caminho in (caminho_jsonl, caminho_md, caminho_json):
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)

    with Path(caminho_jsonl).open("w", encoding="utf-8") as arquivo:
        for documento in documentos:
            arquivo.write(json.dumps(documento, ensure_ascii=False, allow_nan=False) + "\n")

    Path(caminho_json).write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    linhas = [
        "# Perfil da base documental - Etapa 2", "",
        "Fonte: `data/processed/reviews_preparadas.csv`.", "",
        "| Indicador | Valor |", "|---|---:|",
    ]
    for chave, valor in relatorio.items():
        if isinstance(valor, int):
            linhas.append(f"| {chave} | {valor:,} |".replace(",", "."))
    linhas += ["", "## Notas na base textual", "", "| Nota | Quantidade |", "|---|---:|"]
    for nota, quantidade in relatorio["notas_base_textual"].items():
        linhas.append(f"| {nota} | {quantidade} |")
    linhas += [
        "", "## Limites da interpretacao", "",
        "- Uma linha textual origina um documento; IDs naturais podem se repetir.",
        "- Textos curtos e repetidos foram mantidos.",
        "- Nao foram criados embeddings nesta etapa.",
        "- Frequencia de temas nao pode ser inferida so da busca semantica.",
        "- O arquivo JSONL contem comentarios e deve permanecer fora do GitHub.",
    ]
    Path(caminho_md).write_text("\n".join(linhas) + "\n", encoding="utf-8")
