# ADR-005 — Topologia das interfaces Admin/PDV, autenticação e escopo de sessão

| Campo | Valor |
|---|---|
| Produto | MT SGI — MT Sistema de Gestão Integrada |
| Identificador | ADR-005 |
| Estado | **PROPOSTA — NÃO ACEITA; exige aprovação expressa** |
| Proposta registrada | 2026-11-09 (America/Fortaleza) |
| Categoria | D1 — arquitetura de interfaces, autenticação e segurança |
| Referências | SDD-001 §§3–4,8,13; SDD-002 IAM/Sales/Payments e matriz RBAC pendente; SDD-003 §§2,8–9; ADR-001 ACEITA |
| Dependências | ADR-002 (sessão de caixa), ADR-003 (ambiente), stack SDD-003 proposta, matriz RBAC ainda não aprovada |
| Finanças e dados | Apenas ambiente demonstrativo com dados sintéticos; custo adicional **R$ 0** |

## 1. Contexto e fronteiras já estabelecidas

A decisão aprovada na ADR-001 prevê um **backend monolítico modular** com domínios internos sob contratos públicos. SDD-001 apresenta **duas interfaces lógicas**: gestão administrativa e PDV. Isso **não** equivale a aprovar duas aplicações publicadas, dois deployments, um framework web definitivo ou a forma de sessão. Autenticação e autorização são responsabilidade do backend IAM; controles no frontend não concedem permissão.

**Requisitos não negociáveis:**
- UI **Admin**: manutenção de cadastro, compras/recebimentos, estoques, usuários/papéis e relatórios, sempre condicionada à autorização.
- UI **PDV**: operações de caixa e venda simulada; não pode editar preço, inventário ou RBAC apenas por ter acesso à tela.
- A mesma identidade pode assumir papéis autorizados, mas **loja, terminal, sessão de caixa e ação** devem ser conferidos pelo backend a cada comando.
- Nenhuma conexão bancária, pagamento real, documento fiscal, PII ou sessão comercial real.
- Dados de preço/custo e histórico devem permanecer no backend; não confiar em montantes calculados somente na UI.
- O fluxo offline de conclusão de venda **não** está autorizado, pois não há política para reconciliar estoque, caixa e idempotência desconectados (ADR-002 pendente).

## 2. Alternativas de topologia

| Alternativa | Desenho | Vantagens | Riscos |
|---|---|---|---|
| A — **Duas interfaces lógicas sob a mesma origem local** | caminhos `/admin` e `/pdv`, backend `/api/v1`, uma implantação local ou dois bundles servidos na mesma origem | simplifica cookies/CORS, evita duas autenticações independentes, custo reduzido e teste E2E integrado | build e deploy podem compartilhar ciclo; isolamento de frontend é lógico, não de infraestrutura |
| B — Dois frontends físicos e origens diferentes | aplicações Admin/PDV separadas com backend central | isolamento de build e evoluções distintas | CORS, cookies, CSRF, sessão e manutenção mais complexos; mais recursos CI |
| C — Um frontend único com navegação por papel | uma SPA com rotas Admin/PDV | build simples; bom para demo | risco de acoplamento de permissões/fluxos e regressões cruzadas; negar rota na UI não garante RBAC |

**Recomendação não vinculante:** opção A como compromisso para o MVP local, preservando módulos/componentes de UI separados por domínio e permitindo extração futura via ADR. SDD-003 sugere React/Vite, mas a escolha da stack permanece pendente.

## 3. Alternativas de autenticação e sessão

| Alternativa | Benefícios | Restrições e ameaças |
|---|---|---|
| A — **Sessão de servidor e cookie HttpOnly** | revogação central, menor risco de exposição de credencial em JavaScript, encaixa em mesma origem | exige anti-CSRF conforme verbos/fluxos, Secure em HTTPS, SameSite, expiração, rotação e armazenamento seguro |
| B — Token bearer em memória | desacoplamento de origem e facilidade para APIs | token pode vazar por XSS, renovação e logout são complexos; não persistir em localStorage por padrão |
| C — JWT persistido em localStorage | implementação aparentemente fácil | roubo por XSS e revogação difícil; **não recomendar** no contexto atual |

**Recomendação técnica:** opção A com cookie HttpOnly, escopo explícito da sessão e política CSRF testada. A implementação local via HTTP/loopback exige exceção restrita e documentada à exigência de `Secure` usada em HTTPS; isso **não** é permissão para publicar cookies inseguros na internet. Se frontends estiverem em origens diferentes, reavaliar SameSite, CSRF e CORS antes de implantar.

## 4. Contratos conceituais de sessão — sujeitos a aceite

