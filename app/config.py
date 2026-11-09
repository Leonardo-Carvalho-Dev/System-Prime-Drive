import os

from dotenv import load_dotenv

# Carrega o .env da raiz do projeto, se existir. Em produção, o systemd já injeta as
# variáveis via EnvironmentFile; load_dotenv() nunca sobrescreve o que já está no
# ambiente, então é seguro chamar sempre.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    SIPROV_MODE = os.environ.get("SIPROV_MODE", "fake")
    SIPROV_USUARIO = os.environ.get("SIPROV_USUARIO", "")
    SIPROV_SENHA = os.environ.get("SIPROV_SENHA", "")
    SIPROV_COD_LOJA = int(os.environ.get("SIPROV_COD_LOJA") or "0")
    # Só para rodadas de validação de usabilidade (Fase 9): placas que o FakeSiprovClient
    # deve recusar de propósito, para demonstrar a Tela 3 com falhas. Vazio em produção.
    SIPROV_FALHAS_DEMO = os.environ.get("SIPROV_FALHAS_DEMO", "")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "importafrota.db")
    # Desligar só em desenvolvimento local sem HTTPS (nunca em produção).
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
    # Opcional: cria esse usuário no primeiro start se ele ainda não existir (ex.: ambiente
    # de demonstração sem acesso a shell). Vazio por padrão — nenhum usuário é criado.
    SEED_USUARIO_NOME = os.environ.get("SEED_USUARIO_NOME", "")
    SEED_USUARIO_SENHA = os.environ.get("SEED_USUARIO_SENHA", "")
    SEED_USUARIO_PERFIL = os.environ.get("SEED_USUARIO_PERFIL", "suporte")
