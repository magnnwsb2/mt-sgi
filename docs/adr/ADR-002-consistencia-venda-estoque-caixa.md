# ADR-002 — Consistência transacional entre venda, estoque, pagamentos simulados e caixa

| Campo | Valor |
|---|---|
| Produto | MT SGI |
| Identificador | ADR-002 |
| Estado | **PROPOSTA — NÃO ACEITA; exige aprovação expressa** |
| Proposta registrada | 2026-11-08 |
| Versão | 0.1.0 |
| Decisão anterior | ADR-001 ACEITA: monólito modular inicialmente |
| Escopo | Venda em PDV, baixa/concorrência de estoque, pagamento simulado, sessão de caixa, auditoria, idempotência, eventos e reversão |
| Dependência cruzada | ADR-004 para unidade, arredondamento e custo histórico |
| Limite absoluto | Apenas operações fictícias, dados sintéticos, R$ 0 de custo |

> **Não implementar esta ADR enquanto não for explicitamente aprovada.** A ADR-001 garante a organização modular, mas **não** resolveu os limites transacionais. Este documento fornece uma alternativa recomendada e os trade-offs para escolha consciente.

## 1. Problema

Uma venda comercial precisa registrar seus itens e totais, retirar unidades do estoque, guardar o pagamento **simulado**, associar o caixa, auditar o evento e evitar duplicidade após reenvio. Se uma parte confirmar e outra falhar, a plataforma pode informar venda inexistente, aceitar estoque negativo, duplicar baixa ou apresentar caixa inconsistente. O sistema terá diversos operadores/terminais concorrentes e está sujeito a quedas de processo, latência e respostas HTTP perdidas.

Não existe pagamento bancário real no MVP. “Pagamento confirmado” significa apenas **registro administrativo/simulado**; não significa autorização de adquirente, liquidação, liquidez financeira real ou operação fiscal.

## 2. Objetivos e invariantes

- **TX-001 — Atomicidade local:** venda confirmada, itens, saída de estoque, pagamentos simulados, lançamento de caixa, auditoria crítica, chave idempotente e outbox necessária persistem como unidade ou nenhum efeito persiste.
- **TX-002 — Exclusividade:** reenvios concorrentes com mesma intenção e mesma chave produzem uma única venda.
- **TX-003 — Estoque não negativo:** duas vendas simultâneas não podem consumir a mesma última unidade, nem criar disponibilidade negativa.
- **TX-004 — Cálculo confiável:** total de itens/descontos, valor do pagamento e troco simulado (se permitido) reconciliáveis; dinheiro exato, não float.
- **TX-005 — Caixa válido:** a venda exige sessão de caixa aberta e elegível, associada ao operador/terminal/loja de modo verificável.
- **TX-006 — Integridade histórica:** preços, custos e conversões permanecem fixados nos itens da venda; estoque/auditoria são lançamentos compensáveis, não sobrescritas silenciosas.
- **TX-007 — Recuperação:** timeout após commit pode ser consultado/repetido sem nova operação; falha antes do commit não gera meia venda.
- **TX-008 — Reproducibilidade:** tests de concorrência, falha, reconciliação e recovery executáveis localmente, sem rede ou serviço pago.

## 3. Alternativas consideradas

| Opção | Descrição | Benefícios | Custos e riscos |
|---|---|---|---|
| A — **PostgreSQL ACID local / UoW** | todos os efeitos transacionais críticos são persistidos na **mesma transação física do banco** por portas de aplicação dos módulos | rollback completo, locking forte, menos infraestrutura, consistente com ADR-001 | domínio Sales pode orquestrar coordenação; futuras extrações exigirão redesign de consistência |
| B — Saga de serviços físicos | módulos comunicam por mensagens/rede, persistência separada, compensações e retries | autonomia de serviços; integração externa natural | falha parcial, conciliação complexa, eventual inconsistency, observabilidade e múltiplos deploys; não justificada no MVP |
| C — várias transações locais sem coordenação | venda salva, estoque baixa, pagamento/caixa depois em commits separados | implementação aparentemente simples | **inaceitável:** venda parcialmente persistida, duplicidade e reconciliação difícil |

