
"""Triagem conservadora de perguntas fora do escopo da Olist.

Este modulo nao substitui a avaliacao contextual do RAG.
Somente intencoes externas de alta confianca sao bloqueadas.
Perguntas ambiguas seguem para a recuperacao semantica.
"""

import re
import unicodedata


def _normalizar(texto: str) -> str:
    """Padroniza o texto para comparar intencoes."""
    decomposicao = unicodedata.normalize(
        "NFKD",
        texto.casefold(),
    )

    sem_acentos = "".join(
        caractere
        for caractere in decomposicao
        if not unicodedata.combining(caractere)
    )

    return " ".join(sem_acentos.split())


# Indicadores de que a pergunta esta relacionada ao
# dominio de avaliacoes e experiencias de consumidores.
_INDICIOS_AVALIACOES = re.compile(
    r"\b(?:olist|avaliac(?:ao|oes)|comentarios?|relatos?|"
    r"clientes?|consumidores?|pedidos?|compras?|"
    r"produtos?|entregas?|reclamac(?:ao|oes)|"
    r"vendedores?|lojas?|reviews?|feedback)\b"
)


# Padroes restritos a solicitacoes inequivocamente externas.
# Nao representam um classificador completo de intencoes.
_INTENCOES_EXTERNAS = (
    # Perguntas de conhecimento geografico geral.
    re.compile(
        r"^(?:qual|quais)\s+(?:e|era|sao|foram)"
        r"\s+a\s+capital\s+(?:de|da|do)\b"
    ),

    # Pedidos de instrucoes culinarias.
    re.compile(
        r"^como\s+(?:preparar|fazer|cozinhar|assar)\s+"
        r"(?:(?:um|uma|o|a)\s+)?"
        r"(?:bolo|pao|pizza|torta|sopa|arroz|"
        r"feijao|lasanha)\b"
    ),
)


def claramente_fora_do_escopo(pergunta: str) -> bool:
    """Identifica apenas intencoes externas de alta confianca."""

    texto = _normalizar(pergunta)

    # Se houver referencia explicita a avaliacoes ou
    # ao dominio de e-commerce, nao bloquear antecipadamente.
    # A pergunta sera avaliada pelo RAG.
    if _INDICIOS_AVALIACOES.search(texto):
        return False

    return any(
        padrao.search(texto) is not None
        for padrao in _INTENCOES_EXTERNAS
    )
