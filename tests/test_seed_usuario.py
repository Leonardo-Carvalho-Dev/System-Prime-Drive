import tempfile
from pathlib import Path

import pytest
from werkzeug.security import check_password_hash

from app import create_app
from app.config import Config
from app.data import repositorio


def _criar_app(**seed_kwargs):
    arquivo_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    arquivo_db.close()

    class ConfigDeTeste(Config):
        TESTING = True
        SECRET_KEY = "chave-de-teste"
        DATABASE_PATH = arquivo_db.name
        SESSION_COOKIE_SECURE = False
        SEED_USUARIO_NOME = seed_kwargs.get("nome", "")
        SEED_USUARIO_SENHA = seed_kwargs.get("senha", "")
        SEED_USUARIO_PERFIL = seed_kwargs.get("perfil", "suporte")

    aplicativo = create_app(ConfigDeTeste)
    return aplicativo, arquivo_db.name


def test_sem_variaveis_de_seed_nenhum_usuario_e_criado():
    app, caminho_db = _criar_app()
    with app.app_context():
        assert repositorio.obter_usuario_por_nome("demo-avaliador") is None
    Path(caminho_db).unlink(missing_ok=True)


def test_com_variaveis_de_seed_cria_usuario_utilizavel_no_login():
    app, caminho_db = _criar_app(nome="demo-avaliador", senha="senha-fictícia-123", perfil="suporte")
    with app.app_context():
        usuario = repositorio.obter_usuario_por_nome("demo-avaliador")
        assert usuario is not None
        assert usuario["perfil"] == "suporte"
        assert check_password_hash(usuario["senha_hash"], "senha-fictícia-123")

    client = app.test_client()
    resposta = client.post("/login", data={"nome": "demo-avaliador", "senha": "senha-fictícia-123"})
    assert resposta.status_code == 302
    assert "/login" not in resposta.headers["Location"]
    Path(caminho_db).unlink(missing_ok=True)


def test_seed_nao_sobrescreve_usuario_ja_existente():
    arquivo_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    arquivo_db.close()

    class ConfigDeTeste(Config):
        TESTING = True
        SECRET_KEY = "chave-de-teste"
        DATABASE_PATH = arquivo_db.name
        SESSION_COOKIE_SECURE = False
        SEED_USUARIO_NOME = "demo-avaliador"
        SEED_USUARIO_SENHA = "senha-original"
        SEED_USUARIO_PERFIL = "suporte"

    app_primeiro_start = create_app(ConfigDeTeste)
    with app_primeiro_start.app_context():
        usuario = repositorio.obter_usuario_por_nome("demo-avaliador")
        id_original = usuario["id_usuario"]

    class ConfigSegundoStart(ConfigDeTeste):
        SEED_USUARIO_SENHA = "senha-diferente"

    app_segundo_start = create_app(ConfigSegundoStart)
    with app_segundo_start.app_context():
        usuario_apos = repositorio.obter_usuario_por_nome("demo-avaliador")

    assert usuario_apos["id_usuario"] == id_original
    assert check_password_hash(usuario_apos["senha_hash"], "senha-original")
    assert not check_password_hash(usuario_apos["senha_hash"], "senha-diferente")

    Path(arquivo_db.name).unlink(missing_ok=True)


@pytest.mark.parametrize("nome,senha", [("", "senha-qualquer"), ("so-nome", "")])
def test_seed_precisa_de_nome_e_senha_juntos(nome, senha):
    app, caminho_db = _criar_app(nome=nome, senha=senha)
    with app.app_context():
        assert repositorio.obter_usuario_por_nome(nome or "so-nome") is None
    Path(caminho_db).unlink(missing_ok=True)
