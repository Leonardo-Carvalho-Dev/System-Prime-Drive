import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    SIPROV_MODE = os.environ.get("SIPROV_MODE", "fake")
    SIPROV_API_URL = os.environ.get("SIPROV_API_URL", "")
    SIPROV_API_KEY = os.environ.get("SIPROV_API_KEY", "")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "importafrota.db")
