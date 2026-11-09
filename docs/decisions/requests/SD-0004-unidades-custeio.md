# SD-0004 — Unidades de estoque, método de CMV e arredondamento (ADR-004)

| Campo | Valor |
|---|---|
| Estado | **PENDENTE — NÃO É APROVAÇÃO** |
| Repositório/branch/PR | `magnnwsb2/mt-sgi`; `docs/adr-003-005-decision-proposals`; PR empilhado à fundação, a registrar |
| Solicitante | AGT-001 Orquestrador, AGT-003 Arquiteto, AGT-007 Estoque, AGT-010 Relatórios |
| Responsável por decidir | Responsável pelo produto |
| Criada em | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — contratos, unidades, operações e regras financeiras simuladas |
| Requisitos/ADRs | SDD-001 §§5–6; SDD-002 §§1–3,7; [ADR-004](../../adr/ADR-004-unidades-custeio-arredondamento.md) PROPOSTA; ADR-002 PROPOSTA |
| Prioridade | **CRÍTICA** para migração de estoque, preço, compras e CMV |
| Trabalho independente | **SIM:** docs e testes matemáticos sintéticos sem mudar contratos |

## 1. Problema

Não foram aprovadas unidade-base, precisão de conversão, método de custeio/CMV, pools de avaliação e regras de arredondamento. Escolhas implícitas provocariam perdas de centavos, valores de estoque irreconciliáveis ou métricas históricas mutáveis.

## 2. Alternativas

| Alternativa | Benefícios | Riscos/custo | Reversibilidade |
|---|---|---|---|
| A — unidade-base exata + CMP móvel | conversões auditáveis, CMV simples, custo R$ 0 | definir pool de custo e concorrência; histórico/versionamento | migração de custos precisa reconciliação |
| B — unidade-base exata + FIFO por camadas | rastreio de custo por camada | complexidade de saídas e devoluções | migração custosa após histórico |
| C — `float` + custo da compra mais recente | poucas linhas de código | precisão inadequada e CMV inconsistente | difícil recuperar histórico |

## 3. Recomendação técnica

**A**, com fator de conversão versionado, custo histórico por saída, aritmética decimal exata e rejeição de quantidades incompatíveis; sem implementação antes da aprovação da precisão e arredondamento.

## 4. Impactos

Catalog/Procurement/Inventory/Sales/Reporting, snapshots, APIs, migrations, transações de ADR-002, retorno de mercadorias, relatórios. Exige testes de concorrência e propriedade. Custo adicional R$ 0, dinheiro fictício; rollback de documentação antes de migração é simples, após migração requer plano específico.

## 5. Perguntas objetivas ao responsável

1. Aprova **unidade-base por produto e conversão versionada**, com quantidades decimais exatas?
2. Para CMV, aprova **custo médio ponderado móvel** em vez de FIFO? O custo será calculado por produto/loja ou por produto/local de estoque?
3. Qual precisão das unidades `UN/KG/L` e dos custos internos? Qual regra de arredondamento em venda e desconto (metade para cima ou para par; por linha ou documento)?
4. Retornos devem reverter **custo histórico da saída original** e ajustes/transferências devem preservar trilha auditável? Custos acessórios de compra ficam fora do primeiro MVP?

Respostas parciais não liberam tópicos remanescentes.

## 6. Decisão

- Estado: **PENDENTE**.
- Texto exato da autorização, data/fuso e link: **não recebidos**.
- Não promover ADR-004 para ACEITA sem decisão completa do aspecto implementado.

## 7. Retomada

Após decisão, registrar no Decision Log, adequar SDD-001/002/003 e ADR-002, formalizar esquemas/contratos, então criar testes determinísticos para custo/estoque antes de código de domínio.
