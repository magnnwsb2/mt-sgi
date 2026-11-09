#!/usr/bin/env python3
"""MT SGI: verificador determinístico da fundação SDD/agentes.

Sem serviços externos, sem autenticação, sem dependências de terceiros.
Não substitui proteção GitHub, revisão humana, análise estática completa ou
verificação de requisitos de negócio. Retorna saída != 0 ao encontrar falha.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

AGENTS = {
    "orchestrator.md": "AGT-001",
    "sdd-guardian.md": "AGT-002",
    "architect.md": "AGT-003",
    "identity-agent.md": "AGT-004",
    "catalog-agent.md": "AGT-005",
    "procurement-agent.md": "AGT-006",
    "inventory-agent.md": "AGT-007",
    "sales-agent.md": "AGT-008",
    "payments-cash-agent.md": "AGT-009",
    "reporting-agent.md": "AGT-010",
    "audit-agent.md": "AGT-011",
    "qa-agent.md": "AGT-012",
    "security-agent.md": "AGT-013",
    "devops-agent.md": "AGT-014",
    "merge-guardian.md": "AGT-015",
}

CORE_DOCUMENTS = (
    "AGENTS.md",
    "README.md",
    "agents/README.md",
    "docs/specs/SDD-001.md",
    "docs/specs/SDD-002-dominios-contratos.md",
    "docs/specs/SDD-003-tecnologias-operacao.md",
    "docs/specs/SDD-004-agentes-autonomia.md",
    "docs/specs/SDD-STATUS.md",
    "docs/adr/ADR-001-arquitetura-modular-extracao-progressiva.md",
    "docs/adr/ADR-002-consistencia-venda-estoque-caixa.md",
    "docs/adr/ADR-006-agentes-autonomia-merge.md",
    "docs/agents/RUNBOOK.md",
    "docs/agents/TASK-CONTRACT.md",
    "docs/operations/MERGE-GUARDIAN.md",
    "docs/decisions/DECISION-LOG.md",
    "docs/decisions/requests/SD-TEMPLATE.md",
    ".github/workflows/governance.yml",
    ".github/pull_request_template.md",
)

REQUIRED_AGENT_SECTIONS = (
    "## 1. Missão",
    "## 2. Bootstrap obrigatório",
    "## 3. Escopo e responsabilidades",
    "## 4. Interfaces e dependências",
    "## 5. Proibições e decisões bloqueadoras",
    "## 6. Plano de implementação e critérios de aceite",
    "## 7. Evidência e transferência de contexto",
)
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "dist", "build"}
TEXT_EXTENSIONS = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".sh", ".env"}
SECRET_PATTERNS = {
    "GitHub classic token": re.compile(r"gh(?:p|o|u|s|r)_[A-Za-z0-9]{30,}"),
    "GitHub fine-grained token": re.compile(r"github_pat_[A-Za-z0-9_]{60,}"),
    "AWS access key": re.compile(r"AKIA[A-Z0-9]{16}"),
    "Private key header": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
}


def find_secret_patterns(text: str) -> list[str]:
    """Apenas padrões fortes; não exibe o segredo encontrado."""
    return [label for label, pattern in SECRET_PATTERNS.items() if pattern.search(text)]


def read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError(relative)
    return path.read_text(encoding="utf-8")


def validate_agent_docs(root: Path) -> list[str]:
    errors: list[str] = []
    folder = root / "agents"
    if not folder.is_dir():
        return ["Diretório agents/ ausente."]
    found = {p.name for p in folder.glob("*.md") if p.name != "README.md"}
    expected = set(AGENTS)
    for name in sorted(expected - found):
        errors.append(f"Perfil de agente obrigatório ausente: agents/{name}")
    for name in sorted(found - expected):
        errors.append(f"Perfil extra sem revisão SDD: agents/{name}")
    ids: set[str] = set()
    for name, expected_id in AGENTS.items():
        if name not in found:
            continue
        try:
            content = read_text(root, f"agents/{name}")
        except (UnicodeError, OSError) as exc:
            errors.append(f"Não foi possível ler agents/{name}: {type(exc).__name__}")
            continue
        headings = re.findall(r"^# (AGT-\d{3}) —", content, re.MULTILINE)
        if headings != [expected_id]:
            errors.append(f"ID inválido ou duplicado no título de agents/{name}; esperado {expected_id}")
        elif headings[0] in ids:
            errors.append(f"ID repetido: {expected_id}")
        else:
            ids.add(headings[0])
        for section in REQUIRED_AGENT_SECTIONS:
            if section not in content:
                errors.append(f"Seção obrigatória ausente em agents/{name}: {section}")
        for reference in ("SDD-001", "SDD-004", "SDD-STATUS", "ADR"):
            if reference not in content:
                errors.append(f"Referência {reference} ausente em agents/{name}")
        if "NÃO É PROCESSO EM BACKGROUND" not in content:
            errors.append(f"Sem limitação explícita de execução em agents/{name}")
    return errors


def validate_core_documents(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in CORE_DOCUMENTS:
        try:
            text = read_text(root, relative)
        except (OSError, UnicodeError):
            errors.append(f"Documento obrigatório ausente/ilegível: {relative}")
            continue
        if not text.strip():
            errors.append(f"Documento obrigatório vazio: {relative}")
    checks = {
        "docs/specs/SDD-001.md": ("SDD-004", "ADR-006", "ADR-002", "PROPOSTA"),
        "docs/specs/SDD-004-agentes-autonomia.md": ("APROVADO", "ChatGPT + GitHub", "Merge Guardian", "GOV-012"),
        "docs/adr/ADR-006-agentes-autonomia-merge.md": ("ACEITA", "ADR-002", "PROPOSTA"),
        "docs/adr/ADR-002-consistencia-venda-estoque-caixa.md": ("PROPOSTA — NÃO ACEITA",),
        "docs/decisions/DECISION-LOG.md": ("GOV-DEC-001", "GOV-DEC-009", "ADR-002 PROPOSTA"),
        "docs/operations/MERGE-GUARDIAN.md": ("fail-closed", "MG-001", "MG-011", "auto-merge"),
        ".github/workflows/governance.yml": ("pull_request:", "contents: read", "governance-validation", "timeout-minutes:"),
    }
    for name, phrases in checks.items():
        try:
            content = read_text(root, name)
        except (OSError, UnicodeError):
            continue
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"Documento {name} não contém a garantia esperada: {phrase}")
    manifest_path = root / "agents/README.md"
    if manifest_path.is_file():
        manifest = manifest_path.read_text(encoding="utf-8")
        for name in AGENTS:
            if f"({name})" not in manifest:
                errors.append(f"Manifesto omite agente: {name}")
    # Conferência cruzada: inventário normativo, manifesto e mapa de validação.
    spec = root / "docs/specs/SDD-004-agentes-autonomia.md"
    if spec.is_file():
        spec_text = spec.read_text(encoding="utf-8")
        # SDD-004 lista Papel | Arquivo | Responsabilidade, sem coluna AGT-ID.
        spec_entries = re.findall(
            r"(?m)^\|[^\n|]+\|\s*`(agents/[^\x60]+\.md)`\s*\|",
            spec_text,
        )
        expected_entries = [f"agents/{name}" for name in AGENTS]
        if spec_entries != expected_entries:
            errors.append("Inventário SDD-004 diverge dos 15 perfis canônicos.")
    if manifest_path.is_file():
        manifest_entries = dict(re.findall(
            r"\|\s*(AGT-\d{3})\s*\|\s*\[[^]]+\]\(([^)]+\.md)\)",
            manifest,
        ))
        expected_manifest = {agent_id: name for name, agent_id in AGENTS.items()}
        if manifest_entries != expected_manifest:
            errors.append("Inventário agents/README.md diverge dos 15 perfis canônicos.")
    return errors


def iter_repo_text(root: Path) -> Iterable[tuple[str, str]]:
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {"AGENTS.md", ".gitignore"}:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        try:
            yield rel.as_posix(), path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            # Leitura difícil não equivale a "seguro": interromper por erro no caller.
            raise ValueError(f"Arquivo texto ilegível: {rel.as_posix()}") from None


def validate_secrets(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, content in iter_repo_text(root):
        for label in find_secret_patterns(content):
            errors.append(f"Padrão possível de credencial ({label}) detectado em {relative}; valor não exibido.")
    return errors


def validate_workflow_policy(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".github/workflows/governance.yml"
    if not path.is_file():
        return errors
    workflow = path.read_text(encoding="utf-8")
    if "pull_request_target" in workflow:
        errors.append("Workflow de governança não pode utilizar pull_request_target.")
    if re.search(r"(?m)^\s*(?:write-all|id-token:\s*write|contents:\s*write)\s*$", workflow):
        errors.append("Workflow de governança contém permissão excessiva.")
    if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", workflow):
        errors.append("Workflow deve limitar permissões globais a contents: read.")
    if re.search(r"(?m)^[ \t]+permissions[ \t]*:", workflow):
        errors.append("Workflow não pode sobrescrever permissões no job.")
    if not re.search(r"(?m)^\s+persist-credentials:\s*false\s*$", workflow):
        errors.append("Checkout deve desabilitar persistência de credenciais.")
    if not re.search(r"(?m)^\s+uses:\s*actions/checkout@[a-f0-9]{40}(?:\s|$)", workflow):
        errors.append("Checkout deve usar SHA completo imutável.")
    if "scripts/validate_governance.py" not in workflow or "unittest" not in workflow:
        errors.append("Workflow não executa validador e testes de regressão.")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(validate_agent_docs(root))
    failures.extend(validate_core_documents(root))
    failures.extend(validate_workflow_policy(root))
    try:
        failures.extend(validate_secrets(root))
    except ValueError as exc:
        failures.append(str(exc))
    return sorted(set(failures))


def main() -> int:
    failures = validate_repository(ROOT)
    if failures:
        print(f"MT SGI GOVERNANCE: FAIL ({len(failures)} ocorrência(s))")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(f"MT SGI GOVERNANCE: PASS — {len(AGENTS)} perfis; estrutura, estados e padrões fortes de segredos verificados.")
    print("AVISO: não valida semântica de negócio, branch protection, reviewers ou auto-merge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
