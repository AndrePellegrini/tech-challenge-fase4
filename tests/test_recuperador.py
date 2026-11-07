
"""Testes do recuperador, com modelo e colecao falsos (sem carregar o indice real)."""

import unittest

import numpy as np

from src.retrieval.recuperador import Recuperador


class ModeloFalso:
    def encode(self, textos, convert_to_numpy=True, normalize_embeddings=True):
        # O SentenceTransformer real devolve numpy.ndarray quando
        # convert_to_numpy=True; replicamos isso aqui para exercitar o
        # mesmo .tolist() que o codigo de producao chama.
        self.ultimo_texto = textos[0]
        return np.array([[0.1, 0.2, 0.3]])


class ColecaoFalsa:
    def query(self, query_embeddings, n_results, include):
        self.ultimo_n_results = n_results
        return {
            "ids": [["doc-1", "doc-2"]],
            "documents": [["Atraso de sete dias", "Produto quebrado"]],
            "metadatas": [[{"review_id": "r1"}, {"review_id": "r2"}]],
            "distances": [[0.1, 0.3]],
        }


class TestRecuperador(unittest.TestCase):
    def setUp(self):
        self.modelo = ModeloFalso()
        self.colecao = ColecaoFalsa()
        self.recuperador = Recuperador(modelo=self.modelo, colecao=self.colecao)

    def test_rejeita_pergunta_vazia(self):
        with self.assertRaisesRegex(ValueError, "vazia"):
            self.recuperador.buscar("   ", k=5)

    def test_adiciona_prefixo_query(self):
        self.recuperador.buscar("Houve atraso?", k=5)
        self.assertEqual(self.modelo.ultimo_texto, "query: Houve atraso?")

    def test_converte_distancia_em_similaridade(self):
        candidatos = self.recuperador.buscar("Houve atraso?", k=5)

        self.assertEqual(len(candidatos), 2)
        self.assertEqual(candidatos[0].id, "doc-1")
        self.assertAlmostEqual(candidatos[0].score, 0.9)
        self.assertEqual(candidatos[1].metadata["review_id"], "r2")


if __name__ == "__main__":
    unittest.main()
