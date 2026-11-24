"""Tests of the status check of check_docs.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_docs


def requirement(req: str, status: str) -> str:
    return f"### {req}: Do something\n\n| Field | Value |\n|---|---|\n| Status | {status} |\n| Version | 1 |\n\n"


def adr(status: str) -> str:
    return f"# ADR-0040: A decision\n\n| Field | Value |\n|---|---|\n| Status | {status} |\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "requirements").mkdir(parents=True)
    (tmp_path / "docs" / "adr").mkdir()
    (tmp_path / "docs" / "requirements" / "README.md").write_text("| Status | Draft |\n", encoding="utf-8")
    (tmp_path / "docs" / "requirements" / "alarms.md").write_text(
        requirement("REQ-ALM-001", "Approved") + requirement("REQ-ALM-002", "Verified"), encoding="utf-8"
    )
    (tmp_path / "docs" / "traceability.md").write_text(
        "| ID | Title | Type | Priority | Phase | Status | AC |\n|---|---|---|---|---|---|---|\n"
        "| REQ-ALM-001 | Do something | FUN | Must | 2 Lab | Approved | AC1 |\n"
        "| | | | | | | AC2 |\n"
        "| REQ-ALM-002 | Do something | FUN | Must | 2 Lab | Verified | AC1 |\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "adr" / "0040-a-decision.md").write_text(
        adr("Accepted; refined by ADR-0041"), encoding="utf-8"
    )
    (tmp_path / "docs" / "adr" / "README.md").write_text(
        "| ADR | Decision | Status |\n|---|---|---|\n| [0040](0040-a-decision.md) | A decision | Accepted, refined |\n",
        encoding="utf-8",
    )
    return tmp_path


def test_merged_statuses_pass(repo: Path) -> None:
    assert check_docs.check_statuses(repo) == []


@pytest.mark.parametrize("status", ["Draft", "Proposed", "Proposed (Accepted on merge)"])
def test_a_requirement_left_draft_or_proposed_fails(repo: Path, status: str) -> None:
    path = repo / "docs" / "requirements" / "alarms.md"
    path.write_text(path.read_text(encoding="utf-8").replace("| Approved |", f"| {status} |"), encoding="utf-8")
    trace = repo / "docs" / "traceability.md"
    trace.write_text(trace.read_text(encoding="utf-8").replace("| Approved |", f"| {status} |"), encoding="utf-8")
    errors = check_docs.check_statuses(repo)
    assert len(errors) == 1
    assert "alarms.md:5: REQ-ALM-001" in errors[0]


def test_a_status_kept_by_the_owner_passes(repo: Path) -> None:
    path = repo / "docs" / "requirements" / "alarms.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("| Approved |", "| Proposed (kept by Dana, PR #120) |"),
        encoding="utf-8",
    )
    trace = repo / "docs" / "traceability.md"
    trace.write_text(trace.read_text(encoding="utf-8").replace("| Approved |", "| Proposed |"), encoding="utf-8")
    assert check_docs.check_statuses(repo) == []


def test_the_matrix_must_follow_the_requirement(repo: Path) -> None:
    trace = repo / "docs" / "traceability.md"
    trace.write_text(trace.read_text(encoding="utf-8").replace("| Verified |", "| Approved |"), encoding="utf-8")
    assert check_docs.check_statuses(repo) == [
        'docs/traceability.md:5: REQ-ALM-002 status "Approved", the requirement says "Verified"'
    ]


def test_an_adr_left_proposed_fails(repo: Path) -> None:
    (repo / "docs" / "adr" / "0040-a-decision.md").write_text(adr("Proposed (Accepted on merge)"), encoding="utf-8")
    errors = check_docs.check_statuses(repo)
    assert len(errors) == 2
    assert errors[0].startswith("docs/adr/0040-a-decision.md:5:")
    assert errors[1] == 'docs/adr/README.md:3: ADR-0040 listed as "Accepted, refined", the ADR says "Proposed"'


def test_the_index_must_follow_the_adr(repo: Path) -> None:
    index = repo / "docs" / "adr" / "README.md"
    index.write_text(index.read_text(encoding="utf-8").replace("Accepted, refined", "Proposed"), encoding="utf-8")
    assert check_docs.check_statuses(repo) == [
        'docs/adr/README.md:3: ADR-0040 listed as "Proposed", the ADR says "Accepted"'
    ]


def test_draft_cannot_be_kept(repo: Path) -> None:
    path = repo / "docs" / "requirements" / "alarms.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("| Approved |", "| Draft (kept by Dana, PR #120) |"), encoding="utf-8"
    )
    trace = repo / "docs" / "traceability.md"
    trace.write_text(trace.read_text(encoding="utf-8").replace("| Approved |", "| Draft |"), encoding="utf-8")
    assert len(check_docs.check_statuses(repo)) == 1


def test_a_status_followed_by_punctuation_passes(repo: Path) -> None:
    (repo / "docs" / "adr" / "0040-a-decision.md").write_text(adr("Accepted: see PR #70"), encoding="utf-8")
    assert check_docs.check_statuses(repo) == []


def test_a_missing_status_row_fails(repo: Path) -> None:
    path = repo / "docs" / "requirements" / "alarms.md"
    path.write_text(path.read_text(encoding="utf-8").replace("| Status | Approved |\n", ""), encoding="utf-8")
    (repo / "docs" / "adr" / "0040-a-decision.md").write_text("# ADR-0040: A decision\n\nStatus: Proposed\n")
    errors = check_docs.check_statuses(repo)
    assert 'docs/requirements/alarms.md:1: REQ-ALM-001 has no "| Status | ... |" row' in errors
    assert 'docs/adr/0040-a-decision.md: no "| Status | ... |" row' in errors


def test_rows_without_a_document_and_documents_without_a_row_fail(repo: Path) -> None:
    trace = repo / "docs" / "traceability.md"
    typo = "| REQ-ALM-009 | Typo | FUN | Must | 2 Lab | Proposed | AC1 |\n"
    trace.write_text(trace.read_text(encoding="utf-8") + typo, encoding="utf-8")
    (repo / "docs" / "adr" / "0041-another.md").write_text(adr("Accepted"), encoding="utf-8")
    index = repo / "docs" / "adr" / "README.md"
    index.write_text(index.read_text(encoding="utf-8") + "| [0042](0042-gone.md) | Gone | Accepted |\n")
    assert check_docs.check_statuses(repo) == [
        "docs/traceability.md:6: REQ-ALM-009 is not in docs/requirements/",
        "docs/adr/README.md:4: ADR-0042 has no file in docs/adr/",
        "docs/adr/README.md: ADR-0041 has no row in the index",
    ]
