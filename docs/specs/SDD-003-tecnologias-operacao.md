# MT SGI — SDD-003: Engenharia, Tecnologias, Segurança e Operação

| Campo | Valor |
|---|---|
| Documento | SDD-003 — anexo integrante do SDD-001 |
| Versão | 0.1.0, **PROPOSTA EM REVISÃO** |
| Escopo | stack, arquitetura de implementação, ciclo de vida, CI, segurança, operação local e custo |
| Arquitetura aceita | ADR-001: monólito modular; **não** microserviços físicos iniciais |
| Restrições | R$ 0, execução local, dados sintéticos, automação no GitHub onde for gratuita |
| Estado da implementação | Não iniciada |

> Os números de versão abaixo são **linhas candidatas**, não patch releases congeladas nem comprovação de compatibilidade ponta a ponta. A seleção de uma linha principal de runtime requer teste de dependências, matriz oficial e aprovação da baseline antes do primeiro código.

## 1. Critérios para selecionar tecnologias

O projeto exige simultaneamente: (1) comunidade ativa e ciclo previsível de segurança; (2) licenciamento compatível com código público; (3) suporte a domínio de varejo e transações consistentes; (4) reprodutibilidade local e CI; (5) ferramentas de teste/depuração gratuitas; (6) suporte à tipagem e modularidade; (7) baixo custo cognitivo/operacional; (8) migração planejável para futuras versões; (9) interfaces públicas e padrões abertos; (10) custo financeiro zero sem depender de créditos.

A decisão não favorece “tecnologia mais recente” em detrimento de estabilidade. Uma versão só entra em produção de referência quando suas dependências essenciais suportam-na oficialmente ou quando há ensaio robusto documentado e risco aceito. Bibliotecas descontinuadas e sem patches de segurança são rejeitadas.

## 2. Matriz tecnológica detalhada

