from io import BytesIO

import openpyxl
import pytest

from app.services.planilha import (
    COLUNAS,
    LINHAS_MAXIMAS,
    EXEMPLO,
    PlanilhaInvalida,
    gerar_modelo,
    ler_planilha,
)


def _planilha_com_linhas(linhas: list[list]) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["instruções"])
    ws.append(COLUNAS)
    for linha in linhas:
        ws.append(linha)
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def test_ler_planilha_rejeita_extensao_errada():
    with pytest.raises(PlanilhaInvalida):
        ler_planilha("planilha.csv", b"qualquer coisa")


def test_ler_planilha_rejeita_arquivo_maior_que_5mb():
    conteudo = b"0" * (5 * 1024 * 1024 + 1)
    with pytest.raises(PlanilhaInvalida):
        ler_planilha("planilha.xlsx", conteudo)


def test_ler_planilha_rejeita_cabecalho_fora_do_modelo():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["instruções"])
    ws.append(["qualquer", "coisa"])
    buffer = BytesIO()
    wb.save(buffer)

    with pytest.raises(PlanilhaInvalida):
        ler_planilha("planilha.xlsx", buffer.getvalue())


def test_ler_planilha_rejeita_mais_de_500_linhas():
    linhas = [EXEMPLO for _ in range(LINHAS_MAXIMAS + 1)]
    conteudo = _planilha_com_linhas(linhas)
    with pytest.raises(PlanilhaInvalida):
        ler_planilha("planilha.xlsx", conteudo)


def test_ler_planilha_devolve_linhas_com_numero_e_dados():
    conteudo = gerar_modelo().getvalue()

    linhas = ler_planilha("modelo.xlsx", conteudo)

    assert len(linhas) == 1
    assert linhas[0]["numero_linha"] == 3
    assert linhas[0]["dados"]["PLACA"] == "ABC1234"


def test_ler_planilha_ignora_linhas_totalmente_vazias():
    conteudo = _planilha_com_linhas([EXEMPLO, [None] * len(COLUNAS), EXEMPLO])

    linhas = ler_planilha("planilha.xlsx", conteudo)

    assert len(linhas) == 2


def test_ler_planilha_nao_executa_texto_malicioso_na_placa():
    linha = list(EXEMPLO)
    indice_placa = COLUNAS.index("PLACA")
    linha[indice_placa] = "=CMD('calc')"
    conteudo = _planilha_com_linhas([linha])

    linhas = ler_planilha("planilha.xlsx", conteudo)

    # a leitura não avalia fórmulas: ou devolve o texto literal, ou None
    # (quando não há valor em cache), nunca executa nada.
    assert linhas[0]["dados"]["PLACA"] in ("=CMD('calc')", None)
