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


def listar_importacoes_recentes(usuario: sqlite3.Row, limite: int = 10) -> list[sqlite3.Row]:
    conexao = obter_conexao()
    if usuario["perfil"] == "suporte":
        return conexao.execute(
            "SELECT * FROM importacao ORDER BY data_hora DESC LIMIT ?", (limite,)
        ).fetchall()
    return conexao.execute(
        "SELECT * FROM importacao WHERE id_usuario = ? ORDER BY data_hora DESC LIMIT ?",
        (usuario["id_usuario"], limite),
    ).fetchall()


def atualizar_situacao_importacao(id_importacao: int, situacao: str) -> None:
    conexao = obter_conexao()
    conexao.execute(
        "UPDATE importacao SET situacao = ? WHERE id_importacao = ?", (situacao, id_importacao)
    )
    conexao.commit()


def criar_linha_importacao(
    id_importacao: int,
    numero_linha: int,
    placa: str,
    plano: str,
    dados_json: str,
    situacao: str,
    mensagem_erro: str | None,
) -> int:
    conexao = obter_conexao()
    cursor = conexao.execute(
        """
        INSERT INTO linha_importacao
            (id_importacao, numero_linha, placa, plano, dados_json, situacao, mensagem_erro)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (id_importacao, numero_linha, placa, plano, dados_json, situacao, mensagem_erro),
    )
    conexao.commit()
    return cursor.lastrowid


def listar_linhas_importacao(id_importacao: int) -> list[sqlite3.Row]:
    conexao = obter_conexao()
    return conexao.execute(
        "SELECT * FROM linha_importacao WHERE id_importacao = ? ORDER BY numero_linha",
        (id_importacao,),
    ).fetchall()


def obter_linha_importacao(id_linha: int) -> sqlite3.Row | None:
    conexao = obter_conexao()
    return conexao.execute(
        "SELECT * FROM linha_importacao WHERE id_linha = ?", (id_linha,)
    ).fetchone()


def atualizar_linha_importacao(
    id_linha: int, placa: str, plano: str, dados_json: str, situacao: str, mensagem_erro: str | None
) -> None:
    conexao = obter_conexao()
    conexao.execute(
        """
        UPDATE linha_importacao
        SET placa = ?, plano = ?, dados_json = ?, situacao = ?, mensagem_erro = ?
        WHERE id_linha = ?
        """,
        (placa, plano, dados_json, situacao, mensagem_erro, id_linha),
    )
    conexao.commit()


def atualizar_resultado_envio_linha(id_linha: int, situacao: str, mensagem_erro: str | None) -> None:
    conexao = obter_conexao()
    conexao.execute(
        "UPDATE linha_importacao SET situacao = ?, mensagem_erro = ? WHERE id_linha = ?",
        (situacao, mensagem_erro, id_linha),
    )
    conexao.commit()


def listar_linhas_por_situacao(id_importacao: int, situacoes: tuple[str, ...]) -> list[sqlite3.Row]:
    conexao = obter_conexao()
    marcadores = ",".join("?" for _ in situacoes)
    return conexao.execute(
        f"SELECT * FROM linha_importacao WHERE id_importacao = ? AND situacao IN ({marcadores}) ORDER BY numero_linha",
        (id_importacao, *situacoes),
    ).fetchall()


def contar_linhas_com_erro(id_importacao: int) -> int:
    conexao = obter_conexao()
    linha = conexao.execute(
        "SELECT COUNT(*) AS total FROM linha_importacao WHERE id_importacao = ? AND situacao = 'com_erro'",
        (id_importacao,),
    ).fetchone()
    return linha["total"]


def excluir_importacao(id_importacao: int) -> None:
    conexao = obter_conexao()
    conexao.execute("DELETE FROM linha_importacao WHERE id_importacao = ?", (id_importacao,))
    conexao.execute("DELETE FROM importacao WHERE id_importacao = ?", (id_importacao,))
    conexao.commit()
