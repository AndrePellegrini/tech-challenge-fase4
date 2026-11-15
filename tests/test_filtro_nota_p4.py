"""Testes do filtro opcional por nota da avaliacao (D027).

Usam modelo, colecao e gerador falsos: nao carregam o indice nem o LLM.
"""

import unittest

import numpy as np

from src.app import processar_pergunta
from src.generation.resposta import RespostaRAG, Status
from src.retrieval.recuperador import Recuperador, montar_filtro_nota
from src.retrieval.tipos import Candidato


class ModeloFalso:
    def encode(self, textos, convert_to_numpy=True, normalize_embeddings=True):
        return np.array([[0.1, 0.2, 0.3]])


class ColecaoFalsa:
    def __init__(self):
        self.argumentos = None

    def query(self, **argumentos):
        self.argumentos = argumentos
        return {
            "ids": [["doc-1"]],
            "documents": [["Produto chegou quebrado"]],
            "metadatas": [[{"review_score": 1, "hash_texto": "h1"}]],
            "distances": [[0.2]],
        }


class RecuperadorRegistrador:
    """Guarda os argumentos recebidos para conferir o repasse dos filtros."""

    def __init__(self, candidatos):
        self.candidatos = candidatos
        self.chamadas = []

    def buscar(self, pergunta, k, **filtros):
        self.chamadas.append({"k": k, **filtros})
        return self.candidatos


class GeradorFalso:
    def gerar(self, mensagens):
        return RespostaRAG(
            status=Status.EVIDENCIAS_INSUFICIENTES,
            resposta="Sem suporte suficiente.",
            afirmacoes=[],
            fontes=[],
        ).model_dump_json()


class TestMontarFiltroNota(unittest.TestCase):
    def test_sem_limites_nao_gera_filtro(self):
        self.assertIsNone(montar_filtro_nota())

    def test_apenas_maximo(self):
        self.assertEqual(
            montar_filtro_nota(nota_max=2),
            {"review_score": {"$lte": 2}},
        )

    def test_apenas_minimo(self):
        self.assertEqual(
            montar_filtro_nota(nota_min=4),
            {"review_score": {"$gte": 4}},
        )

    def test_faixa_usa_and(self):
        self.assertEqual(
            montar_filtro_nota(nota_min=2, nota_max=3),
            {"$and": [
                {"review_score": {"$gte": 2}},
                {"review_score": {"$lte": 3}},
            ]},
        )

    def test_rejeita_valores_fora_da_escala(self):
        for argumentos in ({"nota_min": 0}, {"nota_max": 6}, {"nota_min": True}, {"nota_max": 2.5}):
            with self.subTest(argumentos=argumentos):
                with self.assertRaises(ValueError):
                    montar_filtro_nota(**argumentos)

    def test_rejeita_faixa_invertida(self):
        with self.assertRaisesRegex(ValueError, "maior"):
            montar_filtro_nota(nota_min=4, nota_max=2)


class TestRecuperadorComFiltro(unittest.TestCase):
    def setUp(self):
        self.colecao = ColecaoFalsa()
        self.recuperador = Recuperador(modelo=ModeloFalso(), colecao=self.colecao)

    def test_sem_filtro_nao_envia_where(self):
        self.recuperador.buscar("Houve defeito?", k=5)
        self.assertNotIn("where", self.colecao.argumentos)

    def test_filtro_e_enviado_ao_chromadb(self):
        self.recuperador.buscar("Houve defeito?", k=5, nota_max=2)
        self.assertEqual(self.colecao.argumentos["where"], {"review_score": {"$lte": 2}})
        self.assertEqual(self.colecao.argumentos["n_results"], 5)


class TestProcessarPerguntaComFiltro(unittest.TestCase):
    def setUp(self):
        self.candidatos = [
            Candidato(id="doc-1", texto="Produto chegou quebrado",
                      metadata={"review_score": 1, "hash_texto": "h1"}, score=0.81234),
        ]

    def test_sem_filtro_mantem_chamada_e_contrato_originais(self):
        recuperador = RecuperadorRegistrador(self.candidatos)
        resultado = processar_pergunta("Houve defeito?", recuperador, GeradorFalso())

        self.assertEqual(recuperador.chamadas, [{"k": 50}])
        self.assertNotIn("filtros", resultado)
        self.assertNotIn("evidencias_contexto", resultado)

    def test_filtro_e_repassado_e_registrado_na_saida(self):
        recuperador = RecuperadorRegistrador(self.candidatos)
        resultado = processar_pergunta(
            "Houve defeito?", recuperador, GeradorFalso(), nota_max=2,
        )

        self.assertEqual(recuperador.chamadas, [{"k": 50, "nota_max": 2}])
        self.assertEqual(resultado["filtros"], {"nota_max": 2})
        self.assertEqual(resultado["evidencias_contexto"], [{
            "marcador": "F1",
            "document_id": "doc-1",
            "review_score": 1,
            "similaridade": 0.8123,
        }])

    def test_filtro_invalido_vira_erro_operacional(self):
        recuperador = Recuperador(modelo=ModeloFalso(), colecao=ColecaoFalsa())
        resultado = processar_pergunta(
            "Houve defeito?", recuperador, GeradorFalso(), nota_min=9,
        )
        self.assertEqual(resultado["status"], "erro_operacional")


if __name__ == "__main__":
    unittest.main()
