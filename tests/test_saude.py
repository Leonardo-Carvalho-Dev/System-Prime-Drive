from app import create_app


def test_saude_retorna_ok():
    app = create_app()
    cliente = app.test_client()

    resposta = cliente.get("/saude")

    assert resposta.status_code == 200
    assert resposta.data == b"ok"
