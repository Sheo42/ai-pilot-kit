#!/usr/bin/env python3
"""Turn a copy of the kit into a new project's repository.

Run it once, in the new repository made with "Use this template":

    python3 scripts/kit/init.py --project "Acme Fleet" --owner "Dana" \
        --product "A web service that ..." --security-areas "payments, sign-in"

It fills the placeholders ({{PROJECT}}, {{OWNER}}, {{PRODUCT}}, {{STACK}},
{{SECURITY_AREAS}}, {{DATE}}) in every text file, removes what only the kit
repository needs (KIT.md, CHANGELOG.md, the kit's LICENSE, the kit's own
workflow, test and to-do list in kit/, the kit note at the top of CLAUDE.md,
this folder), writes a short README.md, and keeps KIT_VERSION so the project
knows which kit version it started from. Then it lists what is left to do by
hand: every "<!-- choose: ... -->" marker.

Standard library only. It refuses to run twice: once CLAUDE.md has no kit
note, the repository is a project, not the kit.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

KIT_ONLY_DIRS = ["kit"]
KIT_ONLY = ["KIT.md", "CHANGELOG.md", "LICENSE", ".github/workflows/kit.yml", "scripts/ci/tests/test_kit_init.py"]
KIT_NOTE = re.compile(r"<!-- kit-note -->.*?<!-- /kit-note -->\n*", re.DOTALL)
CHOOSE = re.compile(r"<!-- choose: (.*?) -->")
# A kit placeholder, not a GitHub Actions expression such as ${{ vars.CI_RUNS_ON }}.
PLACEHOLDER = re.compile(r"(?<!\$)\{\{[A-Z_]+\}\}")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".yml", ".yaml", ".jsonc", ".json", ".txt", ""}


def text_files(root: Path) -> list[Path]:
    return [
        path for path in sorted(root.rglob("*"))
        if path.is_file()
        and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        and path.suffix in TEXT_SUFFIXES
        and path.relative_to(root).parts[:2] != ("scripts", "kit")
    ]


def parse(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill the kit's placeholders for a new project.")
    parser.add_argument("--project", required=True, help="project name, as written in titles")
    parser.add_argument("--owner", required=True, help="first name of the product owner")
    parser.add_argument("--product", required=True, help="one sentence: what the product is, for whom")
    parser.add_argument("--security-areas", required=True,
                        help="areas that need the security engineer, for example 'devices, sign-in, payments'")
    parser.add_argument("--stack", default="not chosen yet (the first ADRs choose it)",
                        help="main languages and frameworks, once chosen")
    parser.add_argument("--date", default=date.today().isoformat(), help="start date, YYYY-MM-DD (default today)")
    parser.add_argument("--root", default=".", help="repository root (default: current folder)")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        parser.error(f"--date must be YYYY-MM-DD, not {args.date!r}")
    for name in ("project", "owner", "product", "security_areas", "stack"):
        if not getattr(args, name).strip() or "{{" in getattr(args, name):
            parser.error(f"--{name.replace('_', '-')} must be a real value")
    return args


def main(argv: list[str]) -> int:
    args = parse(argv)
    root = Path(args.root).resolve()
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists() or "<!-- kit-note -->" not in claude_md.read_text(encoding="utf-8"):
        print("CLAUDE.md has no kit note: this repository is already a project. Nothing done.", file=sys.stderr)
        return 1
    values = {
        "{{PROJECT}}": args.project.strip(),
        "{{OWNER}}": args.owner.strip(),
        "{{PRODUCT}}": args.product.strip(),
        "{{STACK}}": args.stack.strip(),
        "{{SECURITY_AREAS}}": args.security_areas.strip(),
        "{{DATE}}": args.date,
    }
    for name in KIT_ONLY:
        (root / name).unlink(missing_ok=True)
    for name in KIT_ONLY_DIRS:
        shutil.rmtree(root / name, ignore_errors=True)
    for path in text_files(root):
        text = path.read_text(encoding="utf-8")
        new = KIT_NOTE.sub("", text)
        for placeholder, value in values.items():
            new = new.replace(placeholder, value)
        if new != text:
            path.write_text(new, encoding="utf-8")
    shutil.rmtree(root / "scripts" / "kit")
    version = (root / "KIT_VERSION").read_text(encoding="utf-8").strip() if (root / "KIT_VERSION").exists() else "?"
    (root / "README.md").write_text(
        f"# {values['{{PROJECT}}']}\n\n{values['{{PRODUCT}}']}\n\n"
        "How this project is run: [docs/process.md](docs/process.md); why: "
        "[docs/method/](docs/method/README.md). "
        f"Started from the AI pilot kit, version {version} (`KIT_VERSION`).\n",
        encoding="utf-8")

    left = []
    for path in text_files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            rel = path.relative_to(root)
            if PLACEHOLDER.search(line):
                left.append(f"{rel}:{number}: placeholder left: {line.strip()}")
            for match in CHOOSE.finditer(line):
                left.append(f"{rel}:{number}: choose {match.group(1)}")
    print(f"{values['{{PROJECT}}']} set up from kit version {version}.")
    if left:
        print("Left to do by hand (bootstrap step 3 of docs/method/bootstrap.md):")
        print("\n".join(f"  {item}" for item in left))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
