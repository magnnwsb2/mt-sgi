# AGENTS.md — Protocolo obrigatório para qualquer agente de desenvolvimento

**Projeto:** MT SGI — MT Sistema de Gestão Integrada  
**Repositório:** https://github.com/magnnwsb2/mt-sgi  
**Idioma de trabalho e documentação:** Português brasileiro  
**Política global:** SDD como fonte de verdade, custo financeiro R$ 0, dados sintéticos, mudanças rastreáveis.

## 1. Bootstrap obrigatório — nunca depender de memória de chat

**Antes de planejar, codificar, revisar, migrar ou declarar trabalho concluído:**

1. Verificar `git status`, branch, `git log -1` e PR/CI aplicáveis. Se apenas navegador/connector estiver disponível, consultar o mesmo estado via GitHub.
2. Ler `docs/specs/SDD-001.md` **integralmente**.
3. Ler os anexos registrados em SDD-001: `docs/specs/SDD-002-dominios-contratos.md`, `docs/specs/SDD-003-tecnologias-operacao.md` e `docs/specs/SDD-STATUS.md`.
4. Ler ADR-001 e ADRs específicas da tarefa. **ADR-002 é PROPOSTA até aprovação expressa**, não norma implementável.
5. Inspecionar arquivos realmente existentes e evidências de testes reais; não assumir que roadmap significa feature implementada.
6. Identificar quais requisitos IDs, domínios, decisões, contratos e testes serão afetados.
7. Só então executar a **próxima tarefa autorizada**, mantendo custo R$ 0.

**Quando faltarem informações:** consultar a fonte normativa ou registrar uma proposta/bloqueio. Não preencher lacunas de negócio por dedução; não dizer que o usuário aprovou algo que não aprovou.

## 2. Precedência e regras de mudança

A hierarquia e o estado documental são definidos em SDD-001 `1`. Restrições expressas do responsável prevalecem; a baseline SDD e seus anexos/ADRs aceitas são a documentação autoritativa. README, conversas e comentários não a substituem. **Se código divergir do SDD, a divergência é defeito ou mudança pendente — não modifique silenciosamente a regra.**

- Mudança arquitetural relevante → registrar alternativas, impactos, riscos, testes e ADR; pedir aprovação expressa.
- Mudança de escopo, custeio, unidades, dinheiro, autorização ou transação → alterar SDD/contratos, solicitar decisão correspondente antes do código.
- Nunca considerar “aprovado” sinônimo de “implementado” ou “validado”.
- Exigir contrato/versionamento e critérios de aceite antes do código.
- Sem novos componentes pagos, cloud, cartão, APIs pagas, créditos promocionais, trials ou licença restritiva como dependência.
- Sem segredos, senhas, tokens ou dados reais de consumidores/empresas em branch, histórico ou artefatos.
- Não executar pagamentos reais, emissão fiscal ou qualquer operação financeira.

## 3. Arquitectura vigente

**ACEITA — ADR-001:** monólito modular em monorepo, único backend implantável inicial e PostgreSQL local proposto; oito bounded contexts com interfaces públicas, proibição de SQL/imports privados entre módulos, sem ciclos, ownership de tabelas/migrações e testes de arquitetura.

**PENDENTE — ADR-002:** transação de venda, estoque, pagamentos simulados e caixa. Não implementar até decisão. **PENDENTES:** ADR-003 (demonstração R$ 0), ADR-004 (unidades e custos), ADR-005 (UI). Stack de Python/FastAPI/React/PostgreSQL/Node é **proposta** até baseline/compatibilidade aprovadas.

## 4. Fluxo obrigatório de trabalho

```text
ler SDD/estado/ADRs
  ↓
identificar escopo e critérios
  ↓
verificar decisões pendentes
  ├─ há decisão crítica pendente → elaborar proposta, parar implementação afetada
  └─ aprovado → atualizar SDD/contratos quando necessário
  ↓
branch e mudança pequena
  ↓
testes + arquitetura + segurança + reprodutibilidade
  ↓
evidência (commit/PR/jobs) + revisão
  ↓
atualizar SDD-STATUS e handoff
```

Evitar alterações diretas em `main` quando revisão por PR for possível. Não fazer merge ou marcar release como pronto com falha de integridade; não mascarar testes falhos. Ao encerrar, registrar **o que foi feito, onde, resultados reais, o que falta, decisões bloqueadoras, próxima ação**.

## 5. Padrões de implementação quando a fase for autorizada

- Separar `domain`/`application`/`ports`/`adapters`; domínio puro não importa framework.
- Reutilizar pacotes somente para tipos universais; não compartilhar entidade de negócio privada.
- Usar valores monetários exatos e timestamps UTC; não usar float para dinheiro.
- Segurança server-side por ação e escopo; logs sem segredos e com correlation ID.
- PostgreSQL real para testes de locking/concurrency; SQLite ou mock não provam semântica de Postgres.
- APIs versionadas; erros RFC 9457; schema de eventos se usados.
- Commits pequenos e com mensagens descritivas; linkar evidências em PR/SDD-STATUS.
- CI pública deve ter scanner e testes próprios. Skills privadas `spec-driven-development` e `pre-commit-security` são referência, não afirmar execução automática sem instalação e evidência.

## 6. Checklist de saída do agente

- [ ] Reli a baseline aplicável e respeitei decisões bloqueadoras.
- [ ] Enumerei mudanças por requisito/ADR.
- [ ] Não fiz afirmação falsa sobre implementação, CI ou aprovação.
- [ ] Registrei testes executados e não executados separadamente.
- [ ] Verifiquei custo R$ 0, ausência de segredos e compatibilidade de licenças.
- [ ] Mantive SDD e anexos coerentes.
- [ ] Atualizei `docs/specs/SDD-STATUS.md` com commit/PR/resultado e próxima etapa.
- [ ] Descrevi ao responsável qualquer aprovação necessária para o avanço.

**Mensagem curta para reinício de contexto:** “Abra o GitHub magnnwsb2/mt-sgi, leia AGENTS.md e todo o SDD (001/002/003/STATUS), depois ADRs; verifique CI, PRs e estado real; continue somente a próxima etapa autorizada. Nada pago, nada fora do SDD.”