| Camada | Candidata / linha | Papel preciso | Motivação e trade-off | Situação |
|---|---|---|---|---|
| Linguagem backend | Python **3.14.x** | casos de uso, serviços HTTP e regras | ecossistema, tipagem e testes; performance menor que linguagens compiladas em certos perfis | PROPOSTA |
| Alternativa de runtime | Python **3.15.x** | futura migração | estável desde 09/10/2026; validar suporte FastAPI/Pydantic/ORM e imagens antes de adotar | ALTERNATIVA |
| HTTP | FastAPI | roteamento, DI, schema e OpenAPI | boa integração com tipagem; evitar anemic domain e lógica dentro de rotas | PROPOSTA |
| Validação/serialização | Pydantic **v2** | contratos de entrada/saída nas bordas | precisão de schemas; modelos Pydantic não viram entidades de domínio | PROPOSTA |
| Servidor ASGI | Uvicorn, configuração mínima | rodar API local | sem dependência de serviço externo; política worker/timeout deverá ser medida | PROPOSTA |
| Persistência | PostgreSQL **18.x** | transações, constraints, índices, locks, MVCC | ACID e integridade; projeto precisa entender contenção e migração de majors | PROPOSTA |
| ORM | SQLAlchemy **2.x** | mapeamento e UoW nas portas de persistência | maturidade, queries explícitas; controlar lazy loads e N+1 | PROPOSTA |
| Migrations | Alembic | mudanças auditáveis de schema | revisão de forward/backward e ownership de domínio | PROPOSTA |
| Web | TypeScript estrito | segurança de tipos na UI e contratos de build | transpilation e dependências adicionais | PROPOSTA |
| UI | React | componentes e fluxos de administração/PDV | ecossistema amplo; abstrações devem manter domínio no backend | PROPOSTA |
| Build frontend | Vite | dev/build otimizado | não fornece SSR/backend; atende demo local | PROPOSTA |
| Toolchain Node | Node.js **26 LTS** | build/lint/teste frontend | linha LTS desde out/2026; avaliar mudanças no ecossistema | PROPOSTA |
| Gestão JS | npm com `package-lock.json` ou pnpm com `pnpm-lock.yaml` | dependências reproduzíveis | escolha única antes do primeiro install; sem misturar lockfiles | PENDENTE |
| Gestão Python | `uv` ou ferramenta equivalente com lockfile | dependências resolvidas e instaladas | rapidez; verificar compatibilidade com CI e build sem custo | PENDENTE |
| Banco local | PostgreSQL via container | fixture/integração e desenvolvimento | aumenta requisito de Docker local; CI usa serviço efêmero | PROPOSTA |
| Orquestração local | Docker Compose | subir API, banco e ferramentas opcionais | sem cluster; não simula todas condições de produção | PROPOSTA |
| Testes Python | pytest, pytest-cov, httpx | unidade, integração HTTP e cobertura | usar banco real para transações/locks em vez de mocks | PROPOSTA |
| Testes UI | Vitest, Testing Library, Playwright | unidade e E2E browser | Playwright aumenta tempo de CI; separar smoke/regressão | PROPOSTA |
| Tipagem/lint backend | Ruff + mypy ou pyright | padronização e tipagem | políticas precisam ser viáveis e mensuradas | PROPOSTA |
| Tipagem/lint frontend | `tsc --noEmit` + ESLint | controle estático | regras estritas desde a fundação | PROPOSTA |
| Contract testing | OpenAPI 3.1, JSON Schema e fixtures | compatibilidade de API/eventos | geração deve ser determinística; contratos antes do código | PROPOSTA |
| CI | GitHub Actions em repo público | validar código e artefatos | runners padrão gratuitos em repositórios públicos sujeito a termos/limites; não usar runners grandes/pagos | PROPOSTA |
| Documentação | Markdown versionado no Git + diagramas Mermaid | texto rastreável, GitHub-native | disciplinas de atualização e auditoria | EM USO |
| Segurança | varredura de segredos, dependências, SAST apropriado | impedir vazamentos e vulnerabilidades | scanners devem ter licença/execução gratuitas verificadas | PROPOSTA |
| Observabilidade | JSON logs + correlation ID; OpenTelemetry local se justificar | rastreio de incidentes | tracing distribuído não é requisito de MVP | PROPOSTA |
| Mensageria | PostgreSQL outbox local **se comprovadamente necessário** | efeitos assíncronos/reports | polling exige idempotência e recuperação; sem broker obrigatório | CONDICIONAL |
| UI deploy estático | GitHub Pages, opcional | docs/screenshots/demo sem API | **não** hospeda PostgreSQL nem FastAPI permanentemente | CONDICIONAL |

### 2.1 Por que não escolher automaticamente outras stacks

- **Java/Spring**: opção tecnicamente robusta, mas adicionaria mudança substancial de linguagem/ecossistema; só trocar por ADR, evidências de necessidade, compatibilidade e custo.
- **Go/Rust**: menor footprint e tipagem forte, porém mais esforço de entrega/ORM ou conversão; avaliar apenas se gargalo medido justificar.
- **Next.js**: alternativa plausível quando SSR/autenticação server-rendered forem necessidades claras; Vite+React basta ao MVP local. ADR-005 pode redefinir frontend.
- **MongoDB**: documentos não substituem facilmente transações/constraints relacionais de caixa e estoque; PostgreSQL é proposta preferida.
- **Kafka/NATS/RabbitMQ**: introduzem operadores, persistência de broker e falhas distribuídas antes da demanda; ADR-001 não os exige.
- **Redis**: não é necessário para correção de idempotência; estado crítico deve sobreviver a processo e estar protegido no banco.
- **Kubernetes/service mesh/cloud**: custo de operação e simulação sem requisitos equivalentes; proibidos como dependência fundamental do MVP.
- **Snowflake/Databricks/serviços gerenciados**: adequados a outros cenários, mas ferem compromisso de execução integral R$ 0 se exigirem cloud/conta/credit card.
- **LLM dentro do PDV**: jamais controlar vendas e saldos por geração probabilística; futuro BDI isolado dos comandos transacionais.

## 3. Estrutura planejada do repositório

A árvore abaixo é **alvo de evolução**, não afirma que as pastas já existem:

