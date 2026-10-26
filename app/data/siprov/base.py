from dataclasses import dataclass


@dataclass
class ResultadoItem:
    sucesso: bool
    mensagem: str | None = None
    codigo_siprov: str | None = None


class SiprovClient:
    """Interface para a integração com o Siprov. O resto do sistema só fala com esta classe."""

    def criar_item(self, codigo_contrato: str, dados: dict) -> ResultadoItem:
        raise NotImplementedError
