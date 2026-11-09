# MT SGI — SDD-002: Domínios, Regras de Negócio, Contratos e Dados

| Campo | Valor |
|---|---|
| Documento | SDD-002, anexo integrante do SDD-001 |
| Versão | 0.1.0 — **PROPOSTA** |
| Contexto | MT Sistema de Gestão Integrada / comércio geral / PDV |
| Estado | Rascunho normativo sujeito à aprovação da baseline global |
| Precedência | SDD-001; ADRs aceitas aplicáveis |
| Bloqueios | ADR-002 transação; ADR-004 custeio/unidades; ADR-005 desenho detalhado UI |

> **ATENÇÃO:** Entidades, operações e fluxos a seguir especificam intenção de negócio e contratos propostos. Nenhuma tabela, endpoint, schema ou teste está implementado por existir neste documento. O responsável aprova decisões pendentes antes de sua materialização.

## 1. Glossário de domínio e semântica

| Termo | Definição operacional |
|---|---|
| Loja/estabelecimento | unidade operacional fictícia onde se vendem produtos; não representa tenant SaaS |
| Local de estoque | armazém/depósito/área de venda dentro de uma loja; posições devem ser identificadas |
| Produto | entidade comercial com SKU, unidade-base, status e histórico de preço; produto inativo não pode entrar em nova venda |
| SKU | identificador de comercialização, único no escopo definido e com política de normalização |
| Código de barras | identificador opcional, precisa regra de unicidade e tratamento de colisão |
| Unidade-base | menor unidade controlada pelo estoque; ex.: UN, KG, L, com escala validada |
| Embalagem | múltiplo ou fração de unidade-base, conversion factor versionado |
| Estoque físico | posição conciliável a partir de todas movimentações válidas |
| Reserva | alocação temporária que reduz o disponível sem necessariamente gerar baixa física |
| Estoque disponível | físico menos reservas elegíveis; nunca negativo por padrão |
| Pedido de compra | compromisso/planejamento de aquisição, não entrada automática no saldo |
| Recebimento | comprovação da quantidade aceita, gatilho para movimentação de entrada |
| Venda | transação comercial simulada com snapshot de preços, custos, itens e estado |
| Pagamento simulado | informação de método e valor, **sem qualquer transferência real de dinheiro** |
| Sessão de caixa | intervalo aberto por operador/terminal; base para reconciliação |
| Movimento de caixa | lançamento rastreável de entrada/saída/ajuste autorizado; não é extrato bancário |
| CMV | custo das mercadorias vendidas, conforme método e política definidos na ADR-004 |
| Margem bruta | receita líquida da venda menos CMV, sem afirmar lucro líquido |
| Evento de auditoria | registro rastreável de ação sensível; não é substituto para log técnico |
| Evento de integração | mensagem de negócio versionada; pode ser entregue mais de uma vez |
| BDI | Business Decision Intelligence, produto separado, consumidor analítico futuro |

## 2. Ownership de domínio, APIs internas e dependências

**Regra global:** cada módulo gerencia suas invariantes e dados privados; comunicação entre domínios por *ports* públicas e contratos documentados. Não há permissão implícita de leitura/edição de tabelas internas por outro módulo. A transação técnica comum no monólito será decidida na ADR-002 sem abolir ownership.

### 2.1 Identity & Access — IAM

**Ownership:** usuários fictícios, credenciais com hash, papéis, permissões, políticas de acesso, sessões. Define autenticação e decisão de autorização; outro domínio solicita autorização e não consulta diretamente tabela de usuário.

**Operações propostas:** `authenticate`, `authorize(actor, action, resource, store_id)`, `create_user`, `assign_role`, `revoke_session`. É obrigatória a distinção 401 (não autenticado) e 403 (autenticado sem permissão).

**Regras:** negação por padrão; não armazenar credenciais claras; auditoria de login, mudança de papel e ação privilegiada; usuário inativado não emite operações novas; tokens/sessões não são registrados em logs. Matriz completa de ações x papel ainda depende de refinamento.

**Eventos possíveis:** `iam.user.deactivated.v1` e `iam.role.changed.v1`, se houver consumidor concreto.

### 2.2 Catalog

**Ownership:** `Product`, `Category`, `Unit`, `PackagingDefinition`, `Barcode`, `PriceListEntry`; proposta de gestão de preços e validade temporal.

**Operações públicas:** `get_product`, `search_products`, `get_current_price(product_id, at)`, `set_price`, `deactivate_product`, `resolve_barcode`, `get_unit_conversion`.

