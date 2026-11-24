#!/usr/bin/env python3
"""Build the traceability matrix from the requirements and the test tags.

Nobody edits the matrix by hand any more: parallel pull requests all changed
the same rows and the same coverage counts of docs/traceability.md and
conflicted. This script builds it each time from three sources:

1. The requirements, in docs/requirements/*.md: each "### REQ-XXX-NNN" block,
   its Category, Priority, Phase and Status rows and its "- **ACn** (method:
   M)" lines.
2. The test tags:
   - Python: `@pytest.mark.req("REQ-XXX-NNN.ACn", ...)` on a test function or
     class, or a module's `pytestmark`; the test ID is `path::name`.
   - TypeScript (Vitest, Playwright): the AC IDs in the title of an `it(`,
     `test(` or `describe(` call, for example
     `it("REQ-MON-002.AC1: lists every site", ...)`; a `describe` title
     counts as one test for the whole block. A requirement ID without its
     AC in a title is a mention and counts for nothing.
   - A whole test file, when no single test can be named (a page test that
     checks the AC across several tests): a line `# req: ID, ID` (Python)
     or `// req: ID, ID` (TypeScript) in the file; the test ID is the path.
   - Check scripts (`scripts/ci/*.sh`, `scripts/ci/*_probe.py`): the AC IDs
     in a message the check prints (a quoted string on a shell line, for
     example `echo "ok    ... (REQ-PLT-008.AC3)"`; a string argument of a
     call in a probe, not a docstring), or in a `# req: ID, ID` comment for
     a check that prints no message, such as a CI scan.
3. The proofs that are not tests (inspection, CI scan, demonstration,
   analysis): one file per proof in docs/verification/, whose "Criterion"
   row names the ACs it proves. A file whose "Result" row starts with
   "Partial" or "Not run" marks those ACs as not fully covered, whatever
   tests they have, and the matrix shows why: that is how a test that proves
   only part of an AC is recorded.

It prints the matrix and the coverage summary in Markdown (CI writes them to
the run summary of the document checks, scripts/ci/check-docs.sh). With
--check it prints nothing on success and fails (exit 1) when:

- a tag or a proof names a requirement or an AC that does not exist, or
  names a requirement without its AC;
- an AC of an Approved, Implemented or Verified Must requirement of a phase whose gate has
  passed has neither a test nor a proof. The passed phases come from
  --gates-passed N (phases 1 to N), default the TRACE_GATES_PASSED setting
  (set in scripts/ci/check-docs.sh), else 0. A gate may also hold ACs of
  requirements of later phases: a file docs/verification/gate-N.md lists
  them in its "Gate criteria" row (the phase 1 gate held three);
- docs/traceability.md holds a row of the old hand-kept matrix again (a line
  starting "| REQ-"), as a pull request opened before the matrix was
  generated may bring back when it merges main.

A test counts once CI runs it: CI fails on any failing test, so a test named
here passes on main. Standard library only.

Usage: python3 scripts/ci/trace.py [repository root] [--check] [--gates-passed N]
"""

from __future__ import annotations

