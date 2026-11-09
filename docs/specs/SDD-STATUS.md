# MT SGI — SDD-STATUS: Registro de Estado, Evidências e Retomada

| Campo | Valor |
|---|---|
| Produto | MT SGI — MT Sistema de Gestão Integrada |
| Atualizado | 2026-11-08 (America/Fortaleza) |
| Estado deste registro | **snapshot factual da preparação documental — revisar com GitHub antes de continuar** |
| Repositório | https://github.com/magnnwsb2/mt-sgi |
| Branch documental de trabalho | `docs/sdd-fundacao-mt-sgi` |
| Pull Request de revisão | **#1 — https://github.com/magnnwsb2/mt-sgi/pull/1 (DRAFT, ABERTO, NÃO MESCLADO)** |
| Branch de baseline | `main` — não pressupor que a documentação proposta já foi mesclada |
| Release de software | **NENHUMA** |
| Aplicação/API/DB/CI implementados | **NÃO** |
| Baseline SDD global aprovada | **NÃO**; documentos em proposta de revisão |
| ADR-001 | **ACEITA**, decisão arquitetural previamente aprovada |
| ADR-002 | **PROPOSTA**, aguardando escolha expressa |

> Este arquivo registra **fatos verificáveis**, mas não transforma proposta em aprovação. Antes de agir, comparar com PRs, commits, árvore e workflows atuais no GitHub. Se estiver desatualizado, corrigir o status em PR sem reescrever retroativamente o histórico.

## 1. Último trabalho realizado

- O repositório público `magnnwsb2/mt-sgi` foi criado inicialmente com README mínimo e licença MIT.
- O responsável escolheu explicitamente o nome **MT SGI — MT Sistema de Gestão Integrada** para o produto de gestão comercial + PDV.
- O responsável aprovou anteriormente ADR-001: **monólito modular com extração progressiva**, usando custo financeiro zero.
- O responsável determinou que o SDD deve ser **a fonte oficial da verdade**, completo, autossuficiente e apto a permitir uma nova conversa do ChatGPT retomar o projeto sem memória de chats anteriores.
- Foi criada a branch `docs/sdd-fundacao-mt-sgi` para apresentar documentação para revisão, **não** para implementar aplicação.
- Nessa branch foram criados o SDD mestre, anexos de domínios/contratos e tecnologias/segurança/operação, ADR-001 adaptada à marca MT SGI, ADR-002 como proposta e AGENTS.md. O README inicial foi ampliado.
- A proposta não introduz nenhuma API paga, hosting, checkout bancário real ou dados privados. **Nenhuma integração de execução foi testada, porque ainda não há código de aplicação.**
- A documentação foi submetida no **PR #1 em estado DRAFT** para revisão. Seu conteúdo ainda não integra automaticamente `main`; o merge e aprovações de negócio são eventos distintos.

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

**Não** foram criados nem validados: `backend/`, `apps/`, `packages/`, banco PostgreSQL, migrations, containers, Docker Compose, autenticação, PDV, API, relatórios, pagamentos simulados, teste de concorrência, dashboard, GitHub Actions, deploy, hospedagem. A documentação descreve o que construir e como verificar, **não demonstra implementação**.

**Não existe** evidência de que as skills privadas `spec-driven-development` ou `pre-commit-security` foram instaladas ou executadas no GitHub público; diretrizes equivalentes são propostas para a futura CI.

## 5. Bloqueios e riscos imediatos

1. Aprovação explícita da baseline documental (o PR pode ser revisado/mesclado sem aprovar automaticamente regras pendentes; essa distinção deve continuar visível).
2. ADR-002 depende de escolha de transação local, política de idempotência, métodos simulados, troco, caixa e cancelamentos/devoluções.
3. ADR-004 define método de custeio e conversões; sem ela, cálculos finais de CMV/margem seriam arriscados.
4. Stack exata e patches requerem prova de compatibilidade e lockfiles antes do primeiro código.
5. ADR-003/005 e matriz RBAC precisam ser resolvidas antes das partes correspondentes da implementação.

## 6. Próxima ação segura — UM PASSO POR VEZ

**Próxima ação:** revisão da fundação documental e **deliberação da ADR-002** com o responsável, sem implementação de vendas/estoque/caixa.

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
