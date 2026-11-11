"""Despachante MT SGI: planeja/audita, sem executar efeitos ou confiar em flags do solicitante.

O contrato é entrada não confiável. A inspeção local é independente do contrato;
não prova nenhum controle remoto GitHub. Apenas stdlib, nenhum token/rede/write.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from scripts.validate_governance import AGENTS, ROOT, validate_repository
except ModuleNotFoundError:  # execução direta: python3 scripts/agent_dispatcher.py
    from validate_governance import AGENTS, ROOT, validate_repository

AGENT_IDS = frozenset(AGENTS.values())
GOV_REQUIREMENTS = frozenset(f"GOV-{i:03d}" for i in range(1, 13))
ALLOWED_ACTIONS = frozenset({"plan_only", "inspect_governance"})
AUDITOR_IDS = frozenset({"AGT-001", "AGT-002", "AGT-012", "AGT-013", "AGT-015"})
STATES = frozenset({"PROPOSTA", "EM_EXECUCAO", "BLOQUEADA", "EM_REVISAO", "CONCLUIDA"})
REQUIRED_FIELDS = frozenset({
    "task_id", "state", "title", "owner_agent", "secondary_agents",
    "repo", "baseline_branch", "baseline_sha", "work_branch",
    "requirements", "accepted_adrs", "pending_decisions", "allowed_paths",
    "blocked_paths", "preconditions", "dependencies", "interfaces",
    "acceptance_criteria", "test_plan", "risk", "rollback", "cost_policy",
    "attempts_by_root_cause", "requested_action",
})
OPTIONAL_FIELDS = frozenset({"pr_number", "outcome"})
SHA = re.compile(r"^[a-f0-9]{40}$")
TASK_ID = re.compile(r"^TC-[0-9]{4,}$")
BRANCH = re.compile(r"^(?:feat|fix|docs|test)/[a-zA-Z0-9._/-]+$")
PATH = re.compile(r"^(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+/?$")


def _paths_valid(values: Any) -> bool:
    if not isinstance(values, list) or not values:
        return False
    for p in values:
        if not isinstance(p, str) or not PATH.fullmatch(p):
            return False
        parts = p.rstrip("/").split("/")
        if any(x in {"", ".", ".."} for x in parts) or parts[0] == ".git":
            return False
    return True


def _path_overlap(a: str, b: str) -> bool:
    a, b = a.rstrip("/"), b.rstrip("/")
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def _str_list(v: Any, *, nonempty: bool = True) -> bool:
    return (
        isinstance(v, list)
        and (bool(v) or not nonempty)
        and all(isinstance(x, str) and bool(x.strip()) and len(x) <= 300 for x in v)
    )


def _inspect_local(root: Path) -> tuple[list[str], dict[str, Any]]:
    """Verifica fatos no checkout; NÃO concede permissão remota."""
    issues = validate_repository(root)
    try:
        sdd = (root / "docs/specs/SDD-001.md").read_text(encoding="utf-8")
        gov = (root / "docs/specs/SDD-004-agentes-autonomia.md").read_text(encoding="utf-8")
        if not all(f"AUT-{n:03d}" in sdd for n in range(1, 13)):
            issues.append("Princípios AUT-001..012 ausentes do SDD-001 do checkout.")
        if "## 14. Contrato de conformidade operacional autônoma" not in gov:
            issues.append("Contrato de conformidade ausente do SDD-004 do checkout.")
    except (OSError, UnicodeError):
        issues.append("SDD local ausente ou ilegível.")
    return sorted(set(issues)), {
        "origin": "local_checkout_only",
        "agents_expected": len(AGENT_IDS),
        "governance": "PASS" if not issues else "FAIL",
        "remote_head": "NOT_VERIFIED",
        "branch_protection": "NOT_VERIFIED",
        "independent_review": "NOT_VERIFIED",
        "write_authorization": "DENIED",
    }


def evaluate(task: Any, *, root: Path = ROOT) -> dict[str, Any]:
    """Classifica a tarefa e, opcionalmente, executa auditoria local somente de leitura."""
    reasons: list[str] = []
    if not isinstance(task, dict):
        return {
            "decision": "BLOCKED", "agent": None, "reasons": ["Contrato não é objeto JSON."],
            "effects": [],
        }
    missing = sorted(REQUIRED_FIELDS - task.keys())
    extra = sorted(task.keys() - REQUIRED_FIELDS - OPTIONAL_FIELDS)
    if missing:
        reasons.append("Campos obrigatórios ausentes: " + ", ".join(missing))
    if extra:
        reasons.append("Campos não reconhecidos: " + ", ".join(extra))
    agent = task.get("owner_agent")
    if not isinstance(agent, str) or agent not in AGENT_IDS:
        reasons.append("Agente proprietário não registrado.")
    secondary = task.get("secondary_agents")
    if not isinstance(secondary, list) or any(
        not isinstance(a, str) or a not in AGENT_IDS for a in secondary
    ):
        reasons.append("Agentes secundários inválidos.")
    task_id = task.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        reasons.append("ID de tarefa inválido.")
    if task.get("repo") != "magnnwsb2/mt-sgi":
        reasons.append("Repositório fora do escopo.")
    if not isinstance(task.get("state"), str) or task["state"] not in STATES:
        reasons.append("Estado de tarefa inválido.")
    if task.get("state") != "EM_EXECUCAO":
        reasons.append("Somente tarefa EM_EXECUCAO pode ser admitida.")
    baseline = task.get("baseline_sha")
    if not isinstance(baseline, str) or not SHA.fullmatch(baseline):
        reasons.append("SHA de baseline inválido; formato não prova identidade remota.")
    if not isinstance(task.get("baseline_branch"), str) or task["baseline_branch"] not in {
        "main", "feat/agent-governance-foundation",
    }:
        reasons.append("Baseline não reconhecida.")
    work_branch = task.get("work_branch")
    if not isinstance(work_branch, str) or not BRANCH.fullmatch(work_branch):
        reasons.append("Branch de trabalho inválida.")
    elif work_branch == task.get("baseline_branch") or ".." in work_branch or "//" in work_branch:
        reasons.append("Branch de trabalho insegura ou igual à baseline.")
    allowed, blocked = task.get("allowed_paths"), task.get("blocked_paths")
    if not _paths_valid(allowed) or not _paths_valid(blocked):
        reasons.append("Escopo de caminhos inválido ou vazio.")
    elif any(_path_overlap(a, b) for a in allowed for b in blocked):
        reasons.append("Escopo permitido conflita com caminho bloqueado por ancestralidade.")
    if task.get("pending_decisions") != []:
        reasons.append("Existem decisões pendentes ou campo inválido.")
    if task.get("dependencies") != []:
        reasons.append("Dependências não resolvidas ou campo inválido.")
    # A declaração da precondição NÃO é prova. _inspect_local() verifica a fonte.
    if task.get("preconditions") != ["GOVERNANCE_REPO_VALID"]:
        reasons.append("Pré-condições não suportadas; não aceitar autodeclaração VERIFICADAS.")
    if task.get("cost_policy") != "R$ 0 — sem serviços faturáveis":
        reasons.append("Política de custo inválida.")
    requested = task.get("requested_action")
    if not isinstance(requested, str) or requested not in ALLOWED_ACTIONS:
        reasons.append("Ação não permitida: somente plan_only/inspect_governance.")
    if requested == "inspect_governance" and agent not in AUDITOR_IDS:
        reasons.append("Papel sem autorização para auditoria de governança.")
    requirements = task.get("requirements")
    if not _str_list(requirements) or any(v not in GOV_REQUIREMENTS for v in requirements):
        reasons.append("Requisitos fora do escopo de governança aprovado.")
    accepted = task.get("accepted_adrs")
    if not _str_list(accepted) or any(v not in {"ADR-001", "ADR-006"} for v in accepted):
        reasons.append("ADR não aceita ou lista inválida.")
    for key in ("title", "risk", "rollback"):
        v = task.get(key)
        if not isinstance(v, str) or not v.strip() or len(v) > 1000:
            reasons.append(f"Campo textual inválido: {key}.")
    for key in ("interfaces", "acceptance_criteria"):
        if not _str_list(task.get(key)):
            reasons.append(f"Campo de lista inválido: {key}.")
    plans = task.get("test_plan")
    if not isinstance(plans, list) or not plans or any(
        not isinstance(x, dict) or not isinstance(x.get("id"), str)
        or not isinstance(x.get("status"), str) for x in plans
    ):
        reasons.append("Plano de testes inválido.")
    counters = task.get("attempts_by_root_cause")
    if not isinstance(counters, dict) or any(
        type(v) is not int or v < 0 or v >= 3 for v in counters.values()
    ):
        reasons.append("Limite de 3 tentativas esgotado ou contador inválido.")
    try:
        local_issues, evidence = _inspect_local(root)
    except (OSError, ValueError, RuntimeError, UnicodeError):
        local_issues = ["Falha ao examinar checkout."]
        evidence = {"origin": "local_checkout_only", "governance": "FAIL",
                    "remote_head": "NOT_VERIFIED", "write_authorization": "DENIED"}
    if local_issues:
        reasons.append("Repositório local não aprovado na inspeção de governança.")
    decision = "BLOCKED" if reasons else ("AUDIT_ONLY" if requested == "inspect_governance" else "PLAN_ONLY")
    return {
        "decision": decision,
        "agent": agent if isinstance(agent, str) and agent in AGENT_IDS else None,
        "task_id": task_id if isinstance(task_id, str) else None,
        # Não vazar conteúdo arbitrário, arquivos, tokens nem dados do contrato.
        "reasons": reasons,
        "evidence": evidence,
        "checks_failed": len(local_issues),
        "effects": [],
        "notice": "Somente planejamento/auditoria local: nenhuma permissão de escrita ou merge.",
    }


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON com chave duplicada.")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="Contrato JSON sintético; nunca segredo")
    args = parser.parse_args()
    try:
        if args.contract.is_symlink() or not args.contract.is_file() or args.contract.stat().st_size > 100_000:
            raise ValueError("Arquivo simbólico, ausente ou grande demais.")
        task = json.loads(
            args.contract.read_text(encoding="utf-8"),
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("JSON não finito.")),
        )
        result = evaluate(task)
    except (OSError, ValueError, UnicodeError, TypeError):
        result = {"decision": "BLOCKED", "agent": None,
                  "reasons": ["Contrato ilegível/inválido."], "effects": []}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["decision"] in {"PLAN_ONLY", "AUDIT_ONLY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
