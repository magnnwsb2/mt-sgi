# MT SGI — Despachante seguro (fase N1: planejamento e auditoria local, sem escrita)

| Campo | Estado |
|---|---|
| Mecanismo | `scripts/agent_dispatcher.py` |
| Estado | **IMPLEMENTADO em branch/PR, não integrado à main** |
| Escopo | validação de contrato JSON e auditoria local governamental, com `PLAN_ONLY`, `AUDIT_ONLY` ou `BLOCKED` |
| Executor LLM autônomo | **NÃO IMPLEMENTADO** |
| Efeitos externos | **NENHUM**; não lê GitHub, não usa token, não cria branch/commit, não executa código de tarefas |
| Aprovação de negócio | **NUNCA** inferida do resultado |
| Custos | biblioteca padrão Python, sem rede ou serviço pago |

## 1. Modelo de confiança

Os 15 perfis em `agents/` são **papéis normativos**. O despachante não os executa nem cria 15 processos; ele identifica o ID registrado e aplica um gate determinístico a uma tarefa, além de executar uma inspeção **local, limitada e somente de leitura** quando recebe `inspect_governance` de papel autorizado. **Qualquer contrato é entrada não confiável.** O campo `preconditions: ["GOVERNANCE_REPO_VALID"]` é **um nome de condição**, não evidência: o despachante precisa verificar o conteúdo SDD/validador do checkout; mesmo o resultado local PASS não prova CI remota, proteção de branch, revisão independente, aprovação de negócio ou permissão de escrita. Portanto, mesmo um `PLAN_ONLY` **não concede autorização de escrita ou execução**.

**Limites de segurança:** saída JSON sanitizada, sem imprimir contrato completo; entrada de até 100 KB; rejeita symlink e JSON inválido; proíbe comandos de execução, pagamento, deploy, rede, merge e alteração de permissões. Não consulta credenciais. Não interpreta instruções de tarefas como comandos. Não há acesso à rede em código, mas o processo Python deve ser executado em ambiente confiável; isto não é sandbox de sistema operacional.

## 2. Como testar (somente em checkout de branch revisada)

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/agent_dispatcher.py docs/agents/examples/TC-0100-plan-only.json
```

Saída esperada: `decision: PLAN_ONLY`, `effects: []`, **governança local PASS**, controle remoto `NOT_VERIFIED` e escrita `DENIED`. O texto `preconditions` deve declarar o **nome da condição suportada**, `GOVERNANCE_REPO_VALID`; **não** declarar `VERIFICADAS` como suposta evidência. A função inspeciona os documentos reais do checkout com `validate_repository` e verifica a presença dos princípios AUT no SDD-001 e do contrato de segurança no SDD-004.

Para uma **operação efetiva de leitura automatizada** (sem escrita), execute:

```sh
python3 scripts/agent_dispatcher.py docs/agents/examples/TC-0101-governance-audit.json
```

Resultado esperado: `AUDIT_ONLY`, `governance: PASS` e `effects: []`. O GitHub Actions roda esta mesma inspeção em PRs; a resposta `remote_head: NOT_VERIFIED` significa que não foi feita consulta externa de proteção ou aprovação. Nenhum campo do contrato pode transformá-la em `VERIFIED`. Se houver decisão pendente, campo inválido, ação diferente de `plan_only` ou `inspect_governance`, papel sem permissão de auditoria ou contador de tentativas atingir 3, a saída é `BLOCKED` e o código de retorno é 2.

## 3. Fluxo de operação — humano/ChatGPT com GitHub conectado

1. Orquestrador lê SDD/ADR/STATUS e a árvore/PR reais; escolhe uma tarefa documental sem decisão D1 pendente.
2. Contrato TC declara ID, agente primário, agentes secundários, branch, SHA, caminhos, dependências, critérios e limites. **Não inserir senhas ou PII**.
3. O despachante **classifica** o pedido e, para `inspect_governance`, executa a auditoria estrutural offline. `BLOCKED` impede avanço; `PLAN_ONLY` permite preparar um plano de revisão, não alterar arquivos.
4. Agente SDD Guardian e Security revisam **separadamente o conteúdo** antes de qualquer escrita futura. O próprio autor não conta como revisão independente.
5. Implementação posterior exige um executor distinto, permissões mínimas, autorização por ação/caminho, logs e gates externos. Nada disso está autorizado por este mecanismo.
6. Merge Guardian aplica MG-001–011, exigindo proteção nativa, CI no head e review independente. Não há bypass.

## 4. O que falta para agentes executores de verdade

- **Fase 2, pendente de desenho e validação:** contrato assinado/vinculado ao SHA real do GitHub; comprovação automática de aprovações/decisões; controle de paths por operação; sandbox e identidade sem privilégios; logs auditáveis; testes adversariais de prompt injection, injeção de comando, race/TOCTOU e vazamento de segredos.
- **Fase 3, pendente:** executor que abra PRs isolados para mudanças de baixo risco, após aprovação específica de seu modelo de autorização. Proibido conceder push direto na `main`, acesso a secrets, alteração de proteção e merge próprio.
- **Pré-requisito externo:** proteção real da `main` e revisão independente, conforme Issue #3. Sem isso, o Merge Guardian permanece BLOQUEADO.

**Não chamar este despachante de "15 agentes de IA trabalhando autonomamente": ele executa somente verificações determinísticas locais e não confere direitos externos.**

## 5. Provas e bloqueios que não podem ser simulados

**N1 — operação autônoma de leitura:** verificação da árvore local de governança, validação de 15 agentes, SDD-001 §16, SDD-004 §14, ADRs aceitas e ausência de segredos em padrões selecionados, sem acionar comandos fornecidos pelo contrato; emitir somente indicadores de alto nível, sem segredos. Contratos com requisitos `FUN-*`, ADR-002/003/004/005 aceitas apenas por alegação, condições `VERIFICADAS`, tentativa nº 3, path overlap e role inadequada são rejeitados. A inspeção local não prova procedência do SHA remoto.

**N2 — inspeção remota vinculada ao SHA:** exige consulta via conector GitHub e verificação de resposta independente do JSON do solicitante. **Não realizada por este script offline.**

**N3/N4 — escrita/integração:** **BLOQUEADAS.** Sem privilégio de escrita no workflow, sem token no contrato e sem API de GitHub acessível ao despachante. O YAML não é enforcement suficiente: GitHub precisa de branch protection/ruleset reais, check required e review independente, antes de um executor remoto separado.

**Ameaça residual:** o autor de um PR pode modificar o próprio validador no diff. Enquanto a `main` estiver desprotegida, execução verde da CI não assegura que esse gate seja obrigatório. Prova de integralidade de *escrita* autônoma **não** pode ser declarada até o bloqueio nativo ser demonstrado em cenário negativo.

**Rastreabilidade:** SDD-001 §16 (AUT-001..012), SDD-004 §14 (N0..N4), [Issue #3](https://github.com/magnnwsb2/mt-sgi/issues/3), `docs/specs/SDD-STATUS.md`.
