
import unittest

from src.escopo import claramente_fora_do_escopo


class TestEscopoP38(unittest.TestCase):

    def test_o01_tratamento_medico(self):
        pergunta = (
            "Qual é o tratamento indicado para "
            "uma infecção de garganta?"
        )

        self.assertTrue(
            claramente_fora_do_escopo(pergunta)
        )

    def test_o02_receita_culinaria(self):
        pergunta = (
            "Me ensine uma receita de bolo de cenoura."
        )

        self.assertTrue(
            claramente_fora_do_escopo(pergunta)
        )

    def test_preserva_pergunta_sobre_avaliacoes(self):
        pergunta = (
            "Quais avaliações elogiam livros "
            "de receitas de bolo?"
        )

        self.assertFalse(
            claramente_fora_do_escopo(pergunta)
        )

    def test_preserva_relato_de_atendimento(self):
        pergunta = (
            "O que os clientes relatam sobre "
            "o tratamento recebido na loja?"
        )

        self.assertFalse(
            claramente_fora_do_escopo(pergunta)
        )

    def test_r01_continua_no_escopo(self):
        pergunta = (
            "Quais relatos descrevem atraso na entrega?"
        )

        self.assertFalse(
            claramente_fora_do_escopo(pergunta)
        )
