# ADR-001 — Monólito modular e extração progressiva de serviços

| Campo | Valor |
|---|---|
| Produto | MT SGI — MT Sistema de Gestão Integrada |
| ID | ADR-001 |
| Estado da decisão | **ACEITA — APROVADA pelo responsável pelo produto** |
| Decidido em | 2026-11-08 |
| Versão do registro | 1.1.0 (renomeado de RetailFlow para MT SGI, sem mudança de decisão) |
| Especificação normativa | `docs/specs/SDD-001.md` e anexos |
| Referências cruzadas | ADR-002 PROPOSTA, ADR-003/004/005 pendentes |
| Limitações | custo R$ 0, sem serviço pago, dados sintéticos e GitHub/local |

> **Aceite da decisão não significa aceite dos testes nem implementação.** A ADR-001 foi aprovada pelo responsável: monólito modular, fronteiras rígidas, possibilidade de extrair microserviços quando houver justificativa real. Sua aplicação no código está totalmente pendente.

## 1. Contexto e forças em tensão

O MT SGI precisa modelar oito domínios de gestão comercial: IAM, catálogo, compras, inventário, vendas/PDV, pagamentos simulados/caixa, relatórios e auditoria. Uma venda consome estoque e registra valores de forma consistente; projeções de relatório podem ficar momentaneamente atrasadas sem invalidar a transação. Precisamos de fronteiras escaláveis, contratos, segurança e atualização tecnológica sem assumir custo financeiro.

**Problema:** iniciar com vários microserviços físicos adiciona rede, consistência distribuída, observabilidade avançada, sagas, deploys, sincronização de contratos e recuperação de falhas antes de existir carga ou equipe que justifique isso. Por outro lado, monólito não modular torna o sistema ilegível e caro de evoluir. A arquitetura deve suportar aprendizado e portfólio profissional sem reproduzir um “microsserviço artificial por pasta”.

### 1.1 Requisitos influentes

- Uma única máquina local deve reproduzir a operação sem conta de nuvem.
- GitHub público pode hospedar código, documentação e CI de runners padrão; não é host permanente de banco/servidor.
- PostgreSQL oferece transações locais e constraints fortes para estoque/venda/caixa; garantias exatas a formalizar na ADR-002.
- Controle de acesso/auditoria devem existir em comandos, não apenas UI.
- Módulos de negócio precisam de ownership rastreável e independência de implementação.
- Relatórios e futuras exportações para BDI têm latência e acoplamento diferentes dos comandos de venda.
- A evolução deve evitar tecnologias legadas, mas upgrades exigem provas e migrações.

## 2. Decisão aprovada

Adotar **monorepo com um backend inicialmente implantado como monólito modular**; cada bounded context é um módulo com entidades, regras, casos de uso, portas públicas, adaptadores e testes independentes. A instância PostgreSQL inicialmente pode ser única, com schemas/tabelas **propriedade de um domínio**. Interfaces web de administração e PDV podem ser logicamente separadas — ADR-005 escolherá layout/deploy.

**Não implantar microserviços físicos no MVP por padrão.** Extração posterior exige motivação mensurável e uma nova ADR aprovada, com plano de migração, compatibilidade, resiliência, consistência, observabilidade, custos e testes.

### 2.1 Regras arquiteturais obrigatórias

**ARC-R01 — Isolamento:** o núcleo de domínio não importa FastAPI, ORM, HTTP, infraestrutura, UI ou classes privadas de outro domínio. Compartilhar entidade de negócio em “shared” é proibido.

**ARC-R02 — Contratos internos:** interações entre domínios usam interface pública de aplicação (ports/commands/queries tipados) ou evento versionado. Código de Sales não executa SQL em tabelas privadas de Inventory.

**ARC-R03 — Ownership de dados:** cada schema/tabela, migração e índice tem módulo dono. Banco físico único não significa compartilhamento irrestrito. Acesso cruzado exige contrato e revisão.

**ARC-R04 — Grafo de dependências:** proibir ciclos. Testes automáticos devem detectar imports proibidos e dependências de infraestrutura invertidas.

**ARC-R05 — Deploy:** começar com **uma unidade de backend**, sem Dockerfile/processo por domínio. Compose local pode incluir esse backend, PostgreSQL e UIs conforme necessidade.

**ARC-R06 — Restrições de infraestrutura:** sem Kubernetes, service mesh, gateway dedicado, broker obrigatório, bancos por serviço ou cloud por antecipação. A ausência desses recursos não limita design de contratos.

**ARC-R07 — Consistência crítica:** ADR-001 **não decide** a transação de Sales + Inventory + Payments/Cash + Audit. Só ADR-002 aprovada pode defini-la. Nenhuma operação distribuída presume atomicidade global.

