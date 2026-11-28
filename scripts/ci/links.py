#!/usr/bin/env python3
"""Draw the links between the project documents as Mermaid diagrams.

GitHub draws a Mermaid block in Markdown (a file, a pull request description,
a run summary) as a diagram, also in a phone's browser, so nothing needs
installing. The links come from the documents the checks already read:

1. Use case to requirement: the requirements and ACs a use case names in
   docs/use-cases.md (its Gaps left out), and the test files tagged
   `uc: UC-NN`. One diagram per use case: the use case, its ACs, their tests.
2. Requirement to requirement and to ADR: the "Related" and "Related ADRs"
   rows of docs/requirements/. One diagram per module; a related requirement
   of another module is drawn too.
3. To-do to to-do: the "Blocked by" column of docs/todo/. One diagram of
   the items that block or are blocked.

An AC, and a requirement through its ACs, is coloured by its coverage in the
traceability matrix (scripts/ci/trace.py), and the label carries the same
sign for who cannot see the colours: covered (green, ✔), partly covered or
some ACs only (orange, ◐), not covered (red, ✘).

One diagram for the whole project would be unreadable past about 50 boxes,
so there is one per use case and one per module. With --only, only the
diagrams named are printed: use cases (UC-03), modules (MON), requirements
(REQ-MON-002, its module's diagram) or TODO for the to-do diagram; the PR
reviewer pastes those of the PR into its merge summary.

CI writes all of them to the run summary (scripts/ci/check-docs.sh). The
checks of the links themselves are in scripts/ci/check_docs.py. Standard
library only.

Usage: python3 scripts/ci/links.py [repository root] [--only ID,ID...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from trace import Trace, collect  # scripts/ci/trace.py, not the standard library module

from check_docs import ADR_MENTION, REQ_MENTION, TODO_MENTION, read_use_cases, uc_tags
from todo_view import all_items

CLASSES = [
    "classDef covered fill:#c8e6c9,stroke:#2e7d32,color:#000",
    "classDef partial fill:#ffe0b2,stroke:#ef6c00,color:#000",
    "classDef missing fill:#ffcdd2,stroke:#c62828,color:#000",
    "classDef other fill:#eceff1,stroke:#546e7a,color:#000",
]
SIGN = {"covered": "✔", "partial": "◐", "missing": "✘"}
LEGEND = "Colours: ✔ green covered, ◐ orange partly covered, ✘ red not covered (`scripts/ci/links.py`)."
TITLE_LIMIT = 60


def node_id(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "_", name)


def label(text: str) -> str:
    """Text inside a Mermaid ["..."] label: no quote, no line break, not too long."""
    text = " ".join(text.replace('"', "'").replace("`", "'").split())
    return text if len(text) <= TITLE_LIMIT else text[: TITLE_LIMIT - 1].rstrip() + "…"


def ac_state(trace: Trace, ac: str) -> str:
    if trace.covered(ac):
        return "covered"
    return "partial" if trace.by_ac.get(ac) else "missing"


def req_state(trace: Trace, req_id: str) -> str:
    acs = [f"{req_id}.{ac}" for ac in trace.requirements[req_id].acs]
    states = {ac_state(trace, ac) for ac in acs}
    if not states:
        return "other"
    return states.pop() if len(states) == 1 else "partial"


class Diagram:
    """One `flowchart LR` block: nodes declared once, edges in the order given."""

    def __init__(self) -> None:
        self.nodes: dict[str, tuple[str, str, str]] = {}  # id -> (label, shape, class)
        self.edges: list[str] = []

    def node(self, name: str, text: str, state: str = "other", shape: str = "box") -> str:
        ident = node_id(name)
        if ident not in self.nodes:
            sign = SIGN.get(state)
            self.nodes[ident] = (f"{sign} {text}" if sign else text, shape, state)
        return ident

    def edge(self, a: str, arrow: str, b: str) -> None:
        line = f"  {a} {arrow} {b}"
        if line not in self.edges:
            self.edges.append(line)

    def render(self) -> list[str]:
        out = ["```mermaid", "flowchart LR"]
        for ident, (text, shape, _) in self.nodes.items():
            out.append(f'  {ident}(["{text}"])' if shape == "round" else f'  {ident}["{text}"]')
        out += self.edges
        for state in ("covered", "partial", "missing", "other"):
            members = [ident for ident, (_, _, s) in self.nodes.items() if s == state]
            if members:
                out.append(f"  class {','.join(members)} {state}")
        out += [f"  {line}" for line in CLASSES]
        return out + ["```"]


def requirement_node(diagram: Diagram, trace: Trace, req_id: str) -> str:
    req = trace.requirements[req_id]
    return diagram.node(req_id, label(f"{req_id}: {req.title}"), req_state(trace, req_id))


def use_case_diagrams(root: Path, trace: Trace) -> list[tuple[str, str, Diagram]]:
    path = root / "docs" / "use-cases.md"
    if not path.exists():
        return []
    found = read_use_cases(path)
    tests: dict[str, list[str]] = {}
    for uc, rel, _ in uc_tags(root):
        tests.setdefault(uc, []).append(rel)
    out = []
    for uc in sorted(found.headings):
        diagram = Diagram()
        start = diagram.node(uc, label(f"{uc}: {found.titles.get(uc, '')}"), shape="round")
        for link in found.links.get(uc, []):
            req_id, _, ac = link.partition(".")
            if req_id not in trace.requirements:
                continue  # check_docs.py reports it
            if not ac:
                diagram.edge(start, "-->", requirement_node(diagram, trace, req_id))
                continue
            if ac not in trace.requirements[req_id].acs:
                continue
            target = diagram.node(link, link, ac_state(trace, link))
            diagram.edge(start, "-->", target)
            for name in trace.by_ac.get(link, []):
                diagram.edge(target, "-.->", diagram.node(f"test {test_file(name)}", label(test_file(name))))
        for rel in tests.get(uc, []):
            diagram.edge(start, "-.->", diagram.node(f"test {rel}", label(rel)))
        out.append((uc, f"{uc}: {found.titles.get(uc, '')}", diagram))
    return out


def test_file(name: str) -> str:
    """The file of a test ID (`path::name`, `path "title"`), so one box stands for each file."""
    return re.split(r'::| "', name, maxsplit=1)[0]


def module_diagrams(trace: Trace) -> list[tuple[str, str, Diagram]]:
    modules: dict[str, list[str]] = {}
    for req_id in sorted(trace.requirements):
        modules.setdefault(req_id.split("-")[1], []).append(req_id)
    out = []
    for module, ids in sorted(modules.items()):
        diagram = Diagram()
        drawn: set[frozenset[str]] = set()
        for req_id in ids:
            here = requirement_node(diagram, trace, req_id)
            fields = trace.requirements[req_id].fields
            for other, _ in REQ_MENTION.findall(fields.get("Related", "")):
                pair = frozenset((req_id, other))
                if other in trace.requirements and other != req_id and pair not in drawn:
                    drawn.add(pair)
                    diagram.edge(here, "---", requirement_node(diagram, trace, other))
            for number in ADR_MENTION.findall(fields.get("Related ADRs", "")):
                diagram.edge(here, "-.->", diagram.node(f"ADR-{number}", f"ADR-{number}", shape="round"))
        out.append((module, f"Module {module}", diagram))
    return out


def todo_diagram(root: Path) -> Diagram | None:
    items = {item.id: item for item in all_items(root)}
    diagram = Diagram()
    for item in items.values():
        for blocker in TODO_MENTION.findall(item.cells.get("Blocked by", "")):
            if blocker == item.id:
                continue
            ends = []
            for todo in (blocker, item.id):
                known = items.get(todo)
                state = "other" if known is None else ("covered" if known.closed else "missing")
                text = label(f"{todo}: {known.cells['Item']}") if known else todo
                ends.append(diagram.node(todo, text, state))
            diagram.edge(ends[0], "-->", ends[1])
    return diagram if diagram.edges else None


def selected(name: str, only: set[str]) -> bool:
    return not only or name in only


def render(root: Path, only: set[str]) -> str:
    trace = collect(root)
    only = {item.split("-")[1] if re.fullmatch(r"REQ-[A-Z]+-\d{3}", item) else item for item in only}
    lines = ["# Links between documents", "", LEGEND, ""]
    sections = [("Use cases", use_case_diagrams(root, trace)), ("Requirements by module", module_diagrams(trace))]
    for heading, diagrams in sections:
        chosen = [(title, diagram) for name, title, diagram in diagrams if selected(name, only)]
        if not chosen:
            continue
        lines += [f"## {heading}", ""]
        for title, diagram in chosen:
            lines += [f"### {title}", "", *diagram.render(), ""]
    if selected("TODO", only) and (todos := todo_diagram(root)):
        lines += ["## To-do items: what blocks what", "", "Green (✔) done, red (✘) open.", "", *todos.render(), ""]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = list(argv)
    only: set[str] = set()
    if "--only" in args:
        index = args.index("--only")
        if index + 1 >= len(args):
            print("--only needs IDs: UC-03,MON,REQ-MON-002,TODO", file=sys.stderr)
            return 2
        only = {item.strip() for item in args[index + 1].split(",") if item.strip()}
        del args[index : index + 2]
    root = Path(args[0]) if args else Path(".")
    sys.stdout.write(render(root, only))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
