
"""Testes de compatibilidade entre os casos P1 e o executor P2."""

import json
import tempfile
import unittest
from pathlib import Path

from src.evaluation.executar_casos import carregar_casos, executar


class TestCarregarCasos(unittest.TestCase):

    def _carregar_exemplo(self, caso):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "casos.jsonl"
            caminho.write_text(
                json.dumps(caso, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return carregar_casos(caminho)

    def test_aceita_formato_p1_e_preserva_modo(self):
        caso = {
            "id": "R01",
            "modo": "recuperacao_e_geracao",
            "pergunta": "Quais relatos descrevem atraso?",
        }

        resultado = self._carregar_exemplo(caso)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["case_id"], "R01")
        self.assertEqual(resultado[0]["id"], "R01")
        self.assertEqual(
            resultado[0]["modo"],
            "recuperacao_e_geracao",
        )

    def test_preserva_compatibilidade_com_formato_p2(self):
        caso = {
            "case_id": "C01",
            "pergunta": "Houve atraso na entrega?",
        }

        resultado = self._carregar_exemplo(caso)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["case_id"], "C01")


class RecuperadorProibido:
    """Falha caso uma fixture controlada acione o ChromaDB."""

    def buscar(self, pergunta, k):
        raise AssertionError(
            "Contexto controlado nao pode executar recuperacao."
        )


class GeradorRegistrador:
    """Simula o Qwen e registra o contexto recebido."""

    def __init__(self):
        self.mensagens = None

    def gerar(self, mensagens):
        self.mensagens = mensagens

        return json.dumps({
            "status": "evidencias_insuficientes",
            "resposta": "Nao ha suporte suficiente para responder.",
            "afirmacoes": [],
            "fontes": [],
        })


class TestExecutarModos(unittest.TestCase):

    def test_a02_usa_exatamente_a_fixture_sem_recuperacao(self):
        """A02 deve receber a fixture sintetica, sem ChromaDB."""

        caminho = (
            Path(__file__).resolve().parents[1]
            / "evaluation"
            / "fixtures"
            / "contextos.jsonl"
        )

        fixtures = [
            json.loads(linha)
            for linha in caminho.read_text(
                encoding="utf-8"
            ).splitlines()
            if linha.strip()
            and json.loads(linha)["case_id"] == "A02"
        ]

        self.assertEqual(len(fixtures), 1)

        gerador = GeradorRegistrador()

        predicoes = executar(
            casos=[{
                "case_id": "A02",
                "modo": "contexto_controlado",
                "pergunta": (
                    "O que o relato informa sobre o dano "
                    "e o funcionamento do produto?"
                ),
            }],
            recuperador=RecuperadorProibido(),
            gerador=gerador,
            fixtures=fixtures,
        )

        self.assertEqual(
            predicoes[0]["retrieved_ids"],
            [],
        )
        self.assertEqual(
            predicoes[0]["context_ids"],
            ["fixture_sintetica_A02"],
        )

        self.assertIsNotNone(gerador.mensagens)


        contexto_enviado = gerador.mensagens[1]["content"]

        marcador_bloco = (
            "EVIDENCIAS_JSON_DADOS_NAO_CONFIAVEIS:\n"
        )

        self.assertIn(
            marcador_bloco,
            contexto_enviado,
        )

        # Extrai e interpreta o JSON enviado ao gerador.
        bloco_json = contexto_enviado.split(
            marcador_bloco, 1
        )[1]

        documentos = json.loads(bloco_json)

        # A fixture deve permanecer como unico documento.
        self.assertEqual(len(documentos), 1)

        self.assertEqual(
            documentos[0]["marcador"],
            "F1",
        )

        self.assertEqual(
            documentos[0]["document_id"],
            "fixture_sintetica_A02",
        )

        # Confirma a preservacao integral do texto,
        # inclusive quebras de linha e instrucao adversarial.
        self.assertEqual(
            documentos[0]["trecho"],
            fixtures[0]["page_content"],
        )


    def test_i01_contexto_vazio_nao_chama_gerador(self):
        """Sem evidencias, I01 deve recusar sem buscar ou gerar."""

        gerador = GeradorRegistrador()

        predicoes = executar(
            casos=[{
                "case_id": "I01",
                "modo": "contexto_controlado",
                "tema": "contexto_vazio",
                "pergunta": (
                    "Quais defeitos foram relatados "
                    "nestas avaliacoes?"
                ),
            }],
            recuperador=RecuperadorProibido(),
            gerador=gerador,
            fixtures=[],
        )

        self.assertEqual(
            predicoes[0]["status"],
            "evidencias_insuficientes",
        )
        self.assertEqual(
            predicoes[0]["retrieved_ids"],
            [],
        )
        self.assertEqual(
            predicoes[0]["context_ids"],
            [],
        )
        self.assertIsNone(gerador.mensagens)


        resposta = predicoes[0]["resposta"].lower()

        self.assertIn(
            "contexto fornecido",
            resposta,
        )

        self.assertNotIn(
            "recuperad",
            resposta,
        )


    def test_modo_recuperacao_continua_usando_recuperador(self):
        """O fluxo P2 deve permanecer funcional."""

        class RecuperadorVazio:
            def __init__(self):
                self.chamado = False

            def buscar(self, pergunta, k):
                self.chamado = True
                return []

        recuperador = RecuperadorVazio()

        predicoes = executar(
            casos=[{
                "case_id": "R01",
                "modo": "recuperacao_e_geracao",
                "pergunta": "Quais relatos descrevem atraso?",
            }],
            recuperador=recuperador,
            gerador=GeradorRegistrador(),
            fixtures=[],
        )

        self.assertTrue(recuperador.chamado)
        self.assertEqual(
            predicoes[0]["status"],
            "evidencias_insuficientes",
        )


    def test_fixture_obrigatoria_ausente_e_erro_operacional(self):
        """I02 sem fixture nao pode parecer uma recusa correta."""

        gerador = GeradorRegistrador()

        predicoes = executar(
            casos=[{
                "case_id": "I02",
                "modo": "contexto_controlado",
                "tema": "premissa_falsa",
                "pergunta": (
                    "O relato comprova que o produto "
                    "apresentou defeito?"
                ),
            }],
            recuperador=RecuperadorProibido(),
            gerador=gerador,
            fixtures=[],
        )

        self.assertEqual(len(predicoes), 1)
        self.assertEqual(
            predicoes[0]["status"],
            "erro_operacional",
        )
        self.assertEqual(predicoes[0]["retrieved_ids"], [])
        self.assertEqual(predicoes[0]["context_ids"], [])
        self.assertIsNone(gerador.mensagens)

if __name__ == "__main__":
    unittest.main()
