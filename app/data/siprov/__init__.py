from .base import ResultadoItem, SiprovClient
from .fake import FakeSiprovClient


def obter_cliente(modo: str, usuario: str = "", senha: str = "", cod_loja: int = 0) -> SiprovClient:
    if modo == "real":
        from .real import RealSiprovClient

        return RealSiprovClient(usuario=usuario, senha=senha, cod_loja=cod_loja)
    return FakeSiprovClient()