```text
mt-sgi/
  AGENTS.md                    # protocolo operacional para agentes
  README.md                    # visão e links, nunca substitui o SDD
  SECURITY.md                  # reporte/escopo de segurança (futuro)
  docs/
    specs/
      SDD-001.md               # autoridade principal
      SDD-002-dominios-contratos.md
      SDD-003-tecnologias-operacao.md
      SDD-STATUS.md
    adr/
      ADR-001-arquitetura-modular-extracao-progressiva.md
      ADR-002-consistencia-venda-estoque-caixa.md
    architecture/
    api/
    runbooks/
    threat-model/
  apps/
    admin-web/
    pos-web/
  backend/
    mt_sgi/
      identity/
      catalog/
      procurement/
      inventory/
      sales/
      payments/
      reporting/
      audit/
  packages/
    api-contracts/
    event-schemas/
    design-system/
    test-fixtures/
  infra/
    compose/
    local-observability/
  tests/
    architecture/
    contract/
    integration/
    concurrency/
    e2e/
    resilience/
    security/
  scripts/
  .github/workflows/
```

Cada módulo Python terá camadas conceituais `domain` (regras puras), `application` (casos de uso/orquestração), `ports` (interfaces públicas e dependências abstratas) e `adapters` (ORM, HTTP, eventos). A separação em diretórios não dispensa testes de importações e acoplamento. Um núcleo compartilhado eventual deve conter somente tipos sem semântica exclusiva de negócio; proibir entidade compartilhada monolítica que drible ownership.

## 4. Política anti-legado, suporte e atualizações

### 4.1 Baseline reproduzível

- Uma **versão major/minor aprovada** por runtime e bibliotecas principais, registradas em `SDD-003` e ADR quando relevantes.
- Exatos patchs/sha256/digests fixados em lockfiles e, quando apropriado, imagens por digest; não usar tags `latest`.
- Arquivos de projeto com intervalos de compatibilidade justificados e lockfile comprometido. Dependências transitivas não atualizadas silenciosamente em CI.
- Ambientes de desenvolvimento e CI com runtimes equivalentes; diferenças registradas (OS/CPU/architecture).
- Build não requer secrets nem API externa de negócio; download de dependências abertas pode exigir rede no *setup*, mas execução/testes de negócio não dependem de serviços remotos.
- SBOM e inventário de licenças quando pipeline estiver implantado.

### 4.2 Cadência e limiares

| Frequência | Atividade | Evidência |
|---|---|---|
| Semanal | verificar dependências, CVEs, mudanças relevantes e EOL | issue/PR e resultado de auditoria |
| Em até 48 h de descoberta de CVE crítica relevante | triagem técnica documentada e plano de mitigação; prazo de correção baseado em risco | avaliação, prioridade e correção/aceite temporário |
| Mensal | revisar patches seguros e incompatibilidades de CI | lockfile, changelog, testes |
| Trimestral | revisar upgrades major de runtime/framework e métricas de manutenção | ADR e ensaio de compatibilidade |
| Antes de EOL | migrar linha de runtime ou registrar risco inaceitável/bloquear release | matriz de versões e PR |
| A cada fase | revisar arquitetura, módulos e dependências proibidas | relatório de arquitetura e CI |

**Nunca** promover major automaticamente sem teste e revisão. Usar estratégia expand-and-contract para schema, APIs e mensagens: adicionar compatibilidade, migrar dados/consumidores, só então remover campos antigos. Rollback de migration destrutiva pode exigir backup/restore; não afirmar reversibilidade universal.

### 4.3 Matriz de suporte verificada — 08/11/2026

- Python 3.15 é estável (lançado em 09/10/2026); Python 3.14 continua em manutenção de bugfix. Preferir 3.14 inicialmente **como proposta** enquanto as bibliotecas e toolchains são comprovadas em CI; alvo 3.15 em matriz de ensaio.
- Node 26 entrou em LTS em outubro de 2026; selecionar **linha 26 LTS proposta**, não adotar `current` apenas por novidade.
- PostgreSQL 18 recebe suporte oficial até novembro de 2030. PostgreSQL 19 está em *release candidate*, com GA planejada para novembro de 2026, portanto não é baseline estável em 08/11/2026.
- FastAPI apresenta suporte documentado a Python 3.14 desde suas release notes; a compatibilidade exata entre versões de Pydantic, SQLAlchemy, drivers PostgreSQL, ferramentas Python e 3.15 precisa de ensaio.

