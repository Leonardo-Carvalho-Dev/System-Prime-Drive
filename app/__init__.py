from datetime import timedelta

from flask import Flask

from .config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    from .data.db import fechar_conexao, inicializar_db

    app.teardown_appcontext(fechar_conexao)
    inicializar_db(app.config["DATABASE_PATH"])

    from .auth import bp as auth_bp
    from .routes.saude import bp as saude_bp

    app.register_blueprint(saude_bp)
    app.register_blueprint(auth_bp)

    return app
