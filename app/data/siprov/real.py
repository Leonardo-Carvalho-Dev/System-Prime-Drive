import requests

from .base import ResultadoItem, SiprovClient

URL_BASE = "https://acesso.siprov.com.br/siprov-api"
TIMEOUT_PADRAO = 10


class RealSiprovClient(SiprovClient):
    """
    Cliente real da API do Siprov (https://doc.siprov.com.br/).

    Autentica com usuário/senha (Basic) em POST /ext/autenticacao, recebendo um
    token Bearer válido por 12h, e cria/atualiza o item do veículo em
    POST /ext/beneficio/veicular. Enviar `codBeneficio` (o código do contrato já
    existente) para adicionar o item a um benefício existente — sem ele, o Siprov
    cria um benefício novo.
    """

    def __init__(self, usuario: str, senha: str, cod_loja: int, timeout: int = TIMEOUT_PADRAO):
        self.usuario = usuario
        self.senha = senha
        self.cod_loja = cod_loja
        self.timeout = timeout
        self._token: str | None = None

    def _autenticar(self) -> None:
        resposta = requests.post(
            f"{URL_BASE}/ext/autenticacao",
            auth=(self.usuario, self.senha),
            timeout=self.timeout,
        )
        resposta.raise_for_status()
        self._token = resposta.json()["authorizationToken"]

    def criar_item(self, codigo_contrato: str, dados: dict) -> ResultadoItem:
        if self._token is None:
            try:
                self._autenticar()
            except requests.RequestException:
                return ResultadoItem(sucesso=False, mensagem="Não foi possível autenticar no Siprov.")

        payload = {
            "codBeneficio": int(codigo_contrato),
            "codLoja": self.cod_loja,
            "cpfCnpj": dados.get("CPF_CNPJ_ASSOCIADO"),
            "codPlano": dados.get("CODIGO_PLANO_SIPROV"),
            "placa": dados.get("PLACA"),
            "chassi": dados.get("CHASSI"),
            "renavam": dados.get("RENAVAM"),
            "marca": dados.get("MARCA"),
            "modelo": dados.get("MODELO"),
            "anoFabricacao": dados.get("ANO_FABRICACAO"),
            "anoModelo": dados.get("ANO_MODELO"),
            "combustivel": dados.get("COMBUSTIVEL_SIPROV"),
            "categoria": dados.get("CATEGORIA_SIPROV"),
            "cor": dados.get("COR"),
        }

        try:
            resposta = requests.post(
                f"{URL_BASE}/ext/beneficio/veicular",
                json=payload,
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=self.timeout,
            )
        except requests.Timeout:
            return ResultadoItem(sucesso=False, mensagem="Tempo esgotado ao falar com o Siprov.")
        except requests.RequestException:
            return ResultadoItem(sucesso=False, mensagem="Sem resposta do Siprov.")

        if resposta.status_code == 200:
            corpo = resposta.json()
            return ResultadoItem(sucesso=True, codigo_siprov=str(corpo.get("codBeneficio")))

        if resposta.status_code == 401:
            self._token = None

        return ResultadoItem(sucesso=False, mensagem=self._extrair_mensagem_erro(resposta))

    @staticmethod
    def _extrair_mensagem_erro(resposta: requests.Response) -> str:
        try:
            corpo = resposta.json()
        except ValueError:
            return resposta.text or f"Erro {resposta.status_code} ao falar com o Siprov."
        return corpo.get("mensagem") or corpo.get("message") or f"Erro {resposta.status_code} ao falar com o Siprov."
