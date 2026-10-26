from unittest.mock import Mock, patch

import requests

from app.data.siprov import ResultadoItem
from app.data.siprov.real import URL_BASE, RealSiprovClient


def _resposta_mock(status_code, corpo_json=None, texto=""):
    resposta = Mock()
    resposta.status_code = status_code
    resposta.text = texto
    if corpo_json is not None:
        resposta.json.return_value = corpo_json
    else:
        resposta.json.side_effect = ValueError("sem corpo json")
    resposta.raise_for_status = Mock()
    return resposta


def _cliente():
    return RealSiprovClient(usuario="usuario-teste", senha="senha-teste", cod_loja=5409)


@patch("app.data.siprov.real.requests.post")
def test_criar_item_com_sucesso(mock_post):
    resposta_auth = _resposta_mock(200, {"authorizationToken": "token-123"})
    resposta_item = _resposta_mock(200, {"codBeneficio": 42, "sequencial": 1})
    mock_post.side_effect = [resposta_auth, resposta_item]

    cliente = _cliente()
    resultado = cliente.criar_item("42", {"PLACA": "ABC1234"})

    assert resultado == ResultadoItem(sucesso=True, mensagem=None, codigo_siprov="42")
    assert mock_post.call_count == 2
    url_autenticacao, url_item = mock_post.call_args_list[0].args[0], mock_post.call_args_list[1].args[0]
    assert url_autenticacao == f"{URL_BASE}/ext/autenticacao"
    assert url_item == f"{URL_BASE}/ext/beneficio/veicular"


@patch("app.data.siprov.real.requests.post")
def test_criar_item_reaproveita_token_entre_chamadas(mock_post):
    resposta_auth = _resposta_mock(200, {"authorizationToken": "token-123"})
    resposta_item = _resposta_mock(200, {"codBeneficio": 42})
    mock_post.side_effect = [resposta_auth, resposta_item, resposta_item]

    cliente = _cliente()
    cliente.criar_item("42", {"PLACA": "ABC1234"})
    cliente.criar_item("42", {"PLACA": "ABC1235"})

    assert mock_post.call_count == 3  # 1 autenticação + 2 itens


@patch("app.data.siprov.real.requests.post")
def test_criar_item_com_erro_4xx_devolve_mensagem_do_siprov(mock_post):
    resposta_auth = _resposta_mock(200, {"authorizationToken": "token-123"})
    resposta_erro = _resposta_mock(400, {"mensagem": "Placa inválida."})
    mock_post.side_effect = [resposta_auth, resposta_erro]

    cliente = _cliente()
    resultado = cliente.criar_item("42", {"PLACA": "INVALIDA"})

    assert resultado.sucesso is False
    assert resultado.mensagem == "Placa inválida."


@patch("app.data.siprov.real.requests.post")
def test_criar_item_com_401_forca_nova_autenticacao_na_proxima_chamada(mock_post):
    resposta_auth = _resposta_mock(200, {"authorizationToken": "token-123"})
    resposta_401 = _resposta_mock(401, texto="Sessão expirada!")
    resposta_auth_2 = _resposta_mock(200, {"authorizationToken": "token-456"})
    resposta_sucesso = _resposta_mock(200, {"codBeneficio": 42})
    mock_post.side_effect = [resposta_auth, resposta_401, resposta_auth_2, resposta_sucesso]

    cliente = _cliente()
    primeiro = cliente.criar_item("42", {"PLACA": "ABC1234"})
    segundo = cliente.criar_item("42", {"PLACA": "ABC1235"})

    assert primeiro.sucesso is False
    assert segundo.sucesso is True
    assert mock_post.call_count == 4


@patch("app.data.siprov.real.requests.post")
def test_criar_item_com_timeout(mock_post):
    resposta_auth = _resposta_mock(200, {"authorizationToken": "token-123"})
    mock_post.side_effect = [resposta_auth, requests.Timeout()]

    cliente = _cliente()
    resultado = cliente.criar_item("42", {"PLACA": "ABC1234"})

    assert resultado.sucesso is False
    assert "esgotado" in resultado.mensagem.lower()


@patch("app.data.siprov.real.requests.post")
def test_criar_item_sem_resposta_do_servidor(mock_post):
    resposta_auth = _resposta_mock(200, {"authorizationToken": "token-123"})
    mock_post.side_effect = [resposta_auth, requests.ConnectionError()]

    cliente = _cliente()
    resultado = cliente.criar_item("42", {"PLACA": "ABC1234"})

    assert resultado.sucesso is False
    assert "siprov" in resultado.mensagem.lower()


@patch("app.data.siprov.real.requests.post")
def test_falha_na_autenticacao_nao_tenta_criar_item(mock_post):
    mock_post.side_effect = requests.ConnectionError()

    cliente = _cliente()
    resultado = cliente.criar_item("42", {"PLACA": "ABC1234"})

    assert resultado.sucesso is False
    assert mock_post.call_count == 1
