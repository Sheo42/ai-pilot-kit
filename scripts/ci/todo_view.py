#!/usr/bin/env python3
"""Build the to-do view from the range files in docs/todo/.

Every thread writes its to-do items in its own file, named after its
reserved range (docs/todo/540-549.md), so parallel pull requests never
add rows at the same place. This script reads all the files and
prints the one list a reader wants, in Markdown:

1. Bugs: open items of the category Bug, whoever owns them (docs/process.md,
   "Bugs"). Not repeated under Team work.
2. Waiting on <owner>: open items whose Owner is the product owner, bugs too.
3. Team work: the other open items, bugs left out.
4. Done: closed items (Status "Done YYYY-MM-DD").

Open items are sorted by priority (P1 first), then by to-do number; Done by
to-do number. CI writes the view to the run summary (scripts/ci/check-docs.sh).

Usage: python3 scripts/ci/todo_view.py [repository root] [--open] [--bugs] [--owner NAME]
  --open        leave out the Done table
  --bugs        print the Bugs table only (the bug list); --open and --owner do not apply
  --owner NAME  who "Waiting on" means; default: TODO_OWNER, else the owner set
                by scripts/kit/init.py
Standard library only.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

COLUMNS = ["ID", "Item", "Category", "Priority", "Owner", "Blocked by", "Status", "Where"]
RANGE_FILE = re.compile(r"^(\d{3,})-(\d{3,})\.md$")  # numbers grow to four digits and more
TODO_ROW = re.compile(r"^\|\s*(TODO-\d{3,})\s*\|")
DONE = re.compile(r"^Done (\d{4}-\d{2}-\d{2})$")
OPEN_STATUSES = ("Open", "Not started", "In progress", "Kit ready")
FENCE = re.compile(r"^\s*(```|~~~)")
DEFAULT_OWNER = "{{OWNER}}"  # filled by scripts/kit/init.py
BUG = "Bug"


@dataclass(frozen=True)
class Item:
    path: Path
    line: int
    cells: dict[str, str]

    @property
    def id(self) -> str:
        return self.cells["ID"]

    @property
    def number(self) -> int:
        return int(self.id.removeprefix("TODO-"))

    @property
    def closed(self) -> str | None:
        match = DONE.match(self.cells["Status"])
        return match.group(1) if match else None


def range_files(root: Path) -> list[Path]:
    """The range files of docs/todo/, by first number (README.md is not one): 999-999.md before 1005-1009.md."""
    folder = root / "docs" / "todo"
    if not folder.is_dir():
        return []
    return sorted(
        (path for path in folder.glob("*.md") if RANGE_FILE.match(path.name)),
        key=lambda path: (int(path.name.split("-", 1)[0]), path.name),
    )


def misnamed_files(root: Path) -> list[Path]:
    """Files of docs/todo/ that are neither README.md nor a range file: CI reports them."""
    folder = root / "docs" / "todo"
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.iterdir() if path.name != "README.md" and not RANGE_FILE.match(path.name))


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_items(path: Path) -> tuple[list[Item], list[str]]:
    """Rows of one range file and the format errors found while reading it."""
    items: list[Item] = []
    errors: list[str] = []
    header: list[str] | None = None
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence or not line.startswith("|"):
            continue
        cells = split_row(line)
        if cells[0] == "ID":
            header = cells
            if header != COLUMNS:
                errors.append(f"{path}:{number}: columns must be {' | '.join(COLUMNS)}")
            continue
        if not TODO_ROW.match(line):
            continue
        if header is None:
            errors.append(f"{path}:{number}: {cells[0]} comes before the table's header row")
            continue
        if header != COLUMNS or len(cells) != len(COLUMNS):
            errors.append(f"{path}:{number}: {cells[0]} has {len(cells)} cells, expected {len(COLUMNS)}")
            continue
        items.append(Item(path, number, dict(zip(COLUMNS, cells, strict=True))))
    return items, errors


def all_items(root: Path) -> list[Item]:
    items: list[Item] = []
    for path in range_files(root):
        items.extend(read_items(path)[0])
    return items


def priority_key(item: Item) -> tuple[int, int]:
    match = re.fullmatch(r"P(\d)", item.cells["Priority"])
    return (int(match.group(1)) if match else 9, item.number)


def table(columns: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


def open_bugs(items: list[Item]) -> list[Item]:
    """Open items of the category Bug, P1 first, then by to-do number."""
    return sorted((item for item in items if item.closed is None and item.cells["Category"] == BUG), key=priority_key)


def bug_table(bugs: list[Item]) -> list[str]:
    columns = ["ID", "Item", "Priority", "Owner", "Status", "Where"]
    return table(columns, [[item.cells[c] for c in columns] for item in bugs])


def bug_count(bugs: list[Item]) -> str:
    counts = {level: sum(1 for item in bugs if item.cells["Priority"] == level) for level in ("P1", "P2", "P3")}
    other = len(bugs) - sum(counts.values())
    text = f"{len(bugs)} open bugs: " + ", ".join(f"{counts[level]} {level}" for level in counts)
    return text + (f", {other} without a priority" if other else "")


def render_bugs(items: list[Item]) -> str:
    bugs = open_bugs(items)
    lines = ["# Bugs", "", f"Built from `docs/todo/` by `scripts/ci/todo_view.py --bugs`: {bug_count(bugs)}.", ""]
    return "\n".join(lines + bug_table(bugs)) + "\n"


def render(items: list[Item], owner: str, include_done: bool = True) -> str:
    bugs = open_bugs(items)
    open_items = [item for item in items if item.closed is None]
    waiting = sorted((item for item in open_items if item.cells["Owner"] == owner), key=priority_key)
    team = sorted(
        (item for item in open_items if item.cells["Owner"] != owner and item.cells["Category"] != BUG),
        key=priority_key,
    )
    done = sorted((item for item in items if item.closed is not None), key=lambda item: item.number)
    lines = [
        "# To-do view",
        "",
        f"Built from `docs/todo/` by `scripts/ci/todo_view.py`: {len(waiting)} waiting on {owner}, "
        f"{len(team)} team work, {len(done)} done; {bug_count(bugs)}.",
        "",
        "## Bugs",
        "",
    ]
    lines += bug_table(bugs)
    lines += ["", f"## Waiting on {owner}", ""]
    lines += table(
        ["ID", "Item", "Category", "Priority", "Where"],
        [[item.cells[c] for c in ("ID", "Item", "Category", "Priority", "Where")] for item in waiting],
    )
    lines += ["", "## Team work", ""]
    team_columns = ["ID", "Item", "Category", "Priority", "Blocked by", "Owner", "Status"]
    lines += table(team_columns, [[item.cells[c] for c in team_columns] for item in team])
    if include_done:
        lines += ["", "## Done", ""]
        lines += table(["ID", "Item", "Closed"], [[item.id, item.cells["Item"], str(item.closed)] for item in done])
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    args = list(argv)
    include_done = "--open" not in args
    bugs_only = "--bugs" in args
    args = [arg for arg in args if arg not in ("--open", "--bugs")]
    owner = os.environ.get("TODO_OWNER", DEFAULT_OWNER)
    if "--owner" in args:
        index = args.index("--owner")
        if index + 1 >= len(args):
            print("--owner needs a name", file=sys.stderr)
            return 2
        owner = args[index + 1]
        del args[index : index + 2]
    root = Path(args[0]) if args else Path(".")
    items = all_items(root)
    sys.stdout.write(render_bugs(items) if bugs_only else render(items, owner, include_done))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