**ARC-R08 — Leitura e projeções:** Reporting pode manter projeções reconstruíveis, versões, checkpoints e status de atualização; não é fonte de verdade transacional.

**ARC-R09 — Contratos públicos:** REST/eventos/exportações possuem schema versionado, testes de contrato, deprecação documentada e correlação.

**ARC-R10 — Segurança/custo:** fixtures sintéticas, credenciais fora do Git, pagamentos somente simulados, nenhuma API paga/conta/cartão/trial necessário, nenhuma afirmação de produção fiscal ou bancária.

### 2.2 Estrutura lógica

```text
       apps/admin-web      apps/pos-web
              \             /
                 HTTP /v1
                     |
           +----------------------+
           | Um backend modular   |
           +----------------------+
           | IAM       | Catalog  |
           | Procurement|Inventory|
           | Sales     | Payments |
           | Reporting | Audit    |
           +----------------------+
                     |
        +-------------------------+
        | PostgreSQL local        |
        | Schemas com ownership   |
        | + outbox se necessário  |
        +-------------------------+
                     |
           projeções/exports
                  BDI futuro
```

Exemplo lógico de namespace: `backend/mt_sgi/{identity,catalog,procurement,inventory,sales,payments,reporting,audit}/` com camadas `domain/application/ports/adapters`. A estrutura física será criada na Fase F1; não se presume que já exista.

## 3. Alternativas estudadas

| Alternativa | Benefícios | Custos/riscos | Veredito |
|---|---|---|---|
| A — Microserviços físicos desde dia 1 | deploy independente, isolamento de runtime, escala seletiva | rede, sagas, broker, monitoramento, contratos distribuídos, aumento de falhas, custo de operação e CI | **REJEITADA para MVP** |
| B — Monólito sem fronteiras | entrega inicial rápida, um deploy, um banco | acoplamento, regras espalhadas, dependências circulares, extração cara, evolução tipo legado | **REJEITADA** |
| C — Monólito modular com extração progressiva | transações locais disponíveis, testes simples, ownership e migração planejada, R$ 0 | disciplina contínua para não virar monólito acoplado; deploy conjunto | **ACEITA** |

A aprovação não implica que serviços físicos sejam objetivo obrigatório. Se o produto continuar sustentável como monólito modular, não extrair por estética ou marketing.

## 4. Impactos específicos dos domínios

| Módulo | Contrato de fronteira | Efeito da decisão / extração |
|---|---|---|
| Identity | autenticar, autorizar e gerenciar sessão por interface pública | não acoplar cliente a schema de usuário; extração só com plano de indisponibilidade de auth |
| Catalog | consulta tipada de produto, unidade e preço em vigência | snapshot no Sales protege histórico; extração comparativamente simples |
| Procurement | recebimento confirmado e comando público de entrada no estoque | idempotência de recebimento e ownership de item; risco de duplicar entrada |
| Inventory | reservar, consultar, consumir, repor e reconciliar via portas | extração **crítica**: exige nova semântica de consistência/compensação |
| Sales | comando idempotente de venda e devolução, snapshot histórico | **crítico** por coordenação de estoque/caixa; não extrair sem falhas e carga comprovadas |
| Payments & Cash | registros **simulados**, sessões e fechamento/reconciliação | **crítico** por consistência financeira; operação real fora de escopo |
| Reporting | projeções e exportações read-only, sem SQL privado | **primeiro candidato preferencial** para extração, se justificável e R$ 0 |
| Audit | append auditável e consulta segregada | persistência/recuperação de auditoria crítica; risco de inconsistência se extrair prematuramente |

Extração sugerida, sem compromisso: **Reporting → Catalog → Procurement**; **Inventory/Sales/Payments** apenas após evidências rigorosas. Identity e Audit são sensíveis a segurança/resiliência e não seguem ordem automática.

## 5. Regras de dados e integração

- Um único PostgreSQL é permitido inicialmente, mas domínio de negócio nunca consulta tabela privada alheia por conveniência.
- Shared kernel mínimo: IDs, dinheiro, tempo e erros genéricos quando estritamente necessários. Não mover `Sale`, `StockMovement` ou modelos ORM para pacote comum.
- Em uma transação local compartilhada por adaptadores, a propriedade da ação e dos dados continua do domínio; UoW concreta, lock/rollback e auditoria dependerão de ADR-002.
- Mensagens de integração devem carregar `event_id`, `event_type`, `schema_version`, `aggregate_id`, `aggregate_version`, `occurred_at`, `correlation_id`, `causation_id`, `producer`, `payload` mínimo.
- Outbox/inbox podem ser usados no mesmo banco quando exigidos. Entrega **at least once**, consumidor idempotente; não prometer “exactly once” fim a fim.
- Relatórios devem informar período, fuso, moeda, regra de devoluções, versão da projeção e instante de atualização.