**Fontes oficiais consultadas:**
- Python versões/suporte: https://devguide.python.org/versions/ e https://www.python.org/doc/versions/
- Node releases: https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule e https://github.com/nodejs/Release
- PostgreSQL suporte: https://www.postgresql.org/support/versioning/
- PostgreSQL 19 RC: https://www.postgresql.org/about/news/postgresql-19-rc-1-released-3409/
- FastAPI release notes: https://fastapi.tiangolo.com/release-notes/
- GitHub Actions uso/cobrança: https://docs.github.com/en/actions/concepts/billing-and-usage

> A data de consulta é contexto, não garantia eterna. Na primeira implementação e a cada trimestre, revalidar a fonte e registrar o patch escolhido no status e lockfiles.

## 5. CI/CD por estágios — plano, NÃO pipeline existente

### 5.1 Gatilhos

- PR para `main`: validações sem gravação no branch principal, sem dados reais nem tokens com privilégio desnecessário.
- Push em `main`: build/testes e artefatos não sensíveis após aprovação do PR.
- Workflow manual opcional: experimentos de carga, migrações em banco descartável e relatórios; nunca criar recursos cobrados.
- Execuções periódicas gratuitas: triagem de dependência somente se limites do GitHub comportarem e sem abuso de cota.

### 5.2 Pipeline alvo e critérios

1. **Documentação:** links internos, referências a ADR/SDD, estado aprovado/proposto, formatação, detectores de divergência.
2. **Segredos e supply chain:** scanner de credenciais com regras testadas; verificar lockfiles/licenças e dependências conhecidas.
3. **Lint e tipos:** Ruff, mypy/pyright, tsc, ESLint, arquivos gerados consistentes.
4. **Arquitetura:** sem ciclos, sem imports internos cruzados, sem ORM/HTTP no núcleo de domínio.
5. **Unitários:** regras de preço, quantidade, custos, autorização e estados; property-based quando útil.
6. **Integração SQL:** PostgreSQL efêmero, migrações e constraints reais; não usar SQLite como prova de locking PostgreSQL.
7. **Contratos:** OpenAPI validado, exemplos payload, diff de compatibilidade, esquemas de eventos e consumidor.
8. **Concorrência/resiliência:** corrida por último produto, reenvio, falhas no commit, reprocessamento/outbox, deadlocks e idempotência.
9. **E2E:** admin e PDV com dados sintéticos; Playwright headless com ambiente local.
10. **Performance:** benchmark separado, hardware e dataset fixos; não falhar PR por medição ruidosa até baseline aprovado.
11. **Migração/backup:** criar banco, aplicar migrações, popular fixtures, restaurar backup e reconciliar quando etapa exigir.
12. **Evidências:** relatório de teste, artefatos sem secretos, versão do commit e status; retenção gratuita conforme regras vigentes.

Bloqueio de merge por falha crítica quando a regra estiver implantada. Nunca escrever “CI verde” sem link, status real e log de job. Os gates entram progressivamente conforme existem módulos; falha por configuração ausente não pode ser escondida por `continue-on-error` genérico.

### 5.3 Ações de segurança em GitHub

- Usar permissões mínimas por job (`contents: read` padrão), limitar ações de terceiros a versões revisadas e preferir SHA completo.
- Proibir checkout de código não confiável com token privilegiado em workflows que possam publicar ou editar branch.
- Reduzir superfície de cache/artifacts; revisar riscos de `pull_request_target` e interpolação de input não confiável em shell.
- Segredos reais não existem nas fixtures; permissões de bot documentadas, sem dependência de conta/cloud de empresa.
- As skills privadas `spec-driven-development` e `pre-commit-security` são diretrizes de engenharia. Como seu acesso é independente, CI pública deve executar verificações próprias; nunca declarar integração automática inexistente.