**Recomendação para aprovação:** **A — transação local ACID PostgreSQL, mantendo fronteiras modulares e outbox transacional apenas quando houver consumidor assíncrono**. B somente após extração física autorizada por nova ADR; C rejeitar.

## 4. Desenho detalhado proposto

### 4.1 Limite da transação e ownership

Um comando de aplicação de Sales/Checkout coordena portas públicas de Inventory, Payments/Cash e Audit, sob uma `UnitOfWork` transacional concreta do backend PostgreSQL. Cada domínio continua dono de suas regras, consultas e persistências privadas; a infraestrutura compartilha um **mesmo contexto de transação** apenas na fronteira autorizada. A API não deve importar SQL de módulos alheios. Rejeitar transações “aninhadas” independentes que poderiam confirmar parcialmente.

**Início da transação:** após autenticação e validação sintática de HTTP, sem confiar em totais fornecidos pelo cliente.

**Commit único proposto:** somente depois de validar disponibilidade, preços/unidades, sessão, pagamento simulado, persistir venda/itens/snapshots, escrever movimentos/posições de estoque, registro de pagamento, movimento de caixa, auditoria, registro idempotente e evento outbox necessário. Qualquer erro antes do commit faz **rollback de todos os efeitos**. A resposta só pode declarar CONCLUÍDA após confirmação do commit.

**I/O externo:** não realizar requisições HTTP, integração bancária, envio de e-mail ou publicação direta a broker antes/de dentro do commit. Eventos assíncronos externos, se houver, são publicados depois a partir de outbox.

### 4.2 Fluxo proposto de checkout

1. Validar sessão/autorização, loja/terminal/caixa e schema de request.
2. Exigir `Idempotency-Key` e canonicalizar payload (itens e quantidades, métodos simulados, loja/caixa, descontos elegíveis). Calcular hash estável.
3. Abrir transação PostgreSQL e garantir unicidade/contenção por `(store_id, operation_type, idempotency_key)`.
4. Se a chave já existir com mesmo hash e resultado final, devolver a resposta previamente armazenada; se divergir, responder **409** sem novos efeitos. Para operação em andamento concorrente, aguardar lock por tempo limitado ou retornar conflito/retry documentado.
5. Travar sessão de caixa aplicável e verificar `OPEN`, loja, terminal e operador autorizado; garantir que fechamento não aconteça simultaneamente sem coordenação.
6. Obter versões de catálogo/preço e conversão elegíveis. Determinar quantidade em unidade-base; calcular totais no backend e snapshots de preço/custo conforme ADR-004.
7. Travar/atualizar posições de estoque de todos os itens em ordem determinística (ex.: por localização e ID de produto) para reduzir deadlock; rejeitar qualquer quantidade indisponível.
8. Persistir `Sale`, `SaleItem`, decrementos de posição e `StockMovement` por lote; garantir referências de origem únicas e consistentes.
9. Registrar valores e métodos de pagamento **simulados**, lançamentos de caixa e auditoria necessária. Exigir reconciliação dos valores pela política aprovada.
10. Persistir estado idempotente completo/resposta reexecutável e evento outbox quando eventos integrarem o fluxo.
11. Confirmar **um commit**, então devolver o resultado. Se a confirmação do commit ao cliente for perdida, o retry pela chave recupera o resultado durável.

**Ordem de locks:** fixar um ordenamento global entre caixa, registro de idempotência e produtos, documentar e testar deadlocks. Não adquirir locks em ordem dependente da ordem enviada pelo usuário.

### 4.3 Estoque, reservas e concorrência

A posição física é respaldada pelo ledger append-only. Cada posição `(location_id, product_id)` precisa de chave única e criação segura contra corrida (row lock/UPSERT com constraint). A autorização de consumo deve ser protegida por escrita condicional sob lock, nunca pela sequência frágil “consultar saldo e depois atualizar sem isolamento”. Checar quantidades e reservas ativas sob a mesma fronteira.

