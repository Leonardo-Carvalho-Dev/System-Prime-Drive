import sqlite3
from pathlib import Path

from flask import current_app, g

CAMINHO_SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def obter_conexao() -> sqlite3.Connection:
    if "conexao_db" not in g:
        g.conexao_db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.conexao_db.row_factory = sqlite3.Row
    return g.conexao_db


def fechar_conexao(excecao=None) -> None:
    conexao = g.pop("conexao_db", None)
    if conexao is not None:
        conexao.close()


def inicializar_db(caminho_banco: str) -> None:
    conexao = sqlite3.connect(caminho_banco)
    try:
        conexao.executescript(CAMINHO_SCHEMA.read_text(encoding="utf-8"))
        conexao.commit()
    finally:
        conexao.close()
