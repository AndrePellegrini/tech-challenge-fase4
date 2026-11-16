
"""Recuperador semantico reutilizavel sobre o indice E5 + ChromaDB existente.

Transforma a busca experimental dos scripts da Etapa 3 em um componente
reutilizavel pelo pipeline RAG (Etapa 2 da integracao). Preserva os
prefixos do E5, os IDs e os metadados ja definidos em D007, D008 e D009.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from src import config
from src.retrieval.tipos import Candidato


def montar_filtro_nota(nota_min: int | None = None, nota_max: int | None = None) -> dict | None:
    """Converte uma faixa de notas (1 a 5) no filtro `where` do ChromaDB.

    Devolve None quando nenhum limite foi informado, para que a busca sem
    filtro continue exatamente igual. Limites fora de 1..5 ou invertidos
    geram ValueError, em vez de uma busca silenciosamente vazia.
    """
    for nome, valor in (("nota_min", nota_min), ("nota_max", nota_max)):
        if valor is None:
            continue
        if isinstance(valor, bool) or not isinstance(valor, int) or not 1 <= valor <= 5:
            raise ValueError(f"{nome} deve ser um inteiro entre 1 e 5")

    if nota_min is not None and nota_max is not None and nota_min > nota_max:
        raise ValueError("nota_min nao pode ser maior que nota_max")

    condicoes = []
    if nota_min is not None:
        condicoes.append({"review_score": {"$gte": nota_min}})
    if nota_max is not None:
        condicoes.append({"review_score": {"$lte": nota_max}})

    if not condicoes:
        return None
    if len(condicoes) == 1:
        return condicoes[0]
    return {"$and": condicoes}


class Recuperador:
    """Carrega o modelo de embeddings e a colecao uma unica vez por processo."""

    def __init__(self, modelo=None, colecao=None):
        # Permite injetar um modelo/colecao falsos nos testes, sem
        # precisar baixar o SentenceTransformer nem abrir o ChromaDB
        # real. Em producao (src/app.py), ambos ficam None e sao
        # criados sob demanda pelas properties abaixo.
        self._modelo = modelo
        self._colecao = colecao

    @property
    def modelo(self):
        # Inicializacao tardia: so baixa/carrega o modelo de embeddings
        # quando alguem realmente chamar buscar() pela primeira vez.
        if self._modelo is None:
            self._modelo = SentenceTransformer(config.MODELO_EMBEDDINGS)
        return self._modelo

    @property
    def colecao(self):
        if self._colecao is None:
            # Falha cedo e com mensagem clara se o indice ainda nao foi
            # construido nesta maquina, em vez de deixar o ChromaDB
            # estourar um erro generico mais adiante.
            if not config.PASTA_VECTORSTORE.exists():
                raise FileNotFoundError(
                    f"Banco vetorial nao encontrado: {config.PASTA_VECTORSTORE}. "
                    "Execute scripts/indexar_base_completa.py antes de consultar."
                )

            cliente = chromadb.PersistentClient(path=str(config.PASTA_VECTORSTORE))
            # embedding_function=None: os vetores da pergunta sao
            # calculados aqui mesmo (metodo buscar), nao pelo ChromaDB;
            # mesma convencao usada nos scripts de indexacao/auditoria.
            self._colecao = cliente.get_collection(
                name=config.COLECAO_CHROMA,
                embedding_function=None,
            )
        return self._colecao

    def buscar(
        self,
        pergunta: str,
        k: int = config.TOP_K_CANDIDATOS,
        nota_min: int | None = None,
        nota_max: int | None = None,
    ) -> list[Candidato]:
        """Retorna ate k candidatos ordenados por similaridade de cosseno.

        nota_min/nota_max (1 a 5, inclusivos) restringem a busca pelo
        metadado review_score ja gravado no indice (D027). Sem filtro, a
        consulta e identica a versao anterior.
        """
        if not pergunta or not pergunta.strip():
            raise ValueError("Pergunta vazia")

        filtro = montar_filtro_nota(nota_min, nota_max)

        # Prefixo "query:" e obrigatorio para o modelo E5 (D007): o
        # mesmo modelo usa "passage:" para os documentos indexados, e
        # misturar os prefixos degrada a qualidade da recuperacao.
        vetor = self.modelo.encode(
            ["query: " + pergunta.strip()],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]

        argumentos_consulta = {
            "query_embeddings": [vetor.tolist()],
            "n_results": k,
            "include": ["documents", "metadatas", "distances"],
        }
        # O filtro e aplicado pelo proprio ChromaDB antes do ranking, de
        # modo que o Top-K inteiro respeita a faixa de notas pedida.
        if filtro is not None:
            argumentos_consulta["where"] = filtro

        resultados = self.colecao.query(**argumentos_consulta)

        # O ChromaDB devolve uma lista de listas (uma por consulta); aqui
        # so fazemos uma consulta por vez, entao sempre usamos o indice [0].
        candidatos = []
        for identificador, texto, metadados, distancia in zip(
            resultados["ids"][0],
            resultados["documents"][0],
            resultados["metadatas"][0],
            resultados["distances"][0],
        ):
            candidatos.append(Candidato(
                id=identificador,
                texto=texto,
                metadata=metadados or {},
                # Distancia de cosseno (0 = identico) convertida para
                # similaridade (1 = identico), mais intuitiva para quem
                # ler o resultado.
                score=1 - distancia,
            ))

        return candidatos
