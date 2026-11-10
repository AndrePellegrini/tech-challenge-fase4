
"""Testes para prompt, parse e verificacao de citacoes da resposta do RAG."""

import json
import unittest

from src.generation.resposta import Status, construir_prompt, gerar_resposta, validar_citacoes, RespostaRAG
from src.retrieval.tipos import Evidencia


class GeradorFalso:
    """Substitui o LLM real por um texto fixo, para testar sem carregar modelo."""

    def __init__(self, texto_saida):
        self.texto_saida = texto_saida
        self.chamado = False

    def gerar(self, mensagens):
        self.chamado = True
        return self.texto_saida


def _evidencia(marcador="F1", document_id="doc-1", trecho="minha outra encomenda esta em atraso"):
    return Evidencia(
        marcador=marcador,
        document_id=document_id,
        review_id="review-1",
        review_score=3,
        trecho=trecho,
        similaridade=0.8,
    )


class TestConstruirPrompt(unittest.TestCase):
    def test_inclui_pergunta_e_marcadores(self):
        evidencias = [_evidencia()]
        mensagens = construir_prompt("Houve atraso?", evidencias)

        self.assertEqual(mensagens[0]["role"], "system")
        self.assertEqual(mensagens[1]["role"], "user")
        self.assertIn("Houve atraso?", mensagens[1]["content"])
        self.assertIn("[F1]", mensagens[1]["content"])

    def test_sem_evidencias_indica_ausencia(self):
        mensagens = construir_prompt("Houve atraso?", [])
        self.assertIn("nenhuma evidencia", mensagens[1]["content"])


class TestValidarCitacoes(unittest.TestCase):
    def test_sem_problemas_quando_citacao_e_valida(self):
        evidencias = [_evidencia()]
        resposta = RespostaRAG(
            status=Status.RESPONDIDA,
            resposta="Um relato menciona atraso [F1].",
            afirmacoes=[{"texto": "Atraso relatado", "fontes": ["F1"]}],
            fontes=[{"marcador": "F1", "document_id": "doc-1", "trecho": "outra encomenda esta em atraso"}],
        )
        self.assertEqual(validar_citacoes(resposta, evidencias), [])

    def test_detecta_marcador_inexistente(self):
        evidencias = [_evidencia()]
        resposta = RespostaRAG(
            status=Status.RESPONDIDA,
            resposta="...",
            fontes=[{"marcador": "F9", "document_id": "doc-1", "trecho": "atraso"}],
        )
        problemas = validar_citacoes(resposta, evidencias)
        self.assertTrue(any("Marcador inexistente" in p for p in problemas))

    def test_detecta_trecho_nao_literal(self):
        evidencias = [_evidencia()]
        resposta = RespostaRAG(
            status=Status.RESPONDIDA,
            resposta="...",
            fontes=[{"marcador": "F1", "document_id": "doc-1", "trecho": "frase que nao existe na fonte"}],
        )
        problemas = validar_citacoes(resposta, evidencias)
        self.assertTrue(any("nao encontrado literalmente" in p for p in problemas))

    def test_detecta_document_id_divergente(self):
        evidencias = [_evidencia()]
        resposta = RespostaRAG(
            status=Status.RESPONDIDA,
            resposta="...",
            fontes=[{"marcador": "F1", "document_id": "doc-errado", "trecho": "atraso"}],
        )
        problemas = validar_citacoes(resposta, evidencias)
        self.assertTrue(any("document_id divergente" in p for p in problemas))