**Invariantes propostas:**
- CAT-001: SKU único por escopo; nunca reutilizar código de produto histórico sem regra de migração.
- CAT-002: preço vigente em BRL, não negativo, com intervalo de vigência sem sobreposição por produto/tabela.
- CAT-003: desativação não apaga histórico de vendas nem pode invalidar snapshot passado.
- CAT-004: mudança de embalagem/medida cria nova versão; venda/recebimento guardam fator efetivamente utilizado.
- CAT-005: código de barras informado deve ter normalização, controle de duplicação e resposta de ambiguidade.

**Risco de projeto:** múltiplas tabelas de preço, promoções, descontos e impostos simulados exigem políticas antes de entrar em uso; não presumir cálculos fiscais.

### 2.3 Procurement

**Ownership:** `Supplier`, `PurchaseOrder`, `PurchaseOrderItem`, `GoodsReceipt`, `GoodsReceiptItem`. Receber não é sinônimo de pagar fornecedor.

**Ciclo proposto:** pedido RASCUNHO → APROVADO → PARCIALMENTE_RECEBIDO → RECEBIDO; CANCELADO para pedido ainda elegível conforme autorização. Recebimento pode ser parcial, mas não pode contabilizar mesma unidade recebida duas vezes.

**Operações públicas:** `create_purchase_order`, `approve_purchase_order`, `register_receipt`, `cancel_order`, `get_receipt`. O recebimento aceito envia comando público ao Inventory, com chave de deduplicação; não persiste tabela privada de estoque.

**Invariantes:**
- PUR-001: quantidades de pedido e recebimento com unidade/fator explícitos.
- PUR-002: recebimento repetido com a mesma identidade operacional não duplica entradas.
- PUR-003: estoque só aumenta quando recebimento for confirmado e invariantes satisfeitas.
- PUR-004: divergência de quantidade/custo entre pedido e recebimento exige registro de motivo e política explícita.
- PUR-005: custo unitário/custo de aquisição devem ser guardados com precisão definida pela ADR-004.

### 2.4 Inventory

**Ownership:** `StockMovement`, `StockReservation`, `StockPosition` (cache/projeção operacional reconciliável), localização e contagem/ajuste.

**Operações públicas:** `get_availability`, `reserve`, `release_reservation`, `commit_consumption`, `receive_goods`, `adjust_stock`, `reconcile_stock`. Contratos serão refinados pela ADR-002.

**Invariantes:**
- INV-001: disponível = físico − reservas ativas; nunca negativo se política não permitir venda sem estoque.
- INV-002: movimento append-only com origem, correlação, ator, unidade e quantidade exata; estorno cria movimento inverso.
- INV-003: reserva não é baixa física; uma reserva consumida não pode voltar a ser consumida.
- INV-004: saída não supera saldo disponível; concorrência deve ser protegida na **persistência**, não apenas por pré-consulta.
- INV-005: posições derivadas correspondem à soma de lançamentos + política de saldo inicial autorizada; reconciliação detecta divergências.
- INV-006: cada movimentação originada em recebimento/venda/retorno tem referência de origem deduplicável.
- INV-007: ajuste manual exige permissão, razão, unidade, quantidade e trilha de auditoria.

**Concorrência:** reservar primeiro não resolve corridas se a escrita final não tiver lock/constraint/controle transacional adequados. Testes simultâneos devem simular múltiplos terminais com o último item disponível.

### 2.5 Sales / POS

**Ownership:** `Sale`, `SaleItem`, `SaleAdjustment`, `SaleReturn`, `SaleReturnItem`, políticas de operação e snapshots de preços/custos; terminal físico/lógico como referência operacional, sem controlar dados privados do caixa.

**Operações propostas:** `quote_sale`, `complete_sale`, `get_sale`, `cancel_sale`, `return_items`, `get_receipt_non_fiscal`.

**Estados propostos:** INICIADA → CONCLUÍDA; REJEITADA em falha antes de confirmação; CANCELADA/DEVOLVIDA_PARCIAL/DEVOLVIDA_TOTAL são transições auditáveis após conclusão, não exclusões. Estados exatos exigem aprovação ADR-002.

