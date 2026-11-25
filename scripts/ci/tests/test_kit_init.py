"""The kit's own test: a copy set up with scripts/kit/init.py is a clean project (KIT.md, "Checks")."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_docs import check_todo_files, check_todo_ids  # noqa: E402

KIT = Path(__file__).resolve().parents[3]
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")  # ${{ ... }} in the workflows is GitHub's, not ours
IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "node_modules")


def set_up(tmp_path: Path) -> tuple[Path, subprocess.CompletedProcess[str]]:
    repo = tmp_path / "project"
    shutil.copytree(KIT, repo, ignore=IGNORE)
    done = subprocess.run(
        [sys.executable, "scripts/kit/init.py", "--project", "Acme Fleet", "--owner", "Dana",
         "--product", "A web service that tracks delivery vans.", "--security-areas", "sign-in, payments",
         "--date", "2027-01-04"],
        cwd=repo, capture_output=True, text=True, check=False)
    return repo, done


def test_init_fills_every_placeholder_and_removes_the_kit_files(tmp_path: Path) -> None:
    repo, done = set_up(tmp_path)
    assert done.returncode == 0, done.stderr
    assert "Acme Fleet set up from kit version" in done.stdout
    assert "choose about 15" in done.stdout  # the markers left to decide by hand are listed
    for path in repo.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".sh", ".yml"}:
            assert not PLACEHOLDER.search(path.read_text(encoding="utf-8")), path
    for gone in ("KIT.md", "CHANGELOG.md", "LICENSE", "scripts/kit", ".github/workflows/kit.yml", "kit"):
        assert not (repo / gone).exists(), gone
    assert (repo / "KIT_VERSION").exists()
    assert (repo / "README.md").read_text(encoding="utf-8").startswith("# Acme Fleet\n\nA web service")
    claude = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert claude.startswith("# Acme Fleet") and "kit-note" not in claude
    assert "Done 2027-01-04" in (repo / "docs/todo/000-009.md").read_text(encoding="utf-8")


def test_the_new_project_passes_its_document_checks(tmp_path: Path) -> None:
    repo, done = set_up(tmp_path)
    assert done.returncode == 0, done.stderr
    checks = subprocess.run(["bash", "scripts/ci/check-docs.sh"], cwd=repo, capture_output=True, text=True,
                            check=False)
    assert checks.returncode == 0, checks.stdout + checks.stderr


def test_init_refuses_to_run_twice(tmp_path: Path) -> None:
    repo, done = set_up(tmp_path)
    assert done.returncode == 0
    shutil.copytree(KIT / "scripts" / "kit", repo / "scripts" / "kit")
    again = subprocess.run([sys.executable, "scripts/kit/init.py", "--project", "X", "--owner", "Y",
                            "--product", "Z", "--security-areas", "W"], cwd=repo, capture_output=True,
                           text=True, check=False)
    assert again.returncode == 1 and "already a project" in again.stderr


def test_the_kits_own_todo_list_passes_the_todo_checks() -> None:
    """kit/docs/todo/ follows the rules of a project's docs/todo/ (kit/docs/todo/README.md)."""
    assert check_todo_ids(KIT / "kit") == []
    assert check_todo_files(KIT / "kit") == []
