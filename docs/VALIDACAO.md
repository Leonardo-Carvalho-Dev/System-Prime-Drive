# Fase 9 — Plano de validação com a Ingrid (fonte: Atividade 2)

> Salve como `docs/VALIDACAO.md` no repositório. O Claude Code deve usar este arquivo para preparar o material das rodadas e, depois, registrar os resultados REAIS que o usuário informar. **Nunca preencha resultados, tempos ou notas por conta própria.**

## 1. O que o Claude Code faz e o que só o usuário faz

| Claude Code (pode fazer) | Usuário (só ele pode fazer) |
|---|---|
| Gerar `frota-teste.xlsx` fictícia (script em `scripts/`) | Conduzir a sessão presencial com a Ingrid |
| Gerar a ficha de observação e o roteiro impresso (arquivos) | Cronometrar, observar e anotar |
| Preparar o ambiente de demonstração com dados fictícios | Pedir e registrar o aceite dela |
| Registrar resultados que o usuário ditar em `docs/validacao/rodada-N.md` | Informar tempos, ajuda, erros e nota |
| Abrir issues, priorizar, corrigir em PRs e rodar testes | Decidir o que corrigir entre as rodadas |

## 2. Preparação (antes da rodada 1)

- [ ] Script `scripts/gerar_planilha_teste.py` que cria `frota-teste.xlsx`: 20 linhas, placas iniciadas por `TST`, planos válidos; **linha 7 com a mesma placa da linha 5** (`TST1A23`) e **linha 12 com plano vazio** (placa `TST4D56`). Nenhum dado real.
- [ ] Ambiente com `SIPROV_MODE=fake` configurado para, no envio, **falhar nas linhas 7 e 12** com a mensagem "Sem resposta do Siprov" (apenas para a Tarefa 3). Nunca usar contrato real.
- [ ] Usuário de teste `suporte` criado (senha digitada pelo usuário) e contrato fictício `CT-TESTE-001`.
- [ ] Gerar `docs/validacao/roteiro-impresso.md` (tarefas da seção 4, sem as metas e sem as respostas) e `docs/validacao/ficha-observacao.md` (seção 6).
- [ ] Teste de ensaio feito pelo próprio usuário (sem a Ingrid) para conferir que o fluxo roda do começo ao fim.

## 3. Método

- **Quem:** Ingrid, atendente do suporte da Prime Drive (representante do público direto). Aceite dela registrado em mensagem antes do teste.
- **Onde e como:** presencial, no escritório, no computador que ela já usa (Chrome, internet normal), sessão individual de 20 minutos, observação lado a lado.
- **Dados:** somente fictícios. Nenhuma informação real de associado aparece.
- **Roteiro da sessão:** apresentação (2 min) → 3 tarefas → nota de satisfação → encerramento com perguntas abertas (3 min).
- **Regras de ajuda:** nível 0 = sem ajuda; nível 1 = dica geral (ex.: "releia a mensagem na tela"); nível 2 = indicar onde olhar. Toda ajuda é anotada. O condutor dá só o objetivo, nunca o passo a passo.
- **Separar observação de opinião:** o que o condutor vê (tempo, erros, ajuda) vai em uma coluna; o que ela comenta vai em outra. Opiniões só são pedidas depois das tarefas.
- **Cronômetro:** inicia quando ela termina de ler a tarefa e para quando o resultado esperado aparece. Pedidos de esclarecimento não interrompem a contagem.
- **Ética:** ela pode parar quando quiser; problemas encontrados são da interface, não dela; só nome e função dela são registrados.

## 4. As três tarefas

### Tarefa 1 — Localizar e iniciar o cadastro de frota por planilha
- **Objetivo para a participante:** "Você precisa cadastrar a frota de um associado que enviou os veículos em planilha. A partir da tela inicial, encontre como obter a planilha modelo, informe o contrato e envie o arquivo para que o sistema comece a verificar os veículos. Fale em voz alta o que está procurando."
- **Estado inicial:** Tela 1 aberta, logada como suporte, sem importação em andamento; `frota-teste.xlsx` na área de trabalho.
- **Dados:** contrato `CT-TESTE-001`; `frota-teste.xlsx` (20 linhas).
- **Resultado esperado:** baixa o modelo (ou diz que o encontrou), digita `CT-TESTE-001`, seleciona o arquivo, envia e chega à Tela 2 com o resumo da importação. **Meta: sem ajuda em até 120 s.**
- **Anotar:** tempo até achar "Baixar modelo" e "Enviar planilha"; hesitações; cliques errados; se entendeu "Código do contrato"; nível de ajuda; falas; dúvida sobre 5 MB / .xlsx.
- **Requisitos:** RF01, RF02, RNF01/RNF02.

