import sqlite3

from .db import obter_conexao


def criar_usuario(nome: str, perfil: str, senha_hash: str) -> int:
    conexao = obter_conexao()
    cursor = conexao.execute(
        "INSERT INTO usuario (nome, perfil, senha_hash) VALUES (?, ?, ?)",
        (nome, perfil, senha_hash),
    )
    conexao.commit()
    return cursor.lastrowid


def obter_usuario_por_nome(nome: str) -> sqlite3.Row | None:
    conexao = obter_conexao()
    return conexao.execute("SELECT * FROM usuario WHERE nome = ?", (nome,)).fetchone()


def obter_usuario_por_id(id_usuario: int) -> sqlite3.Row | None:
    conexao = obter_conexao()
    return conexao.execute("SELECT * FROM usuario WHERE id_usuario = ?", (id_usuario,)).fetchone()


def registrar_tentativa_falha(id_usuario: int, limite: int, bloqueado_até: str | None) -> None:
    conexao = obter_conexao()
    conexao.execute(
        """
        UPDATE usuario
        SET tentativas_falhas = tentativas_falhas + 1,
            bloqueado_até = CASE WHEN tentativas_falhas + 1 >= ? THEN ? ELSE bloqueado_até END
        WHERE id_usuario = ?
        """,
        (limite, bloqueado_até, id_usuario),
    )
    conexao.commit()


def limpar_tentativas_falhas(id_usuario: int) -> None:
    conexao = obter_conexao()
    conexao.execute(
        "UPDATE usuario SET tentativas_falhas = 0, bloqueado_até = NULL WHERE id_usuario = ?",
        (id_usuario,),
    )
    conexao.commit()


def criar_importacao(id_usuario: int, codigo_contrato_siprov: str, data_hora: str, total_linhas: int, modo_envio: str) -> int:
    conexao = obter_conexao()
    cursor = conexao.execute(
        """
        INSERT INTO importacao (id_usuario, codigo_contrato_siprov, data_hora, total_linhas, situacao, modo_envio)
        VALUES (?, ?, ?, ?, 'em_validacao', ?)
        """,
        (id_usuario, codigo_contrato_siprov, data_hora, total_linhas, modo_envio),
    )
    conexao.commit()
    return cursor.lastrowid


def obter_importacao_por_id(id_importacao: int) -> sqlite3.Row | None:
    conexao = obter_conexao()
    return conexao.execute(
        "SELECT * FROM importacao WHERE id_importacao = ?", (id_importacao,)
    ).fetchone()


def usuario_pode_acessar_importacao(usuario: sqlite3.Row, importacao: sqlite3.Row) -> bool:
    if usuario is None or importacao is None:
        return False
    return usuario["perfil"] == "suporte" or usuario["id_usuario"] == importacao["id_usuario"]
