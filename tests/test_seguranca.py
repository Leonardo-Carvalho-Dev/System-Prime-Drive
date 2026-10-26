from io import BytesIO

from app.services.planilha import COLUNAS, EXEMPLO
from conftest import construir_planilha


def _logar(client, nome, senha):
    return client.post("/login", data={"nome": nome, "senha": senha})


def test_login_com_tentativa_de_injecao_sql_nao_quebra_e_nao_autentica(client, criar_usuario):
    criar_usuario()

    resposta = client.post(
        "/login",
        data={"nome": "' OR '1'='1' --", "senha": "' OR '1'='1' --"},
    )

    assert resposta.status_code == 200  # fica na tela de login, não autentica
    with client.session_transaction() as sessao:
        assert "usuario_id" not in sessao


def test_envio_de_planilha_com_tentativa_de_injecao_sql_no_contrato_nao_quebra(client, criar_usuario, planilha_sem_erros):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = client.post(
        "/",
        data={
            "codigo_contrato": "1; DROP TABLE usuario; --",
            "planilha": (BytesIO(planilha_sem_erros), "p.xlsx"),
        },
        content_type="multipart/form-data",
    )

    assert resposta.status_code == 302  # segue o fluxo normal, sem crashar

    # a tabela usuario continua existindo e intacta
    resposta_login = client.get("/login")
    assert resposta_login.status_code == 200


def test_placa_com_script_e_escapada_na_tela_de_validacao(client, criar_usuario):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    linha = list(EXEMPLO)
    linha[COLUNAS.index("PLACA")] = "<script>alert(1)</script>"
    conteudo = construir_planilha([linha])

    resposta_envio = client.post(
        "/",
        data={"codigo_contrato": "CT-TESTE-001", "planilha": (BytesIO(conteudo), "p.xlsx")},
        content_type="multipart/form-data",
    )
    resposta_tela2 = client.get(resposta_envio.headers["Location"])

    assert b"<script>alert(1)</script>" not in resposta_tela2.data
    assert b"&lt;script&gt;" in resposta_tela2.data


def test_pagina_de_erro_interno_nao_vaza_detalhe_tecnico(app, client):
    @app.route("/_rota_que_quebra_de_proposito")
    def rota_que_quebra():
        raise RuntimeError("detalhe interno sigiloso que não pode aparecer pro usuário")

    app.testing = False
    try:
        resposta = client.get("/_rota_que_quebra_de_proposito")
    finally:
        app.testing = True

    assert resposta.status_code == 500
    assert b"detalhe interno sigiloso" not in resposta.data
    assert "Ocorreu um erro interno".encode() in resposta.data
