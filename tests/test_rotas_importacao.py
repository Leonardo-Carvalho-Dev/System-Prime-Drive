from io import BytesIO

from app.data import repositorio


def _logar(client, nome, senha):
    return client.post("/login", data={"nome": nome, "senha": senha})


def _enviar_planilha(client, conteudo, codigo_contrato="CT-TESTE-001", nome_arquivo="planilha.xlsx"):
    return client.post(
        "/",
        data={
            "codigo_contrato": codigo_contrato,
            "planilha": (BytesIO(conteudo), nome_arquivo),
        },
        content_type="multipart/form-data",
    )


def test_inicio_sem_login_redireciona_para_login(client):
    resposta = client.get("/")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_inicio_com_login_mostra_formulario(client, criar_usuario):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = client.get("/")

    assert resposta.status_code == 200
    assert "Cadastro de frota".encode() in resposta.data


def test_baixar_modelo_retorna_xlsx(client, criar_usuario):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = client.get("/modelo.xlsx")

    assert resposta.status_code == 200
    assert "spreadsheetml" in resposta.headers["Content-Type"]


def test_enviar_planilha_sem_erros_cria_importacao_e_vai_para_tela2(app, client, criar_usuario, planilha_sem_erros):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = _enviar_planilha(client, planilha_sem_erros)

    assert resposta.status_code == 302
    assert "/importacoes/" in resposta.headers["Location"]

    resposta_tela2 = client.get(resposta.headers["Location"])
    assert b"Todas as linhas est\xc3\xa3o aprovadas" in resposta_tela2.data


def test_enviar_planilha_com_erro_mostra_erro_na_tela2(client, criar_usuario, planilha_com_erro):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = _enviar_planilha(client, planilha_com_erro)
    resposta_tela2 = client.get(resposta.headers["Location"])

    assert "1 linha(s) precisam de correção".encode() in resposta_tela2.data


def test_consultor_nao_acessa_importacao_de_outro_consultor(app, client, criar_usuario, planilha_sem_erros):
    _, nome_a, senha_a = criar_usuario(nome="joao", perfil="consultor")
    _logar(client, nome_a, senha_a)
    resposta = _enviar_planilha(client, planilha_sem_erros)
    url_importacao = resposta.headers["Location"]
    client.post("/logout")

    _, nome_b, senha_b = criar_usuario(nome="maria", perfil="consultor")
    _logar(client, nome_b, senha_b)

    resposta_negada = client.get(url_importacao)

    assert resposta_negada.status_code == 302
    assert resposta_negada.headers["Location"].endswith("/")


def test_suporte_acessa_importacao_de_qualquer_consultor(app, client, criar_usuario, planilha_sem_erros):
    _, nome_a, senha_a = criar_usuario(nome="joao", perfil="consultor")
    _logar(client, nome_a, senha_a)
    resposta = _enviar_planilha(client, planilha_sem_erros)
    url_importacao = resposta.headers["Location"]
    client.post("/logout")

    _, nome_suporte, senha_suporte = criar_usuario(nome="ingrid", perfil="suporte")
    _logar(client, nome_suporte, senha_suporte)

    resposta_ok = client.get(url_importacao)

    assert resposta_ok.status_code == 200


def test_corrigir_linha_revalida_e_libera_confirmacao(app, client, criar_usuario, planilha_com_erro):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)
    resposta = _enviar_planilha(client, planilha_com_erro)
    id_importacao = int(resposta.headers["Location"].rstrip("/").split("/")[-1])

    with app.app_context():
        linha_com_erro = next(
            linha for linha in repositorio.listar_linhas_importacao(id_importacao) if linha["situacao"] == "com_erro"
        )

    resposta_correcao = client.post(
        f"/importacoes/{id_importacao}/linhas/{linha_com_erro['id_linha']}",
        data={"placa": "ABC9999", "plano": linha_com_erro["plano"]},
    )
    assert resposta_correcao.status_code == 302

    resposta_tela2 = client.get(resposta_correcao.headers["Location"])
    assert b"Todas as linhas est\xc3\xa3o aprovadas" in resposta_tela2.data


def test_confirmar_bloqueado_enquanto_houver_erro(app, client, criar_usuario, planilha_com_erro):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)
    resposta = _enviar_planilha(client, planilha_com_erro)
    id_importacao = int(resposta.headers["Location"].rstrip("/").split("/")[-1])

    client.post(f"/importacoes/{id_importacao}/confirmar")

    with app.app_context():
        importacao = repositorio.obter_importacao_por_id(id_importacao)
    assert importacao["situacao"] == "em_validacao"


def test_confirmar_envia_ao_siprov_e_conclui_sem_erros(app, client, criar_usuario, planilha_sem_erros):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)
    resposta = _enviar_planilha(client, planilha_sem_erros)
    id_importacao = int(resposta.headers["Location"].rstrip("/").split("/")[-1])

    resposta_confirmar = client.post(f"/importacoes/{id_importacao}/confirmar")

    assert f"/importacoes/{id_importacao}/resultado" in resposta_confirmar.headers["Location"]
    with app.app_context():
        importacao = repositorio.obter_importacao_por_id(id_importacao)
        linhas = repositorio.listar_linhas_importacao(id_importacao)
    assert importacao["situacao"] == "concluida"
    assert all(linha["situacao"] == "incluida" for linha in linhas)


def test_tela2_renderiza_select_com_planos_validos(client, criar_usuario, planilha_com_plano_invalido):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = _enviar_planilha(client, planilha_com_plano_invalido)
    resposta_tela2 = client.get(resposta.headers["Location"])
    html = resposta_tela2.data.decode("utf-8")

    assert "<select" in html
    assert '<option value="Plano Prime Drive Completo"' in html
    assert '<option value="Plano Que Não Existe"' not in html


def test_corrigir_com_plano_invalido_continua_rejeitado(app, client, criar_usuario, planilha_com_plano_invalido):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)
    resposta = _enviar_planilha(client, planilha_com_plano_invalido)
    id_importacao = int(resposta.headers["Location"].rstrip("/").split("/")[-1])

    with app.app_context():
        linha = next(
            linha for linha in repositorio.listar_linhas_importacao(id_importacao) if linha["situacao"] == "com_erro"
        )

    client.post(
        f"/importacoes/{id_importacao}/linhas/{linha['id_linha']}",
        data={"placa": linha["placa"], "plano": "Plano Forjado Fora Da Lista"},
    )

    with app.app_context():
        linha_apos = repositorio.obter_linha_importacao(linha["id_linha"])
    assert linha_apos["situacao"] == "com_erro"
    assert "inválido" in linha_apos["mensagem_erro"]


def test_mensagem_de_erro_aparece_na_linha(client, criar_usuario, planilha_com_plano_invalido):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)

    resposta = _enviar_planilha(client, planilha_com_plano_invalido)
    resposta_tela2 = client.get(resposta.headers["Location"])

    html = resposta_tela2.data.decode("utf-8")
    assert '<p class="mensagem-erro-linha">' in html
    assert "Plano inválido" in html


def test_cancelar_exclui_a_importacao(app, client, criar_usuario, planilha_sem_erros):
    _, nome, senha = criar_usuario()
    _logar(client, nome, senha)
    resposta = _enviar_planilha(client, planilha_sem_erros)
    id_importacao = int(resposta.headers["Location"].rstrip("/").split("/")[-1])

    client.post(f"/importacoes/{id_importacao}/cancelar")

    with app.app_context():
        assert repositorio.obter_importacao_por_id(id_importacao) is None