## 6. Estratégia de testes — matriz de riscos

| Nível | O que provar | Exemplo |
|---|---|---|
| Unidade | cálculo decimal, regra de domínio, transição de estado | conversão de caixa para unidade-base, desconto válido |
| Propriedade | invariantes ao longo de muitos inputs | saída nunca gera estoque físico negativo |
| Contrato | formato, erro, schema, compatibilidade | POST /v1/sales exige idempotência, erro 409 |
| Integração | SQL real, transações, constraints, migrations | dois consumidores não vendem última unidade |
| Concorrência | race, interleaving, retry, lock timeout | 1.000 reenvios de mesma chave sem duplicar |
| Resiliência | crash, commit duvidoso, replay e outbox | resposta perdida seguida de retry sem nova venda |
| Segurança | RBAC, sessão, CSRF, SQLi, validação e rate limit | operador tenta ajustar estoque |
| E2E | fluxo do usuário em browser | abrir caixa → vender → fechar e reconciliar |
| Reconciliação | fatos e sumários concorrem com ledger | soma das vendas e estoque confere com lançamentos |
| Carga | limites de latência e throughput | p95 com dataset e hardware explicitados |

Definir ambiente de referência (hardware, memória, versão de container, CPU e dataset sintético), período de aquecimento, concorrência, p50/p95/p99 e repetição. Metas de SLO no SDD-001 são **alvos propostos, não resultados**. Se benchmarks forem instáveis no runner gratuito, usar ambiente local declarado e publicar metodologia.

## 7. Tratamento de transações, falhas e observabilidade

Detalhamento definitivo em **ADR-002**; regras abaixo são princípios de segurança operacional:

- Comandos idempotentes e transações PostgreSQL com garantia de atomicidade apenas onde efetivamente compartilhada a mesma transação.
- Evitar I/O externo dentro de transação crítica; operação remota pode falhar fora do controle do banco.
- Em timeout após gravação, consultar estado por chave idempotente/ID antes de executar novamente.
- Não publicar efeito externo antes do commit; outbox gravada junto à transação quando for adotada.
- Eventos podem repetir; efeito de negócio idempotente por consumidor e checkpoint. Ordenação por aggregate_version quando necessária.
- Lock timeouts, deadlocks e serialização exigem política de retry limitada e segura para operações idempotentes; não mascarar contenção com retry infinito.
- Correlação atravessa request, serviço, persistência e logs; hashes/tokens/senhas não aparecem em logs.
- Logs JSON com timestamp UTC, level, trace/correlation, domínio, operação, duração e erro sem payload sensível.
- Métricas: venda confirmada/falha, conflito de estoque, latência, tentativas idempotentes, lag de projeção/outbox, sessões abertas e falhas de migração.
- Runbooks devem registrar diagnóstico, reversão/restore, comandos seguros, cenário de falha e evidência de recuperação.

## 8. Segurança e ameaças

### 8.1 Autenticação e autorização

- Escolher formalmente sessão segura (cookie HttpOnly/Secure/SameSite + CSRF se necessário) ou mecanismo equivalente; nunca supor que JWT é automaticamente mais seguro.
- Senhas fictícias ainda recebem hashing moderno e política de troca/limite de tentativa.
- RBAC obrigatório por recurso, ação e escopo; autenticação não substitui autorização.
- Cookies HTTPS em deploy real; desenvolvimento local documenta exceções seguras.
- Não guardar tokens em localStorage quando desenho de sessão exigir proteção contra exposição por scripts.
- CSRF, CORS, XSS, SQL injection, mass assignment, autorização objeto a objeto, path traversal e brute-force entram no threat model.
- Nunca confiar em preço/custo total informados pelo frontend: backend calcula a partir de regras/snapshots.
- Campos de criação/alteração não podem permitir alteração arbitrária de owner, role, status ou audit IDs.

### 8.2 Segurança de dados, supply chain e auditoria

