

"""Adaptador do LLM Qwen2.5-1.5B-Instruct local.

Mantem a geracao de texto e registra um diagnostico
sobre a quantidade de tokens e o motivo da parada.
"""

from src import config


class GeradorQwenLocal:
    """Carrega modelo e tokenizador sob demanda."""

    def __init__(self, modelo=None, tokenizador=None):
        self._modelo = modelo
        self._tokenizador = tokenizador

        # Sera preenchido apos cada geracao bem-sucedida.
        self.ultimo_diagnostico = None

    @property
    def tokenizador(self):
        if self._tokenizador is None:
            from transformers import AutoTokenizer

            self._tokenizador = AutoTokenizer.from_pretrained(
                config.MODELO_GERADOR
            )

        return self._tokenizador

    @property
    def modelo(self):
        if self._modelo is None:
            from transformers import AutoModelForCausalLM

            self._modelo = AutoModelForCausalLM.from_pretrained(
                config.MODELO_GERADOR
            )

        return self._modelo

    def contar_tokens(self, texto: str) -> int:
        return len(self.tokenizador.encode(texto))

    def gerar(
        self,
        mensagens: list[dict],
        max_tokens_saida: int = config.MAX_TOKENS_SAIDA,
    ) -> str:
        """Gera uma resposta e registra o motivo da parada."""

        if max_tokens_saida < 1:
            raise ValueError(
                "max_tokens_saida deve ser positivo"
            )

        # Evita reutilizar o diagnostico da pergunta anterior.
        self.ultimo_diagnostico = None

        # Aplica o formato de conversa do Qwen Instruct.
        entrada_formatada = (
            self.tokenizador.apply_chat_template(
                mensagens,
                tokenize=False,
                add_generation_prompt=True,
            )
        )

        entradas = self.tokenizador(
            entrada_formatada,
            return_tensors="pt",
        )

        # Preserva a geracao conservadora utilizada pela P2.
        saida = self.modelo.generate(
            **entradas,
            max_new_tokens=max_tokens_saida,
            do_sample=False,
            pad_token_id=self.tokenizador.eos_token_id,
        )

        # O resultado contem prompt + continuacao.
        # Isolamos somente os tokens novos.
        tamanho_entrada = entradas["input_ids"].shape[1]

        tokens_gerados = saida[0][tamanho_entrada:]

        quantidade = len(tokens_gerados)

        # Identifica os possiveis tokens de encerramento.
        # Alguns modelos podem definir um ou varios EOS IDs.
        eos_ids = set()

        eos_tokenizador = self.tokenizador.eos_token_id

        if eos_tokenizador is not None:
            eos_ids.add(int(eos_tokenizador))

        configuracao_geracao = getattr(
            self.modelo,
            "generation_config",
            None,
        )

        eos_modelo = getattr(
            configuracao_geracao,
            "eos_token_id",
            None,
        )

        if eos_modelo is not None:
            if isinstance(eos_modelo, (list, tuple, set)):
                eos_ids.update(
                    int(token) for token in eos_modelo
                )
            else:
                eos_ids.add(int(eos_modelo))

        ultimo_token = (
            int(tokens_gerados[-1])
            if quantidade
            else None
        )

        # Prioriza EOS: se o modelo encerrou normalmente
        # no ultimo token permitido, isso nao e truncamento.
        if ultimo_token in eos_ids:
            motivo = "eos"

        elif quantidade >= max_tokens_saida:
            motivo = "limite_tokens"

        else:
            motivo = "outro"

        # Diagnostico acessivel apos chamar gerar().
        self.ultimo_diagnostico = {
            "motivo_parada": motivo,
            "tokens_gerados": quantidade,
            "max_tokens_saida": max_tokens_saida,
        }

        texto_gerado = self.tokenizador.decode(
            tokens_gerados,
            skip_special_tokens=True,
        )

        return texto_gerado.strip()
