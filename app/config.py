import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    SIPROV_MODE = os.environ.get("SIPROV_MODE", "fake")
    SIPROV_USUARIO = os.environ.get("SIPROV_USUARIO", "")
    SIPROV_SENHA = os.environ.get("SIPROV_SENHA", "")
    SIPROV_COD_LOJA = int(os.environ.get("SIPROV_COD_LOJA") or "0")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "importafrota.db")
    # Desligar só em desenvolvimento local sem HTTPS (nunca em produção).
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
