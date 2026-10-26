from app.data.siprov import FakeSiprovClient, ResultadoItem, obter_cliente
from app.data.siprov.real import RealSiprovClient


def test_fake_client_tem_sucesso_por_padrao():
    cliente = FakeSiprovClient()

    resultado = cliente.criar_item("CT-TESTE-001", {"PLACA": "ABC1234"})

    assert resultado == ResultadoItem(sucesso=True, mensagem=None, codigo_siprov="FAKE-ABC1234")


def test_fake_client_falha_para_placa_configurada():
    cliente = FakeSiprovClient(placas_que_falham={"ABC1234"})

    resultado = cliente.criar_item("CT-TESTE-001", {"PLACA": "ABC1234"})

    assert resultado.sucesso is False
    assert resultado.mensagem


def test_fake_client_usa_mensagem_de_falha_customizada():
    cliente = FakeSiprovClient(placas_que_falham={"ABC1234"}, mensagem_falha="Sem resposta do Siprov.")

    resultado = cliente.criar_item("CT-TESTE-001", {"PLACA": "ABC1234"})

    assert resultado.mensagem == "Sem resposta do Siprov."


def test_fake_client_com_taxa_de_falha_total_sempre_falha():
    cliente = FakeSiprovClient(taxa_de_falha=1.0)

    resultado = cliente.criar_item("CT-TESTE-001", {"PLACA": "XYZ9999"})

    assert resultado.sucesso is False


def test_fake_client_registra_as_chamadas_feitas():
    cliente = FakeSiprovClient()

    cliente.criar_item("CT-TESTE-001", {"PLACA": "ABC1234"})
    cliente.criar_item("CT-TESTE-001", {"PLACA": "ABC1235"})

    assert len(cliente.chamadas) == 2
    assert cliente.chamadas[0][0] == "CT-TESTE-001"


def test_obter_cliente_modo_fake_retorna_fake_client():
    cliente = obter_cliente("fake")

    assert isinstance(cliente, FakeSiprovClient)


def test_obter_cliente_modo_fake_repassa_placas_e_mensagem_de_falha():
    cliente = obter_cliente("fake", placas_que_falham={"XYZ9999"}, mensagem_falha="Sem resposta do Siprov.")

    resultado = cliente.criar_item("CT-TESTE-001", {"PLACA": "XYZ9999"})

    assert resultado.mensagem == "Sem resposta do Siprov."


def test_obter_cliente_modo_real_retorna_real_client():
    cliente = obter_cliente("real", usuario="u", senha="s", cod_loja=5409)

    assert isinstance(cliente, RealSiprovClient)
    assert cliente.cod_loja == 5409
