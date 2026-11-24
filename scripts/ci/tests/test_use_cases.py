"""Tests of the use-case check of check_docs.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_docs

REQUIREMENT = (
    "### REQ-ALM-001: Raise an alarm\n\n| Field | Value |\n|---|---|\n| Status | Approved |\n\n"
    "**Acceptance criteria**\n\n- **AC1** (method: Test)\n  Given a fault\n"
)
TODOS = (
    "# To-do TODO-956 to 960\n\n| ID | Item | Category | Priority | Owner | Blocked by | Status | Where |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| TODO-956 | Write the journey | Test | P2 | tester | — | Not started | — |\n"
    "| TODO-957 | Wrote the use cases | Process | P2 | tester | — | Done 2026-11-15 | — |\n"
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "requirements").mkdir(parents=True)
    (tmp_path / "docs" / "requirements" / "alarms.md").write_text(REQUIREMENT, encoding="utf-8")
    (tmp_path / "docs" / "todo").mkdir()
    (tmp_path / "docs" / "todo" / "956-960.md").write_text(TODOS, encoding="utf-8")
    (tmp_path / "frontend" / "e2e").mkdir(parents=True)
    return tmp_path


def use_cases(repo: Path, sections: str, index: tuple[str, ...] = ("UC-01",)) -> None:
    rows = "".join(f"| {uc} | A title |\n" for uc in index)
    text = f"# Use cases\n\n## Index\n\n| ID | Title |\n|---|---|\n{rows}\n## Use cases\n\n{sections}"
    (repo / "docs" / "use-cases.md").write_text(text, encoding="utf-8")


def journey(repo: Path, tag: str, before: int = 0) -> None:
    text = "// a line\n" * before + f"// uc: {tag}\nimport x from 'y';\n"
    (repo / "frontend" / "e2e" / "alarm.journey.ts").write_text(text, encoding="utf-8")


def line_of(repo: Path, text: str) -> int:
    lines = (repo / "docs" / "use-cases.md").read_text(encoding="utf-8").splitlines()
    return next(n for n, line in enumerate(lines, start=1) if text in line)


def test_no_file_is_fine(repo: Path) -> None:
    assert check_docs.check_use_cases(repo) == []


def test_tagged_use_case_with_real_acs_passes(repo: Path) -> None:
    use_cases(repo, "### UC-01: Acknowledge an alarm\n\n**Requirements.** REQ-ALM-001.AC1\n")
    journey(repo, "UC-01")
    assert check_docs.check_use_cases(repo) == []


def test_untested_use_case_needs_an_open_todo_in_its_test_paragraph(repo: Path) -> None:
    missing = ['docs/use-cases.md:11: UC-01 has no test tagged "uc: UC-01" and its Test paragraph names '
               "no open to-do item that will write one"]
    use_cases(repo, "### UC-01: Acknowledge an alarm\n\n**Test.** None yet.\n\n**Gaps.** TODO-956 is a gap.\n")
    assert check_docs.check_use_cases(repo) == missing
    use_cases(repo, "### UC-01: Acknowledge an alarm\n\n**Test.** None yet (TODO-957, done).\n")
    assert check_docs.check_use_cases(repo) == missing
    use_cases(repo, "### UC-01: Acknowledge an alarm\n\n**Test.** None yet\n(TODO-956).\n")
    assert check_docs.check_use_cases(repo) == []


def test_unknown_requirement_and_ac_are_refused_outside_the_gaps(repo: Path) -> None:
    use_cases(repo, "### UC-01: Alarm\n\n**Requirements.** REQ-ALM-001.AC7, REQ-ALM-404\n\n"
                    "**Test.** TODO-956\n\n**Gaps.** REQ-ALM-405 is still in an open PR.\n")
    number = line_of(repo, "REQ-ALM-404")
    assert check_docs.check_use_cases(repo) == [
        f"docs/use-cases.md:{number}: REQ-ALM-001 has no AC7",
        f"docs/use-cases.md:{number}: REQ-ALM-404 is not a requirement",
    ]


def test_tag_naming_an_unknown_use_case_is_refused(repo: Path) -> None:
    use_cases(repo, "### UC-01: Alarm\n\n**Test.** TODO-956\n")
    journey(repo, "UC-01, UC-02")
    assert check_docs.check_use_cases(repo) == [
        "frontend/e2e/alarm.journey.ts:1: tag names UC-02, which docs/use-cases.md does not define"
    ]


def test_tag_far_down_a_file_does_not_count(repo: Path) -> None:
    use_cases(repo, "### UC-01: Alarm\n\n**Test.** None yet.\n")
    journey(repo, "UC-01", before=check_docs.UC_TAG_LINES)
    assert len(check_docs.check_use_cases(repo)) == 1


def test_duplicate_and_malformed_headings_are_refused(repo: Path) -> None:
    use_cases(repo, "### UC-01: One\n\n**Test.** TODO-956\n\n### UC-01: Two\n\n**Test.** TODO-956\n\n"
                    "### UC-02 No colon\n")
    errors = check_docs.check_use_cases(repo)
    first, second, loose = (line_of(repo, t) for t in ("UC-01: One", "UC-01: Two", "UC-02 No colon"))
    assert errors == [
        f'docs/use-cases.md:{loose}: a use case heading is written "### UC-NN: Title"',
        f"UC-01 defined 2 times: docs/use-cases.md:{first}, docs/use-cases.md:{second}",
    ]


def test_index_and_sections_match(repo: Path) -> None:
    use_cases(repo, "### UC-01: One\n\n**Test.** TODO-956\n\n### UC-03: Three\n\n**Test.** TODO-956\n",
              index=("UC-01", "UC-02"))
    errors = check_docs.check_use_cases(repo)
    assert errors == [
        f"docs/use-cases.md:{line_of(repo, '| UC-02 |')}: UC-02 is in the index but has no section",
        f"docs/use-cases.md:{line_of(repo, 'UC-03: Three')}: UC-03 is missing from the index",
    ]
