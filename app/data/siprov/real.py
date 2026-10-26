from .base import ResultadoItem, SiprovClient


class RealSiprovClient(SiprovClient):
    """
    Ainda não implementado: falta a documentação real do endpoint do Siprov que
    cria o item do titular (autenticação, campos, formato de resposta e erros).
    Não deve ser usado — e não deve ser inventado — sem essa documentação.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "RealSiprovClient ainda não foi implementado. É necessária a documentação "
            "oficial da API do Siprov (endpoint, autenticação, campos e respostas) "
            "antes de implementar esta classe."
        )

    def criar_item(self, codigo_contrato: str, dados: dict) -> ResultadoItem:
        raise NotImplementedError
