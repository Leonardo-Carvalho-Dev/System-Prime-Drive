from io import BytesIO

from openpyxl import Workbook

from ..data import repositorio
from .planilha import neutralizar_celula

CABECALHO = ["Linha", "Placa", "Plano", "Situação", "Mensagem"]

SITUACOES_LEGIVEIS = {
    "pendente": "Pendente",
    "aprovada": "Aprovada",
    "com_erro": "Com erro",
    "incluida": "Incluída",
    "falhou": "Falhou",
}


def gerar_relatorio(id_importacao: int) -> BytesIO:
    linhas = repositorio.listar_linhas_importacao(id_importacao)

    wb = Workbook()
    ws = wb.active
    ws.title = "Relatório"
    ws.append(CABECALHO)

    for linha in linhas:
        ws.append(
            [
                linha["numero_linha"],
                neutralizar_celula(linha["placa"]),
                neutralizar_celula(linha["plano"]),
                SITUACOES_LEGIVEIS.get(linha["situacao"], linha["situacao"]),
                neutralizar_celula(linha["mensagem_erro"] or ""),
            ]
        )

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)
    return arquivo
