from flask import Flask

from .config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .routes.saude import bp as saude_bp

    app.register_blueprint(saude_bp)

    return app
