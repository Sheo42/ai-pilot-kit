"""Tests of the to-do range files: the view and the checks."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_docs
import todo_view

HEADER = (
    "| ID | Item | Category | Priority | Owner | Blocked by | Status | Where |\n|---|---|---|---|---|---|---|---|\n"
)


def write(root: Path, name: str, rows: str) -> None:
    folder = root / "docs" / "todo"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(f"# To-do\n\n{HEADER}{rows}", encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write(
        tmp_path,
        "540-549.md",
        "| TODO-540 | Ask the DPO | Question | P2 | Dana | — | Open | REQ-PRV-001 |\n"
        "| TODO-541 | Build the view | Process | P1 | developer | — | In progress | — |\n"
        "| TODO-542 | Old work | — | — | — | — | Done 2026-11-08 | — |\n",
    )
    write(
        tmp_path,
        "550-559.md",
        "| TODO-550 | Urgent question | Decision | P1 | Dana | — | Open | — |\n"
        "| TODO-551 | Later work | Test | P3 | tester | TODO-541 | Not started | — |\n",
    )
    (tmp_path / "docs" / "todo" / "README.md").write_text("# Rules\n", encoding="utf-8")
    return tmp_path


def test_view_splits_and_sorts(repo: Path) -> None:
    view = todo_view.render(todo_view.all_items(repo), "Dana")
    waiting, rest = view.split("## Team work")
    team, done = rest.split("## Done")
    assert waiting.index("TODO-550") < waiting.index("TODO-540")  # P1 before P2
    assert "TODO-541" in team and "TODO-551" in team and "TODO-540" not in team
    assert team.index("TODO-541") < team.index("TODO-551")
    assert "| TODO-542 | Old work | 2026-11-08 |" in done
    assert "2 waiting on Dana, 2 team work, 1 done; 0 open bugs: 0 P1, 0 P2, 0 P3" in view


def test_bugs_are_listed_once_first_and_by_priority(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(
        repo,
        "560-569.md",
        "| TODO-560 | Cosmetic | Bug | P3 | developer | — | Not started | — |\n"
        "| TODO-561 | Blocks a journey | Bug | P1 | developer | — | In progress | PR #1 |\n"
        "| TODO-562 | Fixed | Bug | P2 | developer | — | Done 2026-11-14 | — |\n"
        "| TODO-563 | Bug owned by Dana | Bug | P2 | Dana | — | Open | — |\n",
    )
    view = todo_view.render(todo_view.all_items(repo), "Dana")
    bugs, rest = view.split("## Waiting on Dana")
    assert "## Bugs" in bugs
    assert bugs.index("TODO-561") < bugs.index("TODO-563") < bugs.index("TODO-560")
    assert "TODO-562" not in bugs
    waiting, team = rest.split("## Done")[0].split("## Team work")
    assert "| TODO-563 |" in waiting  # a bug Dana owns is still waiting on Dana
    assert all(f"| {bug} |" not in team for bug in ("TODO-560", "TODO-561", "TODO-563"))
    assert "| TODO-562 | Fixed | 2026-11-14 |" in rest
    assert "3 open bugs: 1 P1, 1 P2, 1 P3" in view
    assert todo_view.main([str(repo), "--bugs"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# Bugs") and "## Waiting" not in out and "TODO-540" not in out
    assert "| TODO-561 | Blocks a journey | P1 | developer | In progress | PR #1 |" in out


def test_bug_count_shows_rows_without_a_priority() -> None:
    cells = dict.fromkeys(todo_view.COLUMNS, "—")
    bugs = [todo_view.Item(Path("x"), 1, {**cells, "Priority": p}) for p in ("P1", "—")]
    assert todo_view.bug_count(bugs) == "2 open bugs: 1 P1, 0 P2, 0 P3, 1 without a priority"


def test_view_open_only_and_owner(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert todo_view.main([str(repo), "--open", "--owner", "tester"]) == 0
    out = capsys.readouterr().out
    assert "## Waiting on tester" in out and "## Done" not in out
    assert todo_view.main([str(repo), "--owner"]) == 2


def test_readme_is_not_a_range_file(repo: Path) -> None:
    assert [path.name for path in todo_view.range_files(repo)] == ["540-549.md", "550-559.md"]


def test_four_digit_ranges_are_range_files_sorted_by_number(repo: Path) -> None:
    """A four-digit to-do (TODO-1005): its file and rows are read, after the three-digit ones."""
    write(repo, "1005-1009.md", "| TODO-1005 | Drafts | Process | P2 | developer | — | Not started | — |\n")
    assert [path.name for path in todo_view.range_files(repo)] == ["540-549.md", "550-559.md", "1005-1009.md"]
    assert check_docs.check_todo_files(repo) == []
    assert "TODO-1005" in [item.id for path in todo_view.range_files(repo) for item in todo_view.read_items(path)[0]]


def test_good_files_pass(repo: Path) -> None:
    assert check_docs.check_todo_files(repo) == []
    assert check_docs.check_todo_ids(repo) == []


def test_id_outside_range_and_order(repo: Path) -> None:
    write(
        repo,
        "560-569.md",
        "| TODO-565 | B | Test | P2 | tester | — | Not started | — |\n"
        "| TODO-561 | A | Test | P2 | tester | — | Not started | — |\n"
        "| TODO-570 | C | Test | P2 | tester | — | Not started | — |\n",
    )
    errors = check_docs.check_todo_files(repo)
    assert any("TODO-561 must come before TODO-565" in error for error in errors)
    assert any("TODO-570 is outside the range" in error for error in errors)


def test_open_item_needs_category_priority_and_cells(repo: Path) -> None:
    write(
        repo,
        "560-569.md",
        "| TODO-560 | A | Chore | P4 | tester | — | Not started | — |\n"
        "| TODO-561 | B | Test | P2 |  | — | Not started | — |\n"
        "| TODO-562 | C | — | — | — | — | Done yesterday | — |\n",
    )
    errors = check_docs.check_todo_files(repo)
    assert any("TODO-560: category" in error for error in errors)
    assert any("TODO-560: an open item needs a priority" in error for error in errors)
    assert any("TODO-561: empty Owner" in error for error in errors)
    assert any('TODO-562: status "Done yesterday" is not one of' in error for error in errors)


def test_wrong_columns(repo: Path) -> None:
    folder = repo / "docs" / "todo"
    (folder / "560-569.md").write_text(
        "| ID | Item | Closed |\n|---|---|---|\n| TODO-560 | A | 2026-11-08 |\n", encoding="utf-8"
    )
    errors = check_docs.check_todo_files(repo)
    assert any("columns must be" in error for error in errors)
    assert any("TODO-560 has 3 cells" in error for error in errors)


def test_rows_in_old_list_and_duplicates(repo: Path) -> None:
    (repo / "docs" / "TODO.md").write_text(
        f"# To-do\n\n{HEADER}| TODO-540 | Again | Test | P2 | t | — | Open | — |\n", encoding="utf-8"
    )
    assert any("not in docs/TODO.md" in error for error in check_docs.check_todo_files(repo))
    assert any("TODO-540 defined 2 times" in error for error in check_docs.check_todo_ids(repo))


def test_empty_range(repo: Path) -> None:
    write(repo, "569-560.md", "")
    assert any("is empty" in error for error in check_docs.check_todo_files(repo))


def test_no_todo_folder(tmp_path: Path) -> None:
    assert todo_view.range_files(tmp_path) == []
    assert check_docs.check_todo_files(tmp_path) == []


def test_status_and_date(repo: Path) -> None:
    write(
        repo,
        "560-569.md",
        "| TODO-560 | A | Test | P2 | tester | — | Answered | — |\n"
        "| TODO-561 | B | — | — | — | — | Done 2026-13-45 | — |\n",
    )
    errors = check_docs.check_todo_files(repo)
    assert any('TODO-560: status "Answered"' in error for error in errors)
    assert any('TODO-561: "2026-13-45" is not a date' in error for error in errors)


def test_misnamed_and_overlapping_files(repo: Path) -> None:
    write(repo, "55-59.md", "| TODO-410 | A | Test | P2 | tester | — | Not started | — |\n")
    write(repo, "545-554.md", "")
    errors = check_docs.check_todo_files(repo)
    assert any("docs/todo/55-59.md: a file of docs/todo/" in error for error in errors)
    assert any("545-554.md: range 545 to 554 overlaps docs/todo/540-549.md" in error for error in errors)


def test_fenced_rows_and_missing_header(repo: Path) -> None:
    folder = repo / "docs" / "todo"
    (folder / "560-569.md").write_text(
        "| TODO-560 | A | Test | P2 | tester | — | Not started | — |\n"
        f"{HEADER}```\n| TODO-561 | example | Test | P2 | tester | — | Not started | — |\n```\n",
        encoding="utf-8",
    )
    items, errors = todo_view.read_items(folder / "560-569.md")
    assert items == []
    assert any("TODO-560 comes before the table's header row" in error for error in errors)
