# MT SGI — Despachante seguro de tarefas (fase 1: somente planejamento)

| Campo | Estado |
|---|---|
| Mecanismo | `scripts/agent_dispatcher.py` |
| Estado | **IMPLEMENTADO em branch/PR, não integrado à main** |
| Escopo | validação de contrato JSON e emissão de parecer `PLAN_ONLY` ou `BLOCKED` |
| Executor LLM autônomo | **NÃO IMPLEMENTADO** |
| Efeitos externos | **NENHUM**; não lê GitHub, não usa token, não cria branch/commit, não executa código de tarefas |
| Aprovação de negócio | **NUNCA** inferida do resultado |
| Custos | biblioteca padrão Python, sem rede ou serviço pago |

## 1. Modelo de confiança

Os 15 perfis em `agents/` são **papéis normativos**. O despachante não os executa nem cria 15 processos; ele apenas identifica o ID registrado e aplica um gate determinístico a uma tarefa. **Qualquer contrato é entrada não confiável.** O campo `preconditions: ["VERIFICADAS"]` é uma declaração textual, não prova independente de CI, proteção de branch, aprovação ou permissão. Portanto, mesmo um `PLAN_ONLY` **não concede autorização de escrita ou execução**.

**Limites de segurança:** saída JSON sanitizada, sem imprimir contrato completo; entrada de até 100 KB; rejeita symlink e JSON inválido; proíbe comandos de execução, pagamento, deploy, rede, merge e alteração de permissões. Não consulta credenciais. Não interpreta instruções de tarefas como comandos. Não há acesso à rede em código, mas o processo Python deve ser executado em ambiente confiável; isto não é sandbox de sistema operacional.

## 2. Como testar (somente em checkout de branch revisada)

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/agent_dispatcher.py docs/agents/examples/TC-0100-plan-only.json
```

Saída esperada para o exemplo: `decision: PLAN_ONLY`, `effects: []`. Se alguma decisão estiver pendente, campo faltar, ação solicitada for diferente de `plan_only` ou contador de tentativas atingir 3, saída `BLOCKED` e código de retorno 2.

## 3. Fluxo de operação — humano/ChatGPT com GitHub conectado

1. Orquestrador lê SDD/ADR/STATUS e a árvore/PR reais; escolhe uma tarefa documental sem decisão D1 pendente.
2. Contrato TC declara ID, agente primário, agentes secundários, branch, SHA, caminhos, dependências, critérios e limites. **Não inserir senhas ou PII**.
3. O despachante **somente classifica** o pedido. `BLOCKED` impede avanço; `PLAN_ONLY` permite preparar um plano de revisão, não alterar arquivos.
4. Agente SDD Guardian e Security revisam **separadamente o conteúdo** antes de qualquer escrita futura. O próprio autor não conta como revisão independente.
5. Implementação posterior exige um executor distinto, permissões mínimas, autorização por ação/caminho, logs e gates externos. Nada disso está autorizado por este mecanismo.
6. Merge Guardian aplica MG-001–011, exigindo proteção nativa, CI no head e review independente. Não há bypass.

## 4. O que falta para agentes executores de verdade

- **Fase 2, pendente de desenho e validação:** contrato assinado/vinculado ao SHA real do GitHub; comprovação automática de aprovações/decisões; controle de paths por operação; sandbox e identidade sem privilégios; logs auditáveis; testes adversariais de prompt injection, injeção de comando, race/TOCTOU e vazamento de segredos.
- **Fase 3, pendente:** executor que abra PRs isolados para mudanças de baixo risco, após aprovação específica de seu modelo de autorização. Proibido conceder push direto na `main`, acesso a secrets, alteração de proteção e merge próprio.
- **Pré-requisito externo:** proteção real da `main` e revisão independente, conforme Issue #3. Sem isso, o Merge Guardian permanece BLOQUEADO.

**Não chamar este despachante de "15 agentes trabalhando autonomamente": ele é o primeiro controle técnico de admissão, somente de leitura.**