import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REQ_HEADING = re.compile(r"^#{1,6}\s*(REQ-[A-Z]+-\d{3}):\s*(.*?)\s*$")
ANY_HEADING = re.compile(r"^(#{1,6})\s")
FIELD_ROW = re.compile(r"^\|\s*(Category|Priority|Phase|Status|Related ADRs)\s*\|\s*([^|]*?)\s*\|\s*$")
AC_LINE = re.compile(r"^- \*\*(AC\d+)\*\*\s*\(method:\s*([A-Za-z]+)")
TAG_ID = re.compile(r"\bREQ-[A-Z]+-\d{3}(?:\.AC\d+)?\b")
AC_ID = re.compile(r"\bREQ-[A-Z]+-\d{3}\.AC\d+\b")  # in titles and messages, a bare REQ-XXX-NNN is a mention
TS_TITLE = re.compile(r"\b(?:it|test|describe)((?:\.\w+)*)\(\s*(['\"`])((?:\\.|(?!\2).)*)\2", re.S)
NOT_RUN = {"skip", "todo", "fixme"}  # it.skip, test.fixme...: a test that does not run proves nothing
QUOTED = re.compile(r"\"([^\"\n]*)\"|'([^'\n]*)'")
REQ_COMMENT = re.compile(r"#\s*req:\s*(.*)$")
FILE_COMMENT = re.compile(r"^\s*(?:#|//)\s*req:\s*(.*)$")
CRITERION_ROW = re.compile(r"^\|\s*Criterion\s*\|\s*([^|]*?)\s*\|\s*$")
GATE_ROW = re.compile(r"^\|\s*Gate criteria\s*\|\s*([^|]*?)\s*\|\s*$")
GATE_FILE = re.compile(r"^gate-(\d)\.md$")
RESULT_ROW = re.compile(r"^\|\s*Result\s*\|\s*([^|]*?)\s*\|\s*$")
NOT_FULL = ("Partial", "Not run")
FENCE = re.compile(r"^\s*(```|~~~)")
SKIP_DIRS = {".git", "node_modules", "poc", "dist", "build", ".venv", "venv", "__pycache__", "e2e-results"}
COUNTED = ("Approved", "Implemented", "Verified")  # Approved and later (docs/requirements/README.md)
DEFAULT_GATES_PASSED = 0  # no gate passed yet; scripts/ci/check-docs.sh sets TRACE_GATES_PASSED
LEGACY_ROW = re.compile(r"^\|\s*REQ-[A-Z]+-\d{3}\s*\|")
PHASES = ["1 Skeleton", "2 Lab", "3 Internal review", "4 First customer", "5 Operations", "6 Scale"]  # your phases


@dataclass
class Requirement:
    id: str
    title: str
    where: str
    fields: dict[str, str] = field(default_factory=dict)
    acs: dict[str, str] = field(default_factory=dict)  # AC -> method

    @property
    def status(self) -> str:
        words = self.fields.get("Status", "").split()
        return words[0] if words else ""

    @property
    def phase_number(self) -> int | None:
        match = re.match(r"(\d)\b", self.fields.get("Phase", ""))
        return int(match.group(1)) if match else None


@dataclass(frozen=True)
class Evidence:
    """One test or proof naming one AC."""

    ac: str  # REQ-XXX-NNN.ACn
    name: str  # test ID or proof file
    where: str  # file:line, for errors


