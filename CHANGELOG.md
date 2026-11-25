# Changelog

## Unreleased

1. The kit is public, under the MIT licence (`LICENSE`).
   `scripts/kit/init.py` removes the licence from a new project, whose
   owner chooses its own.
2. `docs.yml` runs on the runner labels of the repository variable
   `CI_RUNS_ON`, or on GitHub's hosted runners when it is unset; a project
   on a self-hosted runner sets the variable instead of editing the
   workflow. A new push to a pull request cancels its older run.
3. `docs/method/ci-runners.md`: hosted or self-hosted runners, never a
   self-hosted runner for a public repository, and how one machine serves
   several repositories.
4. Fix: `docs.yml` was rejected by GitHub since 0.1.0 (`hashFiles` is not
   allowed in a job's `if`), so a project's document checks never ran. The
   check moves to each step's `if`. A project that copied 0.1.0 does the
   same. The kit's CI now runs
   `actionlint` on the workflows.
5. `README.md`, "What you need, and what you do not": a new project needs
   only the copy made by "Use this template"; it does not clone the kit's
   repository and does not need the first project. `docs/method/bootstrap.md`
   and `KIT.md` say the same.

## 0.1.0 (2026-11-24)

First version in its own repository. Until then the kit lived inside its
first project.

1. Files at the paths a project uses (`CLAUDE.md`, `.claude/agents/`,
   `.claude/skills/verify/`), so "Use this template" gives a working
   repository; `scripts/kit/init.py` fills the placeholders.
2. The document checks, the to-do view and the traceability matrix ship
   with the kit (`scripts/ci/`), with their tests; the owner's name and the
   phases are settings, and a project with no requirement yet passes.
3. A document-checks workflow for GitHub's hosted runners.
4. The method documents (`docs/method/`): principles, roles, workflow,
   artefacts, bootstrap.
5. Process, "The kit": how a project keeps its copy and sends improvements
   back.
