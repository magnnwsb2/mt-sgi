"""Despachante seguro dos perfis MT SGI: avalia contratos JSON, sem executar ações.

Somente biblioteca padrão. Fail-closed: ausência/erro de informação bloqueia.
A decisão resultante NÃO constitui aprovação nem autorização GitHub.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

AGENT_IDS = frozenset(f"AGT-{i:03d}" for i in range(1, 16))
STATES = frozenset({"PROPOSTA", "EM_EXECUCAO", "BLOQUEADA", "EM_REVISAO", "CONCLUIDA"})
DANGEROUS_ACTIONS = frozenset({
    "merge", "push_main", "deploy", "payment", "external_network",
    "delete", "change_permissions", "execute_code",
})
REQUIRED_FIELDS = frozenset({
    "task_id", "state", "title", "owner_agent", "secondary_agents",
    "repo", "baseline_branch", "baseline_sha", "work_branch",
    "requirements", "accepted_adrs", "pending_decisions", "allowed_paths",
    "blocked_paths", "preconditions", "dependencies", "interfaces",
    "acceptance_criteria", "test_plan", "risk", "rollback", "cost_policy",
    "attempts_by_root_cause", "requested_action",
})
SHA = re.compile(r"^[a-f0-9]{40}$")
TASK_ID = re.compile(r"^TC-[0-9]{4,}$")
PATH = re.compile(r"^(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+/?$")


def _paths_valid(values: Any) -> bool:
    if not isinstance(values, list) or not values:
        return False
    return all(
        isinstance(v, str) and bool(PATH.fullmatch(v))
        and v not in {".", ".."} and not (v == ".git" or v.startswith(".git/"))
        and all(segment not in {".", ".."} for segment in v.split("/"))
        for v in values
    )


def evaluate(task: Any) -> dict[str, Any]:
    """Avalia pedido de agente; nunca executa ações nem lê credenciais."""
    reasons: list[str] = []
    if not isinstance(task, dict):
        return {"decision": "BLOCKED", "reasons": ["Contrato não é objeto JSON."], "agent": None}
    missing = sorted(REQUIRED_FIELDS - task.keys())
    if missing:
        reasons.append("Campos obrigatórios ausentes: " + ", ".join(missing))
    agent = task.get("owner_agent")
    if not isinstance(agent, str) or agent not in AGENT_IDS:
        reasons.append("Agente proprietário não registrado.")
    secondary = task.get("secondary_agents")
    if not isinstance(secondary, list) or any(not isinstance(a, str) or a not in AGENT_IDS for a in secondary):
        reasons.append("Agentes secundários inválidos.")
    if not isinstance(task.get("task_id"), str) or not TASK_ID.fullmatch(task["task_id"]):
        reasons.append("ID de tarefa inválido.")
    if task.get("repo") != "magnnwsb2/mt-sgi":
        reasons.append("Repositório fora do escopo.")
    if not isinstance(task.get("state"), str) or task["state"] not in STATES:
        reasons.append("Estado de tarefa inválido.")
    if task.get("state") != "EM_EXECUCAO":
        reasons.append("Tarefa não está EM_EXECUCAO.")
    if not isinstance(task.get("baseline_sha"), str) or not SHA.fullmatch(task["baseline_sha"]):
        reasons.append("SHA de baseline inválido ou ausente.")
    if not isinstance(task.get("baseline_branch"), str) or task["baseline_branch"] not in {"main", "feat/agent-governance-foundation"}:
        reasons.append("Baseline não reconhecida.")
    work_branch = task.get("work_branch")
    if not isinstance(work_branch, str) or not work_branch or work_branch in {"main", "master"}:
        reasons.append("Branch de trabalho ausente ou protegida.")
    if not _paths_valid(task.get("allowed_paths")) or not _paths_valid(task.get("blocked_paths")):
        reasons.append("Escopo de caminhos inválido ou vazio.")
    elif any(p in task["blocked_paths"] for p in task["allowed_paths"]):
        reasons.append("Caminho permitido também está bloqueado.")
    if task.get("pending_decisions") != []:
        reasons.append("Existem decisões pendentes ou campo inválido.")
    if task.get("dependencies") != []:
        reasons.append("Existem dependências não comprovadas ou campo inválido.")
    if task.get("preconditions") != ["VERIFICADAS"]:
        reasons.append("Pré-condições não foram comprovadas no contrato.")
    if task.get("cost_policy") != "R$ 0 — sem serviços faturáveis":
        reasons.append("Política de custo não corresponde à regra estrita.")
    action = task.get("requested_action")
    if action != "plan_only":
        reasons.append("Somente a ação plan_only é permitida nesta fase.")
    if isinstance(action, str) and action in DANGEROUS_ACTIONS:
        reasons.append("Ação com efeitos externos explicitamente proibida.")
    for key in ("title", "requirements", "accepted_adrs", "interfaces", "acceptance_criteria", "test_plan", "risk", "rollback"):
        value = task.get(key)
        if not value or (isinstance(value, (list, dict)) and not len(value)):
            reasons.append(f"Campo sem evidência mínima: {key}.")
    if not isinstance(task.get("attempts_by_root_cause"), dict):
        reasons.append("Contador de tentativas inválido.")
    else:
        for count in task["attempts_by_root_cause"].values():
            if type(count) is not int or count < 0 or count >= 3:
                reasons.append("Limite de tentativas atingido ou contador inválido.")
                break
    return {
        "decision": "PLAN_ONLY" if not reasons else "BLOCKED",
        "agent": agent if isinstance(agent, str) and agent in AGENT_IDS else None,
        "task_id": task.get("task_id") if isinstance(task.get("task_id"), str) else None,
        "reasons": reasons,
        "effects": [],
        "notice": "Parecer local sem execução, commit, rede, merge ou aprovação de negócio.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="Arquivo JSON de contrato sintético")
    args = parser.parse_args()
    try:
        if args.contract.is_symlink() or args.contract.stat().st_size > 100_000:
            raise ValueError("Arquivo simbólico ou grande demais.")
        task = json.loads(args.contract.read_text(encoding="utf-8"))
        result = evaluate(task)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        result = {"decision": "BLOCKED", "agent": None, "reasons": ["Contrato ilegível/inválido."], "effects": []}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["decision"] == "PLAN_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
