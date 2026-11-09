# MT SGI — Runbook de Operação dos Agentes

**Regra superior:** SDD-001 e SDD-004. **Ambiente aprovado:** ChatGPT + GitHub conectado. **Não há daemon de agentes** no GitHub nem execução permanente de ChatGPT fora da sessão.

## 1. Reinício de qualquer conversa

Instrua: “Abra `magnnwsb2/mt-sgi`. Verifique main, branches, PRs, checks e status real. Leia AGENTS.md, SDD-001 integral, SDD-002/003/004, SDD-STATUS, ADR-001 e ADR relevante; consulte agents/README.md, decision log e runbook. Continue o próximo trabalho autorizado sem inventar aprovações ou resultado de teste.”

Verifique primeiro se documentos da branch `docs/sdd-fundacao-mt-sgi` e da feature de agentes foram incorporados à `main`; se não, sua documentação não está na baseline. Em PRs encadeados, tratar dependências explicitamente.

## 2. Sessão de trabalho

**Preparar:** identificar SHA do HEAD e baseline, ler artefatos, identificar se tarefa é A0/A1/A2/A3 ou D1/X. Criar/atualizar contrato TC. A próxima tarefa é determinada por dependências e aceite, não por impulso de construir o módulo mais chamativo.

**Executar:** escolher agente primário do inventário, editar branch isolada, executar testes disponíveis e revisar diff. Se testes necessários não estiverem disponíveis, marcar não executados, produzir bloqueio e buscar outra tarefa. O trabalho é sequencial quando a ferramenta não suporta paralelismo real.

**Repetir:** registrar evidências, abrir PR e delegar revisão conforme papéis. Se Merge Guardian barrar, corrigir até 3 tentativas por causa. Se bloqueio exigir decisão, criar SD; o restante continua se independente.

**Encerrar:** atualizar SDD-STATUS e registrar SHA, PR, bloqueios e próxima ação. Sem prometer retomada automática após fim da sessão.

## 3. Modelo híbrido de decisões

Rotineiras: agente decide dentro do contrato. Normais: consolidar e apresentar ao responsável quando consultar o projeto. Críticas: destacar imediatamente na próxima conversa ativa; não é push notification. Nenhuma SD se autoaprova. A resposta do usuário deve ser inequívoca e registrada no GitHub com escopo e data antes de executar a mudança.

## 4. Merge Guardian — operação obrigatória

Ler `docs/operations/MERGE-GUARDIAN.md`. Verificar branch protection e status checks remotos, não apenas a presença do YAML na branch. Auto-merge está condicionado à configuração nativa GitHub e ao parecer vinculado ao **head SHA**. Se repo não permitir auto-merge, registrar BLOQUEADO e nunca usar merge direto como atalho.

## 5. Segurança e custo

GitHub Actions em runner gratuito elegível somente após confirmar limites atuais; para o repositório público, workflow sem token privilegiado e sem SaaS. Não instalar agente pago, GH App adicional, conta cloud, banco persistente ou token de API. Dados sintéticos; nenhum pagamento/fiscal real.

## 6. Checklist de saída

- [ ] Leitura SDD e estado verificados com branch e SHA;
- [ ] Requisitos/ADRs mapeados;
- [ ] Não houve mudança não autorizada;
- [ ] Testes reportados fielmente;
- [ ] Bloqueios e tentativas registrados;
- [ ] PR e commits rastreáveis;
- [ ] STATUS atualizado;
- [ ] Próximo trabalho identificado por dependência.
