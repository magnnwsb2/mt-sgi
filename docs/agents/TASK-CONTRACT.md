# MT SGI — Contrato de Tarefa para Agentes (TC)

| Campo | Valor |
|---|---|
| Identificador documental | TC-TEMPLATE |
| Estado | TEMPLATE — não é trabalho iniciado |
| Documento constitucional | SDD-001 e SDD-004 |
| Finalidade | garantir execução auditável e retomada sem memória de conversa |

## 1. Esquema mínimo obrigatório

Um contrato de tarefa deve ser anexado ao PR, Issue ou arquivo `docs/tasks/TC-NNNN.md` quando for uma entrega longa. Campos são obrigatórios, com `NÃO APLICÁVEL` justificado quando apropriado; `NÃO VERIFICADO` não significa PASS.

```yaml
task_id: TC-0001
state: PROPOSTA                # PROPOSTA | EM_EXECUCAO | BLOQUEADA | EM_REVISAO | CONCLUIDA
title: "Título descritivo sem ambiguidades"
owner_agent: AGT-001
secondary_agents: [AGT-002, AGT-012]
repo: magnnwsb2/mt-sgi
baseline_branch: main
baseline_sha: "SHA exato obtido do GitHub"
work_branch: "feat/exemplo"
pr_number: null
requirements: [GOV-001]      # IDs existentes na especificação
accepted_adrs: [ADR-001]     # apenas ACEITAS
pending_decisions: []
allowed_paths: ["docs/"]
blocked_paths: ["backend/"]
preconditions: ["documentação relevante aprovada"]
dependencies: []
interfaces: ["documento e contrato de entrada/saída"]
acceptance_criteria: ["resultado testável"]
test_plan:
  - id: CT-001
    method: "comando e ambiente"
    expected: "saída e estado verificáveis"
    status: NAO_EXECUTADO
risk: "baixo/medio/alto + justificativa"
rollback: "reverter commit/PR antes de merge"
cost_policy: "R$ 0 — sem serviços faturáveis"
attempts_by_root_cause: {}
outcome:
  commits: []
  jobs: []
  evidence: []
  remaining_blockers: []
  next_action: "..."
```

## 2. Estados e transições

`PROPOSTA→EM_EXECUCAO` somente se todas as pré-condições forem atendidas. `EM_EXECUCAO→BLOQUEADA` se decisão necessária, três tentativas por causa ou teste/ambiente inviável. `EM_EXECUCAO→EM_REVISAO` com commit e testes. `EM_REVISAO→CONCLUIDA` somente com aprovação do gate correspondente e evidência; PR aberto/draft não é conclusão de integração. A tarefa pode ser parcialmente implementada sem ser concluída.

## 3. Dependências e paralelismo

Criar grafo acíclico de tarefas. Nenhum contrato deve editar simultaneamente o mesmo arquivo governamental com outra tarefa; usar branches separadas, rebase seguro e revisão. Transações multi-módulo exigem ADR-002 antes de código. O Orquestrador seleciona próxima tarefa desbloqueada; tarefas independentes podem continuar quando outra bloqueia.

## 4. Tentativas e pós-falha

Manter `attempts_by_root_cause` com causa, hipótese, mudança, comando, resultado e número 1–3. Não reiniciar contador apenas por troca de branch/sessão. Depois de 3 tentativas sem correção, bloquear localmente e abrir solicitação de decisão se necessário. Não reduzir testes/segurança para desbloquear.

## 5. Evidência de execução

O relatório final deve comparar intenção e realidade: estado da branch no GitHub, commits, PR, SHA sob teste, artefatos, logs higienizados, resultados SUCCESS/FAILURE/NOT_RUN, riscos residuais, custo e próxima ação. Nunca registrar um link para job que não existe. Check de CI ausente bloqueia requisito que depende dele.

## 6. Exemplo simples de entrega

Tarefa: GOV-001, cadastro de 15 perfis; proprietário AGT-001; caminhos `agents/*.md`; prova: validador que confere contagem e IDs únicos; PR documental. Não implica que cada perfil está rodando. Não escrever “agentes ativos” sem executor real.

## 7. Contrato de admissibilidade para a auditoria local (AUT-001..012)

**Não confundir campo declarado com evidência externa.** O esquema YAML de tarefa acima continua sendo a forma geral de acompanhamento, mas o despachante offline recebe uma projeção **JSON com `requested_action` obrigatório**. Apenas `plan_only` e `inspect_governance` são aceitos: a inspeção é exclusivamente local e não executa tarefa de domínio.

O campo `preconditions` desse JSON recebe **`["GOVERNANCE_REPO_VALID"]`**, que é o nome de uma condição implementada no código: o despachante lê `SDD-001`, `SDD-004` e executa o validador estrutural real no checkout. O valor antigo `["VERIFICADAS"]` é **rejeitado**, pois não constitui prova. O contrato jamais pode fornecer um objeto `evidence` com `remote_head: VERIFIED` para conceder direitos: campos não reconhecidos são bloqueados. O resultado mostra `remote_head: NOT_VERIFIED` e `write_authorization: DENIED`.

Somente os requisitos `GOV-001..012` entram nessa primeira camada; nenhuma ADR além de `ADR-001` e `ADR-006` pode ser alegada como aceita. Ações de alteração, pagamento, deploy, GitHub write, rede e merge não são operações aceitas por este executor. Um simples `PLAN_ONLY` ou `AUDIT_ONLY` **nunca** eleva privilégio ou autoriza `EM_REVISAO→CONCLUIDA`.

**Exemplos versionados:** `docs/agents/examples/TC-0100-plan-only.json` e `docs/agents/examples/TC-0101-governance-audit.json`. A auditoria do segundo é executada automaticamente pelo CI de governança sem token de escrita, mas **não** verifica a procedência do head remoto nem políticas do repositório. Usar o GitHub conectado para obter essas evidências de forma independente se o plano evoluir para efeitos. Consultar SDD-001 §16, SDD-004 §14 e `docs/agents/SAFE-DISPATCHER.md`.
