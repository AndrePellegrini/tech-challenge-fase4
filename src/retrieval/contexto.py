
"""Selecao de evidencias distintas para o contexto enviado ao LLM.

Implementa o passo 3-4 do fluxo descrito no PDF de entrega P1: agrupar
textos repetidos por hash sem apagar avaliacoes canonicas, nao preencher
o contexto com copias quando ha poucos textos distintos, e limitar o
contexto por um orcamento (numero de documentos e caracteres).
"""

from src.retrieval.tipos import Candidato, Evidencia


def _chave_duplicata(candidato: Candidato) -> str:
    # hash_texto vem de D006/D009 (SHA-256 do page_content.casefold());
    # reaproveitar esse hash evita recalcular a deduplicacao aqui. Se o
    # metadado faltar (por exemplo, em testes), caímos de volta no texto
    # normalizado como chave.
    hash_texto = candidato.metadata.get("hash_texto")
    if hash_texto:
        return hash_texto
    return candidato.texto.casefold().strip()


def montar_contexto(
    candidatos: list[Candidato],
    max_documentos: int,
    max_caracteres: int,
    contador_caracteres=len,
) -> list[Evidencia]:
    """Seleciona ate max_documentos textos distintos, dentro do orcamento.

    candidatos deve vir ordenado por relevancia (melhor primeiro). O
    primeiro candidato sempre entra, mesmo se sozinho ultrapassar o
    orcamento, para evitar um contexto vazio.
    """
    evidencias: list[Evidencia] = []
    vistos: set[str] = set()
    caracteres_usados = 0

    for candidato in candidatos:
        # Candidatos chegam ordenados por relevancia: assim que
        # atingimos o limite de documentos distintos, nao ha motivo
        # para continuar olhando o resto da lista.
        if len(evidencias) >= max_documentos:
            break

        # Pula candidatos cujo texto (ou hash) ja foi selecionado --
        # e assim que evitamos "preencher o contexto com copias", como
        # pede o PDF de entrega P1.
        chave = _chave_duplicata(candidato)
        if chave in vistos:
            continue

        # So aplicamos o orcamento de caracteres a partir do segundo
        # item selecionado: "evidencias" vazio significa que ainda nao
        # aceitamos nenhum candidato, e um contexto vazio seria pior do
        # que um unico documento grande.
        custo = contador_caracteres(candidato.texto)
        if evidencias and caracteres_usados + custo > max_caracteres:
            continue

        vistos.add(chave)
        caracteres_usados += custo

        evidencias.append(Evidencia(
            # F1, F2... na ordem de insercao -- e o marcador que o LLM
            # devera usar para citar esta fonte na resposta.
            marcador=f"F{len(evidencias) + 1}",
            document_id=candidato.id,
            review_id=candidato.metadata.get("review_id"),
            review_score=candidato.metadata.get("review_score"),
            trecho=candidato.texto,
            similaridade=candidato.score,
        ))

    return evidencias
