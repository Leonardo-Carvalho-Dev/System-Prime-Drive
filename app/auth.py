import functools
from datetime import datetime, timedelta, timezone

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .data import repositorio

bp = Blueprint("auth", __name__)

LIMITE_TENTATIVAS = 5
DURACAO_BLOQUEIO = timedelta(minutes=15)
MENSAGEM_GENERICA = "Usuário ou senha inválidos."
MENSAGEM_BLOQUEADO = "Conta temporariamente bloqueada. Tente novamente mais tarde."


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _bloqueado(usuario) -> bool:
    if not usuario["bloqueado_até"]:
        return False
    bloqueado_até = datetime.fromisoformat(usuario["bloqueado_até"])
    return _agora() < bloqueado_até


@bp.before_app_request
def carregar_usuario_logado() -> None:
    id_usuario = session.get("usuario_id")
    g.usuario = repositorio.obter_usuario_por_id(id_usuario) if id_usuario else None


@bp.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        nome = request.form.get("nome", "")
        senha = request.form.get("senha", "")
        usuario = repositorio.obter_usuario_por_nome(nome)

        if usuario is not None and _bloqueado(usuario):
            erro = MENSAGEM_BLOQUEADO
        elif usuario is None or not usuario["ativo"] or not check_password_hash(usuario["senha_hash"], senha):
            if usuario is not None and usuario["ativo"]:
                bloqueado_até = (_agora() + DURACAO_BLOQUEIO).isoformat()
                repositorio.registrar_tentativa_falha(usuario["id_usuario"], LIMITE_TENTATIVAS, bloqueado_até)
            erro = MENSAGEM_GENERICA
        else:
            repositorio.limpar_tentativas_falhas(usuario["id_usuario"])
            session.clear()
            session.permanent = True
            session["usuario_id"] = usuario["id_usuario"]
            return redirect(url_for("saude.saude"))

    return render_template("auth/login.html", erro=erro)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


def login_obrigatorio(view):
    @functools.wraps(view)
    def envolvida(**kwargs):
        if g.usuario is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return envolvida
