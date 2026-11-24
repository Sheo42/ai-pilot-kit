"""Tests of the generated traceability matrix (scripts/ci/trace.py)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import trace

REQUIREMENTS = """# Live monitoring

### REQ-MON-002: Show the fleet at a glance

| Field | Value |
|---|---|
| Category | FUN |
| Priority | Must |
| Phase | 2 Lab |
| Status | Approved |
| Related ADRs | ADR-0015 |

- **AC1** (method: Test)
  Given ...
- **AC2** (method: Test)
  Given ...

### REQ-ING-016: Accept the walking skeleton's device

| Field | Value |
|---|---|
| Category | FUN |
| Priority | Must |
| Phase | 1 Skeleton |
| Status | Verified (phase 1 gate) |

- **AC1** (method: Test)
- **AC2** (method: Inspection; read the code)

### REQ-PRV-012: Use only cookies the platform cannot work without

| Field | Value |
|---|---|
| Category | CMP |
| Priority | Should |
| Phase | 4 First customer |
| Status | Draft |

- **AC1** (method: Test)

```
### REQ-XXX-999: in a fence, not a requirement
```
"""


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write(tmp_path, "docs/requirements/live.md", REQUIREMENTS)
    write(
        tmp_path,
        "backend/tests/test_fleet.py",
        "import pytest\n\n"
        '@pytest.mark.req("REQ-MON-002.AC1")\n'
        "def test_five_sites():\n    pass\n\n"
        '@pytest.mark.req("REQ-ING-016.AC1")\n'
        "class TestDevice:\n"
        "    def test_it_connects(self):\n        pass\n\n"
        "def test_untagged():\n    pass\n",
    )
    write(
        tmp_path,
        "simulator/tests/test_module.py",
        'import pytest\n\npytestmark = [pytest.mark.req("REQ-ING-016.AC1"), pytest.mark.slow]\n\n'
        "async def test_one():\n    pass\n",
    )
    write(
        tmp_path,
        "frontend/src/FleetPage.test.tsx",
        'it("REQ-MON-002.AC2: an owner sees that site only", () => {});\n'
        'it("links to the alarm list (REQ-ALM-017)", () => {});\n'
        "describe(`REQ-MON-002.AC1: the fleet page`, () => {});\n",
    )
    write(tmp_path, "docs/traceability.md", "# Traceability matrix\n\nGenerated.\n")
    return tmp_path


def test_requirements_fields_and_acs(repo: Path) -> None:
    found = trace.read_requirements(repo)
    assert sorted(found) == ["REQ-ING-016", "REQ-MON-002", "REQ-PRV-012"]
    mon = found["REQ-MON-002"]
    assert mon.title == "Show the fleet at a glance" and mon.phase_number == 2
    assert mon.acs == {"AC1": "Test", "AC2": "Test"} and mon.fields["Related ADRs"] == "ADR-0015"
    assert found["REQ-ING-016"].status == "Verified" and found["REQ-ING-016"].acs["AC2"] == "Inspection"


def test_tags_of_python_typescript_and_classes(repo: Path) -> None:
    result = trace.collect(repo)
    assert result.errors == []
    assert result.by_ac["REQ-MON-002.AC1"] == [
        "backend/tests/test_fleet.py::test_five_sites",
        'frontend/src/FleetPage.test.tsx "REQ-MON-002.AC1: the fleet page"',
    ]
    assert result.by_ac["REQ-ING-016.AC1"] == [
        "backend/tests/test_fleet.py::TestDevice::test_it_connects",
        "simulator/tests/test_module.py::test_one",
    ]
    assert result.by_ac["REQ-MON-002.AC2"] == [
        'frontend/src/FleetPage.test.tsx "REQ-MON-002.AC2: an owner sees that site only"'
    ]
    assert not any("untagged" in name for names in result.by_ac.values() for name in names)


def test_file_comments_scripts_and_proofs(repo: Path) -> None:
    write(repo, "frontend/src/SitePage.test.tsx", "// req: REQ-MON-002.AC2 (the file as a whole)\nit('x', () => {});\n")
    write(
        repo,
        "scripts/ci/smoke.sh",
        "#!/usr/bin/env bash\n# checks REQ-MON-002.AC1 in a plain comment: not a tag\n"
        'echo "ok    Only Caddy\'s ports are published (REQ-ING-016.AC1)"\n'
        "# req: REQ-ING-016.AC2\n",
    )
    write(
        repo,
        "docs/verification/REQ-ING-016.AC2-read.md",
        "| Field | Value |\n|---|---|\n| Criterion | REQ-ING-016.AC2, method Inspection |\n| Result | Pass |\n",
    )
    result = trace.collect(repo)
    assert "frontend/src/SitePage.test.tsx" in result.by_ac["REQ-MON-002.AC2"]
    assert (
        result.by_ac["REQ-ING-016.AC1"][-1]
        == 'scripts/ci/smoke.sh "Only Caddy\'s ports are published (REQ-ING-016.AC1)"'
    )
    assert result.by_ac["REQ-ING-016.AC2"] == ["scripts/ci/smoke.sh", "docs/verification/REQ-ING-016.AC2-read.md"]
    assert not any(name.startswith("scripts/ci/smoke.sh") for name in result.by_ac["REQ-MON-002.AC1"])


def test_a_partial_proof_keeps_the_ac_uncovered_and_says_why(repo: Path) -> None:
    write(
        repo,
        "docs/verification/REQ-MON-002.AC1-partial.md",
        "| Field | Value |\n|---|---|\n| Criterion | REQ-MON-002.AC1 |\n"
        "| Result | Partial: sites only, no alarms yet |\n",
    )
    result = trace.collect(repo)
    assert not result.covered("REQ-MON-002.AC1") and result.covered("REQ-MON-002.AC2")
    view = trace.render(result)
    assert "[Partial: sites only, no alarms yet](docs/verification/REQ-MON-002.AC1-partial.md)" in view
    assert "| Approved and later, Must | 2 / 4 | 50% |" in view


def test_wrong_tags_are_errors(repo: Path) -> None:
    write(
        repo,
        "backend/tests/test_wrong.py",
        "import pytest\n\n"
        '@pytest.mark.req("REQ-MON-009.AC1")\ndef test_a():\n    pass\n\n'
        '@pytest.mark.req("REQ-MON-002")\ndef test_b():\n    pass\n\n'
        '@pytest.mark.req("REQ-MON-002.AC7")\ndef test_c():\n    pass\n',
    )
    write(repo, "backend/tests/test_broken.py", "def test_(:\n")
    errors = trace.collect(repo).errors
    assert "backend/tests/test_broken.py: cannot be read" in errors[0]
    assert "backend/tests/test_wrong.py:3: REQ-MON-009.AC1 is not in docs/requirements/" in errors
    assert "backend/tests/test_wrong.py:7: REQ-MON-002 names a requirement, not an AC: add .ACn" in errors
    assert "backend/tests/test_wrong.py:11: REQ-MON-002.AC7: REQ-MON-002 has no AC7" in errors


def test_gate_gaps_and_legacy_rows(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert trace.main([str(repo), "--check", "--gates-passed", "1"]) == 1  # REQ-ING-016.AC2 has no proof
    assert "REQ-ING-016.AC2 (phase 1, gate passed) is not fully covered" in capsys.readouterr().err
    write(repo, "docs/verification/x.md", "| Criterion | REQ-ING-016.AC2 |\n| Result | Pass |\n")
    assert trace.main([str(repo), "--check", "--gates-passed", "1"]) == 0
    assert trace.main([str(repo), "--check", "--gates-passed", "0"]) == 0
    write(repo, "docs/traceability.md", "| REQ-MON-002 | Show the fleet | FUN |\n")
    assert trace.main([str(repo), "--check"]) == 1
    assert "docs/traceability.md:1: a hand-kept matrix row" in capsys.readouterr().err


def test_view_counts_and_settings(
    repo: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    assert trace.main([str(repo)]) == 0
    view = capsys.readouterr().out
    assert "| Approved and later, Must | 3 / 4 | 75% |" in view  # REQ-PRV-012 is Draft, not counted
    assert "| 1 Skeleton | 1 | 2 | 1 |" in view and "| 2 Lab | 1 | 2 | 2 |" in view
    assert "| REQ-MON-002 | Show the fleet at a glance | FUN | Must | 2 Lab | Approved | AC1 | Test |" in view
    assert "| ADR-0015 |" in view
    monkeypatch.setenv("TRACE_GATES_PASSED", "seven")
    assert trace.main([str(repo), "--check"]) == 2
    assert trace.main([str(repo), "--check", "--gates-passed"]) == 2
    assert trace.main([str(repo / "nowhere")]) == 2


def test_tests_that_never_run_count_for_nothing(repo: Path) -> None:
    write(
        repo,
        "backend/tests/test_skipped.py",
        "import pytest\n\n"
        '@pytest.mark.skip(reason="later")\n@pytest.mark.req("REQ-ING-016.AC2")\ndef test_a():\n    pass\n\n'
        '@pytest.mark.skipif(True, reason="CI decides")\n'
        '@pytest.mark.req("REQ-PRV-012.AC1")\ndef test_b():\n    pass\n',
    )
    write(
        repo,
        "frontend/e2e/later.journey.ts",
        'test.fixme("REQ-ING-016.AC2: later", async () => {});\nit.skip("REQ-ING-016.AC2: later", () => {});\n',
    )
    result = trace.collect(repo)
    assert "REQ-ING-016.AC2" not in result.by_ac
    assert result.by_ac["REQ-PRV-012.AC1"] == ["backend/tests/test_skipped.py::test_b"]


def test_implemented_counts_and_later_sections_belong_to_no_requirement(repo: Path) -> None:
    text = (repo / "docs/requirements/live.md").read_text(encoding="utf-8")
    text = text.replace("| Status | Draft |", "| Status | Implemented |")
    text += "\n## Examples\n\n| Status | Draft |\n\n- **AC9** (method: Test)\n"
    write(repo, "docs/requirements/live.md", text)
    found = trace.read_requirements(repo)
    assert found["REQ-PRV-012"].status == "Implemented" and "AC9" not in found["REQ-PRV-012"].acs
    assert "| Approved and later, all | 3 / 5 | 60% |" in trace.render(trace.collect(repo))


def test_probe_docstrings_and_shell_comments_are_mentions(repo: Path) -> None:
    write(
        repo,
        "scripts/ci/public_probe.py",
        '"""Was meant to check REQ-ING-016.AC2, not done yet."""\n\n'
        'def check(what, test):\n    """REQ-ING-016.AC2 again."""\n\n'
        'check("Headers are set (REQ-PRV-012.AC1)", lambda: True)\n',
    )
    write(repo, "scripts/ci/smoke.sh", "echo 'ok    single quotes count too (REQ-MON-002.AC2)'\n")
    result = trace.collect(repo)
    assert "REQ-ING-016.AC2" not in result.by_ac
    assert result.by_ac["REQ-PRV-012.AC1"] == ['scripts/ci/public_probe.py "Headers are set (REQ-PRV-012.AC1)"']
    assert 'scripts/ci/smoke.sh "single quotes count too (REQ-MON-002.AC2)"' in result.by_ac["REQ-MON-002.AC2"]


def test_a_gate_file_adds_acs_of_later_phases(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(repo, "docs/verification/x.md", "| Criterion | REQ-ING-016.AC2 |\n| Result | Pass |\n")
    write(repo, "docs/verification/gate-1.md", "| Gate criteria | REQ-PRV-012.AC1, REQ-MON-002.AC9 |\n")
    assert trace.main([str(repo), "--check", "--gates-passed", "1"]) == 1
    err = capsys.readouterr().err
    assert "docs/verification/gate-1.md:1: REQ-PRV-012.AC1 (in this gate, passed) is not fully covered" in err
    assert "docs/verification/gate-1.md:1: REQ-MON-002.AC9 is not in docs/requirements/" in err
    assert trace.main([str(repo), "--check", "--gates-passed", "0"]) == 0
    assert "REQ-PRV-012.AC1" not in trace.collect(repo).by_ac  # a gate file proves nothing


def test_bytes_that_are_not_utf8_do_not_stop_the_check(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = repo / "frontend/src/Latin.test.ts"
    path.write_bytes('it("REQ-MON-002.AC2: caf\xe9", () => {});\n'.encode("latin-1"))
    assert any(name.startswith("frontend/src/Latin.test.ts") for name in trace.collect(repo).by_ac["REQ-MON-002.AC2"])
    monkeypatch.setenv("TRACE_GATES_PASSED", "")
    assert trace.main([str(repo), "--check"]) == 0  # empty means the default, 0: no gate passed yet
    monkeypatch.setenv("TRACE_GATES_PASSED", "1")
    assert trace.main([str(repo), "--check"]) == 1  # REQ-ING-016.AC2 has no proof


def test_a_new_project_with_no_requirement_passes_the_check(tmp_path: Path) -> None:
    (tmp_path / "docs" / "requirements").mkdir(parents=True)
    assert trace.main([str(tmp_path), "--check"]) == 0
    assert trace.main([str(tmp_path)]) == 2  # the matrix itself needs requirements
