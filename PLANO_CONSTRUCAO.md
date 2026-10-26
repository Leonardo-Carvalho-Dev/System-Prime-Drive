# ImportaFrota Prime Drive — Plano de construção (para o Claude Code)

> Coloque este arquivo na raiz do repositório como `PLANO.md` e peça ao Claude Code:
> "Leia PLANO.md e execute a próxima fase não concluída. Ao terminar, marque as caixas e pare para eu revisar."

## 1. Contexto (leia antes de qualquer coisa)

- **O que é:** ferramenta web que cadastra em massa os itens (veículo + plano) de um associado no Siprov, a partir de uma planilha .xlsx. Hoje a equipe cadastra item por item, o que é lento e gera erro.
- **Usuária principal:** Ingrid (suporte da cooperativa Prime Drive). Também usam os consultores (perfil `consultor`).
- **Fluxo (3 telas):** Início (baixar modelo, enviar planilha, últimas importações) → Validar planilha (erros por linha, corrigir na tela, confirmar) → Resultado (incluídos/falhas, reenviar só as falhas, baixar relatório).
- **Projeto acadêmico (CST ADS):** cada fase abaixo gera evidências para a Atividade 3 (repositório, commits, PRs, testes, pipeline, funcionamento, validações). Por isso o **histórico do git importa**: commits pequenos, PRs revisáveis.
- **Referência de design:** o protótipo de 3 telas já existe (HTML/CSS acessível). Reaproveite o visual: cores, foco amarelo de 4px, alvos de 44px, situações com ícone + texto + cor, linguagem em português.

## 2. Regras que valem sempre

1. **Só dados fictícios** nos testes, exemplos e capturas (contrato `CT-TESTE-001`, placas `TST...`). Nunca dados reais de associados.
2. **Segredos fora do código:** chave da API do Siprov, `SECRET_KEY` e senhas só em variáveis de ambiente (`.env` no `.gitignore`, `.env.example` com nomes vazios). Nunca commitar segredos.
3. **Integração com o Siprov isolada** atrás de uma interface (`SiprovClient`). O resto do sistema nunca chama a API direto. Testes usam um cliente falso (`FakeSiprovClient`).
4. **Nunca testar contra contratos reais.** Se houver ambiente de homologação, usar só ele. Sem homologação: o cliente real fica desligado por padrão (`SIPROV_MODE=fake`).
5. **Git:** uma branch por funcionalidade (`feat/...`, `fix/...`, `test/...`), commits no padrão Conventional Commits em português (`feat: valida placa repetida`), **PR para a `main`** com descrição e checklist. Nada direto na `main` depois da fase 0.
6. **Testes primeiro nas regras de negócio** (pytest). Nenhuma fase termina com testes falhando.
7. **Parar ao fim de cada fase** e resumir o que fez, o que testou e o que falta.

## 3. Stack e estrutura

Python 3.12, Flask 3.x, openpyxl 3.1+, SQLite (sqlite3 do Python, consultas parametrizadas), Jinja2 (autoescape ligado), pytest 8.x, pip-audit, Gunicorn + Nginx em produção.

```
importafrota/
  app/
    __init__.py            # create_app()
    config.py              # lê variáveis de ambiente
    auth.py                # login, sessão, decorators de acesso
    routes/                # camada de apresentação (telas)
    services/              # regras de negócio
      planilha.py          # ler/gerar xlsx
      validacao.py         # regras por linha
      importacao.py        # orquestra o fluxo
    data/                  # camada de dados e integração
      db.py, schema.sql
      repositorio.py
      siprov/
        base.py            # interface SiprovClient
        fake.py            # cliente falso (testes e demo)
        real.py            # cliente real (API do Siprov)
    templates/  static/
  tests/
  .github/workflows/ci.yml
  requirements.txt  requirements-dev.txt
  .env.example  .gitignore  README.md  CLAUDE.md  PLANO.md
```

**Dados (SQLite):** `usuario(id_usuario, nome, perfil[suporte|consultor], senha_hash, ativo)`, `importacao(id_importacao, id_usuario, codigo_contrato_siprov, data_hora, total_linhas, situacao[em_validacao|pronta|enviada|parcial|concluida], modo_envio[api|arquivo])`, `linha_importacao(id_linha, id_importacao, numero_linha, placa, plano, situacao[pendente|aprovada|com_erro|incluida|falhou], mensagem_erro)`.

## 4. Requisitos (resumo; numeração oficial da Atividade 2)

