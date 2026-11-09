# MT SGI — Governança dos 15 agentes (fundação v0.1)

**Autorização:** responsável concedeu autorização mestra em 2026-11-09 para estabelecer a fundação de agentes e executar tarefas rotineiras dentro do escopo aprovado. **Não** aprovou automaticamente ADR-002, ADR-003, ADR-004, ADR-005, stack proposta, contratos definitivos ou baseline SDD global.

## Modelo de execução
Opção C: ChatGPT com GitHub conectado. Os 15 arquivos `agents/*.md` representam especializações e protocolos, não 15 processos concorrentes nem serviço 24/7. A execução depende de sessões e ferramentas disponíveis; não alegar trabalho em background. GitHub persiste contexto, decisões e PRs.

## Política de autonomia
Autorizadas tarefas rotineiras no escopo aprovado: documentação, testes, refatoração compatível, correção de bugs, commits e PRs. Requisitos novos, ADRs, mudanças arquiteturais, segurança, custos, ações destrutivas e regras de negócio não decididas dependem de aprovação expressa. Custo adicional R$ 0 absoluto; apenas dados sintéticos/públicos autorizados.

## Fluxo
1. Orquestrador lê baseline, PRs, checks, SDD-STATUS e dependências.
2. Seleciona tarefa autorizada e atribui papel especializado; mudanças em paralelo somente quando independentes.
3. SDD Guardian valida rastreabilidade; Arquiteto e Segurança verificam limites; QA registra evidências.
4. Implementação em branch isolada e PR pequeno; até três tentativas de correção por causa; após falha, bloquear tarefa e continuar trabalho independente.
5. Merge Guardian revisa de forma independente: SDD/ADRs, testes realmente executados, CI, segurança, contratos, documentação, dependências e licença, custo zero, branch e permissões.
6. Se faltar evidência, status ou proteção: **fail closed**. Não fazer merge. Se todas as condições forem comprovadas, permitir merge automático apenas dentro do escopo autorizado e capacidades efetivas do GitHub.
7. Registrar SHA, PR, checks, decisão, bloqueios e próxima ação no GitHub antes de encerrar sessão.

## Decisões: modelo híbrido
Decisões não críticas ficam agrupadas; bloqueios críticos são destacados na próxima consulta do responsável; tarefas independentes prosseguem. Toda solicitação possui ID SD-NNNN, problema, alternativas, recomendação, impacto, requisitos/ADRs afetados, risco e estado. A aprovação no chat deve ser registrada e confirmada no GitHub antes de orientar implementação.

## Segurança de merge
Não confiar exclusivamente em parecer de LLM: checks determinísticos e evidência verificável são obrigatórios. Não aprovar o próprio PR como revisão independente. Não executar código de PR não confiável com credenciais de escrita. Mudanças em CI, proteções, AGENTS, governança e política do Merge Guardian requerem revisão independente reforçada; na impossibilidade, bloquear merge e solicitar decisão. Verificar se branch protection/auto-merge/required checks estão disponíveis antes de ativá-los; não afirmar configuração sem prova.

## Ordem de implantação
A Governança e documentação → B Fundação dos agentes → C CI e segurança → D testes adversariais de políticas → E desenvolvimento de módulos liberados por decisões aceitas. O PR documental #1 foi **fechado sem merge, como substituído**; o conteúdo proposto está consolidado no PR #2, ainda **aberto contra `main` e não mesclado**. Aprovação operacional da governança, revisão de PR e aceite da baseline de produto são marcos diferentes.

## Registro de estado
O arquivo `docs/specs/SDD-STATUS.md` e os PRs devem distinguir PROPOSTO, APROVADO, IMPLEMENTADO e VALIDADO. Esta fundação documental não significa que 15 agentes estejam executando ou que merge automático esteja habilitado.
