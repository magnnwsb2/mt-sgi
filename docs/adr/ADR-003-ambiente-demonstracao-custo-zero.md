# ADR-003 — Ambiente reproduzível de desenvolvimento e demonstração, sem custo adicional

| Campo | Valor |
|---|---|
| Produto | MT SGI — MT Sistema de Gestão Integrada |
| Identificador | ADR-003 |
| Estado | **PROPOSTA — NÃO ACEITA; exige aprovação expressa** |
| Data da proposta | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — infraestrutura, distribuição e operação |
| Base normativa | SDD-001 §§7–9,11–13; SDD-003 §§3–5,9–11; ADR-001 ACEITA; SDD-004 APROVADO para governança |
| Dependências | Escolha de stack em SDD-003, ADR-002 para transações e ADR-005 para distribuição das UIs |
| Custo adicional máximo | **R$ 0**, inclusive cartão, créditos promocionais, trial e recursos faturáveis |
| Implementação | **NENHUMA**. Este documento é decisão proposta, não autorização de provisionamento |

## 1. Problema e invariantes

O MT SGI exige demonstração integral dos fluxos de gestão comercial e PDV com dados **sintéticos**, sem aplicação de produção, cobrança externa ou dependência de infraestrutura de terceiros. A arquitetura aceita é **monólito modular** (ADR-001); a stack Python/React/PostgreSQL é candidata em SDD-003, ainda sem aceite. A versão demo não é serviço comercial nem SaaS com disponibilidade contínua.

**Invariantes:** (INF-001) custo adicional zero e nenhum cartão/crédito/trial; (INF-002) reprodutibilidade por comandos versionados; (INF-003) nada de pagamentos/fiscal real ou PII; (INF-004) banco e dados nunca permanentemente hospedados pelo GitHub; (INF-005) scripts de setup, teste e teardown; (INF-006) nenhum segredo real em workflows/artifacts; (INF-007) GitHub Pages, se usado, é apenas publicação **estática e demonstrativa**, não API/banco operacional.

## 2. Alternativas comparadas

| Opção | Configuração proposta | Vantagens | Riscos/limitações |
|---|---|---|---|
| A — **Execução local com CI pública efêmera** | desenvolvimento por CLI/container local; PostgreSQL local e serviços efêmeros em runner padrão público; docs e evidências no GitHub | suporta transações, dados temporários e E2E; integra com ADR-001; sem servidor contratado | requer recursos no computador; runners/limites do GitHub podem variar; não oferece demo online permanente |
| B — Somente GitHub Actions/Pages | CI/testes e artefatos efêmeros, interface estática opcional sem backend | elimina dependência de máquina para alguns testes e exibe material público | não mantém DB/API transacional/PDV em tempo real; insuficiente para demonstrar fluxo completo de aplicação |
| C — Serviço de hospedagem externa dito “free tier” | backend/DB em provedor de terceiros | acesso remoto à demo | suspensão, termos variáveis, exigência de cartão, limite/débito e risco de custo; não é autorizável sob a política atual |

**Recomendação técnica não vinculante:** opção A como base, B apenas para evidências estáticas complementares; não utilizar C. A recomendação não constitui aceite de ferramenta ou runtime.

## 3. Topologia candidata (sujeita a ADR-005 e stack)

```text
              Estação local do demonstrador
         ┌─────────────────────────────────┐
         │ UI Admin + UI PDV (interfaces)  │
         │        API local /v1            │
         │  monólito modular — oito áreas  │
         │      PostgreSQL de teste        │
         └─────────────────────────────────┘
                   somente rede local
                           |
                           v
                  GitHub público: fontes
                PR, Actions CI, artefatos
                 Pages (estático opcional)
```

- Ambientes conceituais: **local-dev**, **local-demo** e **CI-ephemeral**. Não existem até a fase de implementação autorizada.
- O estado do banco de demonstração é descartável e **não deve ser confundido** com banco comercial. Seed somente sintético, determinístico e idempotente.
- O fluxo de exposição pública é documentação/artefatos sem dados sensíveis; não abrir porta da API local à internet por padrão.
- Preferir serviços de CI não privilegiados, tokens GitHub com permissões mínimas, ações fixadas por commit e proteção nativa da `main`.
- Se a opção sem container for necessária, scripts alternativos podem ser especificados depois, sem mudar regras de negócio.

