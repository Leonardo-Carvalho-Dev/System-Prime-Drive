from app.auth import LIMITE_TENTATIVAS, MENSAGEM_BLOQUEADO, MENSAGEM_GENERICA
from app.data import repositorio


def test_login_valido_cria_sessao_e_redireciona(client, criar_usuario):
    _, nome, senha = criar_usuario()

    resposta = client.post("/login", data={"nome": nome, "senha": senha})

    assert resposta.status_code == 302
    with client.session_transaction() as sessao:
        assert sessao["usuario_id"] is not None


def test_login_com_senha_errada_mostra_mensagem_generica(client, criar_usuario):
    _, nome, _senha = criar_usuario()

    resposta = client.post("/login", data={"nome": nome, "senha": "senha-errada"})

    assert resposta.status_code == 200
    assert MENSAGEM_GENERICA.encode() in resposta.data


def test_login_com_usuario_inexistente_mostra_a_mesma_mensagem_generica(client):
    resposta = client.post("/login", data={"nome": "ninguem", "senha": "qualquer"})

    assert resposta.status_code == 200
    assert MENSAGEM_GENERICA.encode() in resposta.data


def test_bloqueia_apos_exceder_limite_de_tentativas(app, client, criar_usuario):
    id_usuario, nome, senha = criar_usuario()

    for _ in range(LIMITE_TENTATIVAS):
        client.post("/login", data={"nome": nome, "senha": "senha-errada"})

    resposta = client.post("/login", data={"nome": nome, "senha": senha})

    assert MENSAGEM_BLOQUEADO.encode() in resposta.data
    with app.app_context():
        usuario = repositorio.obter_usuario_por_id(id_usuario)
        assert usuario["bloqueado_até"] is not None


def test_logout_limpa_a_sessao(client, criar_usuario):
    _, nome, senha = criar_usuario()
    client.post("/login", data={"nome": nome, "senha": senha})

    client.post("/logout")

    with client.session_transaction() as sessao:
        assert "usuario_id" not in sessao


def test_senha_hash_usa_scrypt(app, criar_usuario):
    id_usuario, _nome, _senha = criar_usuario()

    with app.app_context():
        usuario = repositorio.obter_usuario_por_id(id_usuario)
        assert usuario["senha_hash"].startswith("scrypt:")


def test_usuario_pode_acessar_importacao_suporte_ve_tudo(app, criar_usuario):
    with app.app_context():
        id_suporte = repositorio.criar_usuario("ingrid", "suporte", "hash")
        id_consultor = repositorio.criar_usuario("joao", "consultor", "hash")
        id_importacao = repositorio.criar_importacao(id_consultor, "CT-TESTE-001", "2026-01-01T10:00:00", 1, "api")

        suporte = repositorio.obter_usuario_por_id(id_suporte)
        importacao = repositorio.obter_importacao_por_id(id_importacao)

        assert repositorio.usuario_pode_acessar_importacao(suporte, importacao) is True


def test_usuario_pode_acessar_importacao_consultor_so_ve_a_propria(app):
    with app.app_context():
        id_consultor_a = repositorio.criar_usuario("joao", "consultor", "hash")
        id_consultor_b = repositorio.criar_usuario("maria", "consultor", "hash")
        id_importacao = repositorio.criar_importacao(id_consultor_a, "CT-TESTE-001", "2026-01-01T10:00:00", 1, "api")

        consultor_b = repositorio.obter_usuario_por_id(id_consultor_b)
        importacao = repositorio.obter_importacao_por_id(id_importacao)

        assert repositorio.usuario_pode_acessar_importacao(consultor_b, importacao) is False


def test_rota_protegida_sem_login_redireciona_para_login(app, client):
    from app.auth import login_obrigatorio

    @app.route("/_rota_de_teste_protegida")
    @login_obrigatorio
    def rota_de_teste_protegida():
        return "ok"

    resposta = client.get("/_rota_de_teste_protegida")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_rota_protegida_com_login_funciona(app, client, criar_usuario):
    from app.auth import login_obrigatorio

    @app.route("/_rota_de_teste_protegida_2")
    @login_obrigatorio
    def rota_de_teste_protegida_2():
        return "ok"

    _, nome, senha = criar_usuario()
    client.post("/login", data={"nome": nome, "senha": senha})

    resposta = client.get("/_rota_de_teste_protegida_2")

    assert resposta.status_code == 200
    assert resposta.data == b"ok"
