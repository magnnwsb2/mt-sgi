# SD-0005 — Interfaces Admin/PDV e modelo seguro de sessão (ADR-005)

| Campo | Valor |
|---|---|
| Estado | **PENDENTE — NÃO É APROVAÇÃO** |
| Repositório/branch/PR | `magnnwsb2/mt-sgi`; `docs/adr-003-005-decision-proposals`; PR empilhado à fundação, a registrar |
| Solicitante | AGT-001 Orquestrador, AGT-004 Identidade e Acesso, AGT-013 Segurança |
| Responsável por decidir | Responsável pelo produto |
| Criada em | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — UI, autenticação, sessão, RBAC e segurança |
| Requisitos/ADRs | SDD-001 §§3–4,8; SDD-002 IAM/Payments; [ADR-005](../../adr/ADR-005-interfaces-autenticacao-sessao.md) PROPOSTA; ADR-002/003 pendentes |
| Prioridade | **CRÍTICA** antes de IAM/PDV efetivos |
| Trabalho independente | **SIM:** revisão de threat model, documentação e testes de contrato sintéticos |

## 1. Problema

A ADR-001 aprovou backend modular, não duas aplicações independentes, nem framework definitivo, nem autenticação. Sem decisão expressa, separar URLs, definir cookies e conceder permissões é mudança de arquitetura e segurança. A sessão de autenticação não equivale à sessão de caixa.

## 2. Alternativas

| Alternativa | Benefícios | Riscos/custo | Reversibilidade |
|---|---|---|---|
| A — Admin e PDV em rotas de mesma origem; sessão servidor/cookie HttpOnly | reduz CORS/cookies cross-origin, revogação central, uma API com IAM e RBAC | proteção CSRF, rotação e expiração obrigatórias | futura separação via ADR |
| B — apps em origens distintas, bearer token em memória | builds independentes | CORS, CSRF/XSS, renovação e infraestrutura mais complexos | migração de auth exigiria testes |
| C — SPA única + token persistente localStorage | implementação inicial simples | menor isolamento e risco XSS/token exposto | migração para sessão revogável difícil |

## 3. Recomendação técnica

**A**, com duas interfaces lógicas, mesmo backend e sessão controlada pelo servidor; ocultar menus não substitui autorização. Não permitir confirmação de venda offline até política transacional e de idempotência aprovadas.

## 4. Impactos

IAM, Admin, PDV, caixa (ADR-002), políticas de loja/terminal, CSRF, cookies Secure/HttpOnly/SameSite, RBAC objeto a objeto, auditoria, testes E2E e acessibilidade. Custo R$ 0. Nenhum framework ou deployment escolhido pela recomendação.

## 5. Perguntas objetivas ao responsável

1. Aprova **Admin e PDV sob mesma origem local**, com fronteiras lógicas e backend compartilhado?
2. Aprova **sessão server-side com cookie HttpOnly e proteção CSRF**, em vez de token em localStorage?
3. Qual a política de expiração, múltiplas sessões, papéis por loja e bloqueio/revogação? Como deve ser a matriz RBAC efetiva?
4. Confirma PDV offline com conclusão local **fora do MVP** e sessão de caixa exclusiva por terminal sujeita à ADR-002?

Uma resposta sobre a topologia não resolve automaticamente detalhes de autorização/segurança.

## 6. Decisão

- Estado: **PENDENTE**.
- Resposta expressa do responsável, data/fuso e referência: **não recebidos**.
- Nenhum contrato de autenticação ou permissão concedido por esta proposta.

## 7. Retomada

Somente após aceitação do ponto aplicável atualizar Decision Log, ADR-005, SDD-001/002/003, threat model, contratos/testes e respectivos requisitos; não criar autenticação ou frontend por pressuposto.
