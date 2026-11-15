
"""Testes de orquestracao do fluxo pergunta -> busca -> contexto -> resposta."""

import unittest

from src.app import processar_pergunta
from src.generation.resposta import RespostaRAG, Status
from src.retrieval.tipos import Candidato


class RecuperadorFalso:
    def __init__(self, candidatos=None, erro=None):
        self.candidatos = candidatos or []
        self.erro = erro

    def buscar(self, pergunta, k):
        if self.erro:
            raise self.erro
        return self.candidatos


class GeradorFalso:
    def __init__(self, resposta=None):
        self.resposta = resposta or RespostaRAG(
            status=Status.RESPONDIDA, resposta="ok", afirmacoes=[], fontes=[]
        )

    def gerar(self, mensagens):
        return self.resposta.model_dump_json()


class TestProcessarPergunta(unittest.TestCase):
    def test_pergunta_vazia_e_erro_operacional(self):
        resultado = processar_pergunta("   ", RecuperadorFalso(), GeradorFalso())
        self.assertEqual(resultado["status"], "erro_operacional")
        self.assertEqual(resultado["retrieved_ids"], [])
        self.assertEqual(resultado["context_ids"], [])

    def test_falha_na_recuperacao_e_erro_operacional_nunca_insuficiencia(self):
        recuperador = RecuperadorFalso(erro=TimeoutError("indice indisponivel"))
        resultado = processar_pergunta("Houve atraso?", recuperador, GeradorFalso())

        self.assertEqual(resultado["status"], "erro_operacional")
        self.assertNotEqual(resultado["status"], "evidencias_insuficientes")

    def test_sem_candidatos_vira_evidencias_insuficientes(self):
        resultado = processar_pergunta("Pergunta sem evidencias", RecuperadorFalso(candidatos=[]), GeradorFalso())
        self.assertEqual(resultado["status"], "evidencias_insuficientes")

    def test_fluxo_feliz_preenche_ids(self):
        candidatos = [
            Candidato(id="doc-1", texto="Atraso de 7 dias", metadata={"hash_texto": "h1"}, score=0.9),
        ]
        recuperador = RecuperadorFalso(candidatos=candidatos)
        resultado = processar_pergunta("Houve atraso?", recuperador, GeradorFalso())

        self.assertEqual(resultado["retrieved_ids"], ["doc-1"])
        self.assertEqual(resultado["context_ids"], ["doc-1"])


    def test_pergunta_geografica_fora_do_escopo(self):
        """Pergunta externa nao deve acionar recuperacao vetorial."""

        recuperador = RecuperadorFalso(
            erro=AssertionError(
                "A recuperacao nao deveria ser executada"
            )
        )

        resultado = processar_pergunta(
            "Qual e a capital da Franca?",
            recuperador,
            GeradorFalso(),
        )

        self.assertEqual(
            resultado["status"],
            "fora_do_escopo",
        )

        self.assertEqual(
            resultado["retrieved_ids"],
            [],
        )

        self.assertEqual(
            resultado["context_ids"],
            [],
        )

    def test_receita_culinaria_fora_do_escopo(self):
        """Pedido de instrucao culinaria nao pertence ao RAG Olist."""

        recuperador = RecuperadorFalso(
            erro=AssertionError(
                "A recuperacao nao deveria ser executada"
            )
        )

        resultado = processar_pergunta(
            "Como preparar um bolo de cenoura?",
            recuperador,
            GeradorFalso(),
        )

        self.assertEqual(
            resultado["status"],
            "fora_do_escopo",
        )

    def test_avaliacoes_de_livros_de_receitas_nao_sao_bloqueadas(self):
        """O tema receita pode ser legitimo dentro das avaliacoes."""

        recuperador = RecuperadorFalso(
            candidatos=[]
        )

        resultado = processar_pergunta(
            "O que os clientes acharam dos livros de receitas?",
            recuperador,
            GeradorFalso(),
        )

        # Nao ha candidatos no teste, logo faltam evidencias.
        # A pergunta, entretanto, pertence ao dominio Olist.
        self.assertEqual(
            resultado["status"],
            "evidencias_insuficientes",
        )



if __name__ == "__main__":
    unittest.main()
