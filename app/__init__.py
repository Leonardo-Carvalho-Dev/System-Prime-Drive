import logging
from datetime import datetime, timedelta

from flask import Flask, render_template

from .config import Config


def formatar_data_br(valor):
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return valor


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.setdefault("DEBUG", False)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    from .data.db import fechar_conexao, inicializar_db

    app.teardown_appcontext(fechar_conexao)
    inicializar_db(app.config["DATABASE_PATH"])

    from .auth import bp as auth_bp
    from .routes.importacao import bp as importacao_bp
    from .routes.saude import bp as saude_bp

    app.register_blueprint(saude_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(importacao_bp)

    app.jinja_env.filters["data_br"] = formatar_data_br

    @app.errorhandler(500)
    def erro_interno(erro):
        app.logger.exception(erro)
        return render_template("erro.html", mensagem="Ocorreu um erro interno. Tente novamente mais tarde."), 500

    @app.errorhandler(404)
    def nao_encontrado(erro):
        return render_template("erro.html", mensagem="Página não encontrada."), 404

    return app
