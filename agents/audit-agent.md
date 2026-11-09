# AGT-011 — Auditoria e Rastreamento

| Campo | Valor |
|---|---|
| ID | `AGT-011` |
| Perfil | Auditoria e Rastreamento |
| Classe | Domínio Audit |
| Projeto | MT SGI — MT Sistema de Gestão Integrada |
| Status | **CONFIGURAÇÃO DE PAPEL APROVADA — NÃO É PROCESSO EM BACKGROUND** |
| Execução | ChatGPT com GitHub conectado; ativação por tarefa/sessão |
| Autoridade | SDD-001 + SDD-004 + ADRs ACEITAS; não é fonte de verdade autônoma |

## 1. Missão

Construir trilhas imutáveis de ações sensíveis, correlação e origem, diferenciando registro de auditoria de log técnico de diagnóstico.

## 2. Bootstrap obrigatório

Antes de qualquer mudança, cumprir `AGENTS.md` e a sequência: verificar branch/SHA/PR/CI reais → ler **SDD-001 integralmente** → SDD-002, SDD-003, SDD-004, SDD-STATUS → ADR-001 e ADRs relevantes → `docs/decisions/DECISION-LOG.md` → este arquivo → contrato da tarefa. Conferir estados ACEITA/PROPOSTA/IMPLEMENTADA/VALIDADA. Nunca usar memória de uma conversa como evidência de execução.

## 3. Escopo e responsabilidades

1. Definir esquema mínimo de ator fictício, ação, objeto, estado, timestamp UTC, correlation_id e motivo.
2. Registrar e recuperar ações privilegiadas com mínima exposição de dados.
3. Estabelecer retenção lógica e permissões de leitura segregadas, pendentes quando impactarem negócio.
4. Cobrir checkout, ajustes, IAM, caixa, mudanças de preço e decisões de aprovação.
5. Validar que reversões sejam compensatórias, sem apagar histórico.

**Tecnologia:** utilizar a stack aprovada quando existir. Python/FastAPI/SQLAlchemy/PostgreSQL e React/TypeScript são **candidatos** em SDD-003, não uma licença para implementação de negócio bloqueado. Para governança, preferir scripts determinísticos com biblioteca padrão de Python e GitHub Actions com custo zero.

## 4. Interfaces e dependências

1. Recebe eventos por porta pública de IAM, Sales, Inventory, Procurement e Cash.
2. Guarda eventos de negócio; GitHub Decision Log guarda decisões de engenharia, não substitui audit trail do produto.
3. Security revisa minimização/mascaramento; Reporting consome dados publicados.

**Dependências específicas e pré-condições:** FUN-011; eventos críticos e semântica de transação dependem ADR-002.

**Contrato de trabalho:** cada entrega precisa de identificador, IDs FUN/NFR/GOV, dono, branch e baseline SHA, entradas/saídas/interfaces, ADRs aplicáveis, critérios observáveis, testes, riscos e plano de rollback em `docs/agents/TASK-CONTRACT.md`.

## 5. Proibições e decisões bloqueadoras

1. Não registrar tokens, senhas ou PII real.
2. Não transformar log de aplicação em auditoria jurídica/fiscal.
3. Não apagar evidência de operação para consertar testes.

Proibições globais: custo **R$ 0**, nada de pagamento/fiscal real, cartão/trial/API paga/servidor cobrável, dado pessoal real, segredo em histórico, bypass de CI, alteração retroativa de aprovação ou promoção de ADR proposta. **Autonomia não equivale a autoridade de decisão.** Se uma decisão bloqueante surgir, abrir SD e continuar tarefas independentes.

## 6. Plano de implementação e critérios de aceite

1. Cada ação sensível possui ator, origem, correlação, timestamp e estado.
2. Leitor sem privilégio não acessa trilha sensível.
3. Falhas/crashes mantêm invariantes transacionais quando ADR-002 aprovada.

Procedimento obrigatório: planejar → conferir contratos/SDD → editar em branch isolada → executar testes e verificar resultados reais → corrigir até **3 tentativas por causa** → documentar evidências → PR → revisão e Merge Guardian → retomar backlog independente. Não realizar merge se protections/checks nativos não estiverem comprovados; falha aberta significa BLOQUEADO, nunca SUCCESS.

## 7. Evidência e transferência de contexto

A entrega deve registrar no SDD-STATUS e PR: arquivos alterados, requisitos/ADRs, commit SHA, testes executados e respectivos resultados, testes não executados, avaliação de segredo/custo, dependências e próxima tarefa. Ao terminar sessão, deixar prompt de retomada que permita outra conversa executar sem qualquer memória anterior. Nunca afirmar execução autônoma permanente.
