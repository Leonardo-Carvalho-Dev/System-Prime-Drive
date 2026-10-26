# ImportaFrota Prime Drive

[![CI](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/actions/workflows/ci.yml/badge.svg)](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/actions/workflows/ci.yml)

Ferramenta web que cadastra em massa os itens (veículo + plano) de um associado no Siprov, a partir de uma planilha `.xlsx`. Reduz o trabalho hoje feito item por item pela equipe de suporte da cooperativa Prime Drive.

## Fluxo (3 telas)
1. **Início** — baixar modelo de planilha, enviar planilha preenchida com o código do contrato, ver últimas importações.
2. **Validar planilha** — erros por linha, correção na própria tela, confirmação do envio.
3. **Resultado** — itens incluídos/falhas, reenvio só das falhas, download do relatório.

O plano completo de construção (fases, requisitos, regras) está em [PLANO_CONSTRUCAO.md](PLANO_CONSTRUCAO.md).

## Como rodar
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
flask --app app run
```
Acesse `http://127.0.0.1:5000/saude` — deve responder `ok`.

Crie um usuário (senha digitada no terminal, nunca salva no código):
```bash
python criar_usuario.py ingrid suporte
```
Depois entre em `http://127.0.0.1:5000/login`.

## Como testar
```bash
pytest
pip-audit
python -m scripts.medir_desempenho
```
Resultados de desempenho e acessibilidade (Lighthouse, axe) em [DESEMPENHO.md](DESEMPENHO.md).

## Stack
Python 3.12, Flask 3.x, openpyxl, SQLite, Jinja2, pytest, pip-audit. Produção: Gunicorn + Nginx.