**Proposta para checkout instantâneo do MVP:** não manter reserva longa para carrinho aberto; validar e consumir em fechamento ACID. Se o produto exigir venda com reserva durável prévia, isso exigirá subespecificação: timeout, expiração, reenvio, liberação e reconciliação sem dupla reserva. A entidade `StockReservation` é prevista, **mas não deve ser implementada por antecipação sem caso de uso aprovado**.

Para o mesmo produto em múltiplas linhas, agregar quantidade-base por localização antes do locking; impedir *oversell* e múltipla baixa. Estoque de múltiplos produtos segue **all-or-nothing**: se um item falhar, nenhum item da venda é consumido.

### 4.4 Idempotência robusta

**Chave obrigatória** para criação de venda; proposta de escopo durável `(store_id, operation_type, key)`, com índice único. A chave deve ser gerada por cliente a cada **intenção** de nova venda; retry da mesma intenção reutiliza a chave. Identidade do ator e do caixa integram o hash e política de autorização, para impedir reutilização abusiva.

- Hash do payload **canonicalizado**, incluindo itens normalizados, unidades, quantidades, descontos e pagamentos simulados. Ordenação/normalização deve ser determinística; nunca hashear JSON bruto se diferenças triviais de ordem/whitespace mudarem semântica.
- Se chave e hash iguais e venda concluída: retornar resposta semanticamente equivalente com mesmo `sale_id`; código 200/201 e header de replay devem ser formalizados no OpenAPI.
- Se chave igual e hash diferente: 409 `IDEMPOTENCY_PAYLOAD_CONFLICT` sem alteração de banco.
- Se operação anterior abortou antes do commit: nova tentativa pode prosseguir normalmente, sem registro parcial.
- Se concorrência no mesmo registro: controle por unicidade transacional + locks/consulta de estado, sem duas vendas.
- **Retenção da chave proposta:** sem expiração automática durante vida útil dos registros da demo. Qualquer TTL futuro exige regra de deduplicação que impeça repetir venda após expiração; exclusão do registro em produção não é decisão livre.
- Se falhar após commit mas antes da resposta: retransmissão obtém resultado persistido; não reexecuta baixa.
- Não usar Redis em memória como único dono da idempotência crítica.

### 4.5 Pagamentos simulados, descontos, troco e sessão de caixa

**Política proposta para deliberação:**
- Métodos: `CASH_SIMULATED`, `PIX_SIMULATED`, `CARD_SIMULATED`.
- Pagamentos fracionados são **candidatos**, não decisão final; com múltiplos registros, valor total aprovado deve cobrir o líquido exato. A decisão sobre métodos mistos, número de parcelas e troco será explicitada com o responsável.
- **Troco** (somente dinheiro simulado) deve ser contabilizado separadamente como valor recebido menos total devido e refletir lançamentos reconciliáveis; rejeitar sobrepagamento com PIX/cartão simulados por padrão.
- Desconto requer política por papel, limite e origem; total jamais confiado ao frontend.
- Se caixa está CLOSED ou foi fechado simultaneamente, não permitir nova venda; fechamento também bloqueia/consulta operações em andamento.
- Dinheiro de gaveta esperado é calculado por movimentações **de caixa físico simulado**, não por todos métodos PIX/cartão como se fossem notas dentro da gaveta.
- Relatórios de transações eletrônicas simuladas são distintos da reconciliação de dinheiro em espécie.
- Não presumir reembolso bancário ao cancelar; gerar registro de estorno **simulado** e manter histórico.

**Pontos abertos:** (a) pagamento único vs misto; (b) troco e métodos eletrônicos; (c) caixa por operador ou por terminal; (d) fechamento de caixa com devolução posterior; (e) política de desconto. Sem aprovação, a proposta não autoriza comportamento arbitrário.

### 4.6 Cancelamento, devoluções e ajustes compensatórios

