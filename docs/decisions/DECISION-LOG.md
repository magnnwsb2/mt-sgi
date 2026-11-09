# MT SGI — Registro de decisões e autorizações (Decision Log)

Este registro documenta **decisões expressas do responsável**, mas não constitui assinatura criptográfica nem identidade de reviewer GitHub. Estados de negócio permanecem no SDD/ADR pertinente. Uma solicitação (SD) somente é atendida após autorização inequívoca e atualização documental rastreável.

| ID | Situação | Assunto | Decisão expressa | Escopo e limite |
|---|---|---|---|---|
| GOV-DEC-001 | **APROVADA — 08/11/2026** | Equipe | 15 agentes, incluindo Merge Guardian | perfis versionados, não 15 processos persistentes |
| GOV-DEC-002 | **APROVADA — 08/11/2026** | Autonomia | uma autorização mestra para execução operacional contínua por sessão | respeitar SDD, bloqueios D1 e proibições X |
| GOV-DEC-003 | **APROVADA — 08/11/2026** | Executor | opção C: **ChatGPT + GitHub** | não requer Ollama, servidor ou API paga; não promete background |
| GOV-DEC-004 | **APROVADA — 08/11/2026** | Integração | merge automatizado após validação pelo Merge Guardian | obrigatório ter proteções e CI nativas verificadas; sem bypass |
| GOV-DEC-005 | **APROVADA — 08/11/2026** | Resiliência | até 3 tentativas por causa; continuar tarefas independentes | registrar tentativas e bloquear localmente após limite |
| GOV-DEC-006 | **APROVADA — 08/11/2026** | Paralelismo | branches isoladas, execução dependente do ambiente e integração serializada | não afirmar agentes paralelos reais na opção C |
| GOV-DEC-007 | **APROVADA — 08/11/2026** | Decisões | modelo híbrido: rotineiras autônomas, ordinárias agrupadas, críticas destacadas na próxima consulta | não inclui notificação push ou decisão implícita |
| GOV-DEC-008 | **APROVADA — 08/11/2026** | Ordem | fases governança → fundação → CI → validação → negócio liberado | novas regras de negócio exigem suas ADRs |
| GOV-DEC-009 | **APROVADA — 08/11/2026** | Início | “Autorização mestra concedida! Pode começar” | implementação das regras aprovadas; **não** muda status de ADR-002 |
| GOV-DEC-010 | **APROVADA — 08/11/2026** | Restrições | custo financeiro adicional zero, SDD prevalece | nenhuma assinatura/API paga, cartão ou segredo real |

## Decisões técnicas e de produto preservadas

- **ADR-001 ACEITA:** monólito modular com extração progressiva; não exige nova aprovação.
- **ADR-002 PROPOSTA:** atomicidade de venda/estoque/caixa e políticas de negócio não foram aprovadas.
- **SDD-001/002/003:** versão global de negócio ainda não aprovada como baseline definitiva.
- **ADR-003/004/005:** pendentes; não antecipar decisão por sugestão de IA.
- **SDD-004 e ADR-006:** aceitas apenas no âmbito de governança de agentes, sem converter propostas de domínio em código obrigatório.

## Solicitações futuras

Criar uma SD usando `docs/decisions/requests/SD-TEMPLATE.md`. Informar risco, escopo, alternativas, dependências e estado. A autorização registrada em chat precisa ser explícita e depois lançada aqui, com link ao registro de decisão/PR e data; a falta de resposta nunca autoriza implementação.

## Limites do registro

A autorização mestra permite fazer commits, branches, PRs, testes, documentação e tarefas dentro da especificação; **não autoriza** desabilitar proteção, fazer merge não verificável, alterar custo zero ou codificar ADR-002 pendente.
