
"""Testes da estrutura compacta de geracao P3.10."""

import json
import unittest

from src.generation.resposta import (
    PROMPT_SISTEMA,
    gerar_resposta,
)
from src.retrieval.tipos import Evidencia


class GeradorFalso:
    """Simula um JSON compacto, sem carregar o Qwen."""

    def gerar(self, mensagens):
        return json.dumps(
            {
                "status": "respondida",
                "resposta": (
                    "Ha relatos de microfone com defeito [F1]."
                ),
                "afirmacoes": [
                    {
                        "texto": "O microfone apresentou defeito.",
                        "fontes": ["F1"],
                    }
                ],
                "fontes": [],
            },
            ensure_ascii=False,
        )


class TestPromptCompactoP310(unittest.TestCase):

    def test_prompt_exige_json_compacto(self):
        prompt = PROMPT_SISTEMA.lower()

        self.assertIn(
            "no maximo 3 afirmacoes",
            prompt,
        )

        self.assertIn(
            "lista de objetos",
            prompt,
        )

        self.assertIn(
            '"fontes": []',
            prompt,
        )

    def test_reconstroi_somente_fontes_citadas(self):
        evidencias = [
            Evidencia(
                marcador="F1",
                document_id="doc_microfone",
                review_id="review_1",
                review_score=1,
                trecho="O microfone apresentou defeito.",
                similaridade=0.9,
            ),
            Evidencia(
                marcador="F2",
                document_id="doc_entrega",
                review_id="review_2",
                review_score=1,
                trecho="O pedido nao foi entregue.",
                similaridade=0.8,
            ),
        ]

        resposta = gerar_resposta(
            "Que defeitos foram relatados?",
            evidencias,
            GeradorFalso(),
        )

        self.assertEqual(
            resposta.status.value,
            "respondida",
        )

        self.assertEqual(len(resposta.afirmacoes), 1)
        self.assertEqual(len(resposta.fontes), 1)

        self.assertEqual(
            resposta.fontes[0].marcador,
            "F1",
        )

        self.assertEqual(
            resposta.fontes[0].document_id,
            "doc_microfone",
        )


if __name__ == "__main__":
    unittest.main()
