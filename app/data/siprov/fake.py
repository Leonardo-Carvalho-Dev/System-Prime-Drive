import random

from .base import ResultadoItem, SiprovClient


class FakeSiprovClient(SiprovClient):
    """Cliente falso para testes e demonstração. Nunca chama a API real do Siprov."""

    def __init__(self, taxa_de_falha: float = 0.0, placas_que_falham: set[str] | None = None):
        self.taxa_de_falha = taxa_de_falha
        self.placas_que_falham = placas_que_falham or set()
        self.chamadas: list[tuple[str, dict]] = []

    def criar_item(self, codigo_contrato: str, dados: dict) -> ResultadoItem:
        self.chamadas.append((codigo_contrato, dados))
        placa = dados.get("PLACA")

        if placa in self.placas_que_falham:
            return ResultadoItem(sucesso=False, mensagem="Falha simulada para esta placa.")

        if self.taxa_de_falha and random.random() < self.taxa_de_falha:
            return ResultadoItem(sucesso=False, mensagem="Falha simulada aleatória.")

        return ResultadoItem(sucesso=True, codigo_siprov=f"FAKE-{placa}")