Não apagar nem reabrir fisicamente a venda concluída. Um comando específico com `Idempotency-Key` própria, razão, autorização, referência original e versionamento verifica elegibilidade. No mesmo limite transacional aprovado, persistir evento de cancelamento/devolução, movimento reverso de estoque quando mercadoria efetivamente retornou em condições vendáveis, registros simulados de estorno, ajustes de caixa e auditoria.

**Devolução parcial:** não exceder quantidade originalmente vendida menos devoluções anteriores; proteção por concorrência. Mercadoria avariada não retorna automaticamente ao estoque vendável. A política de custo reverso deve usar custo histórico conforme ADR-004.

**Caixa já fechado:** não editar lançamentos de sessão encerrada; gerar evento/ajuste em sessão atual ou processo de reconciliação excepcional conforme regra **a aprovar**. Troco/estorno pós-fechamento também dependem dessa política.

## 5. Outbox, relatórios e eventos

Se o fluxo exigir projeções assíncronas ou exportações, gravar evento outbox na **mesma transação** da venda, sem publicar externamente antes do commit. Worker local pode ler eventos pendentes com locking apropriado e registrar `published_at`/checkpoint; em caso de crash, reentregar. Consumidor deduplica por `event_id` e protege versão do agregado.

**Garantia:** efeitos críticos no banco são atômicos dentro do limite PostgreSQL; emissão/consumo de evento entre processos é **at least once** com deduplicação, não transação distribuída global. Projeção Reporting pode ficar defasada mas precisa ser reconstruível e exibir timestamp/lag.

Se não houver consumidor real no primeiro passo de produto, não é necessário inventar worker/broker apenas para criar complexidade.

## 6. Matriz de falha e recuperação

| Falha injetada | Resultado esperado |
|---|---|
| Schema inválido antes da transação | 400/422, nenhuma escrita |
| Falta de autorização | 401/403, nenhuma escrita |
| Estoque insuficiente em um dos itens | 409, rollback integral da venda |
| Outra venda consome a última unidade | só uma conclui, posição nunca negativa |
| Sessão fechada antes da autorização | 409, sem efeito |
| Fechamento de caixa concorre com venda | serialização lógica/lock, não existe venda “fora de caixa” |
| Duplicata mesma chave/payload, concorrente | um `sale_id`; nenhum segundo estoque/pagamento |
| Mesma chave, payload divergente | 409, nenhuma operação nova |
| Exceção durante gravação de movimentos | rollback também de venda, pagamento, auditoria e outbox |
| Crash após commit, antes da resposta | retry devolve `sale_id` já persistido |
| Deadlock / timeout do DB | rollback; retry limitado e seguro somente após estado idempotente consultável |
| Crash do worker da outbox após publicação | reentrega, consumidor deduplica efeito |
| Projeção Reporting atrasada | `refreshed_at`/lag indicados, ledger transacional intacto |
| Cancelamento repetido/concor­rente | no máximo uma compensação por intenção/origem |
| Falha no cálculo do preço/custo | operação rejeitada, nenhuma venda |
| Falha em restore/migração | não marcar release concluída; restaurar backup e investigar |

## 7. Testes e critérios de aceite exigidos

