# Pull requests revisados e mergeados

Repositório: https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive

| PR | Fase | Título | Status |
|---|---|---|---|
| [#3](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/3) | 1 | Pipeline de CI | Mergeado |
| [#4](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/4) | 2 | Planilha e validação (RF01, RF03) | Mergeado |
| [#5](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/5) | 3 | Dados e autenticação (RF02, RNF01) | Mergeado |
| [#6](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/6) | 4 | Telas 1 e 2 (RF02, RF03, RNF04) | Mergeado |
| [#7](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/7) | 5 | Integração com o Siprov (RF04) | Mergeado |
| [#8](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/8) | 6 | Tela 3, relatório e reenvio (RF04, RF05, RF06) | Mergeado |
| [#9](https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive/pull/9) | 7 | Segurança e qualidade (RNF02, RNF03) + fix do CI | Mergeado |

Cada PR corresponde a uma fase do [PLANO_CONSTRUCAO.md](../PLANO_CONSTRUCAO.md), com commits no padrão Conventional Commits em português e descrição do que mudou, requisito atendido e como testar.

**Nota sobre o CI:** os runs #1–#13 (PRs #3 a #9, incluindo os mesmos PRs listados acima no momento da abertura) falharam por um bug no `ci.yml` (`pytest` puro não enxergava o pacote `app`) — corrigido no próprio PR #9. A partir do run #14 o CI passa de verdade (ver `ci-verde.jpg`).
