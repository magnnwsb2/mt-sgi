# MT SGI — MT Sistema de Gestão Integrada

**Plataforma de gestão comercial e ponto de venda (PDV)** para comércio geral, construída sob **Spec-Driven Development (SDD)**, arquitetura modular e compromisso de **custo financeiro zero** na fase de desenvolvimento e demonstração.

> **Estado atual (09/11/2026):** fundação SDD e governança em revisão no [PR #2](https://github.com/magnnwsb2/mt-sgi/pull/2), ainda não mesclado à `main`. **O workflow de CI da governança existe e executou 14 testes com sucesso no commit `ce2d3237cb7e8a77c102c78c507e564339952e9a`** ([evidência](https://github.com/magnnwsb2/mt-sgi/actions/runs/42572182538)); isso não comprova proteção da `main`. **Não há aplicação comercial, API, banco migrado ou PDV implementados, nem funcionalidades de negócio validadas.** ADR-001 aceita; ADR-002 proposta; stack de produto pendente.

## Fonte única da verdade

O projeto **não depende de contexto de conversas do ChatGPT**. Qualquer pessoa ou agente deve iniciar pela documentação versionada abaixo, verificando branch, commits, PRs e evidência real:

1. [AGENTS.md](AGENTS.md) — protocolo de retomada, hierarquia documental e segurança.
2. [SDD-001 — Especificação Mestra](docs/specs/SDD-001.md) — autoridade normativa, escopo, arquitetura, prioridades e aceites.
3. [SDD-002 — Domínios, Regras, Contratos e Dados](docs/specs/SDD-002-dominios-contratos.md).
4. [SDD-003 — Tecnologias, Operação, Segurança e Qualidade](docs/specs/SDD-003-tecnologias-operacao.md).
5. [SDD-004 — Governança operacional dos agentes (APROVADA)](docs/specs/SDD-004-agentes-autonomia.md).
6. [SDD-STATUS — Estado real e Handoff](docs/specs/SDD-STATUS.md).
7. [ADR-001 — Monólito modular e extração progressiva (ACEITA)](docs/adr/ADR-001-arquitetura-modular-extracao-progressiva.md).
8. [ADR-002 — Consistência de venda/estoque/caixa (PROPOSTA)]
9. [ADR-006 — Governança e merge condicionado (ACEITA)](docs/adr/ADR-006-agentes-autonomia-merge.md).(docs/adr/ADR-002-consistencia-venda-estoque-caixa.md).

**Regra:** propostas não são decisões aprovadas; documentação não prova implementação; PR aberto não significa que o conteúdo já integra `main`. Havendo divergência, seguir a constituição documental do SDD-001 e registrar o conflito.

## O que o produto pretende entregar

- Identidade, perfis, permissões e auditoria.
- Catálogo de produtos, SKU, unidades, embalagens e histórico de preços.
- Fornecedores, compras, pedidos e recebimentos.
- Inventário com movimentos rastreáveis e controle de concorrência.
- PDV com venda idempotente, comprovante não fiscal e pagamentos **simulados**.
- Abertura, movimentação, fechamento e reconciliação de caixa.
- Cancelamentos/devoluções auditáveis, com regras a deliberar.
- Relatórios, CMV, margem bruta, histórico e exportação para um futuro **Business Decision Intelligence**, que será um produto separado.

**Fora do escopo MVP:** uso comercial real, dados pessoais reais, NFC-e/NF-e, TEF, liquidação de pagamentos, conexão bancária, SaaS 24/7, APIs ou hospedagem pagas.

## Arquitetura e tecnologias

**Aprovado:** monorepo com **monólito modular inicial** (um backend) e oito domínios com contratos/ownership claros, preparado para extração de serviços **somente se necessária**.

**Stack candidata, sujeita a validação e aceite:** Python 3.14, FastAPI/Pydantic 2, SQLAlchemy 2/Alembic, PostgreSQL 18, TypeScript strict, React/Vite, Node 26 LTS, pytest/Playwright, Docker Compose, GitHub Actions e documentação Markdown. Veja SDD-003 para justificativas, versões, riscos, alternativas, licenças, segurança e manutenção. Não há aplicação disponível para instalação neste estágio.

## Como contribuir com segurança

Antes de alterar arquivos, consulte `AGENTS.md` e a versão de SDD na branch correta. Toda mudança deve referenciar requisito/ADR e atualizar SDD se houver novo comportamento; não incluir segredos, dados comerciais reais ou dependências pagas. Para mudanças estruturais, trabalhe em branch/PR e não faça merge presumindo aprovação de decisões pendentes.

## Retomada do projeto em qualquer ChatGPT

Copie esta instrução para uma nova conversa:

> “Acesse https://github.com/magnnwsb2/mt-sgi. Leia AGENTS.md, SDD-001, SDD-002, SDD-003, SDD-STATUS e todas as ADRs relevantes. Verifique o que já está realmente no GitHub e os testes de CI. O SDD é a fonte oficial da verdade; diferencie propostas de aprovações e código de testes; siga apenas a próxima etapa autorizada sem custo financeiro.”

## Licença

[MIT](LICENSE). O licenciamento do projeto não substitui análise das licenças de dependências futuras.

## Agentes de engenharia — fundação em desenvolvimento

O repositório adota governança de **15 papéis de agentes**, com SDD como fonte normativa, execução por sessões do ChatGPT conectado ao GitHub e autorização operacional controlada. Arquivos de agentes não são processos persistentes ou IAs paralelas.

- [SDD-004 — governança de agentes](docs/specs/SDD-004-agentes-autonomia.md)
- [Inventário dos 15 perfis](agents/README.md)
- [ADR-006 — ChatGPT/GitHub e merge protegido](docs/adr/ADR-006-agentes-autonomia-merge.md)
- [Runbook de execução](docs/agents/RUNBOOK.md)
- [Protocolo do Merge Guardian](docs/operations/MERGE-GUARDIAN.md)
- [Decision Log e aprovações](docs/decisions/DECISION-LOG.md)

**Atenção:** criação de arquivos, CI e ativação real de auto-merge são marcos separados. Consulte SDD-STATUS e os checks/PRs do GitHub antes de afirmar implementação ou aprovação.
