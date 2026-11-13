
import copy
import unittest
import json

from src.generation.resposta import (
    RespostaRAG,
    normalizar_fontes_aninhadas,
    validar_citacoes,
    gerar_resposta,
)
from src.retrieval.tipos import Evidencia


class TestNormalizacaoFontes(unittest.TestCase):

    def setUp(self):
        self.trecho = (
            "Comentario: Produto veio com o canto de plastico "
            "danificado, mas nao afetou o funcionamento."
        )

        self.evidencia = Evidencia(
            marcador="F1",
            document_id="doc-real",
            review_id=None,
            review_score=1,
            trecho=self.trecho,
            similaridade=None,
        )

        self.fonte = {
            "marcador": "F1",
            "document_id": "doc-real",
            "trecho": self.trecho,
        }

    def montar_saida(self, fonte):
        return {
            "status": "respondida",
            "resposta": (
                "O produto apresentou dano, mas continuou "
                "funcionando."
            ),
            "afirmacoes": [
                {
                    "texto": (
                        "O dano nao afetou o funcionamento."
                    ),
                    "fontes": [fonte],
                }
            ],
            "fontes": [],
        }

    def test_normaliza_fonte_aninhada_valida(self):
        dados = self.montar_saida(self.fonte)
        original = copy.deepcopy(dados)

        normalizado = normalizar_fontes_aninhadas(dados)

        self.assertEqual(
            normalizado["afirmacoes"][0]["fontes"],
            ["F1"],
        )

        self.assertEqual(
            normalizado["fontes"],
            [self.fonte],
        )

        # Nao altera a estrutura original recebida.
        self.assertEqual(dados, original)

        resposta = RespostaRAG.model_validate(normalizado)

        self.assertEqual(
            validar_citacoes(resposta, [self.evidencia]),
            [],
        )

    def test_nao_corrige_marcador_inventado(self):
        fonte_falsa = {
            **self.fonte,
            "marcador": "F9",
        }

        dados = self.montar_saida(fonte_falsa)
        normalizado = normalizar_fontes_aninhadas(dados)
        resposta = RespostaRAG.model_validate(normalizado)

        problemas = validar_citacoes(
            resposta,
            [self.evidencia],
        )

        self.assertTrue(problemas)

    def test_nao_corrige_documento_divergente(self):
        fonte_falsa = {
            **self.fonte,
            "document_id": "documento-inventado",
        }

        dados = self.montar_saida(fonte_falsa)
        normalizado = normalizar_fontes_aninhadas(dados)
        resposta = RespostaRAG.model_validate(normalizado)

        problemas = validar_citacoes(
            resposta,
            [self.evidencia],
        )

        self.assertTrue(problemas)

    def test_nao_corrige_trecho_inventado(self):
        fonte_falsa = {
            **self.fonte,
            "trecho": "O cliente recebeu um produto perfeito.",
        }

        dados = self.montar_saida(fonte_falsa)
        normalizado = normalizar_fontes_aninhadas(dados)
        resposta = RespostaRAG.model_validate(normalizado)

        problemas = validar_citacoes(
            resposta,
            [self.evidencia],
        )

        self.assertTrue(problemas)

    def test_preserva_formato_ja_correto(self):
        dados = self.montar_saida("F1")
        dados["fontes"] = [self.fonte]

        normalizado = normalizar_fontes_aninhadas(dados)

        self.assertEqual(normalizado, dados)

    def test_pipeline_aceita_saida_com_fontes_aninhadas(self):
        """O pipeline aceita fonte legitima apos normalizacao."""

        dados = self.montar_saida(self.fonte)

        class GeradorGravado:
            def gerar(self, mensagens):
                return json.dumps(
                    dados,
                    ensure_ascii=False,
                )

        resposta = gerar_resposta(
            pergunta="O dano afetou o funcionamento?",
            evidencias=[self.evidencia],
            gerador=GeradorGravado(),
        )

        self.assertEqual(
            resposta.status.value,
            "respondida",
        )

        self.assertEqual(
            resposta.afirmacoes[0].fontes,
            ["F1"],
        )

        self.assertEqual(
            len(resposta.fontes),
            1,
        )

        self.assertEqual(
            resposta.fontes[0].document_id,
            "doc-real",
        )

        self.assertEqual(
            validar_citacoes(
                resposta,
                [self.evidencia],
            ),
            [],
        )
