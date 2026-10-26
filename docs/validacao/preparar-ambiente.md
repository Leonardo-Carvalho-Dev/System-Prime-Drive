# Preparar o ambiente para a sessão (ou para o ensaio)

## 1. Gerar a planilha de teste

```bash
python -m scripts.gerar_planilha_teste
```
Sem argumento, salva `frota-teste.xlsx` na Área de Trabalho. Para outro destino (por
exemplo, direto no computador da Ingrid):
```bash
python -m scripts.gerar_planilha_teste "C:\caminho\frota-teste.xlsx"
```

## 2. Criar o usuário de teste

```bash
python criar_usuario.py suporte suporte
```
(Digite uma senha só para o teste — nunca a senha real de ninguém.)

## 3. Configurar o `.env` para a Tarefa 3 falhar nas linhas certas

No `.env` usado nessa sessão (nunca em produção):
```
SIPROV_MODE=fake
SIPROV_FALHAS_DEMO=TST7F89,TST4D56
```
`TST7F89` é a placa corrigida da linha 7 (era `TST1A23`, repetida); `TST4D56` é a
placa da linha 12. Com isso, ao confirmar o envio na Tarefa 2, essas duas placas
falham com a mensagem "Sem resposta do Siprov." — criando o cenário da Tarefa 3
(18 incluídos, 2 falhas). **Apague essas duas linhas do `.env` depois da rodada.**

## 4. Rodar o sistema

```bash
flask --app app run
```
Acesse `http://127.0.0.1:5000/login`, entre com o usuário `suporte` e o contrato
fictício `CT-TESTE-001`.

## 5. Conferido tecnicamente (pelo Claude, em 2026-10-26)

Rodei o fluxo completo (upload de `frota-teste.xlsx`, correção das linhas 7 e 12,
confirmação, envio com as 2 falhas configuradas) via requisições diretas à aplicação,
sem navegador. Resultado: 20 linhas lidas → 18 aprovadas / 2 com erro → depois da
correção, 20 aprovadas → depois de confirmar, 18 incluídas / 2 falhas com a mensagem
"Sem resposta do Siprov.". Bate exatamente com o estado inicial descrito para as
Tarefas 1, 2 e 3 em `docs/VALIDACAO.md`.

**Isso não substitui o "teste de ensaio" que o `docs/VALIDACAO.md` pede do usuário**
(seção 2, último item) — ele continua sendo feito por você, sem a Ingrid, no navegador
de verdade, para confirmar que a experiência também funciona na prática antes da
sessão real.
