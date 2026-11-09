# SD-0003 — Demonstração local e CI sem custo adicional (ADR-003)

| Campo | Valor |
|---|---|
| Estado | **PENDENTE — NÃO É APROVAÇÃO** |
| Repositório/branch/PR | `magnnwsb2/mt-sgi`; `docs/adr-003-005-decision-proposals`; PR empilhado à fundação de agentes, a registrar |
| Solicitante | AGT-001 Orquestrador, AGT-014 DevOps, AGT-013 Segurança |
| Responsável por decidir | Responsável pelo produto |
| Criada em | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — infraestrutura e operação |
| Requisitos/ADRs afetados | SDD-001 §§9,11; SDD-003 §§4,5,9; [ADR-003](../../adr/ADR-003-ambiente-demonstracao-custo-zero.md) PROPOSTA |
| Prioridade | **ORDINÁRIA**, bloqueia configuração de ambiente real |
| Trabalho independente | **SIM:** documentos, CI de governança, testes offline, avaliação de licenças/compatibilidade |

## 1. Problema e contexto

A política financeira aprovada exige custo adicional de R$ 0, sem cartão, créditos promocionais ou serviços obrigatórios faturáveis. Não foi decidido onde demonstrar o backend e a persistência. GitHub Actions executa jobs, mas não é hospedagem permanente de API/PostgreSQL.

## 2. Alternativas

| Alternativa | Benefícios | Riscos/custo | Reversibilidade |
|---|---|---|---|
| A — execução local e CI pública efêmera | ensaios de transação e E2E; pode ser 100% sem novo serviço cobrável | precisa computador e checagem contínua das cotas/termos | alta, remover containers/artefatos locais |
| B — GitHub-only com artefatos estáticos | demonstra código, docs e resultados sem máquina local | não hospeda fluxo transacional persistente | alta |
| C — hospedagem gratuita de terceiros | URL da aplicação | disponibilidade/limites e risco de cartão/faturamento | baixa a média, migração necessária |

## 3. Recomendação técnica

**A**, com **B** apenas para documentação e evidências estáticas; **C** não recomendada sob o limite de custo. Todo recurso futuro exige verificação de preço/limites, sem supor gratuidade ilimitada.

## 4. Impactos

Ambiente de desenvolvimento, banco de teste, CI, versionamento de dependências, backup/restore sintético, exposição local e segurança. Não escolhe stack SDD-003 nem autoriza criar serviços. Custo adicional máximo R$ 0, com interrupção fail-closed se surgir cobrança.

## 5. Pergunta objetiva ao responsável

Aprova a **alternativa A**, com a aplicação executada localmente para demonstração completa e GitHub para código/CI/evidências, sem necessidade de demo backend 24/7 nem infraestrutura cobrável?

## 6. Decisão

- Estado: **PENDENTE**.
- Aprovação textual, escopo, data e referência: **não recebidos**.
- Nenhum runtime, infraestrutura ou contrato alterado por esta SD.

## 7. Retomada

Uma aprovação expressa permite detalhar e testar infraestrutura local **apenas após** confirmar stack, licenças e compatibilidade; ADR-002/004/005 continuam independentes e pendentes. Sem aprovação, continuar documentação e validações offline.
