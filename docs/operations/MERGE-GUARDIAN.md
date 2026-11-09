# MT SGI — Operação segura do Merge Guardian

> **Política fail-closed obrigatória:** aprovação textual de uma IA não é mecanismo de segurança GitHub. Um PR somente pode receber merge automatizado se as proteções nativas exigidas estiverem realmente vigentes e verificáveis. O responsável aprovou automerge **condicionado** à segurança; não aprovou um bypass.

## 1. Ameaças que esta política procura evitar

- Autor de PR escreve código vulnerável e apaga testes exigidos no mesmo diff.
- Workflow malicioso em PR usa `pull_request_target` ou token write para exfiltrar dados.
- SDD/ADR PROPOSTA é tratada como ACEITA por conveniência.
- Agente altera suas próprias instruções/gates para se autoaprovar.
- Aprovação sem vínculo a head SHA é reutilizada após novo commit.
- Checks `skipped`, `pending`, `neutral`, inexistentes ou com erro de acesso são tratados como PASS.
- Conflito, reset forçado ou branch desatualizada é incorporado inadvertidamente.
- Autor/revisor é a mesma identidade, mas o texto afirma revisão externa independente.

## 2. Condições cumulativas para aprovação

| ID | Gate | Fonte/aceite |
|---|---|---|
| MG-001 | PR aberto e **não draft**, head/base verificadas, SHA capturado | GitHub PR API |
| MG-002 | diff e escopo autorizados; requisito ID e ADR aplicável ACEITA | SDD + contrato + review |
| MG-003 | SDD atualizado, sem alteração oportunista de políticas | review SDD Guardian |
| MG-004 | testes relevantes executados e STATUS atualizado, sem omissões | CI + logs |
| MG-005 | scanning de credenciais, permissões e dependências, sem bloqueio | CI + Security |
| MG-006 | CI required: todos statuses = SUCCESS para SHA atualizado | Actions + branch protection |
| MG-007 | main protegida contra push direto e bypass, review exigido quando suportado | GitHub Rulesets/Branch protection |
| MG-008 | revisão independente confirmada conforme regra de GitHub | reviews reais; não texto fingido |
| MG-009 | revalidação após último commit; branch sem conflito | SHA/ref/mergeable + tests |
| MG-010 | auto-merge habilitado na configuração do repositório | allow_auto_merge=true |
| MG-011 | parecer com SHA e links de evidência; sem SD crítica pendente | report do Merge Guardian |

**Resultado:** somente se MG-001 a MG-011 = PASS, o Guardian pode solicitar auto-merge. Qualquer FAIL, UNKNOWN, NOT_RUN, PENDING, SKIPPED ou CANCELLED em gate obrigatório = BLOQUEADO. Nunca usar `merge_pull_request` como substituto de proteção.

## 3. Pré-requisitos de configuração no GitHub

Na interface de configurações do repositório (exige permissão administrativa), habilitar *Allow auto-merge* em General/Pull Requests; criar ruleset ou branch protection direcionada à `main`, exigir PR, status check obrigatório **`governance-validation`** depois que existir um run válido, reviews independentes quando suportadas, atualização/revalidação de branch e proteção contra bypass; exigir que aprovações antigas sejam descartadas quando o head mudar. Regras administrativas podem depender de plano/visibilidade do GitHub: consultar a UI antes de pressupor efeito real.

**Se a conexão GitHub disponibilizar apenas leitura dessas configurações, informar ao responsável exatamente o ajuste manual necessário.** Não insistir em automerge sem proteções. Enquanto isso, o Guardian continua revisando PRs sem executar merge.

## 4. Fluxo do parecer

1. Registrar `PR#`, base, head SHA e commit comparado, com data/fuso.
2. Verificar contrato, SDD/ADRs e consequências dos arquivos alterados.
3. Validar presença e resultados dos testes **do mesmo SHA**, incluindo negativos pertinentes.
4. Conferir proteção de branch/ruleset e allow_auto_merge por leitura real; não inferir do YAML.
5. Produzir checklist MG-001–011 com PASS/FAIL/UNKNOWN e evidência linkada.
6. Se bloqueado: indicar causa técnica, devolver ao agente dono, repetir até três tentativas por causa e reavaliar o SHA atualizado.
7. Se tudo passar: usar mecanismo nativo `enable_auto_merge`, observar merge real e registrar resultado; **não** declarar sucesso antes da confirmação.
8. Após merge: verificar que `main` avançou para o commit esperado, CI correspondente e SDD-STATUS registram a integração.

## 5. Limites de segurança dos controles iniciais

`scripts/validate_governance.py` e seu workflow fazem verificação **estrutural** e varredura de padrões específicos. Não conseguem avaliar semântica completa do SDD, qualidade de implementação de negócio, dependências transitivas desconhecidas, bypass por administradores ou proteções remotas. O Guardian precisa de evidência de QA/Security e da política nativa. Alterações no próprio workflow, no validador, nas regras AGENTS/SDD-004 ou neste documento são **mudanças sensíveis**: não podem dispensar revisão independente e decisão expressa quando enfraquecem o gate.

## 6. Evidências e estados

Separar `DOCS_VERSIONADOS`, `TESTES_LOCAIS_PASS`, `CI_PASS_SHA`, `PROTECTIONS_CONFIRMADAS`, `AUTOMERGE_ATIVO`, `MERGE_REALIZADO`. Esse conjunto não pode ser resumido a “pipeline pronto” se qualquer fase faltar.

## 7. Caso de teste negativo obrigatório

Abrir PR de demonstração que faça falhar a validação de governança (ex.: excluir arquivo exigido numa branch de teste) e verificar que o check falha. A evidência adicional de **bloqueio real** depende de ruleset/branch protection configurada; CI falhar isoladamente não prova que uma conta com permissão admin esteja impedida de fazer merge.
