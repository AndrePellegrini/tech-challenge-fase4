
"""Testes para a selecao de evidencias dentro de um orcamento de contexto."""

import unittest

from src.retrieval.contexto import montar_contexto
from src.retrieval.tipos import Candidato


def _candidato(id_, texto, score, hash_texto=None, review_id=None, review_score=None):
    return Candidato(
        id=id_,
        texto=texto,
        metadata={
            "hash_texto": hash_texto or texto.casefold(),
            "review_id": review_id,
            "review_score": review_score,
        },
        score=score,
    )


class TestMontarContexto(unittest.TestCase):
    def test_ordem_e_marcadores(self):
        candidatos = [
            _candidato("doc-1", "Atraso de sete dias", 0.9),
            _candidato("doc-2", "Produto quebrado", 0.8),
        ]
        evidencias = montar_contexto(candidatos, max_documentos=8, max_caracteres=1000)

        self.assertEqual([e.marcador for e in evidencias], ["F1", "F2"])
        self.assertEqual(evidencias[0].document_id, "doc-1")
        self.assertEqual(evidencias[1].document_id, "doc-2")

    def test_remove_duplicatas_por_hash(self):
        candidatos = [
            _candidato("doc-1", "Otimo produto", 0.9, hash_texto="h1"),
            _candidato("doc-2", "Otimo produto", 0.85, hash_texto="h1"),
            _candidato("doc-3", "Entrega rapida", 0.8, hash_texto="h2"),
        ]
        evidencias = montar_contexto(candidatos, max_documentos=8, max_caracteres=1000)

        self.assertEqual(len(evidencias), 2)
        self.assertEqual([e.document_id for e in evidencias], ["doc-1", "doc-3"])

    def test_nao_preenche_com_copias_quando_ha_poucos_textos_distintos(self):
        candidatos = [
            _candidato(f"doc-{i}", "Mesmo texto repetido", 1.0 - i * 0.01, hash_texto="h1")
            for i in range(10)
        ]
        evidencias = montar_contexto(candidatos, max_documentos=8, max_caracteres=1000)

        self.assertEqual(len(evidencias), 1)

    def test_respeita_orcamento_de_caracteres(self):
        candidatos = [
            _candidato("doc-1", "a" * 50, 0.9, hash_texto="h1"),
            _candidato("doc-2", "b" * 50, 0.8, hash_texto="h2"),
            _candidato("doc-3", "c" * 50, 0.7, hash_texto="h3"),
        ]
        evidencias = montar_contexto(candidatos, max_documentos=8, max_caracteres=80)

        # O primeiro sempre entra; os demais só se couberem no orçamento.
        self.assertEqual(len(evidencias), 1)
        self.assertEqual(evidencias[0].document_id, "doc-1")

    def test_primeiro_candidato_entra_mesmo_ultrapassando_orcamento_sozinho(self):
        candidatos = [_candidato("doc-1", "x" * 500, 0.9, hash_texto="h1")]
        evidencias = montar_contexto(candidatos, max_documentos=8, max_caracteres=10)

        self.assertEqual(len(evidencias), 1)

    def test_respeita_limite_de_documentos(self):
        candidatos = [
            _candidato(f"doc-{i}", f"Texto {i}", 1.0 - i * 0.01, hash_texto=f"h{i}")
            for i in range(20)
        ]
        evidencias = montar_contexto(candidatos, max_documentos=5, max_caracteres=10_000)

        self.assertEqual(len(evidencias), 5)


if __name__ == "__main__":
    unittest.main()
