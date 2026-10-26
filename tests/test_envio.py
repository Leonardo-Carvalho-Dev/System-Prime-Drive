from io import BytesIO

from app.data import repositorio
from app.data.siprov import FakeSiprovClient
from app.services.importacao import criar_importacao_a_partir_da_planilha, enviar_itens_aprovados
from app.services.relatorio import gerar_relatorio
from app.services.planilha import COLUNAS, EXEMPLO
from conftest import construir_planilha


def _planilha_duas_linhas():
    linha_a = list(EXEMPLO)
    linha_a[COLUNAS.index("PLACA")] = "ABC1234"
    linha_b = list(EXEMPLO)
    linha_b[COLUNAS.index("PLACA")] = "ABC1235"
    return construir_planilha([linha_a, linha_b])


def test_enviar_itens_aprovados_marca_incluida_quando_cliente_tem_sucesso(app, criar_usuario):
    with app.app_context():
        id_usuario, _, _ = criar_usuario()
        usuario = repositorio.obter_usuario_por_id(id_usuario)
        id_importacao = criar_importacao_a_partir_da_planilha(usuario, "42", "p.xlsx", _planilha_duas_linhas())

        enviar_itens_aprovados(id_importacao, FakeSiprovClient())

        linhas = repositorio.listar_linhas_importacao(id_importacao)
        assert all(linha["situacao"] == "incluida" for linha in linhas)
        importacao = repositorio.obter_importacao_por_id(id_importacao)
        assert importacao["situacao"] == "concluida"


def test_enviar_itens_aprovados_com_falha_parcial(app, criar_usuario):
    with app.app_context():
        id_usuario, _, _ = criar_usuario()
        usuario = repositorio.obter_usuario_por_id(id_usuario)
        id_importacao = criar_importacao_a_partir_da_planilha(usuario, "42", "p.xlsx", _planilha_duas_linhas())

        enviar_itens_aprovados(id_importacao, FakeSiprovClient(placas_que_falham={"ABC1234"}))

        linhas = {linha["placa"]: linha["situacao"] for linha in repositorio.listar_linhas_importacao(id_importacao)}
        assert linhas["ABC1234"] == "falhou"
        assert linhas["ABC1235"] == "incluida"
        importacao = repositorio.obter_importacao_por_id(id_importacao)
        assert importacao["situacao"] == "parcial"


def test_reenviar_so_tenta_de_novo_as_linhas_que_falharam(app, criar_usuario):
    with app.app_context():
        id_usuario, _, _ = criar_usuario()
        usuario = repositorio.obter_usuario_por_id(id_usuario)
        id_importacao = criar_importacao_a_partir_da_planilha(usuario, "42", "p.xlsx", _planilha_duas_linhas())

        enviar_itens_aprovados(id_importacao, FakeSiprovClient(placas_que_falham={"ABC1234"}))

        cliente_do_reenvio = FakeSiprovClient()
        enviar_itens_aprovados(id_importacao, cliente_do_reenvio)

        # só a linha que tinha falhado foi reenviada; a já incluída não duplicou
        assert len(cliente_do_reenvio.chamadas) == 1
        assert cliente_do_reenvio.chamadas[0][1]["PLACA"] == "ABC1234"

        linhas = {linha["placa"]: linha["situacao"] for linha in repositorio.listar_linhas_importacao(id_importacao)}
        assert linhas["ABC1234"] == "incluida"
        assert linhas["ABC1235"] == "incluida"
        importacao = repositorio.obter_importacao_por_id(id_importacao)
        assert importacao["situacao"] == "concluida"


def test_gerar_relatorio_neutraliza_formula_na_placa(app, criar_usuario):
    with app.app_context():
        id_usuario, _, _ = criar_usuario()
        usuario = repositorio.obter_usuario_por_id(id_usuario)
        id_importacao = repositorio.criar_importacao(usuario["id_usuario"], "42", "2026-01-01T00:00:00", 1, "api")
        repositorio.criar_linha_importacao(
            id_importacao, 3, "=CMD('calc')", "Plano X", "{}", "falhou", "=HYPERLINK(\"http://malicioso\")"
        )

        import openpyxl

        arquivo = gerar_relatorio(id_importacao)
        wb = openpyxl.load_workbook(arquivo)
        ws = wb.active
        linha = [c.value for c in ws[2]]

        assert linha[1] == "'=CMD('calc')"
        assert linha[4] == "'=HYPERLINK(\"http://malicioso\")"


def test_siprov_falhas_demo_derruba_as_placas_configuradas_no_confirmar():
    import tempfile
    from pathlib import Path

    from app import create_app
    from app.config import Config

    arquivo_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    arquivo_db.close()

    class ConfigComFalhasDemo(Config):
        TESTING = True
        SECRET_KEY = "chave-de-teste"
        DATABASE_PATH = arquivo_db.name
        SESSION_COOKIE_SECURE = False
        SIPROV_FALHAS_DEMO = "ABC1234"

    app = create_app(ConfigComFalhasDemo)
    client = app.test_client()

    with app.app_context():
        from werkzeug.security import generate_password_hash

        from app.data import repositorio

        repositorio.criar_usuario("ingrid", "suporte", generate_password_hash("senha", method="scrypt"))

    client.post("/login", data={"nome": "ingrid", "senha": "senha"})
    conteudo = _planilha_duas_linhas()
    resposta = client.post(
        "/",
        data={"codigo_contrato": "42", "planilha": (BytesIO(conteudo), "p.xlsx")},
        content_type="multipart/form-data",
    )
    id_importacao = resposta.headers["Location"].rstrip("/").split("/")[-1]

    client.post(f"/importacoes/{id_importacao}/confirmar")

    with app.app_context():
        linhas = {linha["placa"]: (linha["situacao"], linha["mensagem_erro"]) for linha in repositorio.listar_linhas_importacao(int(id_importacao))}

    assert linhas["ABC1234"] == ("falhou", "Sem resposta do Siprov.")
    assert linhas["ABC1235"][0] == "incluida"

    Path(arquivo_db.name).unlink(missing_ok=True)


def test_baixar_relatorio_via_rota(client, criar_usuario, planilha_sem_erros):
    _, nome, senha = criar_usuario()
    client.post("/login", data={"nome": nome, "senha": senha})
    resposta_envio = client.post(
        "/",
        data={"codigo_contrato": "42", "planilha": (BytesIO(planilha_sem_erros), "p.xlsx")},
        content_type="multipart/form-data",
    )
    id_importacao = resposta_envio.headers["Location"].rstrip("/").split("/")[-1]
    client.post(f"/importacoes/{id_importacao}/confirmar")

    resposta = client.get(f"/importacoes/{id_importacao}/relatorio.xlsx")

    assert resposta.status_code == 200
    assert "spreadsheetml" in resposta.headers["Content-Type"]