## 6. Condições para permitir extração de microserviços físicos

**Uma nova ADR só pode aprovar extração se todos os pontos seguintes forem demonstrados:**

1. Motivação medida: escala diferencial, isolamento de segurança, latência, autonomia de deploy, fronteira regulatória ou falhas independentes.
2. Ownership de schema e contrato público estável, versionado e testado; ausência de SQL privado/interação acoplada.
3. Análise das transações interdomínio e respectivas invariantes após a separação.
4. Política de timeout, idempotência, retry limitado, duplicidade, ordem, compensação e reconciliação para operações afetadas.
5. Plano de migração de dados e tráfego por expand-and-contract, rollback/restore, duração e validação.
6. Testes de contrato/provedor/consumidor, carga, caos, concorrência e recuperação com resultado mensurado.
7. Observabilidade verificável, métricas de lag/falha, health checks, trace/correlation IDs e runbook.
8. Cálculo de custo real e confirmação de que o novo desenho continua **R$ 0** dentro do escopo do projeto.
9. Plano operacional de manutenção de múltiplos serviços que não crie dependência externa paga.
10. Aprovação expressa (go/no-go) do responsável pelo produto após revisão da ADR.

Apenas separar pastas ou containers **não demonstra** microserviços legítimos.

## 7. Trade-offs e mitigação

**Ganhos:** implementação inicial menos complexa; ambiente local repetível; melhor oportunidade de transações ACID; menor superfície de ataque/ops; fronteiras testáveis; caminho evolutivo sem sistema legado descontrolado.

**Custos:** deploy conjunto do backend; isolamento de runtime limitado; risco de importação cruzada com crescimento; índice e schema compartilhados requerem disciplina; futura extração ainda demanda trabalho de dados/consistência.

**Mitigações:** teste de grafo e imports; contratos/ownership público; verificação de migrations; PRs pequenos; medição de acoplamento; atualização de runtime suportada; ADR por extração; backup e restore testados.

## 8. Critérios de aceite (decisão aceita, evidência pendente)

| ID | Critério verificável | Evidência exigida | Estado |
|---|---|---|---|
| ARC-001 | Contextos e owners documentados | SDD-001/002 | **ESPECIFICADO**, não codificado |
| ARC-002 | Backend inicial único modular | diagrama, compose e execução | **DECIDIDO**, não executado |
| ARC-003 | Sem imports/SQL privados cruzados | testes arquiteturais + revisão | PENDENTE |
| ARC-004 | Sem ciclos entre módulos | teste de grafo em CI | PENDENTE |
| ARC-005 | Schema/migração por ownership | migrações e mapa de proprietário | PENDENTE |
| ARC-006 | API/evento versionado com contrato | OpenAPI/JSON schema e testes | PENDENTE |
| ARC-007 | Invariantes venda/estoque/caixa comprovadas | ADR-002 aceita + testes | **BLOQUEADO** por ADR-002 |
| ARC-008 | Execução local com custo zero | setup e CI sem cobrança | PENDENTE |
| ARC-009 | Extração só com ADR, migração e prova | política aprovada; execução futura | REGRA ACEITA |
| ARC-010 | Segurança, auditoria e observabilidade | scanners, testes RBAC, logs correlacionados | PENDENTE |

**Condição de encerramento:** esta ADR contém a **decisão aprovada**, mas permanecerá com critérios de implementação abertos até evidências reais no repositório. Não criar selo “concluída” por ter escrito o texto.

## 9. Políticas de evolução

- Alterações de linguagem, runtime, banco, framework central, topologia de deploy, broker, consistência ou extração exigem atualização coordenada do SDD e ADR específica.
- Repositório com lockfiles, pins, análise de CVEs/licenças e testes de compatibilidade em upgrades.
- Sem componentes EOL; patch dentro da linha pode ser atualizado após testes, major tem plano formal.
- Compatibilidade de API/evento é expand-and-contract; deprecações com prazo e rastreio.
- Sustentabilidade de custos revisada antes de adicionar serviços externos.

## 10. Decisões não tomadas aqui

- **ADR-002 (PROPOSTA):** limite ACID, concorrência, retries, pagamentos simulados, reconciliação e reversões.
- **ADR-003 (PENDENTE):** infraestrutura de demo e evidências de custo zero.
- **ADR-004 (PENDENTE):** método de CMV, unidade/embalagem, escalas e arredondamentos.
- **ADR-005 (PENDENTE):** topologia frontend e sessão.
- Demais decisões de RBAC detalhado, contratos finais e retenção seguem a governança SDD.

**Próxima etapa de decisão:** revisão da ADR-002; **não** iniciar implementação de venda/estoque antes de sua aprovação.