## 4. Contratos de execução propostos (NÃO implementados)

| ID | Critério de aceite mensurável | Evidência futura |
|---|---|---|
| INF-A01 | Projeto sobe e encerra com instruções reproduzíveis, versões fixadas e comandos `start/stop/reset` | documentação + logs higienizados |
| INF-A02 | Banco local restaura com fixtures sintéticas, migrações e integridade verificável | testes de restore e hashes |
| INF-A03 | CI executa testes de unidade, contrato, integração e E2E conforme a fase autorizada | checks obrigatórios no SHA atual |
| INF-A04 | Publicação não contém servidor/API/DB hospedados nem credenciais | review do diff, dependências e configurações |
| INF-A05 | Falha no setup não exige cartão, SaaS, prova gratuita ou conta paga | avaliação manual de requisitos/termos |
| INF-A06 | Backup/restore sintéticos e estratégia de rollback documentados | simulação de falha controlada |
| INF-A07 | Demo registra claramente que operação é fictícia e não fiscal | verificação UI/documentação |
| INF-A08 | Se uso do GitHub deixar de ser elegível a custo zero, o fluxo local ainda funciona | roteiro de contingência |

**Matriz de compatibilidade ainda pendente:** versões Python/Node/PostgreSQL, lockfiles, imagens e licenças devem ser escolhidos conforme SDD-003 e comprovados em CI antes de declarar esta ADR implementada.

## 5. Política financeira e operacional fail-closed

Antes de habilitar um novo recurso, registrar tipo de runner, visibilidade do repositório, cotas aplicáveis, termos vigentes, risco de cobrança e fallback. Não alegar elegibilidade ilimitada sem conferência atual. Não instalar planos pagos, runners premium, Codespaces com custos potenciais, hospedagem com cartão ou créditos promocionais. Suspender a atividade afetada se qualquer condição deixar de atender **R$ 0**; manter o desenvolvimento offline/local quando viável.

O GitHub pode hospedar o **código** e a **CI**; isso não autoriza concluir que o GitHub hospeda a aplicação transacional. O uso de artefatos de CI não prova persistência de produção. Observabilidade permitida: stdout/JSON local sanitizado; não usar serviço SaaS obrigatório.

## 6. Riscos, reversão e dependências

- **Risco tecnológico:** versões candidatas de SDD-003 ainda são propostas; validar ecossistema antes de instalação.
- **Risco de CI:** gates que passam sem testes reais do produto não significam aplicação funcionando; cada requisito de aceite deve ter teste específico.
- **Risco de segurança:** exposição da porta local, credencial fictícia reutilizada, artefatos com dados reais. Exigir loopback, fixtures e revisão.
- **Reversão:** remover configuração local/container e artefatos gerados, preservar logs mínimos de QA sem dados sensíveis; não destruir dados fora de diretórios explicitamente previstos.
- **Dependências:** ADR-002 define transação; ADR-004 custo/quantidade; ADR-005 separação de UI/autenticação; a aprovação desta ADR isolada **não libera** nenhuma dessas regras.

## 7. Decisões objetivas solicitadas

1. Aprovar **A — demonstração local com CI efêmera de repositório público**, com Pages limitado a material estático opcional, sem hospedagem operacional?
2. O requisito de demonstração pode ser **sem disponibilidade online 24/7** e depender de máquina local, até que exista nova decisão de infraestrutura?
3. É aceitável disponibilizar somente **artefatos estáticos e documentação pública** enquanto não houver uma implementação local completa?

**Estado final:** PROPOSTA — NÃO ACEITA. Não criar `docker-compose.yml`, deploy, banco ou scripts de provisão como consequência desta proposta sem a aprovação das decisões aplicáveis. Registro da solicitação: `docs/decisions/requests/SD-0003-ambiente-custo-zero.md`.
