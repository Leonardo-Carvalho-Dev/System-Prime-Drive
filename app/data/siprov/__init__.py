from .base import ResultadoItem, SiprovClient
from .fake import FakeSiprovClient


def obter_cliente(
    modo: str,
    usuario: str = "",
    senha: str = "",
    cod_loja: int = 0,
    placas_que_falham: set[str] | None = None,
    mensagem_falha: str | None = None,
) -> SiprovClient:
    if modo == "real":
        from .real import RealSiprovClient

        return RealSiprovClient(usuario=usuario, senha=senha, cod_loja=cod_loja)

    argumentos = {"placas_que_falham": placas_que_falham or set()}
    if mensagem_falha:
        argumentos["mensagem_falha"] = mensagem_falha
    return FakeSiprovClient(**argumentos)
