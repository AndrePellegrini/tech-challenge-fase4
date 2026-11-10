
"""Adaptador do LLM gerador: Qwen2.5-1.5B-Instruct local, via transformers.

Modelo pequeno o suficiente para rodar em CPU sem chave de API, conforme
usado nas aulas e sugerido no guia de implementacao da entrega P1.
"""

from src import config


class GeradorQwenLocal:
    """Carrega o modelo e o tokenizador uma unica vez por processo."""

    def __init__(self, modelo=None, tokenizador=None):
        # Mesma logica de inicializacao tardia do Recuperador: permite
        # testes com um objeto falso (ver tests/test_resposta.py), sem
        # baixar nem carregar o modelo real de ~1.5B de parametros.
        self._modelo = modelo
        self._tokenizador = tokenizador

    @property
    def tokenizador(self):
        if self._tokenizador is None:
            # Import feito aqui dentro (e nao no topo do arquivo) para
            # nao obrigar quem so quer importar o modulo (por exemplo,
            # para testes de outras partes do codigo) a ter transformers
            # instalado.
            from transformers import AutoTokenizer
            self._tokenizador = AutoTokenizer.from_pretrained(config.MODELO_GERADOR)
        return self._tokenizador

    @property
    def modelo(self):
        if self._modelo is None:
            from transformers import AutoModelForCausalLM
            self._modelo = AutoModelForCausalLM.from_pretrained(config.MODELO_GERADOR)
        return self._modelo

    def contar_tokens(self, texto: str) -> int:
        return len(self.tokenizador.encode(texto))

    def gerar(self, mensagens: list[dict], max_tokens_saida: int = config.MAX_TOKENS_SAIDA) -> str:
        """Gera texto a partir de mensagens no formato chat. Decodificacao
        gulosa (sem amostragem), para uma configuracao de geracao conservadora."""
        # apply_chat_template aplica o formato de conversa esperado pelo
        # Qwen2.5-Instruct (system/user/assistant com os tokens especiais
        # corretos); add_generation_prompt=True deixa o texto pronto para
        # o modelo comecar a responder como "assistant".
        entrada_formatada = self.tokenizador.apply_chat_template(
            mensagens,
            tokenize=False,
            add_generation_prompt=True,
        )
        entradas = self.tokenizador(entrada_formatada, return_tensors="pt")

        saida = self.modelo.generate(
            **entradas,
            max_new_tokens=max_tokens_saida,
            # do_sample=False = decodificacao gulosa (greedy): sempre o
            # token mais provavel, sem aleatoriedade. E a "configuracao
            # de geracao conservadora" pedida no PDF de entrega P1 --
            # ajuda a reproduzir o mesmo resultado entre execucoes.
            do_sample=False,
            # Qwen2.5 nao define um pad_token por padrao; usar o
            # eos_token_id evita o aviso do transformers e e a pratica
            # usual para geracao de uma unica sequencia (sem batch).
            pad_token_id=self.tokenizador.eos_token_id,
        )

        # generate() devolve o prompt + a continuacao gerada concatenados;
        # fatiamos a partir do tamanho da entrada para pegar so o texto
        # novo (a resposta do modelo).
        tokens_gerados = saida[0][entradas["input_ids"].shape[1]:]
        return self.tokenizador.decode(tokens_gerados, skip_special_tokens=True).strip()
