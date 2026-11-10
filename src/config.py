
"""Configuracao central: caminhos, modelos e parametros do pipeline RAG."""

from pathlib import Path

# parents[1] porque este arquivo fica em src/, e a raiz do projeto e um
# nivel acima (mesmo padrao usado nos scripts/ existentes).
RAIZ = Path(__file__).resolve().parents[1]

# Dados e indice: onde a Etapa 1/2 (preparacao) e a Etapa 3 (indexacao)
# gravam seus artefatos. Ambos ficam fora do Git (ver .gitignore).
ARQUIVO_DOCUMENTOS = RAIZ / "data" / "processed" / "reviews_documentos.jsonl"
PASTA_VECTORSTORE = RAIZ / "data" / "vectorstore" / "chroma_e5_completo"

# Recuperacao (Etapa 3 - decisoes D007, D008, D009 em docs/decisoes.md):
# mesmo modelo de embeddings e mesma colecao ja indexada, para reutilizar
# o indice existente sem reconstruir nada.
MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
COLECAO_CHROMA = "olist_e5_full_42687_v1"
DIMENSOES_EMBEDDING = 384
# Quantos candidatos buscar no ChromaDB antes de filtrar/selecionar o
# contexto. Ponto de partida sugerido no PDF de entrega P1 (D015).
TOP_K_CANDIDATOS = 50

# Montagem de contexto: limites do que entra, de fato, no prompt do LLM.
# Numeros nao validados ainda com os casos de desenvolvimento reais
# (ver D015); ajustar aqui conforme os experimentos da Etapa 3.
MAX_DOCUMENTOS_CONTEXTO = 8
MAX_CARACTERES_CONTEXTO = 4000

# Geracao: modelo pequeno o suficiente para rodar em CPU sem chave de
# API, escolhido em D016. VERSAO_PROMPT e gravada no trace de cada
# predicao (src/evaluation/executar_casos.py) para rastrear qual versao
# do prompt-base gerou cada resposta, caso o prompt mude no futuro.
MODELO_GERADOR = "Qwen/Qwen2.5-1.5B-Instruct"
MAX_TOKENS_SAIDA = 600
VERSAO_PROMPT = "v1"
