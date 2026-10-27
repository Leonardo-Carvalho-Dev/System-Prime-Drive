# ImportaFrota Prime Drive

[![CI](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/actions/workflows/ci.yml/badge.svg)](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/actions/workflows/ci.yml)

Ferramenta web que cadastra em massa os itens (veículo + plano) de um associado no Siprov, a partir de uma planilha `.xlsx`. Reduz o trabalho hoje feito item por item pela equipe de suporte da cooperativa Prime Drive.

## Fluxo (3 telas)
1. **Início** — baixar modelo de planilha, enviar planilha preenchida com o código do contrato, ver últimas importações.
2. **Validar planilha** — erros por linha, correção na própria tela, confirmação do envio.
3. **Resultado** — itens incluídos/falhas, reenvio só das falhas, download do relatório.

O plano completo de construção (fases, requisitos, regras) está em [docs/PLANO_CONSTRUCAO.md](docs/PLANO_CONSTRUCAO.md).

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

## Implantação
Passo a passo completo (Gunicorn + Nginx + HTTPS, systemd, backup diário do SQLite) em [DEPLOY.md](DEPLOY.md).

## Validação de usabilidade
Plano de validação com a Ingrid (3 tarefas, critérios de aceite) em [docs/VALIDACAO.md](docs/VALIDACAO.md); material pronto para a sessão em [docs/validacao/](docs/validacao/).

## Stack
Python 3.12, Flask 3.x, openpyxl, requests, SQLite, Jinja2, pytest, pip-audit. Produção: Gunicorn + Nginx.

## Integração contínua
O pipeline de CI (`.github/workflows/ci.yml`) roda `pytest` e `pip-audit` em todo push e PR para a `main`. Os primeiros runs (#1–#13) falhavam por um bug no próprio workflow (`pytest` puro não encontrava o pacote `app` — corrigido no PR [#9](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/9)); desde então o CI passa de verdade em todo PR. Detalhes e evidência em [evidencias/prs-revisados.md](evidencias/prs-revisados.md).

## Transparência sobre o uso de IA

Este sistema foi desenvolvido com o apoio do **Claude Code** (assistente de IA da Anthropic) e do Claude para planejamento e redação. A divisão do trabalho foi:

- **Meu trabalho:** identificação do problema real junto à equipe de suporte da Prime Drive, definição do escopo do MVP, decisões de arquitetura e de produto, revisão e merge de cada Pull Request, teste manual do fluxo completo (incluindo o ensaio da Fase 9), configuração do ambiente local, fornecimento das credenciais e documentos reais do Siprov usados na integração, identificação de dois bugs reais durante os testes (CI quebrado desde o início e `.env` não sendo carregado), escolha de dados fictícios e acompanhamento das rodadas de validação.
- **Apoio da IA:** geração de código e testes a partir do plano de construção (`docs/`), sugestões de estrutura, mensagens de commit e revisão de textos.
- **Responsabilidade:** todo o código foi revisado e testado por mim antes de entrar na `main`, por meio de Pull Requests. Eu respondo pelo conteúdo do repositório.

O uso de dados reais foi evitado: todos os exemplos, testes e capturas usam dados fictícios.
