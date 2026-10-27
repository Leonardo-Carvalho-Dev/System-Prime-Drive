import json

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, send_file, url_for

from ..auth import login_obrigatorio
from ..data import repositorio
from ..data.siprov import obter_cliente
from ..services.importacao import corrigir_linha, criar_importacao_a_partir_da_planilha, enviar_itens_aprovados
from ..services.planilha import PlanilhaInvalida, gerar_modelo
from ..services.relatorio import gerar_relatorio
from ..services.validacao import planos_disponiveis

bp = Blueprint("importacao", __name__)


def _obter_cliente_siprov():
    placas_demo = current_app.config.get("SIPROV_FALHAS_DEMO", "")
    placas_que_falham = {p.strip().upper() for p in placas_demo.split(",") if p.strip()}

    return obter_cliente(
        current_app.config["SIPROV_MODE"],
        usuario=current_app.config["SIPROV_USUARIO"],
        senha=current_app.config["SIPROV_SENHA"],
        cod_loja=current_app.config["SIPROV_COD_LOJA"],
        placas_que_falham=placas_que_falham,
        mensagem_falha="Sem resposta do Siprov." if placas_que_falham else None,
    )


@bp.route("/", methods=["GET", "POST"])
@login_obrigatorio
def inicio():
    if request.method == "POST":
        codigo_contrato = request.form.get("codigo_contrato", "").strip()
        arquivo = request.files.get("planilha")

        if not codigo_contrato:
            flash("Informe o código do contrato.")
        elif not arquivo or not arquivo.filename:
            flash("Selecione uma planilha para enviar.")
        else:
            try:
                id_importacao = criar_importacao_a_partir_da_planilha(
                    g.usuario, codigo_contrato, arquivo.filename, arquivo.read()
                )
            except PlanilhaInvalida as erro:
                flash(str(erro))
            else:
                return redirect(url_for("importacao.validar", id_importacao=id_importacao))

    importacoes_recentes = repositorio.listar_importacoes_recentes(g.usuario)
    return render_template("importacao/tela1.html", importacoes=importacoes_recentes)


@bp.route("/modelo.xlsx")
@login_obrigatorio
def baixar_modelo():
    return send_file(
        gerar_modelo(),
        as_attachment=True,
        download_name="modelo-importacao.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/importacoes/<int:id_importacao>")
@login_obrigatorio
def validar(id_importacao):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    linhas = repositorio.listar_linhas_importacao(id_importacao)
    com_erro = [linha for linha in linhas if linha["situacao"] == "com_erro"]
    aprovadas = [linha for linha in linhas if linha["situacao"] != "com_erro"]

    limite_aprovadas_exibidas = 3
    linhas_exibidas = com_erro + aprovadas[:limite_aprovadas_exibidas]
    linhas_exibidas.sort(key=lambda linha: linha["numero_linha"])
    aprovadas_ocultas = len(aprovadas) - min(len(aprovadas), limite_aprovadas_exibidas)

    linhas_exibidas = [
        {**dict(linha), "planos_disponiveis": planos_disponiveis(json.loads(linha["dados_json"]).get("TIPO_VEICULO"))}
        if linha["situacao"] == "com_erro"
        else dict(linha)
        for linha in linhas_exibidas
    ]

    return render_template(
        "importacao/tela2.html",
        importacao=importacao,
        linhas=linhas_exibidas,
        total_linhas=len(linhas),
        total_com_erro=len(com_erro),
        total_aprovadas=len(aprovadas),
        aprovadas_ocultas=aprovadas_ocultas,
    )


@bp.route("/importacoes/<int:id_importacao>/linhas/<int:id_linha>", methods=["POST"])
@login_obrigatorio
def corrigir(id_importacao, id_linha):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    placa = request.form.get("placa", "")
    plano = request.form.get("plano", "")
    corrigir_linha(id_linha, placa, plano)

    return redirect(url_for("importacao.validar", id_importacao=id_importacao))


@bp.route("/importacoes/<int:id_importacao>/confirmar", methods=["POST"])
@login_obrigatorio
def confirmar(id_importacao):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    if repositorio.contar_linhas_com_erro(id_importacao) > 0:
        flash("Corrija as linhas com erro antes de confirmar.")
        return redirect(url_for("importacao.validar", id_importacao=id_importacao))

    repositorio.atualizar_situacao_importacao(id_importacao, "pronta")
    enviar_itens_aprovados(id_importacao, _obter_cliente_siprov())
    return redirect(url_for("importacao.resultado", id_importacao=id_importacao))


@bp.route("/importacoes/<int:id_importacao>/resultado")
@login_obrigatorio
def resultado(id_importacao):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    linhas = repositorio.listar_linhas_importacao(id_importacao)
    incluidas = [linha for linha in linhas if linha["situacao"] == "incluida"]
    falhas = [linha for linha in linhas if linha["situacao"] == "falhou"]

    return render_template(
        "importacao/tela3.html",
        importacao=importacao,
        total_linhas=len(linhas),
        total_incluidas=len(incluidas),
        falhas=falhas,
    )


@bp.route("/importacoes/<int:id_importacao>/reenviar", methods=["POST"])
@login_obrigatorio
def reenviar(id_importacao):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    enviar_itens_aprovados(id_importacao, _obter_cliente_siprov())
    return redirect(url_for("importacao.resultado", id_importacao=id_importacao))


@bp.route("/importacoes/<int:id_importacao>/relatorio.xlsx")
@login_obrigatorio
def baixar_relatorio(id_importacao):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    return send_file(
        gerar_relatorio(id_importacao),
        as_attachment=True,
        download_name=f"relatorio-importacao-{id_importacao}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/importacoes/<int:id_importacao>/cancelar", methods=["POST"])
@login_obrigatorio
def cancelar(id_importacao):
    importacao = repositorio.obter_importacao_por_id(id_importacao)
    if importacao is None or not repositorio.usuario_pode_acessar_importacao(g.usuario, importacao):
        flash("Importação não encontrada.")
        return redirect(url_for("importacao.inicio"))

    repositorio.excluir_importacao(id_importacao)
    flash("Importação cancelada.")
    return redirect(url_for("importacao.inicio"))
