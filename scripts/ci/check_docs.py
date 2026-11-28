#!/usr/bin/env python3
"""Checks on the project documents, run in CI and locally.

1. Every requirement ID (REQ-XXX-NNN) is defined once, in docs/requirements/.
2. Every to-do ID (TODO-NNN) has one row only, across the range files of docs/todo/.
3. Every ADR number is used by one file only in docs/adr/.
4. Every glossary term is defined once in docs/glossary.md.
5. Every relative link in a Markdown file points to a file or folder that exists.
6. Each range file of docs/todo/ (named NNN-MMM.md) holds only IDs of its range,
   sorted by to-do number, with the columns of scripts/ci/todo_view.py; an open
   item has a category and a priority, a closed one the status "Done YYYY-MM-DD";
   docs/TODO.md holds no to-do rows (it points to the view).
7. No requirement or ADR is left "Draft" or "Proposed" after its merge: merging
   approves requirements and accepts ADRs (docs/requirements/README.md), so
   those two statuses are refused unless the product owner kept them in a PR,
   written "Proposed (kept by <owner>, PR #N)". The status in
   docs/traceability.md and in the index docs/adr/README.md is the one of the file.
8. Use cases (docs/use-cases.md, docs/process.md "Use cases"): each UC-NN is
   defined once under a "### UC-NN: Title" heading and listed in the index;
   every requirement and AC it names outside its Gaps exists; every `uc:` tag
   on a test file's first lines names a defined use case; a use case with no
   tagged test names, in its Test paragraph, the open to-do item that will
   write it.
9. Links between documents: every requirement a "Related" row names exists
   (and its AC, when one is named) and is not the requirement itself; every
   ADR a "Related ADRs" row names has its file in docs/adr/, unless it is
   written "ADR-NNNN to come" (its number reserved, the ADR not written
   yet). The diagrams of scripts/ci/links.py draw these links.

Usage: python3 scripts/ci/check_docs.py [repository root]
Exit code 0 when all checks pass, 1 otherwise. Standard library only.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from trace import files, read_requirements, text_of  # scripts/ci/trace.py, not the standard library module
from urllib.parse import unquote

from todo_view import OPEN_STATUSES, RANGE_FILE, TODO_ROW, misnamed_files, range_files, read_items

SKIP_DIRS = {".git", "node_modules", "dist", ".ruff_cache", ".pytest_cache", "__pycache__"}

REQ_HEADING = re.compile(r"^#{1,6}\s*(REQ-[A-Z]+-\d{3})\b")
ADR_FILE = re.compile(r"^(\d{4})-.+\.md$")
GLOSSARY_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|")
# [text](target) and ![alt](target); the target stops at a space or ")".
MD_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")


def markdown_files(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.rglob("*.md"))
        if not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    ]


def prose_lines(path: Path) -> Iterator[tuple[int, str]]:
    """Yield (line number, line) outside fenced code blocks, without inline code."""
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, INLINE_CODE.sub("", line)


def duplicates(found: dict[str, list[str]]) -> list[str]:
    return [f"{key} defined {len(places)} times: {', '.join(places)}" for key, places in sorted(found.items())
            if len(places) > 1]


def check_requirement_ids(root: Path) -> list[str]:
    found: dict[str, list[str]] = defaultdict(list)
    req_dir = root / "docs" / "requirements"
    for path in sorted(req_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        for number, line in prose_lines(path):
            match = REQ_HEADING.match(line)
            if match:
                found[match.group(1)].append(f"{path.relative_to(root)}:{number}")
    return duplicates(found)


def check_todo_ids(root: Path) -> list[str]:
    found: dict[str, list[str]] = defaultdict(list)
    for path in range_files(root):
        for item in read_items(path)[0]:
            found[item.id].append(f"{path.relative_to(root)}:{item.line}")
    legacy = root / "docs" / "TODO.md"
    if legacy.exists():
        for number, line in prose_lines(legacy):
            match = TODO_ROW.match(line)
            if match:
                found[match.group(1)].append(f"{legacy.relative_to(root)}:{number}")
    return duplicates(found)


CATEGORIES = {"Decision", "Question", "Review", "Requirements", "Architecture", "Security", "Test", "Bug", "Process"}


def check_todo_files(root: Path) -> list[str]:
    errors = []
    legacy = root / "docs" / "TODO.md"
    if legacy.exists():
        for number, line in prose_lines(legacy):
            if TODO_ROW.match(line):
                errors.append(f"docs/TODO.md:{number}: to-do rows go in the range files of docs/todo/, "
                              "not in docs/TODO.md")
    errors += [
        f"{path.relative_to(root)}: a file of docs/todo/ is README.md or a range file "
        "named NNN-MMM.md (for example 540-549.md)"
        for path in misnamed_files(root)
    ]
    ranges: list[tuple[int, int, Path]] = []
    for path in range_files(root):
        name = path.relative_to(root)
        match = RANGE_FILE.fullmatch(path.name)
        low, high = (int(match.group(1)), int(match.group(2))) if match else (0, -1)
        if low > high:
            errors.append(f"{name}: range {low} to {high} is empty")
        for other_low, other_high, other in ranges:
            if low <= other_high and other_low <= high:
                errors.append(f"{name}: range {low} to {high} overlaps {other.relative_to(root)}")
        ranges.append((low, high, path))
        items, format_errors = read_items(path)
        errors += [error.replace(str(path), str(name), 1) for error in format_errors]
        previous = None
        for item in items:
            where = f"{name}:{item.line}: {item.id}"
            if not low <= item.number <= high:
                errors.append(f"{where} is outside the range of this file ({low} to {high})")
            if previous and item.number <= previous.number:
                errors.append(f"{where} must come before {previous.id} (sort by to-do number)")
            previous = item
            status = item.cells["Status"]
            if item.closed is not None:
                try:
                    date.fromisoformat(item.closed)
                except ValueError:
                    errors.append(f"{where}: \"{item.closed}\" is not a date (YYYY-MM-DD)")
            elif status not in OPEN_STATUSES:
                errors.append(f"{where}: status \"{status}\" is not one of {', '.join(OPEN_STATUSES)} "
                              "or \"Done YYYY-MM-DD\"")
            if item.closed is None:
                if item.cells["Category"] not in CATEGORIES:
                    errors.append(f"{where}: category \"{item.cells['Category']}\" is not one of "
                                  f"{', '.join(sorted(CATEGORIES))}")
                if not re.fullmatch(r"P[123]", item.cells["Priority"]):
                    errors.append(f"{where}: an open item needs a priority P1, P2 or P3")
                for column in ("Item", "Owner", "Blocked by", "Status", "Where"):
                    if not item.cells[column]:
                        errors.append(f"{where}: empty {column} (write \"—\" when there is nothing)")
    return errors


def check_adr_numbers(root: Path) -> list[str]:
    found: dict[str, list[str]] = defaultdict(list)
    for path in sorted((root / "docs" / "adr").glob("*.md")):
        match = ADR_FILE.match(path.name)
        if match:
            found[f"ADR-{match.group(1)}"].append(str(path.relative_to(root)))
    return duplicates(found)


def check_glossary_terms(root: Path) -> list[str]:
    found: dict[str, list[str]] = defaultdict(list)
    path = root / "docs" / "glossary.md"
    for number, line in prose_lines(path):
        match = GLOSSARY_ROW.match(line)
        if not match:
            continue
        term = match.group(1)
        if term == "Term" or set(term) <= set("-: "):  # table header and separator rows
            continue
        found[term.lower()].append(f"{path.relative_to(root)}:{number}")
    return duplicates(found)


def check_relative_links(root: Path) -> list[str]:
    errors = []
    for path in markdown_files(root):
        for number, line in prose_lines(path):
            for target in MD_LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
                    continue  # external link (https:, mailto:...) or anchor in the same file
                file_part = unquote(target.split("#", 1)[0])
                if not file_part:
                    continue
                base = root if file_part.startswith("/") else path.parent
                if not (base / file_part.lstrip("/")).exists():
                    errors.append(f"{path.relative_to(root)}:{number}: broken link to {target}")
    return errors


REQ_STATUSES = {"Approved", "Implemented", "Verified", "Rejected", "Deprecated"}
ADR_STATUSES = {"Accepted", "Rejected", "Deprecated", "Superseded"}
KEPT_BY_OWNER = re.compile(r"^Proposed \(kept by [^,()]+, PR #\d+\)")
STATUS_ROW = re.compile(r"^\|\s*Status\s*\|\s*([^|]*?)\s*\|\s*$")
TRACE_ROW = re.compile(r"^\|\s*(REQ-[A-Z]+-\d{3})\s*\|")
ADR_INDEX_ROW = re.compile(r"^\|\s*\[(\d{4})\]\(")


def first_word(status: str) -> str:
    return re.split(r"[\s,;:.(]", status, maxsplit=1)[0]


def status_error(where: str, status: str, allowed: set[str]) -> str | None:
    if first_word(status) in allowed or KEPT_BY_OWNER.match(status):
        return None
    return (f"{where}: status \"{status}\" is not one of {', '.join(sorted(allowed))}; a merged PR approved it, "
            "unless the owner kept it: \"Proposed (kept by <owner>, PR #N)\"")


def requirement_statuses(root: Path) -> dict[str, tuple[str, str]]:
    """Map each requirement ID to (its status, where the status line is); no status row gives ("", heading)."""
    found: dict[str, tuple[str, str]] = {}
    for path in sorted((root / "docs" / "requirements").glob("*.md")):
        if path.name == "README.md":
            continue
        current = None
        for number, line in prose_lines(path):
            heading = REQ_HEADING.match(line)
            if heading:
                current = heading.group(1)
                found.setdefault(current, ("", f"{path.relative_to(root)}:{number}"))
                continue
            row = STATUS_ROW.match(line)
            if row and current and not found[current][0]:
                found[current] = (row.group(1), f"{path.relative_to(root)}:{number}")
    return found


def check_statuses(root: Path) -> list[str]:
    errors = []
    requirements = requirement_statuses(root)
    for req, (status, where) in sorted(requirements.items()):
        if not status:
            errors.append(f"{where}: {req} has no \"| Status | ... |\" row")
            continue
        error = status_error(f"{where}: {req}", status, REQ_STATUSES)
        if error:
            errors.append(error)
    trace = root / "docs" / "traceability.md"
    if trace.exists():
        for number, line in prose_lines(trace):
            match = TRACE_ROW.match(line)
            if not match:
                continue
            if match.group(1) not in requirements:
                errors.append(f"docs/traceability.md:{number}: {match.group(1)} is not in docs/requirements/")
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            expected = first_word(requirements[match.group(1)][0])
            if len(cells) > 5 and first_word(cells[5]) != expected:
                errors.append(f"docs/traceability.md:{number}: {match.group(1)} status \"{cells[5]}\", "
                              f"the requirement says \"{expected}\"")
    adr_dir = root / "docs" / "adr"
    adr_status: dict[str, str] = {}
    for path in sorted(adr_dir.glob("*.md")):
        match = ADR_FILE.match(path.name)
        if not match:
            continue
        adr_status[match.group(1)] = ""
        for number, line in prose_lines(path):
            row = STATUS_ROW.match(line)
            if row:
                adr_status[match.group(1)] = row.group(1)
                error = status_error(f"{path.relative_to(root)}:{number}", row.group(1), ADR_STATUSES)
                if error:
                    errors.append(error)
                break
        if not adr_status[match.group(1)]:
            errors.append(f"{path.relative_to(root)}: no \"| Status | ... |\" row")
    index = adr_dir / "README.md"
    if index.exists():
        listed_adrs = set()
        for number, line in prose_lines(index):
            match = ADR_INDEX_ROW.match(line)
            if not match:
                continue
            listed_adrs.add(match.group(1))
            if match.group(1) not in adr_status:
                errors.append(f"docs/adr/README.md:{number}: ADR-{match.group(1)} has no file in docs/adr/")
                continue
            listed = line.strip().strip("|").split("|")[-1].strip()
            expected = first_word(adr_status[match.group(1)])
            if first_word(listed) != expected:
                errors.append(f"docs/adr/README.md:{number}: ADR-{match.group(1)} listed as \"{listed}\", "
                              f"the ADR says \"{expected}\"")
        unlisted = sorted(adr_status.keys() - listed_adrs)
        errors += [f"docs/adr/README.md: ADR-{adr} has no row in the index" for adr in unlisted]
    return errors


UC_HEADING = re.compile(r"^###\s*(UC-\d{2}):\s*(\S.*?)\s*$")
UC_LOOSE = re.compile(r"^#{1,6}\s*UC-\d")  # a heading meant as a use case, well formed or not
UC_INDEX_ROW = re.compile(r"^\|\s*(UC-\d{2})\s*\|")
UC_ID = re.compile(r"\bUC-\d{2}\b")
UC_TAG = re.compile(r"^\s*(?://|#)\s*uc:\s*(.*)$")
UC_TAG_LINES = 10  # the tag goes on a test file's first lines (docs/process.md, "Use cases")
LABEL = re.compile(r"^\*\*([A-Za-z ]+)\.\*\*")  # **Test.**, **Gaps.** ...
REQ_MENTION = re.compile(r"\b(REQ-[A-Z]+-\d{3})(?:\.(AC\d+))?\b")
TODO_MENTION = re.compile(r"\bTODO-\d{3,}\b")


@dataclass
class UseCases:
    headings: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    planned: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))  # UC -> TODOs in its Test paragraph
    index: dict[str, int] = field(default_factory=dict)  # UC -> line of its Index row
    mentions: list[tuple[int, str, str]] = field(default_factory=list)  # (line, REQ, AC) outside the Gaps
    titles: dict[str, str] = field(default_factory=dict)  # UC -> title
    links: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))  # UC -> REQ or REQ.AC, Gaps left out
    errors: list[str] = field(default_factory=list)


def read_use_cases(path: Path) -> UseCases:
    found = UseCases()
    current: str | None = None
    label = ""
    for number, line in prose_lines(path):
        where = f"docs/use-cases.md:{number}"
        heading = UC_HEADING.match(line)
        if heading:
            current, label = heading.group(1), ""
            found.headings[current].append(where)
            found.titles.setdefault(current, heading.group(2))
            continue
        if UC_LOOSE.match(line):
            found.errors.append(f"{where}: a use case heading is written \"### UC-NN: Title\"")
        if re.match(r"^#{1,6}\s", line):
            current, label = None, ""
        row = UC_INDEX_ROW.match(line)
        if row and current is None:
            found.index[row.group(1)] = number
        if labelled := LABEL.match(line):
            label = labelled.group(1)
        if current and label == "Test":
            found.planned[current].update(TODO_MENTION.findall(line))
        if label != "Gaps":  # a gap may name a requirement that is still in an open PR
            found.mentions += [(number, req, ac) for req, ac in REQ_MENTION.findall(line)]
            if current:
                for req, ac in REQ_MENTION.findall(line):
                    link = f"{req}.{ac}" if ac else req
                    if link not in found.links[current]:
                        found.links[current].append(link)
    return found


def uc_tags(root: Path) -> list[tuple[str, str, int]]:
    """The `uc:` tags on the first lines of the test files: (UC, file, line)."""
    tags: list[tuple[str, str, int]] = []
    for test in files(root, (".ts", ".tsx", ".py")):
        rel = test.relative_to(root)
        if rel.parts[:2] == ("scripts", "ci"):
            continue  # the checks and their own tests
        for number, line in enumerate(text_of(test).splitlines()[:UC_TAG_LINES], start=1):
            if tag := UC_TAG.match(line):
                tags += [(uc, rel.as_posix(), number) for uc in UC_ID.findall(tag.group(1))]
    return tags


def check_use_cases(root: Path) -> list[str]:
    path = root / "docs" / "use-cases.md"
    if not path.exists():
        return []
    found = read_use_cases(path)
    errors = found.errors + duplicates(found.headings)
    errors += [f"docs/use-cases.md:{n}: {uc} is in the index but has no section" for uc, n in found.index.items()
               if uc not in found.headings]
    errors += [f"{places[0]}: {uc} is missing from the index" for uc, places in found.headings.items()
               if uc not in found.index]
    requirements = read_requirements(root)
    for number, req, ac in found.mentions:
        if req not in requirements:
            errors.append(f"docs/use-cases.md:{number}: {req} is not a requirement")
        elif ac and ac not in requirements[req].acs:
            errors.append(f"docs/use-cases.md:{number}: {req} has no {ac}")
    tagged: set[str] = set()
    for uc, rel, number in uc_tags(root):
        tagged.add(uc)
        if uc not in found.headings:
            errors.append(f"{rel}:{number}: tag names {uc}, which docs/use-cases.md does not define")
    open_todos = {item.id for todo in range_files(root) for item in read_items(todo)[0]
                  if item.cells.get("Status") in OPEN_STATUSES}
    for uc, places in sorted(found.headings.items()):
        if uc in tagged:
            continue
        if not found.planned[uc] & open_todos:
            errors.append(f"{places[0]}: {uc} has no test tagged \"uc: {uc}\" and its Test paragraph names "
                          "no open to-do item that will write one")
    return errors


ADR_MENTION = re.compile(r"\bADR-(\d{4})\b(\s+to come\b)?")


def related_adrs(text: str) -> list[str]:
    """The ADR numbers a "Related ADRs" row names, without the ones "to come"."""
    return [number for number, to_come in ADR_MENTION.findall(text) if not to_come]


def check_related(root: Path) -> list[str]:
    requirements = read_requirements(root)
    adrs = {match.group(1) for path in (root / "docs" / "adr").glob("*.md") if (match := ADR_FILE.match(path.name))}
    errors = []
    for req in sorted(requirements.values(), key=lambda r: r.id):
        for other, ac in REQ_MENTION.findall(req.fields.get("Related", "")):
            if other == req.id:
                errors.append(f"{req.where}: {req.id} names itself in Related")
            elif other not in requirements:
                errors.append(f"{req.where}: Related names {other}, which docs/requirements/ does not define")
            elif ac and ac not in requirements[other].acs:
                errors.append(f"{req.where}: Related names {other}.{ac}: {other} has no {ac}")
        for number in related_adrs(req.fields.get("Related ADRs", "")):
            if number not in adrs:
                errors.append(f"{req.where}: Related ADRs names ADR-{number}, which has no file in docs/adr/")
    return errors


CHECKS = [
    ("Requirement IDs are unique", check_requirement_ids),
    ("To-do IDs are unique", check_todo_ids),
    ("To-do range files: IDs in range, sorted, columns filled", check_todo_files),
    ("ADR numbers are unique", check_adr_numbers),
    ("Glossary terms are unique", check_glossary_terms),
    ("Relative links resolve", check_relative_links),
    ("Merged requirements and ADRs are not left Draft or Proposed", check_statuses),
    ("Use cases: unique, real requirements and ACs, every one tested or planned", check_use_cases),
    ("Related requirements and ADRs exist", check_related),
]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    failed = False
    for title, check in CHECKS:
        errors = check(root)
        print(f"{'FAIL' if errors else 'ok  '}  {title}")
        for error in errors:
            print(f"      {error}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