| ID | Critério | Evidência |
|---|---|---|
| TXA-001 | Commit único garante all-or-nothing | teste de rollback em cada ponto de gravação |
| TXA-002 | 1.000 tentativas simultâneas de mesma chave não duplicam venda | teste em PostgreSQL real, 1 venda/1 baixa/1 conjunto de pagamentos |
| TXA-003 | Payload divergente com chave igual retorna 409 | contrato HTTP + verificação de banco |
| TXA-004 | Última unidade disputada por terminais distintos não gera negativo | stress multi-processo/threads contra DB real |
| TXA-005 | Quantidade de vários itens é atômica | falta de um item impede consumo dos demais |
| TXA-006 | Caixa fechado e fechamento concorrente impedem venda inválida | testes de lock e matrizes de estado |
| TXA-007 | Pagamento simulado reconcilia total/troco conforme política aprovada | casos tabela de pagamentos + cash ledger |
| TXA-008 | Custo e preço persistem em snapshots; alteração futura não muda venda passada | testes de histórico e migrations |
| TXA-009 | Falha/crash no commit e resposta perdida são recuperáveis | teste de injeção de falhas e idempotência |
| TXA-010 | Cancelamentos/devoluções não apagam trilha nem duplicam reversões | testes de compensação e autorização |
| TXA-011 | Auditoria/outbox persistem na mesma transação quando exigidas | injeção de falha antes/após commit |
| TXA-012 | Projeções reprocessáveis e deduplicadas | teste de reentrega + reconciliação |
| TXA-013 | Nenhuma chamada financeira externa é efetuada | teste de isolamento de rede/fixtures |
| TXA-014 | Zero uso de float para dinheiro e conversões exatas | propriedades e casos de arredondamento ADR-004 |

**Estado de todos os TXA:** PENDENTE. Estes itens não estão testados/implementados pelo registro de proposta.

## 8. Trade-offs, riscos e planos de migração

**Vantagens da opção A:** simplifica consistência do MVP; permite teste de dados reais do PostgreSQL sem rede de microserviços; evita inconsistências entre venda e caixa; reduz infraestrutura e facilita custo zero.

**Desvantagens:** todos os efeitos críticos ainda compartilham banco físico, aumentando contenção; necessidade de ordenar locks; domínio orquestrador precisa delimitar dependências; uptime e deploy do backend são conjuntos; extração futura de Inventory ou Payments altera semântica de consistência.

**Mitigações:** UoW explícita, ownership, contratos, testes de concorrência, benchmark, rastreabilidade de problemas, separação de consultas/projeções, ADR nova com saga quando houver extração; nunca dividir transação sem novo desenho.

**Mudança posterior para microserviço:** exige decidir *onde* a venda é oficialmente confirmada, reservas com expiração, saga, compensação, estado pendente, entrega de mensagens, DLQ, reconciliação e testes com falhas de rede. Não assumir que SQL local consegue atravessar serviços físicos.

## 9. Questões a aprovar antes de mudar estado para ACEITA

1. **Limite transacional:** aprovar PostgreSQL local ACID + UnitOfWork compartilhada via portas no MVP?
2. **Política de reserva:** no checkout instantâneo, confirmar sem reserva longa de carrinho (reserva durável fica fora do MVP)?
3. **Métodos/troco:** permitir pagamentos mistos e troco simulado, ou começar com uma modalidade por venda?
4. **Caixa:** sessão exclusiva por terminal, com operador identificado, e rejeição de venda após fechamento?
5. **Cancelamento/devolução:** primeiro MVP suporta cancelamento completo; devolução parcial pode ser fase posterior? Qual o fluxo de caixa se sessão fechada?
6. **Custos/unidades:** alinhar cálculos com ADR-004 antes do código; nunca “chutar” custos de margem.
7. **Status HTTP de replay/timeout e retenção idempotente:** finalizar no OpenAPI antes da implementação.

**Recomendação técnica:** aprovar alternativa A como modelo de consistência; manter demais políticas de negócio explicitamente pendentes até deliberação.

## 10. Estado e próximas ações

- **Status:** PROPOSTA. Não possui aprovação explícita, commit de código de negócio nem evidência de testes.
- **Ação segura seguinte:** apresentar ao responsável os trade-offs e perguntas da seção 9, atualizar documentação com decisão formal e somente então especificar contratos finais e testes.
- **Não fazer:** implementar backend de vendas, declarar garantia de atomicidade já alcançada, criar broker sem ADR ou habilitar pagamentos reais.

**Rastreabilidade:** SDD-001 (sec. 4–6, 13); SDD-002 (Sales/Inventory/Payments, cenários CEN-005..013); SDD-003 (testes/segurança/custo); ADR-001 (arquitetura).
