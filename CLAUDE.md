# Regras do projeto ImportaFrota Prime Drive

Plano completo de fases e requisitos: `docs/PLANO_CONSTRUCAO.md`.

## Regras que valem sempre
1. Só dados fictícios em testes, exemplos e capturas (contrato `CT-TESTE-001`, placas `TST...`). Nunca dados reais de associados.
2. Segredos fora do código: chave da API do Siprov, `SECRET_KEY` e senhas só em variáveis de ambiente (`.env` no `.gitignore`, `.env.example` com nomes vazios). Nunca commitar segredos.
3. Integração com o Siprov isolada atrás de uma interface (`SiprovClient`). O resto do sistema nunca chama a API direto. Testes usam um cliente falso (`FakeSiprovClient`).
4. Nunca testar contra contratos reais. Se houver ambiente de homologação, usar só ele. Sem homologação: o cliente real fica desligado por padrão (`SIPROV_MODE=fake`).
5. Git: uma branch por funcionalidade (`feat/...`, `fix/...`, `test/...`), commits no padrão Conventional Commits em português (`feat: valida placa repetida`), PR para a `main` com descrição e checklist. Nada direto na `main` depois da Fase 0.
6. Testes primeiro nas regras de negócio (pytest). Nenhuma fase termina com testes falhando.
7. Parar ao fim de cada fase e resumir o que fez, o que testou e o que falta.

## Comandos
```bash
pip install -r requirements-dev.txt
flask --app app run
pytest
pip-audit
```