**Invariantes:**
- SAL-001: mesma chave idempotente e mesma intenção comercial retorna uma única venda; conflito se payload divergir.
- SAL-002: venda concluída tem itens, quantidades, preços/custos históricos, descontos, total e caixa corretos.
- SAL-003: toda linha usa identificador/versão de unidade e fator de conversão no instante da operação.
- SAL-004: confirmação não deixa “meia venda”: políticas de transação e recuperação da ADR-002.
- SAL-005: cancelamento/devolução tem motivo, autor, referência à venda original e lançamentos compensatórios.
- SAL-006: venda concluída não pode depender de preço/custo atual para reproduzir totais históricos.
- SAL-007: uma venda não pode ser registrada por operador sem sessão/escopo de caixa elegível.

### 2.6 Payments & Cash

**Ownership:** `PaymentRecord`, `CashSession`, `CashMovement`, `CashReconciliation`; pagamentos simulados, não dados bancários.

**Operações públicas:** `open_cash_session`, `get_cash_status`, `record_simulated_payment`, `register_cash_movement`, `close_cash_session`, `get_reconciliation`.

**Invariantes:**
- PAY-001: métodos possíveis simulados (`CASH_SIMULATED`, `PIX_SIMULATED`, `CARD_SIMULATED`); não capturar transação financeira nem tokens de pagamento.
- PAY-002: registros financeiros simulados referenciam venda/caixa; política de pagamento misto, troco, arredondamento e falha está **pendente ADR-002**.
- CASH-001: sessão de caixa tem operador/terminal/loja, hora de abertura, valor inicial declarado, estado e responsável pelo encerramento.
- CASH-002: fechamento compara esperado versus contado, guarda diferença, autor e justificativa; não “corrige” automaticamente saldo.
- CASH-003: caixa fechado não aceita nova venda/movimento sem regra explícita de exceção.
- CASH-004: estornos não apagam venda/pagamento original; geram lançamentos identificáveis.

### 2.7 Reporting

**Ownership:** projeções derivadas, KPIs, exportações e dicionário de métricas. Lê exclusivamente interfaces de domínio/eventos/publicações autorizadas. Não escreve no ledger de vendas/estoque.

**Operações:** `get_sales_report(period, filters)`, `get_stock_report`, `get_margin_report`, `export_facts`, `get_projection_status`.

**Obrigatório:** indicar `as_of`, `refreshed_at`, período e fuso, regra de cancelamento, granularidade, moeda, versão do contrato, dados ausentes e métricas. Projeção atrasada não equivale a inconsistência transacional.

### 2.8 Audit

**Ownership:** `AuditEvent`. Campos mínimos: ID, ator, escopo, ação, entidade, ID de entidade, horário UTC, identificador de correlação, resultado, justificativa (se aplicável), dados não sensíveis para análise.

**Operações:** `append_audit`, `search_audit` restrito a usuários autorizados. Não registrar senhas, credenciais, payloads de autenticação, dados pessoais desnecessários ou informações financeiras reais.

**Invariantes:** o registro de operações críticas precisa garantia de persistência/recuperação; desenho final depende de ADR-002 para fluxos transacionais e da modelagem de segurança.

## 3. Modelo lógico de dados — ESBOÇO não migrado

**Ownership inicial proposto por módulo/schema** na instância única PostgreSQL:

| Schema lógico | Entidades/tabelas indicativas |
|---|---|
| `iam` | users, roles, permissions, user_roles, sessions |
| `catalog` | products, categories, units, packaging_versions, product_barcodes, price_entries |
| `procurement` | suppliers, purchase_orders, purchase_order_items, goods_receipts, goods_receipt_items |
| `inventory` | stock_locations, stock_movements, stock_reservations, stock_positions |
| `sales` | sales, sale_items, sale_returns, sale_return_items, idempotency_records |
| `payments` | simulated_payments, cash_sessions, cash_movements, cash_reconciliations |
| `reporting` | sales_facts, inventory_facts, projection_checkpoints |
| `audit` | audit_events |
| `integration` (proposta) | outbox_events, inbox_receipts |

Regra física: nome, indices, constraints e ownership devem ser declarados em migrações; projetar chaves compostas e escopo de unicidade; timestamps UTC; FKs intra-schema quando apropriadas. Uma FK física entre domínios não confere direito de SQL interdomínio na aplicação: avaliar acoplamento e futura extração.

### 3.1 Campos mínimos por objeto

