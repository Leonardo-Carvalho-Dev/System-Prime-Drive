"""Gera frota-teste.xlsx para a rodada de validação com a Ingrid (Fase 9, docs/VALIDACAO.md).

20 veículos fictícios (placas TST...). Duas linhas propositalmente com erro, para a Tarefa 2:
- linha 7: mesma placa da linha 5 (TST1A23) -> "placa repetida".
- linha 12: plano em branco (placa TST4D56) -> "campo obrigatório".

Uso:
    python -m scripts.gerar_planilha_teste [destino]

Sem argumento, salva em frota-teste.xlsx na Área de Trabalho do usuário atual.
"""

import sys
from pathlib import Path

from app.services.planilha import COLUNAS, gerar_modelo

PLANO_PADRAO = "Plano Prime Drive Completo"
VALOR_PLANO_PADRAO = 7.2
TIPO_VEICULO_PADRAO = "Carros - Motos"
TIPO_SIPROV_PADRAO = "LEVE"
COMBUSTIVEL_PADRAO = "FLEX"

TOTAL_LINHAS = 20
NUMERO_LINHA_DUPLICADA_A = 5
NUMERO_LINHA_DUPLICADA_B = 7
NUMERO_LINHA_PLANO_VAZIO = 12
PLACA_DUPLICADA = "TST1A23"
PLACA_PLANO_VAZIO = "TST4D56"


def _linha_padrao(placa: str, plano: str | None = PLANO_PADRAO) -> list:
    # VALOR_PLANO_1 fica preenchido mesmo quando o plano está em branco: a tela de
    # correção só edita Placa e Plano, então só o nome do plano deve faltar.
    dados = {
        "CPF_CNPJ_ASSOCIADO": "000.111.222-33",
        "NUMERO_CONTRATO": "100",
        "PLACA": placa,
        "CHASSI": "9BWZZZ377VT004251",
        "RENAVAM": "987654321",
        "MARCA": "Fiat",
        "MODELO": "Uno Fire 1.6",
        "ANO_FABRICACAO": 2010,
        "ANO_MODELO": 2010,
        "COMBUSTIVEL": COMBUSTIVEL_PADRAO,
        "TIPO_VEICULO": TIPO_VEICULO_PADRAO,
        "TIPO_SIPROV": TIPO_SIPROV_PADRAO,
        "COR": "Prata",
        "NOME_PLANO_1": plano,
        "VALOR_PLANO_1": VALOR_PLANO_PADRAO,
    }
    return [dados[coluna] for coluna in COLUNAS]


def gerar_linhas() -> list[list]:
    linhas = []
    for i in range(TOTAL_LINHAS):
        numero_linha = i + 3  # linha 1 = instruções, linha 2 = cabeçalho, dados a partir da linha 3

        if numero_linha == NUMERO_LINHA_DUPLICADA_A or numero_linha == NUMERO_LINHA_DUPLICADA_B:
            placa = PLACA_DUPLICADA
            plano = PLANO_PADRAO
        elif numero_linha == NUMERO_LINHA_PLANO_VAZIO:
            placa = PLACA_PLANO_VAZIO
            plano = None
        else:
            placa = f"TST{1000 + numero_linha}"
            plano = PLANO_PADRAO

        linhas.append(_linha_padrao(placa, plano))

    return linhas


def gerar_planilha_teste(destino: Path) -> Path:
    arquivo = gerar_modelo()

    import openpyxl

    wb = openpyxl.load_workbook(arquivo)
    ws = wb.active
    ws.delete_rows(3, ws.max_row - 2)  # tira a linha de exemplo do modelo

    for linha in gerar_linhas():
        ws.append(linha)

    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)
    return destino


def main() -> None:
    if len(sys.argv) > 1:
        destino = Path(sys.argv[1])
    else:
        destino = Path.home() / "Desktop" / "frota-teste.xlsx"

    caminho = gerar_planilha_teste(destino)
    print(f"Planilha de teste gerada em: {caminho}")
    print(
        f"Linhas {NUMERO_LINHA_DUPLICADA_A} e {NUMERO_LINHA_DUPLICADA_B}: placa repetida ({PLACA_DUPLICADA})."
    )
    print(f"Linha {NUMERO_LINHA_PLANO_VAZIO}: plano em branco (placa {PLACA_PLANO_VAZIO}).")


if __name__ == "__main__":
    main()
