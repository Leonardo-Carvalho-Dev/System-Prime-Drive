import tempfile
from io import BytesIO
from pathlib import Path

import openpyxl
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import Config
from app.data import repositorio
from app.services.planilha import COLUNAS, EXEMPLO


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


def construir_planilha(linhas: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["instruções"])
    ws.append(COLUNAS)
    for linha in linhas:
        ws.append(linha)
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def planilha_sem_erros() -> bytes:
    linha_a = list(EXEMPLO)
    linha_a[COLUNAS.index("PLACA")] = "ABC1234"
    linha_b = list(EXEMPLO)
    linha_b[COLUNAS.index("PLACA")] = "ABC1235"
    return construir_planilha([linha_a, linha_b])


@pytest.fixture
def planilha_com_erro() -> bytes:
    linha_valida = list(EXEMPLO)
    linha_valida[COLUNAS.index("PLACA")] = "ABC1234"
    linha_invalida = list(EXEMPLO)
    linha_invalida[COLUNAS.index("PLACA")] = "PLACA-INVALIDA"
    return construir_planilha([linha_valida, linha_invalida])
