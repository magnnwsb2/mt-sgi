"""Testes unitários do validador de governança: sem rede e sem secrets reais."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate_governance import (
    AGENTS,
    ROOT,
    find_secret_patterns,
    validate_agent_docs,
    validate_core_documents,
    validate_repository,
    validate_workflow_policy,
)


class GovernanceTests(unittest.TestCase):
    def test_inventory_exactly_fifteen(self) -> None:
        self.assertEqual(len(AGENTS), 15)
        self.assertEqual(len(set(AGENTS.values())), 15)

    def test_agent_profiles_present_and_valid(self) -> None:
        self.assertEqual(validate_agent_docs(ROOT), [])

    def test_core_docs_present(self) -> None:
        self.assertEqual(validate_core_documents(ROOT), [])

    def test_workflow_policy(self) -> None:
        self.assertEqual(validate_workflow_policy(ROOT), [])

    def test_repository_validation(self) -> None:
        self.assertEqual(validate_repository(ROOT), [])

    def test_synthetic_github_token_detected(self) -> None:
        fake = "gh" + "p_" + "A" * 36
        self.assertIn("GitHub classic token", find_secret_patterns(fake))

    def test_synthetic_fine_grained_token_detected(self) -> None:
        fake = "github_" + "pat_" + "B" * 80
        self.assertIn("GitHub fine-grained token", find_secret_patterns(fake))

    def test_synthetic_aws_key_detected(self) -> None:
        fake = "AK" + "IA" + "C" * 16
        self.assertIn("AWS access key", find_secret_patterns(fake))

    def test_synthetic_private_key_header_detected(self) -> None:
        fake = "-----BEGIN " + "PRIVATE KEY-----"
        self.assertIn("Private key header", find_secret_patterns(fake))

    def test_normal_document_not_flagged(self) -> None:
        self.assertEqual(find_secret_patterns("Exemplo: nunca colocar tokens no repositório."), [])

    def test_missing_agent_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copytree(ROOT / "agents", root / "agents")
            (root / "agents" / "inventory-agent.md").unlink()
            self.assertTrue(any("inventory-agent.md" in e for e in validate_agent_docs(root)))

    def test_unregistered_agent_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copytree(ROOT / "agents", root / "agents")
            (root / "agents" / "unexpected-agent.md").write_text("# novo", encoding="utf-8")
            self.assertTrue(any("Perfil extra" in e for e in validate_agent_docs(root)))

    def test_missing_section_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copytree(ROOT / "agents", root / "agents")
            p = root / "agents" / "qa-agent.md"
            text = p.read_text(encoding="utf-8")
            p.write_text(text.replace("## 6. Plano de implementação e critérios de aceite", "## substituído"), encoding="utf-8")
            self.assertTrue(any("Seção obrigatória" in e for e in validate_agent_docs(root)))

    def test_missing_core_document_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertTrue(any("AGENTS.md" in e for e in validate_core_documents(root)))

    def test_empty_core_document_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("  ", encoding="utf-8")
            self.assertTrue(any("Documento obrigatório vazio: AGENTS.md" in e
                                for e in validate_core_documents(root)))

    def test_workflow_unsafe_permissions_are_blocking(self) -> None:
        original = (ROOT / ".github/workflows/governance.yml").read_text(encoding="utf-8")
        mutations = (
            ("  contents: read", "  contents: write"),
            ("  contents: read", "  id-token: write"),
            ("  contents: read", "  write-all"),
            ("pull_request:", "pull_request_target:"),
            ("persist-credentials: false", "persist-credentials: true"),
            ("actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683",
             "actions/checkout@v4"),
            ("    runs-on: ubuntu-latest", "    permissions:\\n      contents: write\\n    runs-on: ubuntu-latest"),
            ("python3 scripts/validate_governance.py", "echo skipped-validator"),
            ("python3 -m unittest", "echo skipped-tests"),
        )
        for before, after in mutations:
            with self.subTest(after=after):
                self.assertIn(before, original)
                with tempfile.TemporaryDirectory() as d:
                    root = Path(d)
                    workflow = root / ".github/workflows/governance.yml"
                    workflow.parent.mkdir(parents=True)
                    workflow.write_text(original.replace(before, after, 1), encoding="utf-8")
                    self.assertTrue(validate_workflow_policy(root), msg=after)

    def test_manifest_inventory_drift_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "agents").mkdir()
            (root / "docs/specs").mkdir(parents=True)
            shutil.copy(ROOT / "docs/specs/SDD-004-agentes-autonomia.md",
                        root / "docs/specs/SDD-004-agentes-autonomia.md")
            source = (ROOT / "agents/README.md").read_text(encoding="utf-8")
            (root / "agents/README.md").write_text(
                source.replace("AGT-015", "AGT-999", 1), encoding="utf-8"
            )
            self.assertTrue(any("Inventário agents/README.md" in e
                                for e in validate_core_documents(root)))

    def test_sdd_inventory_drift_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "agents").mkdir()
            (root / "docs/specs").mkdir(parents=True)
            shutil.copy(ROOT / "agents/README.md", root / "agents/README.md")
            source = (ROOT / "docs/specs/SDD-004-agentes-autonomia.md").read_text(encoding="utf-8")
            (root / "docs/specs/SDD-004-agentes-autonomia.md").write_text(
                source.replace("AGT-015", "AGT-999", 1), encoding="utf-8"
            )
            self.assertTrue(any("Inventário SDD-004" in e
                                for e in validate_core_documents(root)))

    def test_no_dependency_on_paid_services(self) -> None:
        doc = (ROOT / "docs/specs/SDD-004-agentes-autonomia.md").read_text(encoding="utf-8")
        self.assertIn("R$ 0", doc)
        self.assertIn("não", doc.lower())


if __name__ == "__main__":
    unittest.main()