| Id | Prioridade | O sistema deve |
|---|---|---|
| RF01 | Obrigatório | Gerar e baixar modelo de planilha em português, colunas na ordem do cadastro do Siprov |
| RF02 | Obrigatório | Receber a planilha + código do contrato e registrar a importação com suas linhas |
| RF03 | Obrigatório | Validar cada linha (obrigatórios, formato da placa, plano válido, placa repetida), mostrar linha + motivo e bloquear o envio com erro |
| RF04 | Obrigatório | Enviar ao Siprov os itens aprovados, só após confirmação, e registrar o resultado de cada item |
| RF05 | Desejável | Relatório final (incluídos, falhas, motivo) com opção de baixar |
| RF06 | Desejável | Reenviar apenas as linhas que falharam, sem duplicar as já incluídas |
| RNF01 | Obrigatório | Autenticação com hash scrypt, sessão assinada (HttpOnly, Secure, SameSite=Lax, 30 min), bloqueio de 15 min após 5 tentativas, mensagem genérica |
| RNF02 | Obrigatório | OWASP Top 10: validação no servidor (.xlsx, 5 MB, 500 linhas), SQL parametrizado, escape no Jinja2, neutralizar células com `=`, `+`, `-`, `@` no relatório, sem detalhe técnico em erros, pip-audit |
| RNF03 | Obrigatório | Página de envio em até 3 s (Fast 3G); validar 300 linhas e mostrar erros em até 5 s |
| RNF04 | Obrigatório | Acessibilidade: contraste 4,5:1, não depender só de cor, uso só por teclado, rótulos, alvos de 44 px, zoom 200%, alertas em região aria-live, Lighthouse ≥ 90 |

**Critérios de aceite (Given/When/Then) para virar testes:**
- *Given* planilha com 20 veículos e 2 placas repetidas; *When* a usuária envia; *Then* a lista mostra as 2 linhas com motivo e o botão Confirmar fica bloqueado.
- *Given* planilha sem erros; *When* a usuária confirma; *Then* todos os itens são enviados e o relatório mostra todos como incluídos.
- *Given* 2 itens falharam no envio; *When* a usuária pede reenvio; *Then* só esses 2 são enviados de novo e os já incluídos não duplicam.
- *Given* usuário sem login; *When* abre uma URL de importação; *Then* é redirecionado ao login.

## 5. Fases (cada uma = uma ou mais PRs; marque ao concluir)

### Fase 0 — Configuração do repositório
- [ ] `git init`, `.gitignore` (Python, `.env`, `*.db`, `.venv`), licença opcional, `README.md` (o que é, como rodar, como testar)
- [ ] `requirements.txt` com versões fixas e `requirements-dev.txt` (pytest, pip-audit)
- [ ] `CLAUDE.md` curto com as regras da seção 2 e comandos (`pytest`, `flask run`)
- [ ] Estrutura de pastas e `create_app()` com rota `/saude` retornando "ok"
- [ ] Proteção da `main` (explicar ao usuário como ligar no GitHub: PR obrigatório, CI verde)
- [ ] Commit inicial na `main`; a partir daqui, tudo por branch + PR

### Fase 1 — Pipeline de integração contínua (CI)
- [ ] `.github/workflows/ci.yml`: em push e PR → Python 3.12, `pip install`, `pytest`, `pip-audit`
- [ ] Um teste mínimo (`/saude`) para o CI ficar verde
- [ ] Badge do CI no README

### Fase 2 — Planilha e validação (RF01, RF03) — núcleo do valor
- [ ] `branch feat/modelo-planilha`: gerar modelo .xlsx (colunas: placa, plano, demais campos exigidos pelo Siprov), com instruções na primeira linha. **Pergunte ao usuário a ordem/colunas reais do cadastro do Siprov.**
- [ ] `branch feat/leitura-planilha`: ler .xlsx com openpyxl (somente leitura), rejeitar tipo/tamanho/linhas fora do limite com mensagem clara
- [ ] `branch feat/validacao-linhas`: regras (obrigatórios, formato de placa antiga e Mercosul, plano na lista de planos, placa repetida na mesma importação); retorna aprovadas e erros com número da linha e motivo
- [ ] Testes (pytest) cobrindo cada regra, o caso das 20 linhas com 2 placas repetidas e a planilha de 300 linhas (tempo ≤ 5 s)
- [ ] Teste de segurança: texto malicioso na placa tratado como texto

### Fase 3 — Dados e autenticação (RF02, RNF01)
- [ ] Schema SQLite e repositório com consultas parametrizadas
- [ ] Usuários `suporte` e `consultor` (script `criar_usuario.py`, senha lida do terminal, nunca no código)
- [ ] Login, logout, sessão de 30 min, bloqueio após 5 falhas, mensagem genérica
- [ ] Decorator de acesso: rota sem login redireciona; importação só do próprio usuário (suporte vê todas)
- [ ] Testes: login válido/inválido, bloqueio na 6ª tentativa, acesso a importação de outro usuário negado, coluna `senha_hash` começa com `scrypt`

