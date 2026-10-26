import time

import pytest

from app.services.planilha import COLUNAS, EXEMPLO
from app.services import validacao
from app.services.validacao import placa_valida, plano_valido, validar_linha, validar_linhas


def _linha_valida(**sobrescritas) -> dict:
    dados = dict(zip(COLUNAS, EXEMPLO))
    dados.update(sobrescritas)
    return dados


@pytest.mark.parametrize("placa", ["ABC1234", "abc1234", "ABC1D23", "  ABC1234  "])
def test_placa_valida_aceita_formato_antigo_e_mercosul(placa):
    assert placa_valida(placa) is True


@pytest.mark.parametrize("placa", ["ABCD123", "AB1234", "1234ABC", "", None, "=CMD('calc')"])
def test_placa_valida_rejeita_formatos_invalidos_e_nao_crasha(placa):
    assert placa_valida(placa) is False


@pytest.fixture
def catalogo_de_teste(monkeypatch):
    catalogo = [
        {"nome": "Plano Leve", "categoria_veiculo": "Carros - Motos", "ativo": True},
        {"nome": "Plano Pesado", "categoria_veiculo": "PESADO - SEM RASTREADOR", "ativo": True},
        {"nome": "Plano Universal", "categoria_veiculo": "Todos", "ativo": True},
        {"nome": "Plano Desativado", "categoria_veiculo": "Carros - Motos", "ativo": False},
    ]
    monkeypatch.setattr(validacao, "PLANOS_VALIDOS", catalogo)
    return catalogo


def test_plano_valido_quando_nome_e_categoria_coincidem(catalogo_de_teste):
    assert plano_valido("Plano Leve", "Carros - Motos") is True


def test_plano_valido_para_categoria_todos(catalogo_de_teste):
    assert plano_valido("Plano Universal", "Utilitário") is True


def test_plano_invalido_quando_categoria_incompativel(catalogo_de_teste):
    assert plano_valido("Plano Pesado", "Carros - Motos") is False


def test_plano_invalido_quando_inativo(catalogo_de_teste):
    assert plano_valido("Plano Desativado", "Carros - Motos") is False


def test_plano_invalido_quando_nao_existe(catalogo_de_teste):
    assert plano_valido("Plano Inexistente", "Carros - Motos") is False


def test_validar_linha_sem_erros_quando_tudo_certo():
    assert validar_linha(_linha_valida()) == []


def test_validar_linha_detecta_campo_obrigatorio_faltando():
    dados = _linha_valida(MARCA=None)
    erros = validar_linha(dados)
    assert any("MARCA" in erro for erro in erros)


def test_validar_linha_detecta_placa_invalida():
    dados = _linha_valida(PLACA="PLACA-INVALIDA")
    erros = validar_linha(dados)
    assert any("Placa" in erro for erro in erros)


def test_validar_linha_detecta_plano_incompativel_com_categoria():
    dados = _linha_valida(NOME_PLANO_1="App Pesado R$30.000", TIPO_VEICULO="Carros - Motos")
    erros = validar_linha(dados)
    assert any("Plano" in erro for erro in erros)


def test_validar_linha_detecta_combustivel_invalido():
    dados = _linha_valida(COMBUSTIVEL="Hibrido")
    erros = validar_linha(dados)
    assert any("COMBUSTIVEL" in erro for erro in erros)


@pytest.mark.parametrize("combustivel", ["flex", "FLEX", " Flex "])
def test_validar_linha_aceita_combustivel_em_qualquer_caixa(combustivel):
    dados = _linha_valida(COMBUSTIVEL=combustivel)
    assert validar_linha(dados) == []


def test_validar_linha_detecta_tipo_siprov_invalido():
    dados = _linha_valida(TIPO_SIPROV="CARRO")
    erros = validar_linha(dados)
    assert any("TIPO_SIPROV" in erro for erro in erros)


def _linhas(quantidade: int) -> list[dict]:
    linhas = []
    for i in range(quantidade):
        dados = _linha_valida(PLACA=f"ABC{1000 + i}"[:7])
        linhas.append({"numero_linha": i + 3, "dados": dados})
    return linhas


def test_validar_linhas_aceita_planilha_sem_erros():
    linhas = _linhas(20)

    aprovadas, com_erro = validar_linhas(linhas)

    assert len(aprovadas) == 20
    assert com_erro == []


def test_validar_linhas_com_20_veiculos_e_2_placas_repetidas():
    linhas = _linhas(20)
    linhas[1]["dados"]["PLACA"] = linhas[0]["dados"]["PLACA"]  # força 2 linhas com a mesma placa

    aprovadas, com_erro = validar_linhas(linhas)

    assert len(com_erro) == 2
    assert len(aprovadas) == 18
    assert all("Placa repetida" in erro for linha in com_erro for erro in linha["erros"])


def test_validar_linhas_300_linhas_em_ate_5_segundos():
    linhas = _linhas(300)

    inicio = time.perf_counter()
    aprovadas, com_erro = validar_linhas(linhas)
    duracao = time.perf_counter() - inicio

    assert len(aprovadas) == 300
    assert com_erro == []
    assert duracao <= 5


def test_validar_linhas_nao_crasha_com_texto_malicioso_na_placa():
    linhas = _linhas(1)
    linhas[0]["dados"]["PLACA"] = "=CMD('calc')"

    aprovadas, com_erro = validar_linhas(linhas)

    assert aprovadas == []
    assert len(com_erro) == 1
    assert any("Placa" in erro for erro in com_erro[0]["erros"])
