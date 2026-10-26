import argparse
import getpass
import sqlite3
import sys

from werkzeug.security import generate_password_hash

from app import create_app
from app.data import repositorio


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria um usuário do ImportaFrota.")
    parser.add_argument("nome", help="Nome de usuário (login)")
    parser.add_argument("perfil", choices=["suporte", "consultor"])
    args = parser.parse_args()

    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirme a senha: ")
    if senha != confirmacao:
        print("As senhas não coincidem.", file=sys.stderr)
        raise SystemExit(1)

    senha_hash = generate_password_hash(senha, method="scrypt")

    app = create_app()
    with app.app_context():
        try:
            repositorio.criar_usuario(args.nome, args.perfil, senha_hash)
        except sqlite3.IntegrityError:
            print(f"Já existe um usuário chamado '{args.nome}'.", file=sys.stderr)
            raise SystemExit(1)

    print(f"Usuário '{args.nome}' ({args.perfil}) criado com sucesso.")


if __name__ == "__main__":
    main()