- **Product:** `id`, `sku`, `name`, `category_id`, `base_unit`, `active`, `version`, `created_at`, `updated_at`.
- **PriceEntry:** `id`, `product_id`, `currency`, `amount_cents`, `valid_from`, `valid_to`, `version`.
- **GoodsReceiptItem:** `id`, `receipt_id`, `product_id`, `quantity_original`, `unit`, `conversion_factor`, `quantity_base`, `unit_cost_snapshot`.
- **StockMovement:** `id`, `product_id`, `location_id`, `quantity_delta_base`, `unit`, `reason_code`, `origin_type`, `origin_id`, `occurred_at`, `actor_id`, `correlation_id`.
- **StockReservation:** `id`, `product_id`, `location_id`, `quantity_base`, `status`, `expires_at`, `origin_id`, `version`.
- **Sale:** `id`, `store_id`, `register_id`, `cash_session_id`, `status`, `currency`, `gross_cents`, `discount_cents`, `net_cents`, `created_at`, `completed_at`, `actor_id`, `correlation_id`.
- **SaleItem:** `id`, `sale_id`, `product_id`, `quantity`, `unit`, `conversion_factor`, `unit_price_cents`, `unit_cost_snapshot`, `discount_cents`, `line_total_cents`.
- **PaymentRecord:** `id`, `sale_id`, `cash_session_id`, `method`, `amount_cents`, `status`, `recorded_at`.
- **CashSession:** `id`, `store_id`, `register_id`, `operator_id`, `opened_at`, `closed_at`, `status`, `opening_float_cents`.
- **AuditEvent:** `id`, `actor_id`, `action`, `resource_type`, `resource_id`, `correlation_id`, `occurred_at`, `metadata_redacted`.
- **OutboxEvent:** `id`, `aggregate_type`, `aggregate_id`, `event_type`, `schema_version`, `payload`, `created_at`, `published_at`, `attempts`.

Os campos são **indicativos**, não justificam migrar/tabelar antes de ADR-002/004 e contratos revisados.

## 4. API HTTP proposta — contratos versionados

**Perfil:** JSON em UTF-8, caminhos versionados `/v1`, OpenAPI 3.1, formatos ISO 8601 UTC, IDs UUID, decimal como *string* quando aplicável (sem perda binária), moeda ISO 4217 BRL. Campos não conhecidos devem ser tratados por política de compatibilidade explícita. Erros RFC 9457; **cada endpoint exige teste de autorização**.

| ID | Método e recurso | Autorização e efeito |
|---|---|---|
| API-001 | `POST /v1/auth/login` | credencial fictícia → sessão; rate limit e auditoria |
| API-002 | `POST /v1/auth/logout` | revogar sessão |
| API-003 | `GET /v1/products` | catálogo paginado e pesquisável |
| API-004 | `POST /v1/products` | gestor/admin; cria SKU único |
| API-005 | `GET /v1/products/{id}` | consulta autorizada |
| API-006 | `POST /v1/products/{id}/prices` | gestão de preço com vigência e versão |
| API-007 | `POST /v1/purchase-orders` | cria pedido |
| API-008 | `POST /v1/purchase-orders/{id}/approve` | aprova pedido |
| API-009 | `POST /v1/receipts` | entrada recebida e idempotente |
| API-010 | `GET /v1/stock/positions` | saldos por produto/local |
| API-011 | `POST /v1/stock/adjustments` | gestor: ajuste com justificativa |
| API-012 | `POST /v1/cash-sessions` | abrir caixa; verifica exclusividade |
| API-013 | `POST /v1/sales` | venda idempotente: dependência ADR-002 |
| API-014 | `GET /v1/sales/{id}` | recibo não fiscal/detalhes |
| API-015 | `POST /v1/sales/{id}/cancel` | cancelamento autorizado e compensatório |
| API-016 | `POST /v1/sales/{id}/returns` | devolução parcial/total, política pendente |
| API-017 | `POST /v1/cash-sessions/{id}/close` | fechamento e reconciliação |
| API-018 | `GET /v1/reports/sales` | período, filtros e `refreshed_at` |
| API-019 | `GET /v1/reports/inventory` | posições/projeções |
| API-020 | `GET /health/live` e `GET /health/ready` | checks com política segura de exposição |

**Cabeçalhos previstos:** `Authorization` ou cookie de sessão segura (escolha pendente), `Idempotency-Key` para comandos elegíveis, `X-Correlation-ID` validado/sanitizado, `Content-Type: application/json`, `Accept: application/json`.

### 4.1 Exemplo de comando de venda (apenas contrato de proposta)

