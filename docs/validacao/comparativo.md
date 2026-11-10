# Comparativo — Rodada 1 × Rodada 2

Participante: Ingrid (atendente do suporte da Prime Drive). Mesma versão do sistema nas
duas rodadas (commit `9532845`) — nenhuma mudança no código entre elas.

| | Rodada 1 (27/10/2026) | Rodada 2 (27/10/2026) |
|---|---|---|
| Tarefa 1 — enviar planilha | Concluída sozinha | Concluída sozinha |
| Tarefa 2 — corrigir erros | Dificuldade média, ajuda nível 1 | Concluída sozinha, sem ajuda |
| Tarefa 3 — ver resultado | Concluída sozinha | Concluída sozinha |
| Nota de satisfação (1–5) | não coletada | 4 |
| Decisão (plano da Experiência Prática 2) | Aceito com ajustes | Aceito |

## Leitura do resultado

A melhora na tarefa 2 da rodada 1 para a rodada 2 reflete familiaridade adquirida pela
participante, não uma mudança no software — as duas rodadas rodaram na mesma versão. A
dificuldade real observada na rodada 1 (encontrar e corrigir a linha com erro) foi o motivo
da correção aplicada depois, no PR #15 (commit `0c25828`, branch `fix/clareza-correcao-erros`):
mensagem de erro de cada linha junto ao formulário de correção, foco automático no primeiro
campo com erro, e o campo Plano virando uma lista com os planos válidos da categoria do
veículo (antes era texto livre, fonte comum de erro de digitação).

## Limite

Uma única participante nas duas rodadas: a evidência é inicial, não permite generalizar
para outros perfis de usuário. A correção do PR #15 ainda não passou por uma nova rodada de
validação com usuária real.