### Tarefa 2 — Corrigir os erros da planilha e confirmar o envio (função central)
- **Objetivo:** "O sistema encontrou problemas em algumas linhas da planilha. Entenda quais são, corrija o que for necessário e envie os veículos ao Siprov. Se preferir não enviar, diga o que faria. Fale em voz alta o que está entendendo da tela."
- **Estado inicial:** Tela 2 aberta: 20 lidas, 18 aprovadas, 2 com erro; botão "Confirmar envio ao Siprov" desabilitado.
- **Dados:** linha 7 com placa repetida (`TST1A23`, igual à da linha 5) → correção a digitar: `TST7F89`; linha 12 com plano vazio (`TST4D56`) → escolher "Plano Leves".
- **Resultado esperado:** campos das linhas 7 e 12 corrigidos, as duas passam a "Aprovada", o botão é habilitado e ela confirma, chegando à Tela 3. **Meta: sem ajuda em até 240 s e sem clicar no botão desabilitado mais de uma vez.**
- **Anotar:** se leu o alerta antes de agir; se entendeu cada mensagem de erro; erros de digitação; cliques no botão desabilitado; se viu a dica; se tentou corrigir na planilha em vez de na tela (hipótese a validar); tempo; ajuda; falas.
- **Requisitos:** RF03, RF04, RNF02, RNF04.

### Tarefa 3 — Interpretar o resultado e decidir sobre as falhas
- **Objetivo:** "A importação foi enviada ao Siprov. Diga com suas palavras quantos veículos entraram e quantos não, qual foi o motivo da falha e o que você faria em seguida para resolver. Faça a ação que escolher."
- **Estado inicial:** Tela 3 aberta: "concluída com 2 falhas", totais 20/18/2, tabela dos 2 itens que falharam.
- **Dados:** falhas nas linhas 7 (`TST1A23`) e 12 (`TST4D56`), motivo "Sem resposta do Siprov".
- **Resultado esperado:** diz corretamente 18 entraram e 2 falharam, cita o motivo, e escolhe "Reenviar apenas as 2 falhas" (ou "Baixar relatório" explicando por quê). Descreve o que o ícone e o texto do aviso dizem (não só a cor). **Meta: sem ajuda em até 120 s.**
- **Anotar:** se confundiu 20/18/2; se leu o motivo; ação escolhida; se percebeu o aviso sem ajuda; se pediu algo que não existe; tempo; ajuda; nota final de satisfação.
- **Requisitos:** RF04, RF05, RF06, RNF04.

## 5. Critérios de aceitação e regra de decisão

| Critério | Medida | Aprovado | Atendido com ajustes | Não atendido |
|---|---|---|---|---|
| Usabilidade | Tarefas concluídas sem ajuda (nível 0) e dentro do tempo-meta | 3 de 3 (100%) | 2 de 3 (67%) | menos de 2 de 3 |
| Eficiência | Tempo da Tarefa 2 (metas das tarefas 1 e 3: 120 s cada) | até 240 s | 240–360 s | acima de 360 s ou sem conclusão |
| Satisfação | Pergunta: "Quão fácil foi usar esta ferramenta para cadastrar a frota?" (1 = muito difícil … 5 = muito fácil) | nota 4 ou 5 | nota 3, se os outros dois estiverem aprovados | nota 1 ou 2 |

**Decisão final:**
- **Aceito:** todos aprovados e nenhuma falha crítica.
- **Aceito com ajustes:** 67%, ou Tarefa 2 entre 240 e 360 s, ou nota 3 (com os outros aprovados), sem falha crítica. Corrigir e repetir uma rodada curta.
- **Não aceito:** menos de 2 de 3, ou Tarefa 2 acima de 360 s, ou nota 1–2, ou qualquer falha crítica. Redesenhar antes de avançar.

**Falhas críticas (correção obrigatória):** impossível concluir a função central; perda ou envio errado sem aviso; alerta de erro não percebido ou não lido por leitor de tela; botão desabilitado sem explicação.

**Divergências:** tempo bom mas sem compreensão → vale o critério mais rígido (reprovado). Nota alta com falha de usabilidade → corrigir a falha mesmo assim. Tempo estourado por dúvida pontual já corrigida → repetir a tarefa após o ajuste.

**Limite da evidência:** uma única participante = evidência inicial, sem generalização estatística. Se possível, repetir com uma segunda pessoa do suporte na rodada 2.

## 6. Ficha de observação (modelo para `docs/validacao/rodada-N.md`)

```
Rodada: __    Data: __/__/____    Versão (commit): ________    Participante: Ingrid
Navegador/dispositivo: ________    Aceite registrado em: __/__/____

| Tarefa | Concluiu (S/N) | Tempo (s) | Meta (s) | Erros/cliques sem efeito | Ajuda (0/1/2) | Observações do condutor | Falas da participante |
|---|---|---|---|---|---|---|---|
| 1 |  |  | 120 |  |  |  |  |
| 2 |  |  | 240 |  |  |  |  |
| 3 |  |  | 120 |  |  |  |  |

Taxa de sucesso: __ de 3        Nota de satisfação (1–5): __    Motivo da nota (opinião): ________
Falhas críticas: ________
Decisão (Aceito / Aceito com ajustes / Não aceito): ________
Problemas encontrados → issue #: ________
Mudanças feitas depois (PRs): ________
```

## 7. Depois de cada rodada (o que o Claude Code faz)

1. Registrar a ficha com os dados que o usuário informar, sem alterar números.
2. Abrir uma *issue* por problema (título curto, evidência da ficha, tela afetada, requisito, severidade: crítica / alta / média / baixa).
3. Propor correções em ordem de severidade; cada uma em branch + PR + teste.
4. Antes da rodada 2: atualizar o ambiente, rodar toda a suíte de testes e o CI.
5. Após a rodada 2: montar em `docs/validacao/comparativo.md` a tabela rodada 1 × rodada 2 (tempo, ajuda, nota, decisão) e o que mudou no produto entre elas.