```http
POST /v1/sales HTTP/1.1
Content-Type: application/json
Idempotency-Key: 01JEXAMPLEUNIQUEKEY
X-Correlation-ID: 01JCORRELATION

{
  "store_id": "3a5f9da8-cb33-4b28-a3fb-df9023c1d7c1",
  "register_id": "31987278-d512-4aac-8db1-4c7f0ccb702e",
  "cash_session_id": "8f1ee0dc-faf3-4d61-90ec-fc0ef90b7a8e",
  "items": [
    {"product_id": "0e88893e-731e-4fbf-9444-b1093415ae7c", "quantity": "2.000", "unit": "UN"}
  ],
  "payments": [
    {"method": "PIX_SIMULATED", "amount_cents": 3600}
  ]
}
```

**Exemplo de resposta proposta (201):**

```json
{
  "sale_id": "4b5bd2d2-9c2d-4e18-abdd-0e6eb86ef201",
  "status": "COMPLETED",
  "currency": "BRL",
  "gross_cents": 3600,
  "discount_cents": 0,
  "net_cents": 3600,
  "correlation_id": "01JCORRELATION",
  "contract_version": "1.0",
  "completed_at": "2026-11-08T21:00:00Z"
}
```

**Não são regras aprovadas:** escolha do nome dos estados, política de resposta da repetição (200 vs 201), TTL da chave, estrutura final de desconto, forma de autenticação. Esses pontos dependem de validação dos contratos e ADR-002.

### 4.2 Tratamento de erros

| HTTP | Categoria | Comportamento |
|---|---|---|
| 400 | JSON/forma malformada | não executar, informar campos inválidos sem dados sensíveis |
| 401 | não autenticado | sessão inexistente/expirada |
| 403 | não autorizado | papel/escopo não permite operação |
| 404 | não encontrado | política de não exposição de recursos |
| 409 | conflito | SKU existente, idempotência divergente, estoque insuficiente, concorrência/caixa fechado |
| 422 | regra/validação semântica | item inativo, quantidade ou unidade inválida, desconto proibido |
| 429 | limite de requisições | proteger login/endpoints sensíveis; quando aplicável, Retry-After |
| 500 | falha não prevista | não vazar SQL/stacktrace; registrar correlação interna |
| 503 | dependência indisponível | readiness e erro explícito sem estado parcial |

Modelo RFC 9457 com `type`, `title`, `status`, `detail` seguro, `instance` opcional, `correlation_id` e código de erro de domínio estável. O status de negócio e o HTTP são distinções diferentes. Contratos OpenAPI finais devem fornecer schemas por operação, exemplos, segurança e códigos correspondentes.

## 5. Eventos e mudança de estado

**Eventos candidatos, NÃO obrigatoriedade de broker agora:**

- `catalog.product.created.v1`
- `catalog.product.price_changed.v1`
- `procurement.receipt.confirmed.v1`
- `inventory.stock.adjusted.v1`
- `sales.sale.completed.v1`
- `sales.sale.cancelled.v1`
- `sales.sale.returned.v1`
- `payments.payment.recorded.v1` (simulado)
- `cash.session.closed.v1`

Envelope mínimo recomendado:

```json
{
  "event_id": "c75abc4e-6c77-4b2f-b23e-70511e2a13bb",
  "event_type": "sales.sale.completed.v1",
  "schema_version": "1.0",
  "occurred_at": "2026-11-08T21:00:00Z",
  "aggregate_id": "4b5bd2d2-9c2d-4e18-abdd-0e6eb86ef201",
  "aggregate_version": 1,
  "producer": "sales",
  "correlation_id": "01JCORRELATION",
  "causation_id": null,
  "payload": {"sale_id": "4b5bd2d2-9c2d-4e18-abdd-0e6eb86ef201"}
}
```

**Política:** gravar evento transacionalmente quando design exigir outbox, processamento ao menos uma vez, consumidor idempotente, regras explícitas de ordenação por agregado, retry com backoff e dead-letter/reconciliação conforme necessidade demonstrada. Publicação bem-sucedida não prova que todos consumidores aplicaram evento; testes de falha e checkpoint obrigatório.

## 6. Cenários de aceitação — Gherkin textual