- `authenticate(credentials)`: resultado opaco para o cliente, sem senha nos logs; credenciais da demo são sintéticas, com hash e limites de tentativa.
- `authorize(actor, action, resource, store_id)`: negação por padrão e por objeto. UI oculta itens como conveniência, não mecanismo de autorização.
- `revoke_session(id)`, `expire_session`, `rotate_session`: revogação eficaz, expiração por inatividade e absoluta a definir; login/logout/alteração de privilégio são auditáveis.
- `CashSession`: **não é** a sessão de autenticação. Caixa tem loja, terminal, operador e estado; seu ciclo e regras de fechamento dependem da ADR-002.
- Troca de loja ou terminal não reaproveita autorização por inferência; validações ocorrem no servidor e dependem de RBAC formal.
- Identidade e permissão não são atributos confiáveis enviados pela UI; proveniência vem da sessão autenticada e da decisão de autorização do IAM.
- Erros `401` e `403` não devem expor existência de recurso alheio; `409` e idempotência do PDV dependem de contrato de negócio aprovado.

### Matriz RBAC preliminar — não normativa

| Ação / recurso | Administrador | Gestor | Operador de caixa | Auditor |
|---|---|---|---|---|
| Administrar usuários e papéis | Candidata | Não presumir | Negar | Negar |
| Catálogo/preço | Candidata | A deliberar | Negar escrita | Leitura a deliberar |
| Compra/recebimento | A deliberar | Candidata | Negar | Leitura a deliberar |
| Ajuste físico de estoque | A deliberar | Candidata | Negar | Leitura a deliberar |
| Abrir/vender/fechar caixa do próprio terminal | A deliberar | A deliberar | Candidata | Negar escrita |
| Autorizar cancelamentos | A deliberar | Candidata | Não presumir | Negar escrita |
| Consultar relatório/auditoria | A deliberar | Candidata | Somente próprio escopo, a deliberar | Leitura segregada |

`Candidata` significa **aguardando autorização**, não concessão por padrão. O escopo de loja, o escopo de terminal e a propriedade de objeto também dependem de aprovação.

## 5. Riscos e ameaças

- **CSRF:** comandos mutáveis com cookies precisam defesa específica e testes de origem/token.
- **XSS:** sanitização/encoding, CSP compatível e não inserir segredos em JavaScript.
- **IDOR/BOLA:** autorização por recurso e loja no backend, não apenas papel ou menu.
- **Sessão sequestrada:** TTL, renovação após login, revogação, logout, proteção contra fixation e logs higienizados.
- **Brute force:** limite de tentativas com comportamento observável sem expor usuários existentes.
- **POS desconectado:** não usar fila local para completar venda; tratar conexão perdida com resultado incerto via idempotência da ADR-002.
- **Escopo de terminal:** impedir que operador use sessão de caixa de outra loja/terminal, sujeito a regras explicitamente aprovadas.
- **Acessibilidade e responsividade:** metas alinhadas ao WCAG 2.2 AA como alvo de teste, sem afirmar conformidade não testada.
- **Deploy:** portas de teste em loopback; não criar servidor público nem exigência de domínio/SSL pago.

## 6. Critérios de aceite propostos (ainda não implementados)

| ID | Ensaio | Resultado esperado |
|---|---|---|
| UI-A01 | Operador chama API de gestão de usuários diretamente | `403`, sem efeito |
| UI-A02 | Sessão expira/revogada | próxima ação protegida falha; novo login necessário |
| UI-A03 | Login altera privilégio ou recebe sessão pré-fixada | identificador de sessão regenerado |
| UI-A04 | POST com cookie sem defesa CSRF válida | rejeitado, nenhuma escrita |
| UI-A05 | Operador de loja A tenta agir em caixa de loja B | acesso negado, auditoria |
| UI-A06 | UI PDV perde conexão durante conclusão | não declara sucesso; consulta/retry conforme ADR-002 |
| UI-A07 | Duas interfaces na mesma origem | não criam autenticações independentes nem ampliam sessão |
| UI-A08 | Navegação sem JavaScript ou requisição HTTP manual tenta bypass de UI | backend continua impondo RBAC |
| UI-A09 | Acesso via navegador em mobile/tablet | fluxos de demo navegáveis e sem overflow crítico |
| UI-A10 | Demonstração local | nenhuma porta pública, cartão, serviço pago ou pagamento real |

## 7. Questões de decisão

1. Aprovar **A — duas interfaces lógicas Admin/PDV sob mesma origem local**, podendo ter builds distintos, sem dois deploys obrigatórios?
2. Aprovar **sessão controlada pelo servidor via cookie HttpOnly**, com CSRF, revogação e expiração, em vez de JWT em localStorage?
3. O mesmo usuário pode ter diversos papéis por loja? É permitida mais de uma sessão de autenticação simultânea? Qual expiração mínima/absoluta desejada?
4. Para o MVP, a sessão de caixa deve ser **exclusiva por terminal com operador identificado** (a deliberar em conjunto com ADR-002)?
5. Quais permissões da matriz preliminar são efetivamente aprovadas? Há segregação obrigatória de aprovação para ajustes e cancelamentos?
6. Confirmar que **PDV offline com confirmação local** fica fora do MVP por segurança de consistência?

**Estado e próximo passo:** PROPOSTA — NÃO ACEITA. Aguardar resposta expressa do responsável, depois registrar no Decision Log, atualizar SDD-001/002/003, threat model e testes. Esta ADR isolada não autoriza código, cookies, deploy ou concessão de RBAC. Solicitação: `docs/decisions/requests/SD-0005-interfaces-sessao.md`.