def read_requirements(root: Path) -> dict[str, Requirement]:
    found: dict[str, Requirement] = {}
    for path in sorted((root / "docs" / "requirements").glob("*.md")):
        current: Requirement | None = None
        in_fence = False
        for number, line in enumerate(text_of(path).splitlines(), start=1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            heading = REQ_HEADING.match(line)
            if heading:
                current = Requirement(heading.group(1), heading.group(2), f"{path.relative_to(root)}:{number}")
                found[current.id] = current
                continue
            other = ANY_HEADING.match(line)
            if other and len(other.group(1)) <= 3:
                current = None  # a section after the requirements (notes, examples) belongs to none of them
            if current is None:
                continue
            row = FIELD_ROW.match(line)
            if row and row.group(1) not in current.fields:
                current.fields[row.group(1)] = row.group(2)
                continue
            ac = AC_LINE.match(line)
            if ac:
                current.acs[ac.group(1)] = ac.group(2)
    return found


def text_of(path: Path) -> str:
    """A file's text; bytes that are not UTF-8 become U+FFFD instead of stopping the whole check."""
    return path.read_text(encoding="utf-8", errors="replace")


def files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        out.extend(Path(dirpath) / name for name in sorted(filenames) if name.endswith(suffixes))
    return out


def req_args(node: ast.expr) -> list[tuple[str, int]] | None:
    """The string arguments of a `pytest.mark.req(...)` call, or None if it is not one."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == "req"):
        return None
    if not (isinstance(func.value, ast.Attribute) and func.value.attr == "mark"):
        return None
    return [
        (arg.value, arg.lineno) for arg in node.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    ]


def skipped(node: ast.expr) -> bool:
    """An unconditional `@pytest.mark.skip` (or `xfail`): the test proves nothing. `skipif` is left to CI."""
    target = node.func if isinstance(node, ast.Call) else node
    return isinstance(target, ast.Attribute) and target.attr in ("skip", "xfail")


def marks(nodes: list[ast.expr]) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for node in nodes:
        items = node.elts if isinstance(node, (ast.List, ast.Tuple)) else [node]
        for item in items:
            args = req_args(item)
            if args:
                out.extend(args)
    return out


def python_evidence(root: Path) -> tuple[list[Evidence], list[str]]:
    evidence: list[Evidence] = []
    errors: list[str] = []
    for path in files(root, (".py",)):
        if not (path.name.startswith("test_") or path.name.endswith("_test.py")):
            continue
        rel = path.relative_to(root).as_posix()
        evidence += file_tags(path, rel)
        try:
            tree = ast.parse(text_of(path), filename=rel)
        except SyntaxError as error:
            errors.append(f"{rel}: cannot be read ({error.msg})")
            continue
        module_marks: list[tuple[str, int]] = []
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets
            ):
                module_marks += marks([node.value])

        evidence += tests_in(tree.body, rel, "", module_marks)
    return evidence, errors


def tests_in(body: list[ast.stmt], rel: str, prefix: str, inherited: list[tuple[str, int]]) -> list[Evidence]:
    """The tags of the test functions in `body`, with those of their classes and module."""
    found: list[Evidence] = []
    for node in body:
        if isinstance(node, ast.ClassDef):
            found += tests_in(node.body, rel, f"{prefix}{node.name}::", inherited + marks(node.decorator_list))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            if any(skipped(d) for d in node.decorator_list):
                continue
            name = f"{rel}::{prefix}{node.name}"
            found += [Evidence(tag, name, f"{rel}:{line}") for tag, line in inherited + marks(node.decorator_list)]
    return found


def typescript_evidence(root: Path) -> list[Evidence]:
    evidence: list[Evidence] = []
    for path in files(root, (".ts", ".tsx")):
        name = path.name
        if not (".test." in name or ".spec." in name or ".journey." in name):
            continue
        rel = path.relative_to(root).as_posix()
        evidence += file_tags(path, rel)
        text = text_of(path)
        for match in TS_TITLE.finditer(text):
            if NOT_RUN & set(match.group(1).split(".")):
                continue
            title = match.group(3)
            line = text.count("\n", 0, match.start()) + 1
            for tag in AC_ID.findall(title):
                evidence.append(Evidence(tag, f'{rel} "{short(title)}"', f"{rel}:{line}"))
    return evidence


def file_tags(path: Path, rel: str) -> list[Evidence]:
    """The `# req:` or `// req:` lines of a test file: the whole file proves those ACs."""
    evidence: list[Evidence] = []
    for number, line in enumerate(text_of(path).splitlines(), start=1):
        comment = FILE_COMMENT.match(line)
        if comment:
            evidence += [Evidence(tag, rel, f"{rel}:{number}") for tag in TAG_ID.findall(comment.group(1))]
    return evidence


def short(text: str, limit: int = 80) -> str:
    """A title or message for the matrix cell: one line, no pipe, at most `limit` characters."""
    text = " ".join(text.replace("|", "/").replace("`", "'").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def script_evidence(root: Path) -> list[Evidence]:
    evidence: list[Evidence] = []
    folder = root / "scripts" / "ci"
    paths = sorted(folder.glob("*.sh")) + sorted(folder.glob("*_probe.py")) if folder.is_dir() else []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        for number, line in enumerate(text_of(path).splitlines(), start=1):
            comment = REQ_COMMENT.search(line)
            if comment:
                evidence += [Evidence(tag, rel, f"{rel}:{number}") for tag in TAG_ID.findall(comment.group(1))]
                continue
            if path.suffix == ".sh" and not line.lstrip().startswith("#"):
                for message in (a or b for a, b in QUOTED.findall(line)):
                    evidence += message_tags(rel, message, number)
        if path.suffix == ".py":
            evidence += probe_messages(path, rel)
    return evidence


def message_tags(rel: str, message: str, number: int) -> list[Evidence]:
    name = f'{rel} "{short(message.removeprefix("ok").strip())}"'
    return [Evidence(tag, name, f"{rel}:{number}") for tag in AC_ID.findall(message)]


def probe_messages(path: Path, rel: str) -> list[Evidence]:
    """The AC IDs in the string arguments of a probe's calls (`check("... (REQ-X.AC1)", ...)`), not its docstrings."""
    try:
        tree = ast.parse(text_of(path), filename=rel)
    except SyntaxError:
        return []
    found: list[Evidence] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found += message_tags(rel, arg.value, arg.lineno)
    return found


def proof_evidence(root: Path) -> tuple[list[Evidence], dict[str, str]]:
    """The proofs of docs/verification/, and the ACs they say are not fully covered (AC -> link and reason)."""
    evidence: list[Evidence] = []
    not_full: dict[str, str] = {}
    folder = root / "docs" / "verification"
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        rel = path.relative_to(root).as_posix()
        tags: list[Evidence] = []
        result = ""
        for number, line in enumerate(text_of(path).splitlines(), start=1):
            row = CRITERION_ROW.match(line)
            if row and not tags:
                tags = [Evidence(tag, rel, f"{rel}:{number}") for tag in TAG_ID.findall(row.group(1))]
            outcome = RESULT_ROW.match(line)
            if outcome and not result:
                result = outcome.group(1)
        evidence += tags
        if result.startswith(NOT_FULL):
            for item in tags:
                not_full[item.ac] = f"[{short(result, 120)}]({rel})"
    return evidence, not_full


@dataclass
class Trace:
    requirements: dict[str, Requirement]
    by_ac: dict[str, list[str]]  # AC -> tests and proofs
    not_full: dict[str, str]  # AC -> why it is not fully covered
    errors: list[str]

    def covered(self, ac: str) -> bool:
        return bool(self.by_ac.get(ac)) and ac not in self.not_full


def collect(root: Path) -> Trace:
    """Requirements, the tests and proofs of each AC, and the tag errors."""
    requirements = read_requirements(root)
    python, errors = python_evidence(root)
    proofs, not_full = proof_evidence(root)
    by_ac: dict[str, list[str]] = {}
    for item in python + typescript_evidence(root) + script_evidence(root) + proofs:
        req, _, ac = item.ac.partition(".")
        if req not in requirements:
            errors.append(f"{item.where}: {item.ac} is not in docs/requirements/")
        elif not ac:
            errors.append(f"{item.where}: {item.ac} names a requirement, not an AC: add .ACn")
        elif ac not in requirements[req].acs:
            errors.append(f"{item.where}: {item.ac}: {req} has no {ac}")
        elif item.name not in by_ac.setdefault(item.ac, []):
            by_ac[item.ac].append(item.name)
    return Trace(requirements, by_ac, {ac: why for ac, why in not_full.items() if ac in by_ac}, errors)


def gate_extras(root: Path, gates_passed: int) -> list[Evidence]:
    """The ACs that docs/verification/gate-N.md adds to a passed gate N."""
    extras: list[Evidence] = []
    folder = root / "docs" / "verification"
    for path in sorted(folder.glob("gate-*.md")) if folder.is_dir() else []:
        match = GATE_FILE.match(path.name)
        if not match or int(match.group(1)) > gates_passed:
            continue
        rel = path.relative_to(root).as_posix()
        for number, line in enumerate(text_of(path).splitlines(), start=1):
            row = GATE_ROW.match(line)
            if row:
                extras += [Evidence(tag, rel, f"{rel}:{number}") for tag in AC_ID.findall(row.group(1))]
    return extras


def gate_gaps(trace: Trace, gates_passed: int, extras: list[Evidence] | None = None) -> list[str]:
    gaps = []
    for item in extras or []:
        req_id, _, ac = item.ac.partition(".")
        if req_id not in trace.requirements or ac not in trace.requirements[req_id].acs:
            gaps.append(f"{item.where}: {item.ac} is not in docs/requirements/")
        elif not trace.covered(item.ac):
            gaps.append(f"{item.where}: {item.ac} (in this gate, passed) is not fully covered")
    for req in sorted(trace.requirements.values(), key=lambda r: r.id):
        phase = req.phase_number
        if req.status not in COUNTED or req.fields.get("Priority") != "Must" or phase is None or phase > gates_passed:
            continue
        gaps += [
            f"{req.where}: {req.id}.{ac} (phase {phase}, gate passed) is not fully covered"
            for ac in req.acs
            if not trace.covered(f"{req.id}.{ac}")
        ]
    return gaps


def legacy_rows(root: Path) -> list[str]:
    path = root / "docs" / "traceability.md"
    if not path.exists():
        return []
    return [
        f"docs/traceability.md:{number}: a hand-kept matrix row; the matrix is generated now: "
        "keep main's version of the file and tag the tests (docs/traceability.md, 'Tagging a test')"
        for number, line in enumerate(text_of(path).splitlines(), start=1)
        if LEGACY_ROW.match(line)
    ]


def table(columns: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    return lines + ["| " + " | ".join(row) + " |" for row in rows]


def percent(covered: int, total: int) -> str:
    return f"{round(100 * covered / total)}%" if total else "—"


def render(trace: Trace) -> str:
    requirements, by_ac = trace.requirements, trace.by_ac
    counted = [r for r in requirements.values() if r.status in COUNTED]

    def counts(reqs: list[Requirement]) -> tuple[int, int]:
        acs = [f"{r.id}.{ac}" for r in reqs for ac in r.acs]
        return sum(1 for ac in acs if trace.covered(ac)), len(acs)

    must = [r for r in counted if r.fields.get("Priority") == "Must"]
    lines = [
        "# Traceability matrix",
        "",
        "Built by `scripts/ci/trace.py` from `docs/requirements/`, the test tags and `docs/verification/` "
        "(`docs/traceability.md` says how to tag).",
        "",
        "## Coverage summary",
        "",
    ]
    rows = []
    for scope, reqs in (("Approved and later, Must", must), ("Approved and later, all", counted)):
        covered, total = counts(reqs)
        rows.append([scope, f"{covered} / {total}", percent(covered, total)])
    lines += table(["Scope", "ACs covered / total", "Coverage"], rows)
    lines += ["", "Must requirements per phase:", ""]
    rows = []
    for number, phase in enumerate(PHASES, start=1):
        reqs = [r for r in must if r.phase_number == number]
        covered, total = counts(reqs)
        rows.append([phase, str(len(reqs)), str(total), str(covered)])
    lines += table(["Phase", "Must requirements", "Must ACs", "Covered"], rows)
    lines += ["", "## Matrix", ""]
    rows = []
    for req in sorted(requirements.values(), key=lambda r: (r.id.split("-")[1], r.id)):
        first = True
        for ac, method in (req.acs or {"—": "—"}).items():
            names = by_ac.get(f"{req.id}.{ac}", [])
            cell = ", ".join(f"`{name}`" for name in names)
            result = trace.not_full.get(f"{req.id}.{ac}", "Covered" if names else "")
            head = (
                [
                    req.id,
                    req.title,
                    req.fields.get("Category", ""),
                    req.fields.get("Priority", ""),
                    req.fields.get("Phase", ""),
                    req.fields.get("Status", ""),
                ]
                if first
                else [""] * 6
            )
            tail = [req.fields.get("Related ADRs", "")] if first else [""]
            rows.append([*head, ac, method, cell, result, *tail])
            first = False
    columns = ["Requirement", "Title", "Cat.", "Prio.", "Phase", "Status", "AC", "Method"]
    lines += table([*columns, "Tests and proofs", "Result", "ADRs"], rows)
    return "\n".join(lines).replace("|  |", "| |") + "\n"


def main(argv: list[str]) -> int:
    args = list(argv)
    check = "--check" in args
    args = [arg for arg in args if arg != "--check"]
    gates = os.environ.get("TRACE_GATES_PASSED") or str(DEFAULT_GATES_PASSED)
    if "--gates-passed" in args:
        index = args.index("--gates-passed")
        if index + 1 >= len(args):
            print("--gates-passed needs a phase number", file=sys.stderr)
            return 2
        gates = args[index + 1]
        del args[index : index + 2]
    if not re.fullmatch(r"[0-6]", gates):
        print(f"TRACE_GATES_PASSED or --gates-passed must be a phase number 0 to 6, not {gates!r}", file=sys.stderr)
        return 2
    root = Path(args[0]) if args else Path(".")
    trace = collect(root)
    if not trace.requirements and not check:
        print(f"no requirement found in {root / 'docs' / 'requirements'}", file=sys.stderr)
        return 2
    # With --check, a new project with no requirement yet passes: any tag it has names a missing one and fails.
    if check:
        extras = gate_extras(root, int(gates))
        problems = trace.errors + gate_gaps(trace, int(gates), extras) + legacy_rows(root)
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1 if problems else 0
    sys.stdout.write(render(trace))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
