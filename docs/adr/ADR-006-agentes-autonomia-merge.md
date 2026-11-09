# ADR-006 — Execução de agentes ChatGPT + GitHub e merge automático protegido

| Campo | Valor |
|---|---|
| Estado | **ACEITA — 08/11/2026** (governança operacional) |
| Autoridade | Responsável pelo MT SGI, autorização mestra explícita |
| Referência normativa | SDD-004 |
| Efeito na arquitetura de negócio | **NENHUM**: ADR-001 aceita; ADR-002 segue PROPOSTA |
| Opção adotada | C — ChatGPT com GitHub, sem executor local/nuvem pago |
| Revisão | nova ADR/SD para mudar executor ou direitos de aprovação |

## Contexto

O projeto necessita especialização por domínio, continuidade sem reexplicar histórico e automação operacional com o mínimo de intervenções. A restrição de custo zero e o SDD tornam inadequada a hipótese de serviço de IA pago, ou afirmar 15 agentes paralelos e permanentes apenas a partir de Markdown.

## Alternativas avaliadas

- **GitHub Actions como host de IA:** Actions é ambiente de CI mas não fornece inferência LLM gratuita ilimitada; não adotar como executor de agentes.
- **Ollama local:** exige máquina ligada, compatibilidade de modelo e operação local; possível evolução, não selecionada.
- **Servidor próprio/runner:** maior manutenção e dependência de hardware; não selecionado.
- **Híbrido ChatGPT+Ollama+Actions:** mais complexo; não selecionado neste marco.
- **ChatGPT + GitHub (ACEITA):** conexão já disponível, gerenciamento por sessões e estado persistente; execução não permanente.

## Decisão

1. Definir 15 perfis versionados em `agents/`; cada perfil subordinado ao SDD e ao orquestrador lógico, sem autonomia para alterar regras normativas.
2. Autorização mestra cobre A0/A1/A2 e A3 **condicionada**; nunca autoriza D1/X conforme SDD-004.
3. Loop lógico até limite da sessão, tarefa bloqueada ou recurso indisponível; handoff no GitHub. Nenhuma garantia de execução assíncrona/segundo plano.
4. Modelo híbrido de SD e no máximo três tentativas por causa.
5. Auto-merge **somente** após Merge Guardian, testes/reviews, status checks required e proteção nativa `main` comprovados. Se repositório `allow_auto_merge=false`, registrar bloqueio, não contornar.
6. Separação de autor/revisor independente no GitHub deve ser real; uma segunda instrução de IA não cria identidade ou aprovação de outro membro.
7. GitHub Actions roda somente checks determinísticos com permissões mínimas, nunca inferência de IA por serviços pagos.
8. Custo financeiro adicional R$ 0, sem cartão/trial/crédito, sem dados pessoais e sem pagamentos reais.

## Consequências positivas

Respeito ao ownership, revisão sistemática, rastreabilidade, retomada entre chats e execução operacional com poucos pedidos de permissão. Falhas documentais podem ser detectadas cedo por CI sem acoplar ao backend.

## Limitações e riscos aceitos

ChatGPT não permanece ativo após sessão por criação de Markdown; uma única identidade GitHub não simula aprovação independente. O repo pode não oferecer proteção/auto-merge na configuração atual; a fundação não deve ser falsamente declarada completa. Scripts de validação documental verificam apenas invariantes simples. Ativar auto-merge seguro requer verificação manual/automática das regras nativas e testes negativos.

## Critérios de aceite

SDD-004 aprovado, inventário 15 arquivos, runbook, decision log, templates, validador+testes+workflow, PR com CI real, status correto. **Auto-merge operacional somente quando protections/reviews/required checks comprovados**. Nenhum requisito de venda/caixa/estoque tem aprovação por esta ADR.
