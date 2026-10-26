from flask import Blueprint

bp = Blueprint("saude", __name__)


@bp.route("/saude")
def saude():
    return "ok"
