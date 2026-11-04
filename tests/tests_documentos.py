
"""Testes para garantir que a preparacao documental nao perca informacoes."""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.preprocessing.documentos import construir_documentos, salvar_resultados


class TestDocumentos(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([
            {"document_id": "doc-1", "review_id": "review-1", "order_id": "pedido-1",
             "review_score": 1, "review_comment_title": None,
             "review_comment_message": "Não   recebi o produto!", "review_creation_date": "2018-01-01"},
            {"document_id": "doc-2", "review_id": "review-1", "order_id": "pedido-2",
             "review_score": 5, "review_comment_title": "Ótimo!",
             "review_comment_message": None, "review_creation_date": "2018-01-02"},
            {"document_id": "doc-3", "review_id": "review-3", "order_id": "pedido-3",
             "review_score": 5, "review_comment_title": "Ótimo!",
             "review_comment_message": None, "review_creation_date": "2018-01-03"},
        ])

    def test_preserva_negacao_e_acentos(self):
        docs, _ = construir_documentos(self.df)
        self.assertEqual(docs[0]["page_content"], "Comentario: Não recebi o produto!")

    def test_preserva_titulos_e_ids_repetidos(self):
        docs, perfil = construir_documentos(self.df)
        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[1]["metadata"]["tipo_texto"], "somente_titulo")
        self.assertEqual(perfil["review_ids_repetidos_no_recorte"], 1)
        self.assertEqual(perfil["textos_repetidos"], 1)

    def test_rejeita_document_id_repetido(self):
        df = self.df.copy()
        df.loc[1, "document_id"] = "doc-1"
        with self.assertRaisesRegex(ValueError, "unico"):
            construir_documentos(df)

    def test_salva_jsonl_e_relatorios(self):
        docs, perfil = construir_documentos(self.df)
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            salvar_resultados(docs, perfil, raiz / "doc.jsonl", raiz / "rel.md", raiz / "rel.json")
            linhas = (raiz / "doc.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(linhas), 3)
            self.assertEqual(json.loads(linhas[0])["id"], "doc-1")
            self.assertTrue((raiz / "rel.md").exists())


if __name__ == "__main__":
    unittest.main()
