"""Testes offline de despacho seguro; sem credenciais, rede ou efeitos."""
from __future__ import annotations

import copy
import unittest

from scripts.agent_dispatcher import AGENT_IDS, evaluate


def valid_contract():
    return {
        "task_id": "TC-0100",
        "state": "EM_EXECUCAO",
        "title": "Planejar revisão documental",
        "owner_agent": "AGT-001",
        "secondary_agents": ["AGT-002", "AGT-013"],
        "repo": "magnnwsb2/mt-sgi",
        "baseline_branch": "feat/agent-governance-foundation",
        "baseline_sha": "a" * 40,
        "work_branch": "feat/agent-safe-dispatcher",
        "requirements": ["GOV-001"],
        "accepted_adrs": ["ADR-001", "ADR-006"],
        "pending_decisions": [],
        "allowed_paths": ["docs/"],
        "blocked_paths": ["backend/", ".github/"],
        "preconditions": ["VERIFICADAS"],
        "dependencies": [],
        "interfaces": ["Parecer JSON"],
        "acceptance_criteria": ["Nenhum efeito externo"],
        "test_plan": [{"id": "AT-001", "status": "NAO_EXECUTADO"}],
        "risk": "baixo",
        "rollback": "Reverter commit antes de merge",
        "cost_policy": "R$ 0 — sem serviços faturáveis",
        "attempts_by_root_cause": {},
        "requested_action": "plan_only",
    }


class DispatcherTests(unittest.TestCase):
    def test_exact_agent_inventory(self):
        self.assertEqual(len(AGENT_IDS), 15)

    def test_valid_plan_only_has_no_effects(self):
        result = evaluate(valid_contract())
        self.assertEqual(result["decision"], "PLAN_ONLY", result)
        self.assertEqual(result["effects"], [])

    def test_missing_fields_fail_closed(self):
        c = valid_contract()
        del c["preconditions"]
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_pending_business_decision_blocks(self):
        c = valid_contract()
        c["pending_decisions"] = ["ADR-002"]
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_unverified_preconditions_block(self):
        c = valid_contract()
        c["preconditions"] = ["verificar depois"]
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_non_zero_cost_blocks(self):
        c = valid_contract()
        c["cost_policy"] = "free trial"
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_main_as_work_branch_blocks(self):
        c = valid_contract()
        c["work_branch"] = "main"
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_executing_any_effect_blocks(self):
        for action in ("merge", "push_main", "deploy", "payment", "execute_code", "external_network", "delete", "change_permissions", "commit"):
            with self.subTest(action=action):
                c = valid_contract()
                c["requested_action"] = action
                self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_retry_budget_exhausted_blocks(self):
        c = valid_contract()
        c["attempts_by_root_cause"] = {"causa": 3}
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_unregistered_agent_blocks(self):
        c = valid_contract()
        c["owner_agent"] = "AGT-999"
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_dependency_blocks(self):
        c = valid_contract()
        c["dependencies"] = ["PR-2"]
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_invalid_path_blocks(self):
        for bad in ("../secrets", "/root", "docs/../../secret", "docs//test", ".git/config"):
            with self.subTest(path=bad):
                c = valid_contract()
                c["allowed_paths"] = [bad]
                self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_conflicting_path_blocks(self):
        c = valid_contract()
        c["blocked_paths"] = ["docs/"]
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_invalid_json_types_fail_closed_without_crash(self):
        cases = [
            None, [], "hello", {"owner_agent": []}, {"state": {}},
            {"requested_action": ["merge"]}, {"baseline_branch": []},
        ]
        for value in cases:
            with self.subTest(value=value):
                self.assertEqual(evaluate(value)["decision"], "BLOCKED")

    def test_invalid_secondary_agent_type_blocks(self):
        c = valid_contract()
        c["secondary_agents"] = [[]]
        self.assertEqual(evaluate(c)["decision"], "BLOCKED")

    def test_invalid_attempt_counter_blocks(self):
        for counter in (True, -1, "1", None):
            with self.subTest(counter=counter):
                c = valid_contract()
                c["attempts_by_root_cause"] = {"x": counter}
                self.assertEqual(evaluate(c)["decision"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
