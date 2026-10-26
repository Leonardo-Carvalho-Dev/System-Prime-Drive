# Desempenho e acessibilidade (RNF03, RNF04)

Medido em 2026-10-26, ambiente local (`flask run`, SQLite, sem otimizações de produção).

## Validação de 300 linhas (meta: ≤ 5s)

5 medições com `python -m scripts.medir_desempenho` (`validar_linhas()` sobre 300 linhas aprovadas):

| Medição | Tempo (s) |
|---|---|
| 1 | 0,0025 |
| 2 | 0,0022 |
| 3 | 0,0028 |
| 4 | 0,0041 |
| 5 | 0,0027 |
| **Mediana** | **0,0027** |

Bem abaixo da meta de 5s.

## Página de envio (meta: ≤ 3s em Fast 3G)

Medido de duas formas:

1. **Local** (Flask test client, sem rede) — mediana de 0,0016s nas 5 medições do mesmo script. Serve só para detectar regressão de código, não representa rede real.
2. **Lighthouse** (`npx lighthouse`, throttling simulado de rede/CPU — aproxima Fast 3G/mobile):

| Página | Performance | LCP |
|---|---|---|
| `/login` | 100 | — |
| `/` (Tela 1 — envio) | 100 | 908 ms |
| `/importacoes/<id>` (Tela 2) | 100 | — |
| `/importacoes/<id>/resultado` (Tela 3) | 100 | — |

LCP (Largest Contentful Paint) de 908 ms na Tela 1, bem abaixo do limite de 3s.

## Acessibilidade (meta: Lighthouse ≥ 90)

| Página | Lighthouse Accessibility | axe-core (violações) |
|---|---|---|
| `/login` | 100 | 0 |
| `/` (Tela 1) | 100 | 0 |
| `/importacoes/<id>` (Tela 2) | 100 | 0 |
| `/importacoes/<id>/resultado` (Tela 3) | 100 | 0 |

O axe-core encontrou 1 violação moderada na primeira rodada (`region`: o rodapé não estava dentro de uma landmark) — corrigido envolvendo o rodapé em `<footer>` (`app/templates/base.html`). Depois da correção, 0 violações em todas as páginas.

## Como reproduzir

```bash
# desempenho
python -m scripts.medir_desempenho

# Lighthouse (com o servidor rodando em :5000 e um cookie de sessão válido)
npx lighthouse http://localhost:5000/ --only-categories=performance,accessibility --throttling-method=simulate

# axe-core (no console do navegador, com a página aberta)
# cole o conteúdo de https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js e rode: await axe.run()
```