class TestGerarResposta(unittest.TestCase):
    def test_sem_evidencias_nao_chama_o_modelo(self):
        gerador = GeradorFalso("nao deveria ser usado")
        resposta = gerar_resposta("Pergunta qualquer", [], gerador)

        self.assertEqual(resposta.status, Status.EVIDENCIAS_INSUFICIENTES)
        self.assertFalse(gerador.chamado)

    def test_resposta_valida_e_aceita(self):
        evidencias = [_evidencia()]
        saida = json.dumps({
            "status": "respondida",
            "resposta": "Uma avaliacao relata atraso de uma encomenda [F1].",
            "afirmacoes": [
                {
                    "texto": "Uma encomenda esta em atraso",
                    "fontes": ["F1"],
                }
            ],
            "fontes": [{"marcador": "F1", "document_id": "doc-1", "trecho": "outra encomenda esta em atraso"}],
        })
        gerador = GeradorFalso(saida)
        resposta = gerar_resposta("Houve atraso?", evidencias, gerador)

        self.assertEqual(resposta.status, Status.RESPONDIDA)
        self.assertEqual(len(resposta.fontes), 1)

    def test_json_invalido_vira_erro_operacional(self):
        evidencias = [_evidencia()]
        gerador = GeradorFalso("isso nao e um JSON")
        resposta = gerar_resposta("Houve atraso?", evidencias, gerador)

        self.assertEqual(resposta.status, Status.ERRO_OPERACIONAL)

    def test_citacao_invalida_vira_erro_operacional(self):
        evidencias = [_evidencia()]
        saida = json.dumps({
            "status": "respondida",
            "resposta": "...",
            "afirmacoes": [],
            "fontes": [{"marcador": "F1", "document_id": "doc-1", "trecho": "frase inventada pelo modelo"}],
        })
        gerador = GeradorFalso(saida)
        resposta = gerar_resposta("Houve atraso?", evidencias, gerador)

        self.assertEqual(resposta.status, Status.ERRO_OPERACIONAL)

    def test_json_com_texto_extra_e_recuperado(self):
        evidencias = [_evidencia()]
        corpo = json.dumps({
            "status": "fora_do_escopo",
            "resposta": "Pergunta fora do dominio.",
            "afirmacoes": [],
            "fontes": [],
        })
        gerador = GeradorFalso(f"Aqui esta minha resposta:\n{corpo}\nFim.")
        resposta = gerar_resposta("Qual a previsao do tempo?", evidencias, gerador)

        self.assertEqual(resposta.status, Status.FORA_DO_ESCOPO)

    def test_rejeita_resposta_sem_afirmacoes_e_sem_fontes(self):
        evidencias = [_evidencia()]

        saida = json.dumps({
            "status": "respondida",
            "resposta": "Todos os clientes tiveram atraso de 7 dias.",
            "afirmacoes": [],
            "fontes": [],
        })

        gerador = GeradorFalso(saida)

        resposta = gerar_resposta(
            "Quais problemas de entrega foram relatados?",
            evidencias,
            gerador,
        )

        self.assertEqual(
            resposta.status,
            Status.ERRO_OPERACIONAL,
        )

    def test_reconstroi_fontes_omitidas_pelo_modelo(self):
        evidencias = [_evidencia()]

        saida = json.dumps({
            "status": "respondida",
            "resposta": "Uma encomenda esta em atraso [F1].",
            "afirmacoes": [
                {
                    "texto": "Uma encomenda esta em atraso",
                    "fontes": ["F1"],
                }
            ],
            "fontes": [],
        })

        gerador = GeradorFalso(saida)

        resposta = gerar_resposta(
            "Houve atraso?",
            evidencias,
            gerador,
        )

        self.assertEqual(
            resposta.status,
            Status.RESPONDIDA,
        )

        self.assertEqual(len(resposta.fontes), 1)
        self.assertEqual(resposta.fontes[0].marcador, "F1")
        self.assertEqual(resposta.fontes[0].document_id, "doc-1")
        self.assertEqual(
            resposta.fontes[0].trecho,
            "minha outra encomenda esta em atraso",
        )

    def test_json_truncado_informa_limite_de_tokens(self):
        """Falha de parse deve preservar o diagnostico de truncamento."""
        evidencias = [_evidencia()]

        gerador = GeradorFalso(
            '{"status": "respondida", "resposta": "Um cliente'
        )

        gerador.ultimo_diagnostico = {
            "motivo_parada": "limite_tokens",
            "tokens_gerados": 600,
            "max_tokens_saida": 600,
        }

        resposta = gerar_resposta(
            "Quais problemas foram relatados?",
            evidencias,
            gerador,
        )

        self.assertEqual(
            resposta.status,
            Status.ERRO_OPERACIONAL,
        )

        self.assertIn(
            "limite_tokens",
            resposta.resposta,
        )

    def test_json_invalido_apos_eos_informa_diagnostico(self):
        """JSON incorreto com EOS nao deve ser chamado de truncamento."""
        evidencias = [_evidencia()]

        gerador = GeradorFalso(
            "Esta resposta nao esta em formato JSON."
        )

        gerador.ultimo_diagnostico = {
            "motivo_parada": "eos",
            "tokens_gerados": 42,
            "max_tokens_saida": 600,
        }

        resposta = gerar_resposta(
            "Houve problemas de entrega?",
            evidencias,
            gerador,
        )

        self.assertEqual(
            resposta.status,
            Status.ERRO_OPERACIONAL,
        )

        self.assertIn("eos", resposta.resposta)
        self.assertNotIn(
            "limite_tokens",
            resposta.resposta,
        )
    def test_insuficiencia_com_fonte_inventada_e_rejeitada(self):
        """Recusas tambem precisam respeitar as fontes reais."""
        evidencias = [_evidencia()]

        saida = json.dumps({
            "status": "evidencias_insuficientes",
            "resposta": "Nao foi possivel determinar o prazo [F9].",
            "afirmacoes": [
                {
                    "texto": "Prazo nao identificado",
                    "fontes": ["F9"],
                }
            ],
            "fontes": [
                {
                    "marcador": "F9",
                    "document_id": "documento-inexistente",
                    "trecho": "Prazo de entrega desconhecido",
                }
            ],
        })

        resposta = gerar_resposta(
            "Qual foi o prazo de entrega?",
            evidencias,
            GeradorFalso(saida),
        )

        self.assertEqual(
            resposta.status,
            Status.ERRO_OPERACIONAL,
        )

    def test_fora_do_escopo_com_fonte_inventada_e_rejeitado(self):
        """Fonte inexistente nao pode ser aceita em nenhuma recusa."""
        evidencias = [_evidencia()]

        saida = json.dumps({
            "status": "fora_do_escopo",
            "resposta": "Pergunta fora do dominio.",
            "afirmacoes": [],
            "fontes": [
                {
                    "marcador": "F99",
                    "document_id": "documento-falso",
                    "trecho": "Informacao inventada",
                }
            ],
        })

        resposta = gerar_resposta(
            "Qual e a capital da Franca?",
            evidencias,
            GeradorFalso(saida),
        )

        self.assertEqual(
            resposta.status,
            Status.ERRO_OPERACIONAL,
        )

    def test_recusa_legitima_sem_fontes_e_aceita(self):
        """Uma recusa pode ser valida sem citar documentos."""
        evidencias = [_evidencia()]

        saida = json.dumps({
            "status": "evidencias_insuficientes",
            "resposta": (
                "A avaliacao nao informa a data exata "
                "de entrega do pedido."
            ),
            "afirmacoes": [],
            "fontes": [],
        })

        resposta = gerar_resposta(
            "Qual foi a data exata da entrega?",
            evidencias,
            GeradorFalso(saida),
        )

        self.assertEqual(
            resposta.status,
            Status.EVIDENCIAS_INSUFICIENTES,
        )

if __name__ == "__main__":
    unittest.main()
