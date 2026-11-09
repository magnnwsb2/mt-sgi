# SD-0002 — Escolha de consistência transacional do PDV (ADR-002)

| Campo | Valor |
|---|---|
| Estado | **PENDENTE — NÃO AUTORIZA IMPLEMENTAÇÃO** |
| Repositório/branch/PR | `magnnwsb2/mt-sgi`; `docs/adr-003-005-decision-proposals`; PR de propostas a registrar após criação |
| Solicitante | AGT-001 Orquestrador, AGT-003 Arquiteto, AGT-002 Guardião SDD |
| Responsável por decidir | Responsável pelo produto |
| Criada em | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — regras comerciais, transações e contratos |
| Requisitos/ADRs afetados | SDD-001 §§4–6; SDD-002 Sales, Inventory, Payments; [ADR-002](../../adr/ADR-002-consistencia-venda-estoque-caixa.md) PROPOSTA; ADR-001 ACEITA |
| Prioridade | **CRÍTICA** para backend Sales/Inventory/Payments |
| Trabalho independente | **SIM:** governança, docs e testes de contratos sem afirmar regras finais |

## 1. Problema e contexto

Uma venda simulada precisa ser consistente entre venda, baixa de estoque, pagamento simulado, caixa e auditoria. O SDD-001 define metas, mas não aprovou fronteira da transação, política de reserva, troco, devoluções ou retorno idempotente. Criar checkout agora equivaleria a decidir silenciosamente.

## 2. Alternativas e trade-offs

| Alternativa | Benefícios | Riscos/custo | Migração/reversibilidade |
|---|---|---|---|
| A — PostgreSQL ACID local com UnitOfWork compartilhada por portas | atomicidade e reconciliação simples, compatível com ADR-001 e R$ 0 | locking/concorrência requer testes reais; extração futura necessita nova ADR | novos serviços exigirão repensar consistência |
| B — saga entre serviços físicos | desacoplamento físico | múltiplos estados parciais, compensações e infraestrutura desnecessária no MVP | mais custo e dificuldade de teste |
| C — persistências independentes sem coordenação | implementação aparentemente rápida | alto risco de baixa duplicada e caixa inconsistente | difícil reparação de dados |

## 3. Recomendação técnica, não autorização

Recomenda-se A, sem fila/broker obrigatório, associada a idempotência durável, snapshots históricos e consistência no commit. Para permitir um MVP progressivo, recomenda-se deliberar separadamente: nenhuma reserva longa de carrinho; pagamento único simulado por venda inicialmente; dinheiro simulado com troco; caixa exclusivo por terminal/operador; cancelamento integral no MVP e devoluções parciais em fase futura. Todas essas são **propostas**, não decisões.

## 4. Impactos

Módulos Sales, Inventory, Payments & Cash, Audit; modelo SQL/migrations, locks, testes de concorrência, resposta HTTP de reenvio, caixa, relatórios e ADR-004. Nenhum custo adicional e nenhuma transação bancária/fiscal real. Rollback: interromper antes de migrations/implementação e registrar escolha; após dados persistidos exige plano novo.

## 5. Perguntas objetivas ao responsável

**Decisão principal:** aprova a **opção A — transação única ACID local, com interfaces modulares e idempotência persistente**, como regra do MVP?

**Políticas complementares que também exigem resposta antes do respectivo código:** reserva durável ou não; métodos de pagamento simulados únicos/mistos e troco; vínculo caixa/terminal/operador; cancelamento/devolução parcial; tratamento de caixa encerrado; replays e timeout HTTP. Respostas parciais liberam apenas tópicos expressamente decididos.

## 6. Decisão

- Estado: **PENDENTE**.
- Texto exato, data/fuso e referência de autorização: **não recebidos**.
- Arquivos e SHAs de efetivação: **nenhum**.
- Não inferir aceite da autorização operacional dos agentes.

## 7. Retomada

Após resposta explícita, registrar decisão no Decision Log, atualizar ADR-002 e SDDs e abrir tarefas/testes específicos. Até lá, não implementar checkout, estoque transacional nem caixa com política presumida.
