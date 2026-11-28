"""Tests of the link diagrams (scripts/ci/links.py) and of the Related check of check_docs.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_docs
import links


def requirement(req_id: str, title: str, related: str = "—", adrs: str = "—", acs: int = 2) -> str:
    lines = "".join(f"- **AC{n}** (method: Test)\n  Given ...\n" for n in range(1, acs + 1))
    return (
        f"### {req_id}: {title}\n\n| Field | Value |\n|---|---|\n| Status | Approved |\n"
        f"| Related | {related} |\n| Related ADRs | {adrs} |\n\n**Acceptance criteria**\n\n{lines}\n"
    )


MONITORING = "# Monitoring\n\n" + requirement(
    "REQ-MON-001", "Show the fleet on a map", related="REQ-MON-002, REQ-ALM-001", adrs="ADR-0001"
) + requirement("REQ-MON-002", "List the vans", related="REQ-MON-001")
ALARMS = "# Alarms\n\n" + requirement("REQ-ALM-001", "Raise an alarm", acs=1)
USE_CASES = (
    "# Use cases\n\n## Index\n\n| ID | Title |\n|---|---|\n| UC-01 | Follow a van |\n\n## Use cases\n\n"
    "### UC-01: Follow a van\n\n**Requirements.** REQ-MON-001.AC1, REQ-MON-001.AC2, REQ-ALM-001\n\n"
    "**Test.** `e2e/follow.journey.ts`\n\n**Gaps.** REQ-MON-404 is in an open pull request.\n"
)
TODOS = (
    "# To-do TODO-010 to 019\n\n| ID | Item | Category | Priority | Owner | Blocked by | Status | Where |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| TODO-010 | Draw the map | Test | P2 | developer | — | Done 2026-11-20 | — |\n"
    "| TODO-011 | List the vans | Test | P2 | developer | TODO-010 | Not started | — |\n"
    "| TODO-012 | Alarm sound | Test | P3 | developer | — | Not started | — |\n"
    "| TODO-013 | Old map | Test | P3 | developer | — | Done 2026-11-18 | — |\n"
    "| TODO-014 | Map tiles, see #12 | Test | P3 | developer | TODO-013 | Done 2026-11-21 | — |\n"
)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write(tmp_path, "docs/requirements/monitoring.md", MONITORING)
    write(tmp_path, "docs/requirements/alarms.md", ALARMS)
    write(tmp_path, "docs/adr/0001-record-architecture-decisions.md", "# ADR-0001\n")
    write(tmp_path, "docs/use-cases.md", USE_CASES)
    write(tmp_path, "docs/todo/010-019.md", TODOS)
    write(tmp_path, "e2e/follow.journey.ts", '// uc: UC-01\nit("REQ-MON-001.AC1: shows the map", () => {});\n')
    write(tmp_path, "docs/verification/map.md", "| Criterion | REQ-MON-001.AC2 |\n| Result | Partial: no phone |\n")
    return tmp_path


def test_use_case_diagram_draws_acs_tests_and_coverage(repo: Path) -> None:
    out = links.render(repo, {"UC-01"})
    assert "## Requirements by module" not in out
    assert 'UC_01(["UC-01: Follow a van"])' in out
    assert 'REQ_MON_001_AC1["✔ REQ-MON-001.AC1"]' in out
    assert 'REQ_MON_001_AC2["◐ REQ-MON-001.AC2"]' in out  # a partial proof
    assert 'REQ_ALM_001["✘ REQ-ALM-001: Raise an alarm"]' in out  # a whole requirement, no test
    assert "UC_01 --> REQ_MON_001_AC1" in out
    assert "REQ_MON_001_AC1 -.-> test_e2e_follow_journey_ts" in out
    assert "UC_01 -.-> test_e2e_follow_journey_ts" in out  # the uc: tag
    assert out.count('test_e2e_follow_journey_ts["') == 1  # one box per test file
    assert "REQ-MON-404" not in out  # the Gaps are left out
    assert "class REQ_MON_001_AC1 covered" in out


def test_module_diagram_draws_related_once_and_adrs(repo: Path) -> None:
    out = links.render(repo, {"REQ-MON-002"})  # a requirement selects its module
    assert "### Module MON" in out and "### Module ALM" not in out
    assert out.count("REQ_MON_001 --- REQ_MON_002") + out.count("REQ_MON_002 --- REQ_MON_001") == 1
    assert "REQ_MON_001 --- REQ_ALM_001" in out  # another module's requirement is drawn too
    assert "REQ_MON_001 -.-> ADR_0001" in out
    assert 'REQ_MON_001["◐ REQ-MON-001: Show the fleet on a map"]' in out  # one AC covered, one partial


def test_todo_diagram_draws_blockers_only(repo: Path) -> None:
    out = links.render(repo, {"TODO"})
    assert "TODO_010 --> TODO_011" in out
    assert 'TODO_010["✔ TODO-010: Draw the map"]' in out
    assert 'TODO_011["✘ TODO-011: List the vans"]' in out
    assert "TODO_012" not in out  # blocks nothing, blocked by nothing
    assert "TODO_013" not in out and "TODO_014" not in out  # a done item's blockers are left out


def test_todo_diagram_says_when_no_open_item_waits(repo: Path) -> None:
    write(repo, "docs/todo/010-019.md", TODOS.replace("| Not started | — |\n", "| Done 2026-11-22 | — |\n"))
    out = links.render(repo, {"TODO"})
    assert "```mermaid" not in out and "No open item waits on another." in out


def test_only_with_an_ac_selects_its_module(repo: Path) -> None:
    out = links.render(repo, {"REQ-MON-002.AC1"})
    assert "### Module MON" in out and "### Module ALM" not in out


def test_only_naming_no_diagram_is_an_error(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(links.UnknownIds, match="REQ-MON-999, UC-3 names no diagram"):
        links.render(repo, {"UC-01", "UC-3", "REQ-MON-999"})
    assert links.main([str(repo), "--only", "MON,UC-3"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and "UC-3 names no diagram" in captured.err
    assert links.main([str(repo), "--only", "MON,TODO"]) == 0


def test_a_diagram_too_big_is_named_not_drawn(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    diagram = links.Diagram()
    diagram.edge(diagram.node("a", "A"), "-->", diagram.node("b", "B"))
    assert links.drawn(diagram)[0] == "```mermaid"
    monkeypatch.setattr(links, "MAX_EDGES", 0)
    assert links.drawn(diagram) == [
        "Too big to draw: " + f"{len(chr(10).join(diagram.render()[1:-1])):,}"
        + " characters and 1 links, past Mermaid's 50,000 and 0. Draw a part of it with `scripts/ci/links.py --only`."
    ]
    monkeypatch.setattr(links, "MAX_EDGES", 500)
    monkeypatch.setattr(links, "MAX_TEXT", 10)
    assert links.drawn(diagram)[0].startswith("Too big to draw:")
    out = links.render(repo, {"MON"})
    assert "### Module MON" in out and "```mermaid" not in out and "Too big to draw:" in out


def test_everything_without_only(repo: Path) -> None:
    out = links.render(repo, set())
    for heading in ("### UC-01: Follow a van", "### Module ALM", "### Module MON", "## To-do items"):
        assert heading in out
    assert out.count("```mermaid") == 4


def test_labels_are_safe_and_short() -> None:
    text = links.label('A "quoted" `title`\nthat goes on and on, far past the sixty characters of a box')
    assert text == "A 'quoted' 'title' that goes on and on, far past the sixty…"
    assert len(text) <= links.TITLE_LIMIT
    assert links.label("Fix #12 <b>now</b> & go") == "Fix #35;12 #lt;b#gt;now#lt;/b#gt; & go"
    assert links.label("x" * 59 + "<>") == "x" * 59 + "…"  # cut first, so no entity code is cut


def test_todo_labels_escape_pr_numbers(repo: Path) -> None:
    write(repo, "docs/todo/010-019.md", TODOS.replace("List the vans", "List the vans after #12"))
    assert 'TODO_011["✘ TODO-011: List the vans after #35;12"]' in links.render(repo, {"TODO"})


def test_empty_project_prints_only_the_legend(tmp_path: Path) -> None:
    out = links.render(tmp_path, set())
    assert "```mermaid" not in out and links.LEGEND in out


def test_related_check_passes_on_real_links(repo: Path) -> None:
    assert check_docs.check_related(repo) == []


def test_an_adr_to_come_is_accepted_and_not_drawn(repo: Path) -> None:
    write(repo, "docs/requirements/alarms.md", "# Alarms\n\n" + requirement(
        "REQ-ALM-001", "Raise an alarm", adrs="ADR-0001, ADR-0042 to come", acs=1
    ))
    assert check_docs.check_related(repo) == []
    out = links.render(repo, {"ALM"})
    assert "REQ_ALM_001 -.-> ADR_0001" in out and "ADR_0042" not in out


def test_related_check_reports_broken_links(repo: Path) -> None:
    write(repo, "docs/requirements/alarms.md", "# Alarms\n\n" + requirement(
        "REQ-ALM-001", "Raise an alarm", related="REQ-ALM-001, REQ-MON-999, REQ-MON-002.AC7", adrs="ADR-0042", acs=1
    ))
    where = "docs/requirements/alarms.md:3"
    assert check_docs.check_related(repo) == [
        f"{where}: REQ-ALM-001 names itself in Related",
        f"{where}: Related names REQ-MON-999, which docs/requirements/ does not define",
        f"{where}: Related names REQ-MON-002.AC7: REQ-MON-002 has no AC7",
        f"{where}: Related ADRs names ADR-0042, which has no file in docs/adr/",
    ]
