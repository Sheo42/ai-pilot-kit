# Changelog

## Unreleased

1. `README.md`, "What you need, and what you do not": a new project needs
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
