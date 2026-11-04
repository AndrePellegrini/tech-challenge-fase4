import unittest
import pandas as pd
from scripts.explorar_avaliacoes import preparar_avaliacoes, criar_perfil


class TestExploracao(unittest.TestCase):
    def test_textos_e_ids(self):
        df = pd.DataFrame([
            {"review_id": "a", "order_id": "p1", "review_score": 1,
             "review_comment_title": None, "review_comment_message": "  Nao   recebi o produto! ",
             "review_creation_date": "2018-01-01"},
            {"review_id": "a", "order_id": "p2", "review_score": 5,
             "review_comment_title": " Excelente ", "review_comment_message": None,
             "review_creation_date": "2018-01-02"},
            {"review_id": "c", "order_id": "p3", "review_score": 4,
             "review_comment_title": None, "review_comment_message": None,
             "review_creation_date": "2018-01-03"},
        ])
        good = preparar_avaliacoes(df)
        self.assertEqual(len(good), 2)
        self.assertEqual(good.iloc[0]["texto"], "Comentario: Nao recebi o produto!")
        self.assertIn("Excelente", good.iloc[1]["texto"])
        self.assertEqual(good["document_id"].nunique(), 2)
        perfil = criar_perfil(df, good)
        self.assertEqual(perfil["review_id_repetidos"], 1)
        self.assertEqual(perfil["sem_texto"], 1)
        self.assertEqual(perfil["somente_titulo"], 1)


if __name__ == "__main__":
    unittest.main()
