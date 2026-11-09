# MT SGI — SDD-STATUS: Registro de Estado, Evidências e Retomada

| Campo | Valor |
|---|---|
| Produto | MT SGI — MT Sistema de Gestão Integrada |
| Atualizado | 2026-11-08 (America/Fortaleza) |
| Estado deste registro | **snapshot da governança de agentes em implementação — conferir CI/PRs em tempo real** |
| Repositório | https://github.com/magnnwsb2/mt-sgi |
| Branch documental de trabalho | `docs/sdd-fundacao-mt-sgi` (PR #1, base de proposta) |
| Branch dos agentes | `feat/agent-governance-foundation` (derivada da branch documental) |
| Pull Request consolidado | **#2 — https://github.com/magnnwsb2/mt-sgi/pull/2 (BASE main, NÃO MESCLADO; aguardando proteção/automerge)** |
| Pull Request documental anterior | **#1 — https://github.com/magnnwsb2/mt-sgi/pull/1 (FECHADO COMO SUBSTITUÍDO, SEM MERGE)** |
| Branch de baseline | `main` — não pressupor que a documentação proposta já foi mesclada |
| Release de software | **NENHUMA** |
| Aplicação/API/DB/CI implementados | **NÃO** |
| Baseline SDD global aprovada | **NÃO**; documentos em proposta de revisão |
| ADR-001 | **ACEITA**, decisão arquitetural previamente aprovada |
| ADR-002 | **PROPOSTA**, aguardando escolha expressa |
| SDD-004 / ADR-006 | **APROVADAS PARA GOVERNANÇA** (não para regras de negócio) |
| Agentes versionados | **15 arquivos em agents/** na branch de feature; não são executores persistentes |
| Gate de governança | **CI VALIDADA NO PR #2**: 14 testes PASS; run https://github.com/magnnwsb2/mt-sgi/actions/runs/42546296223 |
| GitHub auto-merge | **DESABILITADO** (allow_auto_merge=false); main `protected=false`; impedimento Issue #3 |

> Este arquivo registra **fatos verificáveis**, mas não transforma proposta em aprovação. Antes de agir, comparar com PRs, commits, árvore e workflows atuais no GitHub. Se estiver desatualizado, corrigir o status em PR sem reescrever retroativamente o histórico.

## 1. Último trabalho realizado

- O repositório público `magnnwsb2/mt-sgi` foi criado inicialmente com README mínimo e licença MIT.
- O responsável escolheu explicitamente o nome **MT SGI — MT Sistema de Gestão Integrada** para o produto de gestão comercial + PDV.
- O responsável aprovou anteriormente ADR-001: **monólito modular com extração progressiva**, usando custo financeiro zero.
- O responsável determinou que o SDD deve ser **a fonte oficial da verdade**, completo, autossuficiente e apto a permitir uma nova conversa do ChatGPT retomar o projeto sem memória de chats anteriores.
- Foi criada a branch `docs/sdd-fundacao-mt-sgi` para apresentar documentação para revisão, **não** para implementar aplicação.
- Nessa branch foram criados o SDD mestre, anexos de domínios/contratos e tecnologias/segurança/operação, ADR-001 adaptada à marca MT SGI, ADR-002 como proposta e AGENTS.md. O README inicial foi ampliado.
- A proposta não introduz nenhuma API paga, hosting, checkout bancário real ou dados privados. **Nenhuma integração de execução foi testada, porque ainda não há código de aplicação.**
- A documentação foi inicialmente submetida no PR #1 (histórico), depois integralmente consolidada no PR #2 contra `main`; o PR #1 foi **fechado sem merge como substituído**. Ainda não existe integração à `main`; merge e aprovação de negócio são eventos distintos.

## 2. Registro das entregas documentais

| Caminho | Commit inicial na branch | Estado de conteúdo |
|---|---|---|
| `docs/specs/SDD-001.md` | `c40e471a87281a33b6d76ee8c745d8bae85e59be` | Proposta v0.3.0: mestre, hierarquia, retomada, escopo, decisões |
| `docs/specs/SDD-002-dominios-contratos.md` | `1fa8617a25b3063f4556768d2aadff2eed258202` | Proposta v0.1.0: domínios, dados, REST/eventos, métricas, cenários |
| `docs/specs/SDD-003-tecnologias-operacao.md` | `deba735684e1c11eb9a677f47c9f64d9a1722828` | Proposta v0.1.0: stack, versões, manutenção, CI, segurança e custo |
| `docs/adr/ADR-001-arquitetura-modular-extracao-progressiva.md` | `da17e82f676c39e1a4a2b9c87eb86198fbf0bd7d` | **Decisão ACEITA**; critérios de implementação pendentes |
| `docs/adr/ADR-002-consistencia-venda-estoque-caixa.md` | `391ac1c93d2c85a69655e1f8cd0265037ae76588` | **PROPOSTA**, não aprovada |
| `AGENTS.md` | `59b95bd60dfba0b419938e3495699d262604fd55` | protocolo de agentes e continuidade |
| `README.md` | `79bf39facd2be7f85e1544393dd98751c741c115` | visão pública vinculada ao SDD |
| `docs/specs/SDD-STATUS.md` | commit de criação deste arquivo | snapshot do trabalho/documentação |

Esses SHAs identificam **commits iniciais de cada arquivo** na branch, não SHA do conteúdo atual nem aprovação de merge. O commit da branch e o estado do PR devem ser consultados no GitHub a cada reinício.

### 2.1 Verificação documental efetuada nesta preparação

- Conferidos diretamente na branch os **oito arquivos alterados** do PR #1 e a presença de seus conteúdos; total de aproximadamente **1.581 linhas de Markdown** (contagem sujeita a futuras revisões).
- Conferidas as referências internas do README para AGENTS, SDD, STATUS e ADRs; a licença MIT referenciada já existe na branch `main`.
- Conferido que ADR-001 está marcada ACEITA e ADR-002 está marcada PROPOSTA; não foi executado teste de aplicação, contrato, desempenho ou scanner de segurança.
- Esta verificação é **estática/documental manual**, sem workflow automatizado de CI; seu resultado não pode ser rotulado como validação de software.

## 3. Decisões — matriz de autorização

| ID | Item | Estado | Regras para continuar |
|---|---|---|---|
| DEC-001 | Nome MT SGI e objetivo gestão comercial/PDV | **APROVADO** | usar nomenclatura MT SGI, não RetailFlow |
| DEC-002 | Custo zero e dados sintéticos | **APROVADO** | não adicionar custo/API paga/cartão/trial |
| DEC-003 | SDD como fonte da verdade e handoff independente | **APROVADO** | seguir AGENTS/SDD em qualquer conversa |
| DEC-004 | Monólito modular com futura extração progressiva | **APROVADO (ADR-001)** | preservar ownership e limites, sem microserviços físicos no MVP |
| DEC-005 | Atomicidade de venda/estoque/caixa | **PENDENTE (ADR-002)** | escolher alternativa e regras de negócio |
| DEC-006 | Demo local, GitHub e política operacional R$ 0 | **PENDENTE (ADR-003)** | formalizar evidência antes de infraestrutura |
| DEC-007 | Unidades, custo, margem, troco/rounding | **PENDENTE (ADR-004)** | não implementar cálculos definitivos |
| DEC-008 | Admin/PDV frontend e sessão | **PENDENTE (ADR-005)** | não assumir deploy/topologia |
| DEC-009 | Python/FastAPI/React/Node/Postgres | **PROPOSTO** | testar compatibilidade e obter aceite da baseline |
| DEC-010 | APIs, SQL, domínio e eventos | **PROPOSTOS** | contratos e schemas finais dependem de decisões |

## 4. O que NÃO foi feito

**Não** foram criados nem validados: `backend/`, `apps/`, `packages/`, banco PostgreSQL, migrations, containers, Docker Compose, autenticação, PDV, API, relatórios, pagamentos simulados, teste de concorrência, dashboard, deploy, hospedagem. **Exceção documental/CI:** workflow GitHub Actions de governança, validador Python e testes de governança já foram adicionados na branch de agentes, ainda sujeitos a execução e checagem dos jobs. A documentação descreve o que construir e como verificar, **não demonstra implementação**.

**Não existe** evidência de que as skills privadas `spec-driven-development` ou `pre-commit-security` foram instaladas ou executadas no GitHub público; diretrizes equivalentes são propostas para a futura CI.

## 5. Bloqueios e riscos imediatos

1. Aprovação explícita da baseline documental (o PR pode ser revisado/mesclado sem aprovar automaticamente regras pendentes; essa distinção deve continuar visível).
2. ADR-002 depende de escolha de transação local, política de idempotência, métodos simulados, troco, caixa e cancelamentos/devoluções.
3. ADR-004 define método de custeio e conversões; sem ela, cálculos finais de CMV/margem seriam arriscados.
4. Stack exata e patches requerem prova de compatibilidade e lockfiles antes do primeiro código.
5. ADR-003/005 e matriz RBAC precisam ser resolvidas antes das partes correspondentes da implementação.

## 6. Próxima ação segura — UM PASSO POR VEZ

**Próxima ação imediata (bloqueio externo identificado):** habilitar em GitHub UI a proteção real de `main`, checks obrigatórios e auto-merge, conforme Issue #3; então reavaliar PR #2 com o Merge Guardian. Enquanto isso, agentes podem desenvolver tarefas de governança independentes, mas **não podem mesclar**. **Próxima decisão de negócio:** deliberar ADR-002; não implementar vendas/estoque/caixa antecipadamente.

Sugestão técnica submetida à decisão: transação única PostgreSQL ACID dentro do monólito modular, com UnitOfWork compartilhada por portas, idempotência durável, bloqueio de concorrência, movimentos imutáveis e outbox se houver consumidor. **Não considerar essa sugestão aprovada.**

**Após aprovação ADR-002:** atualizar seu estado para ACEITA com data/justificativa, ajustar SDD-001/002/003 e SDD-STATUS, documentar políticas abertas e continuar apenas para a próxima ADR necessária (custo/unidades/UI), sem “pular” para código.

## 7. Procedimento para uma conversa nova

1. Abrir o repo e verificar o **conteúdo de `main` e PRs pendentes**.
2. Ler `AGENTS.md` e o SDD inteiro conforme ordem do SDD-001.
3. Conferir cada decisão contra documentação e merge; não supor que branch de proposta está em `main`.
4. Checar se este status mudou no GitHub, substituindo esta fotografia por informação mais recente.
5. Perguntar apenas decisões ainda pendentes e materialmente bloqueadoras; não repetir questões já respondidas.
6. Se sem autorização para modificar, produzir proposta revisável; se houver autorização, criar branch/PR rastreável.
7. Encerrar com novos commits/PRs, evidências de validação e próxima ação neste arquivo.

**Comando de retomada:** “No GitHub magnnwsb2/mt-sgi, leia primeiro AGENTS.md, SDD-001, SDD-002, SDD-003 e SDD-STATUS, depois ADR-001/002. Verifique branch/PR/CI; mantenha o SDD como fonte de verdade, o custo R$ 0 e siga a próxima etapa aprovada.”

## 8. Marco GOV — autorização mestra, agentes e integração (08/11/2026)

**Autorizações expressas, documentadas em SDD-004/ADR-006/Decision Log:** 15 perfis (oito domínios, seis transversais e Merge Guardian), opção C (ChatGPT conectado ao GitHub), execução operacional autônoma **durante a sessão** até limites e bloqueios, decisões híbridas, três correções por causa, branches isoladas e merge automatizado **apenas após verificação de CI, proteção nativa e revisão independente**. Não foi aprovada a ADR-002.

**Artefatos adicionados à branch `feat/agent-governance-foundation`:**
- `docs/specs/SDD-004-agentes-autonomia.md`, commit `55ed65a20e013d0a68c2c1887d42fc0e4db88a90`, formaliza a governança operacional aprovada;
- **15 arquivos `agents/*.md`**, commit `c6b252a3df29d625e1272a7c8146ba5782485636`, especializados por contexto;
- `docs/adr/ADR-006-agentes-autonomia-merge.md`, `docs/decisions/DECISION-LOG.md`, modelo SD, contrato de tarefa, runbook, Merge Guardian e integração com AGENTS/SDD-001/README, commit `8268e69debd77aeb633a640dd5175bf128523324`;
- `scripts/validate_governance.py`, `tests/test_governance.py`, `.github/workflows/governance.yml`, template PR, commit `42cfc3d0a96866674b641384ca12e50bff324b14`; correção de regex por commit `33b33fbcd80b8d96eccfd4b71fe6094c25168a9c`.

**PR consolidado:** `#2` foi redirecionado diretamente à `main` (inclui a fundação SDD inicial do PR #1 + todos os agentes/CI); **não integrado**. O PR #1 foi fechado como substituído, **sem merge**; nenhum merge realizado. O PR #4 foi criado para teste negativo, teve CI FAIL como esperado e foi fechado sem merge.

**Restrição verificada:** `allow_auto_merge=false`, `main.protected=false` e `main.protection.enabled=false` no GitHub; GET /rulesets retornou lista vazia e GET detalhado de branch protection resultou **403 por limitação da integração**. Merge Guardian em **BLOQUEADO PARA MERGE**. Issue administrativa [#3](https://github.com/magnnwsb2/mt-sgi/issues/3) contém instruções de configuração única na UI. Não usar `merge_pull_request` como atalho.

**Próximas atividades seguras e autorizadas:** conferir CI estrutural em PR #2; corrigir falhas comprovadas; inspecionar se há regras nativas; documentar o ajuste administrativo necessário se a conexão não puder fazê-lo; testar cenário negativo no validador; atualizar este status com links dos jobs. Com proteção remota confirmada e requisitos aceitos, um PR poderá receber automerge. A discussão da ADR-002 permanece pendente para qualquer lógica de checkout.

## 9. Evidências verificadas — CI positiva e negativa

**Execução positiva:** [GitHub Actions run 42546296223](https://github.com/magnnwsb2/mt-sgi/actions/runs/42546296223) no PR #2 direcionado a `main`, commit `c460d6066fd345359bde8c5bd7704ec19846b54a`, estado COMPLETED e conclusão SUCCESS. A execução imediatamente anterior [42546022222](https://github.com/magnnwsb2/mt-sgi/actions/runs/42546022222) comprovou explicitamente nos logs: `MT SGI GOVERNANCE: PASS — 15 perfis` e **14 testes em Python passando** (`Ran 14 tests`, `OK`). A execução posterior confirma o gate contra `main`; verificar logs específicos da nova execução em caso de dúvida. Um run cancelado no meio de atualização de PR não é sucesso e não substitui o run subsequente aprovado.

**Execução negativa deliberada:** branch isolada `test/governance-negative-proof`, commit de teste `23f659be280d1ba13ea02c41403d1ef0b0356e8a`, PR [#4](https://github.com/magnnwsb2/mt-sgi/pull/4). Uma seção obrigatória de `agents/qa-agent.md` foi propositalmente renomeada. [Run 42546520146](https://github.com/magnnwsb2/mt-sgi/actions/runs/42546520146) foi COMPLETED/FAILURE; erro literal: `Seção obrigatória ausente em agents/qa-agent.md: ## 6. Plano de implementação e critérios de aceite`. O PR #4 foi **fechado sem merge**, e a ref da branch de teste foi devolvida ao commit válido da feature por force-with-lease; a violação não foi integrada.

**Conclusão estritamente limitada:** demonstrou-se que o gate determinístico aceita o estado documentado válido e rejeita a violação sintética. **Ainda não foi demonstrado** que a proteção remota impede um usuário admin de efetuar merge, que existe reviewer independente de identidade, ou que auto-merge está habilitado. Nenhuma dessas evidências pode ser inferida de um resultado PASS em Actions.

**Bloqueio administrativo:** [Issue #3](https://github.com/magnnwsb2/mt-sgi/issues/3). Até a configuração da `main` ser concluída e confirmada, não fazer merge de #2 ou qualquer outra PR. A autorização mestra permanece válida para o trabalho operacional autorizado não bloqueado. SDD-002/003 e ADR-002 mantêm seus estados de proposta, sem implementação do domínio.

## 10. Auditoria de retomada — 09/11/2026

- Branch `feat/agent-governance-foundation`, PR #2 aberto contra `main`; consulta via GitHub conectado.
- Inventário SDD-004: 15 perfis canônicos localizados e inspecionados; `agents/audit.md` era um perfil abreviado redundante, não canônico. Removido no commit `e4dfadb1b222d11c76ba7c20d0753d8f1b9d29bd`; `agents/audit-agent.md` preservado.
- `docs/agents/AGENT-GOVERNANCE.md` permanece como documentação transversal, não como décimo sexto agente.
- `allow_auto_merge=false` confirmado por metadados do repositório. Issue #3 aberta; proteção nativa da `main` ainda requer verificação/configuração administrativa. Merge Guardian: **BLOQUEADO**; nenhum merge executado.
- CI: os 14 testes PASS e o teste negativo documentados são evidências históricas; **não foram reexecutados nem validados para o commit de remoção nesta sessão**. Checks do novo head: NÃO VERIFICADOS.
- Decisões: ADR-001 e ADR-006 aceitas; SDD-004 aprovado apenas para governança; ADR-002 proposta; ADR-003/004/005 e baseline global pendentes. Nenhum módulo comercial implementado nesta retomada.
- Próxima ação: conferir execução de CI no novo SHA, revisar diff do PR #2 e aplicar controles de proteção/required checks da `main` antes de qualquer merge. Custo adicional observado nesta tarefa: R$ 0.
