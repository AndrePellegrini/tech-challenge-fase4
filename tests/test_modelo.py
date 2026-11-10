
"""Testes de diagnostico da geracao sem carregar o Qwen real."""

import unittest
import torch

from src.generation.modelo import GeradorQwenLocal


class TokenizadorFalso:
    eos_token_id = 99

    def apply_chat_template(
        self, mensagens, tokenize=False, add_generation_prompt=True
    ):
        return "prompt simulado"

    def __call__(self, texto, return_tensors="pt"):
        return {
            "input_ids": torch.tensor([[10, 11, 12]])
        }

    def decode(self, tokens, skip_special_tokens=True):
        return "resposta simulada"


class ModeloFalso:
    def __init__(self, tokens_gerados):
        self.tokens_gerados = tokens_gerados

    def generate(self, **kwargs):
        return torch.tensor([
            [10, 11, 12] + self.tokens_gerados
        ])


class TestDiagnosticoGeracao(unittest.TestCase):

    def test_detecta_limite_de_tokens(self):
        gerador = GeradorQwenLocal(
            modelo=ModeloFalso([41, 42, 43]),
            tokenizador=TokenizadorFalso(),
        )

        texto = gerador.gerar(
            [{"role": "user", "content": "Pergunta"}],
            max_tokens_saida=3,
        )

        self.assertEqual(texto, "resposta simulada")
        self.assertEqual(
            gerador.ultimo_diagnostico["motivo_parada"],
            "limite_tokens",
        )
        self.assertEqual(
            gerador.ultimo_diagnostico["tokens_gerados"],
            3,
        )

    def test_detecta_encerramento_normal(self):
        gerador = GeradorQwenLocal(
            modelo=ModeloFalso([41, 42, 99]),
            tokenizador=TokenizadorFalso(),
        )

        gerador.gerar(
            [{"role": "user", "content": "Pergunta"}],
            max_tokens_saida=3,
        )

        self.assertEqual(
            gerador.ultimo_diagnostico["motivo_parada"],
            "eos",
        )


if __name__ == "__main__":
    unittest.main()
