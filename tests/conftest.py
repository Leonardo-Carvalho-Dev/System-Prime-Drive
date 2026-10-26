import tempfile
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import Config
from app.data import repositorio


@pytest.fixture
def app():
    arquivo_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    arquivo_db.close()

    class ConfigDeTeste(Config):
        TESTING = True
        SECRET_KEY = "chave-de-teste"
        DATABASE_PATH = arquivo_db.name
        SESSION_COOKIE_SECURE = False

    aplicativo = create_app(ConfigDeTeste)

    yield aplicativo

    Path(arquivo_db.name).unlink(missing_ok=True)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def criar_usuario(app):
    def _criar(nome="ingrid", perfil="suporte", senha="senha-forte-123"):
        with app.app_context():
            senha_hash = generate_password_hash(senha, method="scrypt")
            id_usuario = repositorio.criar_usuario(nome, perfil, senha_hash)
            return id_usuario, nome, senha

    return _criar
