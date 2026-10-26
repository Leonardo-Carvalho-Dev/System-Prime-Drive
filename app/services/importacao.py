import json
from datetime import datetime, timezone

from ..data import repositorio
from .planilha import ler_planilha
from .validacao import validar_linhas


def criar_importacao_a_partir_da_planilha(usuario, codigo_contrato_siprov: str, nome_arquivo: str, conteudo: bytes) -> int:
    linhas = ler_planilha(nome_arquivo, conteudo)
    aprovadas, com_erro = validar_linhas(linhas)

    id_importacao = repositorio.criar_importacao(
        id_usuario=usuario["id_usuario"],
        codigo_contrato_siprov=codigo_contrato_siprov,
        data_hora=datetime.now(timezone.utc).isoformat(),
        total_linhas=len(linhas),
        modo_envio="api",
    )

    erros_por_numero_linha = {linha["numero_linha"]: linha["erros"] for linha in com_erro}

    for linha in linhas:
        erros = erros_por_numero_linha.get(linha["numero_linha"])
        repositorio.criar_linha_importacao(
            id_importacao=id_importacao,
            numero_linha=linha["numero_linha"],
            placa=str(linha["dados"].get("PLACA") or ""),
            plano=str(linha["dados"].get("NOME_PLANO_1") or ""),
            dados_json=json.dumps(linha["dados"], ensure_ascii=False),
            situacao="com_erro" if erros else "aprovada",
            mensagem_erro="; ".join(erros) if erros else None,
        )

    return id_importacao


def revalidar_importacao(id_importacao: int) -> None:
    linhas_salvas = repositorio.listar_linhas_importacao(id_importacao)

    linhas = [
        {"numero_linha": linha["numero_linha"], "dados": json.loads(linha["dados_json"])}
        for linha in linhas_salvas
    ]
    aprovadas, com_erro = validar_linhas(linhas)
    erros_por_numero_linha = {linha["numero_linha"]: linha["erros"] for linha in com_erro}

    for linha_salva in linhas_salvas:
        erros = erros_por_numero_linha.get(linha_salva["numero_linha"])
        dados = json.loads(linha_salva["dados_json"])
        repositorio.atualizar_linha_importacao(
            id_linha=linha_salva["id_linha"],
            placa=str(dados.get("PLACA") or ""),
            plano=str(dados.get("NOME_PLANO_1") or ""),
            dados_json=linha_salva["dados_json"],
            situacao="com_erro" if erros else "aprovada",
            mensagem_erro="; ".join(erros) if erros else None,
        )


def corrigir_linha(id_linha: int, placa: str, nome_plano: str) -> None:
    linha_salva = repositorio.obter_linha_importacao(id_linha)
    dados = json.loads(linha_salva["dados_json"])
    dados["PLACA"] = placa
    dados["NOME_PLANO_1"] = nome_plano

    repositorio.atualizar_linha_importacao(
        id_linha=id_linha,
        placa=placa,
        plano=nome_plano,
        dados_json=json.dumps(dados, ensure_ascii=False),
        situacao=linha_salva["situacao"],
        mensagem_erro=linha_salva["mensagem_erro"],
    )

    revalidar_importacao(linha_salva["id_importacao"])
