from io import BytesIO

from openpyxl import Workbook

COLUNAS = [
    "CPF_CNPJ_ASSOCIADO",
    "NUMERO_CONTRATO",
    "PLACA",
    "CHASSI",
    "RENAVAM",
    "MARCA",
    "MODELO",
    "ANO_FABRICACAO",
    "ANO_MODELO",
    "COMBUSTIVEL",
    "TIPO_VEICULO",
    "COR",
    "NOME_PLANO_1",
    "VALOR_PLANO_1",
]

INSTRUCOES = (
    "Preencha uma linha por veículo. Todas as colunas são obrigatórias. "
    "TIPO_VEICULO deve ser uma destas categorias: Carros - Motos, Utilitário, "
    "PESADO - SEM RASTREADOR, PESADO - COM RASTREADOR ou Reboque/SemiReboque. "
    "NOME_PLANO_1 deve ser um plano ativo compatível com o TIPO_VEICULO."
)

EXEMPLO = [
    "000.111.222-33",
    "100",
    "ABC1234",
    "9BWZZZ377VT004251",
    "987654321",
    "Fiat",
    "Uno Fire 1.6",
    2010,
    2010,
    "Flex",
    "Carros - Motos",
    "Prata",
    "Plano Prime Drive Completo",
    7.2,
]


def gerar_modelo() -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Modelo"

    ws.append([INSTRUCOES])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLUNAS))

    ws.append(COLUNAS)
    ws.append(EXEMPLO)

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)
    return arquivo
