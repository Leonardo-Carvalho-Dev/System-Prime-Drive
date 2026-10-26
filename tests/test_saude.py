def test_saude_retorna_ok(client):
    resposta = client.get("/saude")

    assert resposta.status_code == 200
    assert resposta.data == b"ok"
