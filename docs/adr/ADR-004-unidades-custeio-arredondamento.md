# ADR-004 — Unidades, conversões, custeio histórico e arredondamentos

| Campo | Valor |
|---|---|
| Produto | MT SGI — MT Sistema de Gestão Integrada |
| Identificador | ADR-004 |
| Estado | **PROPOSTA — NÃO ACEITA; exige aprovação expressa** |
| Data da proposta | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — regras de negócio, contratos e persistência |
| Rastreabilidade | SDD-001 §§3,5–6; SDD-002 §§1–3,6–7; SDD-003 §§6–7; ADR-001 ACEITA; ADR-002 PROPOSTA |
| Dependências | ADR-002 para checkout e retornos; aprovação de contratos de compra/estoque/venda |
| Custo e dados | R$ 0; somente fixtures sintéticas; sem fiscal real |

> **Nota de segurança normativa:** todos os fatores de conversão, escalas e métodos descritos abaixo são candidatos de implementação e de teste. A recomendação não escolhe o método de custeio por conta do responsável.

## 1. Decisões que esta ADR precisa resolver

- **CST-001 — Unidade de controle:** representar cada produto em uma unidade-base explícita, com dimensões distintas (unidade, massa, volume). Não somar categorias incompatíveis.
- **CST-002 — Conversão:** embalagem e fração expressas por fator exato e **versionado**, com snapshot em pedidos, recebimentos, movimentos e vendas. Proibir conversão física implícita entre KG e L.
- **CST-003 — Precisão:** quantidades em decimal exato, com escala por produto/unidade e validação antes de qualquer escrita. Valores monetários jamais em `float` ou truncados silenciosamente.
- **CST-004 — Custo:** selecionar método oficial e pool de avaliação (por produto, loja/local ou lote). O CMV deverá usar custo histórico congelado.
- **CST-005 — Arredondamento:** decidir escala interna e em qual fronteira o preço/custo é arredondado (item, linha, venda); nunca esconder divergência de centavos.
- **CST-006 — Retornos:** decidir como devolver quantidade e valor de custo histórico sem alterar a venda original.
- **CST-007 — Auditoria:** toda correção de fator, custo, estoque ou preço depois de movimentação requer novo registro versionado/compensatório, não UPDATE destrutivo de fatos passados.
- **CST-008 — Relatórios:** quantidade, custo, receita, CMV e margem com fórmula, moeda, dimensão, período e data de atualização explícitos; não confundir margem com lucro líquido.

## 2. Alternativas de unidade e precisão

| Alternativa | Descrição | Benefícios | Desvantagens |
|---|---|---|---|
| A — **Unidade-base e fator racional/decimal exato** | produto guarda unidade-base; embalagem referencia versão com fator exato; cada lançamento preserva quantidade original, unidade e fator | auditável, conversões estáveis, suporte a caixa/fracionamento | exige escala e validação explícitas |
| B — Quantidade como inteiro de embalagem | cada produto guarda somente peças/caixas inteiras | muito simples | falha para KG, litros e embalagens parciais; dados incompatíveis com SDD-002 |
| C — Converter tudo em `float` | número binário com conversões imediatas | implementação rápida | erros de representação, custo divergente e conciliação frágil; **rejeitar tecnicamente** |

**Recomendação condicionada:** A, usando aritmética decimal exata (ex.: `Decimal` em Python e `NUMERIC` em SQL, caso a stack seja aprovada); a escala e os tipos de DB permanecem pendentes.

### Exemplos sintéticos para critérios de aceite

- Produto `POTE`, unidade-base `UN`, versão de embalagem `CX10` com fator 10: **200 caixas × 10 = 2.000 unidades**. Compra por R$ 30.000 gera custo total de referência R$ 30.000, sujeito à política de apropriação.
- Produto `ARROZ`, unidade-base `KG`, venda de `0,750 KG`: requer escala compatível com a granularidade aprovada. Não converter para unidade de peça.
- Produto `SUCO`, unidade-base `L`, embalagem `500 mL` com fator `0,5 L`: 6 embalagens = 3 L. Fator e versão persistem.
- Embalagem alterada de 10 para 12 unidades: **não altera** os 200 recebimentos históricos nem vendas passadas; criar nova versão vigente.
- Se o fator produzir quantidade-base abaixo da escala suportada, a transação deve ser rejeitada com erro explícito, não arredondar silenciosamente e gerar produto fictício.

## 3. Alternativas de custeio de estoque

| Método | Algoritmo e impacto | Benefícios | Custos/limitações |
|---|---|---|---|
| A — **Custo médio ponderado móvel (CMP)** | cada entrada elegível recalcula custo de avaliação no escopo definido; saídas congelam custo vigente; ajustes/devoluções possuem regras especiais | implementação e relatórios mais simples para MVP | precisa serialização concorrente e definir custo por local, transferências e compras retroativas |
| B — PEPS/FIFO por camadas | entradas criam camadas de quantidades/custos; saídas consomem camadas na ordem documentada | rastreabilidade por lote/camada | reprocessamento, devoluções e estoque multi-local são mais complexos |
| C — Último custo de compra | saída usa preço da última compra | simplicidade aparente | distorce valor histórico e não reconcilia com camadas/valor efetivo; não recomendar como CMV |
| D — Custo informado manualmente na venda | operador define custo da saída | flexibilidade | risco de manipulação e ausência de integridade histórica; não recomendar |