| ID | Contexto e ação | Resultado obrigatório |
|---|---|---|
| CEN-001 | SKU novo com dados válidos | produto cadastrado, histórico auditável |
| CEN-002 | SKU duplicado no mesmo escopo | conflito; nenhuma segunda entidade |
| CEN-003 | recebimento confirmado de 10 caixas × 12 UN | 120 UN-base no estoque; custo convertido conforme ADR-004 |
| CEN-004 | mesmo recebimento reenviado | nenhuma segunda entrada |
| CEN-005 | duas vendas concorrentes disputam a última unidade | somente uma conclui; estoque não negativo |
| CEN-006 | mesmo pedido de venda reenviado após resposta perdida | uma única venda e resposta compatível |
| CEN-007 | mesma chave de venda com itens diferentes | erro de conflito e nenhuma alteração nova |
| CEN-008 | pagamento “PIX_SIMULATED” | registro interno; nenhuma rede/banco real acionado |
| CEN-009 | operador sem permissão ajusta estoque | 403, sem movimento |
| CEN-010 | caixa fechado recebe tentativa de venda | rejeição, sem venda nem baixa |
| CEN-011 | cancelamento autorizado | original preservado + compensações/registro de motivo |
| CEN-012 | relatório com projeção atrasada | mostra `refreshed_at` e não altera ledger |
| CEN-013 | falha entre operações do commit crítico | invariantes mantidas e recuperação possível |
| CEN-014 | restauração de banco em ambiente limpo | totais, movimentos e auditoria conciliados |
| CEN-015 | dados de IA/BI consultados | números calculados por regras, nunca inventados |

Cenários que dependem de política contábil/financeira permanecem propostos até ADR-002/004; fixtures devem ser versionadas e conter resultado esperado.

## 7. Dicionário de indicadores — contratos analíticos

| Métrica | Fórmula conceitual | Cuidado obrigatório |
|---|---|---|
| Receita bruta | soma de valores brutos de vendas elegíveis | descontos, cancelamentos e período definidos |
| Receita líquida comercial | receita bruta − descontos − devoluções/estornos elegíveis | **não** equivale necessariamente à receita líquida contábil/fiscal |
| CMV | soma do custo histórico atribuído às unidades vendidas, líquido de devoluções conforme política | método de custo e retornos pendentes ADR-004 |
| Margem bruta monetária | receita líquida comercial − CMV | não considera despesas operacionais |
| Margem bruta percentual | margem bruta / receita líquida × 100 | denominador zero deve retornar “não aplicável” |
| Quantidade vendida | soma de unidades-base (segmentada por produto/unidade compatível) | não somar KG e UN indiscriminadamente |
| Estoque físico | soma reconciliável dos movimentos por produto/local | ajustes e corte temporal |
| Estoque disponível | físico − reservas ativas | reservas com expiração e estado |
| Valor de estoque | quantidade × método de avaliação de custos | escolher ADR-004 e lote/variação conforme política |
| Diferença de caixa | valor contado − valor esperado | informar método e fechamento; não confundir com lucro |

**Exemplo de consistência obrigatória — mercadoria fictícia:** compra de 200 caixas com 10 potes cada por R$ 30.000 → 2.000 potes, custo médio indicativo R$ 15/pote; venda de 1.143 potes a R$ 18 → receita bruta de R$ 20.574; CMV indicativo R$ 17.145; margem bruta indicativa R$ 3.429; saldo físico 857 potes, **na ausência de outras movimentações**, sem concluir lucro líquido. O exemplo não substitui a política de custos da ADR-004.

## 8. Restrições de segurança e autorização transversais

- Toda mutação sensível faz avaliação server-side de ação, ator e recurso; ações negadas não deixam mutações persistidas.
- Input validado contra esquemas versionados; consultas parametrizadas; sem SQL concatenado com valores de usuário.
- Senhas com hashing adequado e política de tentativa; segredos em variáveis; não registrar dados sensíveis nem expor stack traces.
- Logs e auditoria com correlação, sem vazar credenciais/dados de pagamento (nenhum dado bancário real permitido).
- Inventário, custeio, fechamento e cancelamento têm permissões distintas para mitigar fraudes.
- Dados sintéticos suficientes para carga e edge cases, nunca dados reais de empresas ou clientes.

## 9. Backlog de decisões indispensáveis antes do código de negócio

1. **ADR-002:** transação, idempotência, estoque, meios de pagamento simulados, caixa, fechamento, reversões, timeout e recuperação.
2. **ADR-004:** escalas e conversões, método de CMV, impostos simulados se houver, arredondamentos, custo por devolução.
3. Autenticação e modelo de sessão; matriz RBAC por recurso/escopo.
4. Campos obrigatórios dos contratos OpenAPI e modelos de migração.
5. Política de relatórios: janela de atualização, cancelamentos/devoluções e versão de exportação.
6. Ambiente de teste de referência e massa de dados.
7. Aprovação explícita da baseline SDD e critérios por fase.

**Próximo documento para deliberação:** ADR-002 proposta. Até sua aceitação, preservar incertezas explicitamente e não implementar o fluxo de venda/estoque/caixa.
