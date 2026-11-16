"""Executa as perguntas de exemplo da documentacao com o pipeline real.

Carrega o recuperador (E5 + ChromaDB) e o Qwen uma unica vez e roda as
perguntas de demonstracao baseadas no enunciado do Tech Challenge,
incluindo os exemplos com filtro por nota (D027). O resultado completo
de cada pergunta, com tempo de execucao, e salvo em JSON para servir de
base reprodutivel ao arquivo docs/exemplos.md.

Uso:
    python scripts/gerar_exemplos.py
    python scripts/gerar_exemplos.py --id E01 --id E07
"""

import argparse
import json
import platform
import sys
import time
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src import config  # noqa: E402
from src.app import processar_pergunta  # noqa: E402
from src.generation.modelo import GeradorQwenLocal  # noqa: E402
from src.retrieval.recuperador import Recuperador  # noqa: E402

SAIDA_PADRAO = RAIZ / "reports" / "exemplos_respostas.json"

# Perguntas do enunciado (paginas 4, 5, 8 e 9), mais dois casos de limite.
EXEMPLOS = [
    {"id": "E01", "categoria": "Investigacao de reclamacoes",
     "pergunta": "Quais são os principais problemas relatados pelos clientes em suas avaliações?"},
    {"id": "E02", "categoria": "Investigacao de um tema especifico",
     "pergunta": "O que os clientes relatam sobre problemas relacionados à entrega?"},
    {"id": "E03", "categoria": "Busca por experiencias positivas",
     "pergunta": "Quais aspectos da experiência de compra são mais elogiados pelos clientes?"},
    {"id": "E04", "categoria": "Exploracao baseada em evidencias",
     "pergunta": "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?"},
    {"id": "E05", "categoria": "Qualidade dos produtos",
     "pergunta": "Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?"},
    {"id": "E06", "categoria": "Investigacao de insatisfacao (filtro por nota)",
     "pergunta": "Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?",
     "nota_max": 2},
    {"id": "E07", "categoria": "Metadados: nota baixa (filtro por nota)",
     "pergunta": "Quais são os principais problemas relatados nas avaliações?",
     "nota_max": 1},
    {"id": "E08", "categoria": "Metadados: nota alta (filtro por nota)",
     "pergunta": "O que os clientes mais elogiam na entrega?",
     "nota_min": 5},
    {"id": "E09", "categoria": "Evidencias insuficientes",
     "pergunta": "Quantos clientes moram na cidade de Curitiba?"},
    {"id": "E10", "categoria": "Fora do escopo (regra de escopo)",
     "pergunta": "Me ensine uma receita de bolo de cenoura."},
    {"id": "E11", "categoria": "Pergunta externa sem regra de escopo",
     "pergunta": "Qual a previsão do tempo em São Paulo amanhã?"},
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--id", dest="ids", action="append", help="Executa apenas este exemplo (repetivel)")
    parser.add_argument("--saida", default=str(SAIDA_PADRAO))
    argumentos = parser.parse_args()

    exemplos = EXEMPLOS
    if argumentos.ids:
        desconhecidos = set(argumentos.ids) - {e["id"] for e in EXEMPLOS}
        if desconhecidos:
            parser.error("IDs desconhecidos: " + ", ".join(sorted(desconhecidos)))
        exemplos = [e for e in EXEMPLOS if e["id"] in set(argumentos.ids)]

    recuperador = Recuperador()
    gerador = GeradorQwenLocal()

    resultados = []
    for exemplo in exemplos:
        print(f"[{exemplo['id']}] {exemplo['pergunta']}", flush=True)
        inicio = time.monotonic()
        resultado = processar_pergunta(
            exemplo["pergunta"],
            recuperador,
            gerador,
            nota_min=exemplo.get("nota_min"),
            nota_max=exemplo.get("nota_max"),
        )
        duracao = round(time.monotonic() - inicio, 1)
        print(f"    -> {resultado['status']} ({duracao} s)", flush=True)
        resultados.append({**exemplo, "tempo_segundos": duracao, "resultado": resultado})

    saida = {
        "data_execucao": date.today().isoformat(),
        "ambiente": {
            "python": platform.python_version(),
            "sistema": platform.platform(),
            "dispositivo": "CPU",
        },
        "configuracao": {
            "modelo_embeddings": config.MODELO_EMBEDDINGS,
            "colecao": config.COLECAO_CHROMA,
            "modelo_gerador": config.MODELO_GERADOR,
            "versao_prompt": config.VERSAO_PROMPT,
            "top_k_candidatos": config.TOP_K_CANDIDATOS,
            "max_documentos_contexto": config.MAX_DOCUMENTOS_CONTEXTO,
            "max_caracteres_contexto": config.MAX_CARACTERES_CONTEXTO,
            "max_tokens_saida": config.MAX_TOKENS_SAIDA,
        },
        "exemplos": resultados,
    }

    caminho = Path(argumentos.saida)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Salvo em {caminho}")


if __name__ == "__main__":
    main()