### Fase 4 — Telas 1 e 2 (RF02, RF03, RNF04)
- [ ] Layout base com cabeçalho, indicador de passos, link "pular para o conteúdo", foco visível (reaproveitar `style.css` do protótipo)
- [ ] Tela 1: baixar modelo, enviar planilha com código do contrato, últimas importações
- [ ] Tela 2: resumo, alerta (`role="alert"`), tabela com situação (ícone + texto + cor), correção na própria tela (placa, plano), revalidação a cada correção, botão Confirmar desabilitado com dica enquanto houver erro, botão Cancelar
- [ ] Testes de rota (Flask test client) para o fluxo; checar acessibilidade manualmente (teclado, zoom 200%) e com Lighthouse

### Fase 5 — Integração com o Siprov (RF04) — **só com a documentação da API**
- [ ] Interface `SiprovClient` (`criar_item(contrato, placa, plano) -> ResultadoItem`) e `FakeSiprovClient` configurável para simular sucesso e falha
- [ ] **Pare e peça ao usuário** a documentação do endpoint que cria item do titular (autenticação, campos, respostas e erros). Não invente a API.
- [ ] `RealSiprovClient` conforme a documentação, com timeout, tratamento de erro, sem logar segredos; ligado por `SIPROV_MODE=real`
- [ ] Alternativa (plano B, só se a API não permitir): gerar arquivo de importação no formato do Siprov
- [ ] Testes com o cliente falso e com respostas simuladas do cliente real (mock HTTP): sucesso, erro 4xx, timeout, sem resposta

### Fase 6 — Tela 3, relatório e reenvio (RF04, RF05, RF06)
- [ ] Confirmar envio → enviar cada item aprovado, gravar resultado por linha (incluída/falhou + motivo)
- [ ] Tela 3: aviso (`role="status"`), totais, tabela de falhas, botões Reenviar apenas as falhas, Baixar relatório, Nova importação
- [ ] Reenvio sem duplicar (idempotência por linha: só linhas `falhou`)
- [ ] Relatório .xlsx baixável, com células iniciadas por `=`, `+`, `-`, `@` neutralizadas
- [ ] Testes: falha parcial, reenvio só das falhas, relatório sem fórmulas executáveis

### Fase 7 — Segurança e qualidade (RNF02, RNF03)
- [ ] Revisar cada item do mapa OWASP do projeto (injeção SQL, XSS, controle de acesso, autenticação, upload, configuração) e escrever um teste para cada
- [ ] Debug desligado em produção, erros genéricos para o usuário, detalhe só em log interno
- [ ] Medir desempenho (página de envio ≤ 3 s em Fast 3G; validação de 300 linhas ≤ 5 s, mediana de 5 medições) e registrar em tabela
- [ ] `pip-audit` limpo; rodar Lighthouse (acessibilidade ≥ 90) e axe, guardar relatórios

### Fase 8 — Implantação e evidências
- [ ] Passo a passo de implantação no README (Gunicorn + Nginx + HTTPS em instância Linux pequena), backup diário do arquivo SQLite
- [ ] Rodar o fluxo completo com dados fictícios e guardar: prints das 3 telas, saída do `pytest`, CI verde, lista de PRs revisados
- [ ] Preparar roteiro da validação (usar o plano de 3 tarefas e critérios já definidos na Atividade 2)

### Fase 9 — Rodadas de validação e aprimoramento
- [ ] Rodada 1 com a Ingrid (ficha de observação: tempo, ajuda, erros, nota); registrar resultados reais
- [ ] Abrir uma *issue* para cada problema encontrado, priorizar e corrigir em PRs
- [ ] Rodada 2 após os ajustes; comparar com a rodada 1 e aplicar a regra de decisão (Aceito / Aceito com ajustes / Não aceito)

## 6. Definição de pronto (para cada PR)
- Testes novos e antigos passam; CI verde.
- Sem segredos, sem dados reais, sem arquivos `.db` no commit.
- Descrição do PR com: o que mudou, requisito atendido (RF/RNF), como testar.
- Revisão técnica registrada (comentário de revisão ou checklist de auto-revisão), pois a atividade avalia revisão e PRs.

## 7. Perguntas que o Claude Code deve fazer ao usuário (não adivinhar)
1. Quais colunas e qual ordem o cadastro de item do titular tem no Siprov? Quais são os planos válidos?
2. Qual é o endpoint, a autenticação e o formato da resposta da API que cria item do titular? Existe ambiente de homologação ou contrato de teste?
3. Onde será hospedado (instância Linux já existente?) e qual é o repositório no GitHub?
4. Quais usuários iniciais criar (nomes e perfis)? As senhas são digitadas por ele, nunca por você.
