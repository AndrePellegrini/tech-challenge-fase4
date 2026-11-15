
"""Testes da selecao adaptativa do prompt P3.11."""

import unittest

from src.generation.prompt_v3 import PROMPT_SISTEMA_V3
from src.generation.resposta import (
    PROMPT_SISTEMA,
    construir_prompt,
)
from src.retrieval.tipos import Evidencia


def criar_evidencias(quantidade):
    """Cria evidencias sinteticas para testar o prompt."""
    return [
        Evidencia(
            marcador=f"F{i}",
            document_id=f"doc_{i}",
            review_id=f"review_{i}",
            review_score=1,
            trecho=f"Produto com defeito relatado {i}.",
            similaridade=0.9,
        )
        for i in range(1, quantidade + 1)
    ]


class TestPromptAdaptativoP311(unittest.TestCase):

    def test_contexto_pequeno_usa_prompt_original(self):
        for quantidade in [0, 1, 2, 3]:
            with self.subTest(documentos=quantidade):
                mensagens = construir_prompt(
                    "Quais problemas foram relatados?",
                    criar_evidencias(quantidade),
                )

                self.assertEqual(
                    mensagens[0]["content"],
                    PROMPT_SISTEMA_V3,
                )

    def test_contexto_maior_usa_prompt_compacto(self):
        for quantidade in [4, 8]:
            with self.subTest(documentos=quantidade):
                mensagens = construir_prompt(
                    "Quais problemas foram relatados?",
                    criar_evidencias(quantidade),
                )

                self.assertEqual(
                    mensagens[0]["content"],
                    PROMPT_SISTEMA,
                )


if __name__ == "__main__":
    unittest.main()
