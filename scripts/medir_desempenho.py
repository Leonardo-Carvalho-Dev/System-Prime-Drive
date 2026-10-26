import statistics
import time

from app import create_app
from app.config import Config
from app.services.planilha import COLUNAS, EXEMPLO
from app.services.validacao import validar_linhas


def _linhas(quantidade: int) -> list[dict]:
    linhas = []
    for i in range(quantidade):
        dados = dict(zip(COLUNAS, EXEMPLO))
        dados["PLACA"] = f"ABC{1000 + i}"
        linhas.append({"numero_linha": i + 3, "dados": dados})
    return linhas


def medir_validacao_300_linhas(repeticoes: int = 5) -> list[float]:
    linhas = _linhas(300)
    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        validar_linhas(linhas)
        tempos.append(time.perf_counter() - inicio)
    return tempos


def medir_pagina_de_envio(repeticoes: int = 5) -> list[float]:
    class ConfigDeMedicao(Config):
        TESTING = True
        SECRET_KEY = "chave-de-medicao"
        DATABASE_PATH = "medicao-desempenho.db"
        SESSION_COOKIE_SECURE = False

    app = create_app(ConfigDeMedicao)
    cliente = app.test_client()

    from werkzeug.security import generate_password_hash

    from app.data import repositorio

    with app.app_context():
        if repositorio.obter_usuario_por_nome("medicao") is None:
            repositorio.criar_usuario("medicao", "suporte", generate_password_hash("senha", method="scrypt"))

    cliente.post("/login", data={"nome": "medicao", "senha": "senha"})

    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        cliente.get("/")
        tempos.append(time.perf_counter() - inicio)
    return tempos


def main() -> None:
    print("## Validação de 300 linhas (meta: ≤ 5s)\n")
    tempos_validacao = medir_validacao_300_linhas()
    for i, t in enumerate(tempos_validacao, start=1):
        print(f"- medição {i}: {t:.4f}s")
    print(f"- **mediana: {statistics.median(tempos_validacao):.4f}s**\n")

    print("## Página de envio — GET / (meta: ≤ 3s em Fast 3G)\n")
    tempos_pagina = medir_pagina_de_envio()
    for i, t in enumerate(tempos_pagina, start=1):
        print(f"- medição {i}: {t:.4f}s")
    print(f"- **mediana: {statistics.median(tempos_pagina):.4f}s**")
    print(
        "\n(Medição local via Flask test client, sem rede; a condição Fast 3G foi "
        "medida separadamente com Lighthouse, que simula a rede — ver DESEMPENHO.md.)"
    )


if __name__ == "__main__":
    main()
