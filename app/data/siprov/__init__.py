from .base import ResultadoItem, SiprovClient
from .fake import FakeSiprovClient


def obter_cliente(modo: str) -> SiprovClient:
    if modo == "real":
        from .real import RealSiprovClient

        return RealSiprovClient()
    return FakeSiprovClient()
