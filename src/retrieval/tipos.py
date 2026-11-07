
"""Tipos compartilhados entre recuperacao e geracao."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Candidato:
    """Um documento recuperado do indice vetorial, antes da selecao de contexto.

    Corresponde a uma linha crua devolvida pelo ChromaDB: ainda pode
    conter textos duplicados ou mais candidatos do que cabem no
    orcamento do prompt. A deduplicacao e o corte por orcamento
    acontecem depois, em src/retrieval/contexto.py.
    """

    id: str  # id tecnico do documento (olist_review_row_XXXXXX)
    texto: str  # page_content original, sem o prefixo "passage:"
    metadata: dict  # metadados originais do documento (review_id, nota, hash...)
    score: float  # similaridade de cosseno (1 - distancia do ChromaDB)


@dataclass
class Evidencia:
    """Um documento selecionado para o contexto, com marcador de citacao (F1, F2...).

    O marcador e o que o LLM deve usar para citar a fonte na resposta
    (por exemplo "[F1]"); ele so existe apos a selecao de contexto,
    diferente do Candidato, que nao tem marcador.
    """

    marcador: str  # "F1", "F2"... na ordem em que entrou no contexto
    document_id: str  # mesmo valor de Candidato.id, repetido para rastreabilidade
    review_id: Optional[str]
    review_score: Optional[int]
    trecho: str  # texto literal enviado ao LLM; citacoes devem ocorrer dentro dele
    similaridade: Optional[float]