**Recomendação técnica:** CMP móvel para MVP, condicionada à escolha explícita do pool (loja x local) e à ADR-002 para locks/UoW. Não transformar recomendação em decisão aceita.

**Exemplo do SDD-002, apenas para ensaio:** 2.000 potes, custo total R$ 30.000; venda de 1.143 potes por R$ 18 cada, sem desconto, com custo unitário R$ 15. Receita bruta **R$ 20.574**, CMV **R$ 17.145**, margem bruta **R$ 3.429**, saldo físico **857 potes**. Este caso supõe ausência de outras entradas, perdas, devoluções e impostos; não comprova método oficial nem lucro líquido.

## 4. Precisão e arredondamento — alternativas

| Fronteira | Candidato | Risco a resolver |
|---|---|---|
| Preço de venda publicado | inteiro de centavos por unidade comercial ou NUMERIC com escala escolhida | preço por massa/fração pode gerar centavos fracionários antes do total |
| Custo unitário interno | NUMERIC de maior escala do que a moeda (ex.: 6 casas, **somente sugestão**) | custos por unidades fracionadas devem reconciliar com valor da entrada |
| Total de linha | quantizar BRL a centavos pelo modo definido (ex.: ROUND_HALF_UP) | soma de linhas pode diferir do arredondamento do total bruto |
| Total do documento | somar linhas monetizadas e descontos alocados sem perder centavos | políticas de desconto e tributos simulados ainda pendentes |
| Relatórios/CMV | custo histórico da saída e política consistente de saldos residuais | diferença acumulada entre soma de saídas e estoque avaliado |

**Decisões necessárias:** modo de arredondamento (metade para cima x metade para par), etapa de aplicação (linha x documento), número de casas de custo interno, valores de desconto por item e alocação do centavo residual. Uma opção precisa ser testada contra casos de borda; não usar arredondamento do contexto da linguagem por acidente.

## 5. Recebimento, transferências, ajustes e devoluções

- **Recebimento:** quantidade aceita converte para base; custo total de aquisição é fonte, não inferência de preço de venda. Frete/impostos/bonificação só entram se uma política futura decidir.
- **Transferência:** preserva quantidade total e transfere valor patrimonial conforme o pool escolhido. Uma transferêcia entre locais não pode inventar CMV.
- **Ajuste/inventário:** exige razão, autorização e lançamento compensatório auditável; custos de perdas/ganhos dependem de regra aprovada.
- **Devolução de venda:** limite de quantidade e custo de reversão historicamente atribuídos à venda original, se aprovados pela ADR-002; mercadoria avariada não volta automaticamente ao disponível.
- **Recebimento retroativo:** proibir reescrita silenciosa de saídas já fechadas. Definir correção contábil/reconciliação em ADR específica se necessário.
- **Relatório:** mostrar quantidade na unidade-base e na unidade original quando útil; não somar KG e UN como um total único.

## 6. Testes de aceite propostos (não executados)

| ID | Entrada | Resultado esperado, sujeito às escolhas |
|---|---|---|
| CST-A01 | 200 × CX10 | 2.000 UN; snapshot da versão do fator |
| CST-A02 | 6 × 500mL | 3 L, sem `float` |
| CST-A03 | fator antigo alterado após recebimento | entradas históricas inalteradas |
| CST-A04 | embalagem abaixo da escala autorizada | erro de validação, nenhuma gravação parcial |
| CST-A05 | múltiplas entradas por custos diferentes | CMP ou FIFO conforme regra formal, mesmo resultado em replay |
| CST-A06 | venda e devolução de quantidade parcial | custo da venda original preservado e reversão reconciliada |
| CST-A07 | preço/custo alterado depois da venda | receita/CMV históricos não mudam |
| CST-A08 | duas saídas simultâneas do último estoque | quantidade não negativa, locking conforme ADR-002 |
| CST-A09 | fechamento com frações de centavo | soma de linhas = total; resíduos auditados |
| CST-A10 | relatório por unidade incompatível | resultado segmentado ou rejeição da soma incompatível |

## 7. Perguntas decisórias e dependências

1. **Método de custeio:** CMP móvel por produto/loja, PEPS/FIFO por lote, ou outro? Qual pool de estoque/custo?
2. **Precisão:** unidade inteira `UN`, decimal de 3 casas para massa e volume, ou escala configurável por produto? Qual regra para subunidades?
3. **Arredondamento:** qual modo (HALF_UP/HALF_EVEN) e em qual ponto (linha/documento)? Como tratar centavos residuais e descontos?
4. **Retornos/ajustes:** reversão pelo custo histórico da venda e retenção de lançamentos imutáveis? Como valorar perdas, transferências e devoluções para estoque?
5. **Custos acessórios:** frete, descontos comerciais e impostos *simulados* entram no custo de aquisição no MVP ou ficam fora inicialmente?

**Estado:** PROPOSTA — NÃO ACEITA. A ADR-004 não autoriza migração, API, fórmula definitiva ou cálculo de margem por conveniência. A aprovação deve constar no Decision Log e atualizar SDD-001/002/003, testes, esquemas e ADR-002 conforme necessário. Solicitação: `docs/decisions/requests/SD-0004-unidades-custeio.md`.
