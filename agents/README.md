# MT SGI — Diretório de agentes (15 perfis)

**Importante:** arquivos Markdown aqui são **instruções versionadas**, não processos residentes, contas de usuário, workers, bots automaticamente instanciados ou garantia de 15 IAs concorrentes. A opção aprovada é ChatGPT + GitHub; para cada tarefa, o executor deve seguir as instruções do perfil pertinente.

## Fonte de verdade

1. `AGENTS.md` orienta o bootstrap.
2. `docs/specs/SDD-001.md` tem precedência e referencia os demais anexos.
3. `docs/specs/SDD-004-agentes-autonomia.md` registra autorização operacional e governança.
4. ADRs ACEITAS definem arquitetura/negócio; ADRs PROPOSTAS não autorizam código.
5. `docs/specs/SDD-STATUS.md` informa evidências e retomada, mas deve ser conferido contra o GitHub.
6. Este diretório detalha os **papéis especializados**, subordinados à constituição.

## Inventário e gatilhos

| ID | Perfil | Quando selecionar |
|---|---|---|
| AGT-001 | [Orquestrador](orchestrator.md) | iniciar/retomar planejamento, dependências e ciclo de tarefas |
| AGT-002 | [Guardião do SDD](sdd-guardian.md) | validar rastreabilidade, estados e decisão |
| AGT-003 | [Arquiteto](architect.md) | verificar fronteiras e contratos |
| AGT-004 | [Identidade e Acesso](identity-agent.md) | FUN-001, autenticação e RBAC |
| AGT-005 | [Catálogo](catalog-agent.md) | FUN-002/003 e preço |
| AGT-006 | [Compras](procurement-agent.md) | FUN-004 e recebimento |
| AGT-007 | [Estoque](inventory-agent.md) | FUN-005, ledger e concorrência |
| AGT-008 | [Vendas/PDV](sales-agent.md) | FUN-006/009, checkout idempotente |
| AGT-009 | [Pagamentos e Caixa](payments-cash-agent.md) | FUN-007/008, caixa fictício |
| AGT-010 | [Relatórios](reporting-agent.md) | FUN-010/012, dicionário/exportação |
| AGT-011 | [Auditoria](audit-agent.md) | FUN-011 e integridade |
| AGT-012 | [QA e Testes](qa-agent.md) | casos de aceite, testes e resultados |
| AGT-013 | [Segurança](security-agent.md) | credenciais, IAM, threat model e revisão |
| AGT-014 | [DevOps](devops-agent.md) | CI, build, reprodutibilidade e custo |
| AGT-015 | [Merge Guardian](merge-guardian.md) | gates de aprovação de PR e bloqueios |

## Ativação lógica

O ChatGPT não precisa criar 15 chats. O orquestrador lê o inventário, assume um papel, confere o contrato e as dependências, trabalha e produz evidências. Pode delegar ferramentas disponíveis quando houver suporte explícito, mas **não deve fingir paralelismo ou background**. Nenhum perfil consegue conceder acesso extra ao GitHub.

## Procedimento

Consultar `docs/agents/RUNBOOK.md` e o modelo `docs/agents/TASK-CONTRACT.md`. Um Merge Guardian que apenas escreve “aprovado” **não** é check obrigatório de GitHub nem revisão por usuário independente. As regras nativas da branch precisam estar configuradas e verificadas antes de habilitar auto-merge.
