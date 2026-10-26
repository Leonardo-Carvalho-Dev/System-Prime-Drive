import json
import re
from collections import Counter
from pathlib import Path

from .planilha import COLUNAS

PLACA_ANTIGA = re.compile(r"^[A-Z]{3}[0-9]{4}$")
PLACA_MERCOSUL = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")

CAMINHO_PLANOS_VALIDOS = Path(__file__).resolve().parent.parent / "data" / "planos_validos.json"


def _carregar_planos_validos() -> list[dict]:
    with open(CAMINHO_PLANOS_VALIDOS, encoding="utf-8") as arquivo:
        return json.load(arquivo)


PLANOS_VALIDOS = _carregar_planos_validos()


def placa_valida(placa) -> bool:
    if not isinstance(placa, str):
        return False
    placa_normalizada = placa.strip().upper()
    return bool(PLACA_ANTIGA.match(placa_normalizada) or PLACA_MERCOSUL.match(placa_normalizada))


def plano_valido(nome_plano, categoria_veiculo) -> bool:
    if not isinstance(nome_plano, str):
        return False
    return any(
        plano["ativo"]
        and plano["nome"] == nome_plano
        and plano["categoria_veiculo"] in (categoria_veiculo, "Todos")
        for plano in PLANOS_VALIDOS
    )


def validar_linha(dados: dict) -> list[str]:
    erros = []

    for campo in COLUNAS:
        valor = dados.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            erros.append(f"O campo {campo} é obrigatório.")

    if erros:
        return erros

    if not placa_valida(dados["PLACA"]):
        erros.append("Placa em formato inválido (use o formato antigo AAA0000 ou Mercosul AAA0A00).")

    if not plano_valido(dados["NOME_PLANO_1"], dados["TIPO_VEICULO"]):
        erros.append("Plano inválido, inativo ou incompatível com o tipo de veículo informado.")

    return erros


def _normalizar_placa(placa) -> str:
    return str(placa).strip().upper() if placa else ""


def validar_linhas(linhas: list[dict]) -> tuple[list[dict], list[dict]]:
    contagem_placas = Counter(
        _normalizar_placa(linha["dados"].get("PLACA")) for linha in linhas if linha["dados"].get("PLACA")
    )

    aprovadas = []
    com_erro = []

    for linha in linhas:
        erros = validar_linha(linha["dados"])

        placa_normalizada = _normalizar_placa(linha["dados"].get("PLACA"))
        if placa_normalizada and contagem_placas[placa_normalizada] > 1:
            erros.append("Placa repetida nesta importação.")

        if erros:
            com_erro.append({**linha, "erros": erros})
        else:
            aprovadas.append(linha)

    return aprovadas, com_erro