- Dados **sintéticos** por padrão, sem PII real; qualquer uso real futuro exige escopo de LGPD, base legal, retenção, direitos do titular e operação segura antes de acontecer.
- Segredos: arquivos ignorados, variáveis de ambiente, nenhum segredo hardcoded ou em Git history. Remoção de arquivo não remove histórico; vazamentos exigem revogação/rotação e tratamento histórico.
- Dependências revisadas para licença e CVEs, pins/reprodutibilidade; CVE triada por superfície real de ataque.
- Auditoria registra ações administrativas, vendas, cancelamentos e ajustes com integridade operacional; proteção contra manipulação e retenção serão formalizadas.
- Backups locais sintéticos e restauração testada; acesso por menor privilégio e execução sem redes externas quando possível.

**Referências de análise:** OWASP ASVS, OWASP API Security Top 10, OWASP Top 10, RFC 9457, OpenAPI 3.1, WCAG 2.2 AA e boas práticas de segurança GitHub Actions. A aderência integral a normas deve ser verificada, nunca presumida por simples menção documental.

## 9. Política operacional de custo financeiro zero

| Componente | Permitido | Vedado |
|---|---|---|
| Desenvolvimento | editor e ferramentas gratuitas, Docker local, executáveis FOSS | assinatura obrigatória, cartão, trials |
| Banco | PostgreSQL local e serviço efêmero em runner padrão público | RDS/Cloud SQL/banco gerenciado cobrável |
| CI | GitHub Actions em runner padrão de repositório público, conforme termos | runner premium/maior, plano com cobrança obrigatória |
| Documentação | Markdown no GitHub e Pages estático opcional | backend “gratuito” com surpresa de billing |
| Dados | fixtures sintéticas, dados públicos com licenças compatíveis | dados pessoais ou proprietários sem consentimento |
| API externa | nenhuma para operação central | pagamento real, IA paga, banco externo obrigatório |
| Observabilidade | logs/metrics local, artefatos seguros | SaaS cobrável obrigatório |
| Demonstração | instruções Docker/CLI e evidências, front estático opcional | prometer uptime 24/7 sem infraestrutura financiada |

A ausência de cobrança depende de configuração e uso. Antes de habilitar qualquer recurso de GitHub com condições de preço, verificar termos e parâmetros atualizados; não presumir gratuidade ilimitada de armazenamento, Codespaces ou runner diferenciado. Se um recurso gratuito deixar de existir, o projeto deve continuar localmente.

## 10. Operação e runbooks mínimos (futuros)

Repositório deve documentar quando implementado:

1. Pré-requisitos de sistema e versões testadas.
2. Instalação sem cartão/serviço pago; banco local isolado, portas, volumes e arquivos `.env.example` sem segredos.
3. Inicialização e parada segura, health checks, migrações e seed sintético.
4. Teste de ponta a ponta com resultados determinísticos.
5. Diagnóstico de conexão, migrations, deadlock, timeout, caixa/estoque divergentes.
6. Backup, restauração, validação de checksums e reversão de release.
7. Atualização de dependência/runtime e política de rollback.
8. Extração de módulos só após nova ADR.
9. Limpeza de dados sintéticos e preservação dos artefatos relevantes.
10. Publicação de evidências/benchmark de maneira transparente.

## 11. Checklist de aprovação da stack e operação

- [ ] Matriz verificada de versões *patch*, licenças e suporte.
- [ ] Ensaios compatibilidade Python 3.14/3.15 × FastAPI × Pydantic × SQLAlchemy × driver.
- [ ] Ensaios compatibilidade Node 26 × React × Vite × TypeScript × Playwright.
- [ ] Política escolhida de lockfile Python e JS, imagens e atualização.
- [ ] PostgreSQL 18 com testes reais de locking, migrations e backup.
- [ ] Baseline de CI sem faturamento externo e sem segredos.
- [ ] Matriz RBAC e threat model revisados.
- [ ] Condições de erro e carga de referência definidas.
- [ ] ADR-002 e ADR-004 aprovadas para os fluxos que delas dependem.
- [ ] Aprovação expressa do responsável pelo produto.

**Alterações futuras:** nunca atualizar esta especificação isoladamente quando afetar o SDD-001, contratos, ADR, testes e status; o SDD como conjunto é dono da verdade.
