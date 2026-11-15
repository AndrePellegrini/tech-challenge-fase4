
"""Testes das instrucoes de abstencao do gerador."""

import unittest

from src.generation.resposta import construir_prompt


class TestPromptPremissas(unittest.TestCase):

    def test_prompt_orienta_verificar_premissas(self):
        mensagens = construir_prompt(
            "Qual foi a causa do cancelamento do pedido?",
            [],
        )

        sistema = mensagens[0]["content"].lower()

        self.assertIn(
            "premissas nao comprovadas",
            sistema,
        )

        self.assertIn(
            "evidencias_insuficientes",
            sistema,
        )

    def test_prompt_exige_suporte_para_causas(self):
        mensagens = construir_prompt(
            "Por que o produto foi devolvido?",
            [],
        )

        sistema = mensagens[0]["content"].lower()

        self.assertIn(
            "causa ou motivo",
            sistema,
        )

        self.assertIn(
            "ocorrencia",
            sistema,
        )

    def test_prompt_exige_justificativa_textual_na_recusa(self):
        mensagens = construir_prompt(
            "Qual foi a causa do cancelamento?",
            [],
        )

        sistema = mensagens[0]["content"].lower()

        self.assertIn(
            "o campo resposta nunca pode ser vazio",
            sistema,
        )

        self.assertIn(
            "frase completa",
            sistema,
        )

        self.assertIn(
            "evidencias_insuficientes",
            sistema,
        )

    def test_prompt_exige_fontes_em_lista_plana(self):
        mensagens = construir_prompt(
            "O que as avaliacoes permitem concluir?",
            [],
        )

        sistema = mensagens[0]["content"].lower()

        self.assertIn(
            "lista plana de objetos json",
            sistema,
        )

        self.assertIn(
            "nunca uma lista de listas",
            sistema,
        )

        self.assertIn(
            '"fontes": []',
            sistema,
        )

if __name__ == "__main__":
    unittest.main()
