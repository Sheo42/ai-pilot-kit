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

6. Link diagrams: `scripts/ci/links.py` draws, in Mermaid, each use case
   with its ACs and tests, each module's requirements with their `Related`
   requirements and ADRs, and the to-do items that block others, coloured
   by test coverage. CI puts them in the run summary; the PR reviewer
   pastes a PR's own into its merge summary. `check_docs.py` now fails on a
   `Related` or `Related ADRs` row naming something that does not exist
   (`docs/traceability.md`, "Diagrams of the links").
7. Mutation tests: `docs/mutation/README.md` says when to run them, which
   modules are critical, how to set up the tool and cut its noise, the four
   verdicts (Gap, Bug, Equivalent, Accepted) and the fresh session's sample
   check; `docs/templates/mutation-ledger.md` is the file each run fills.
   `docs/process.md`, the tester agent, the artefacts table and the
   glossary point to them.
8. Issues between projects: a project asks another, or the kit, for
   something with a `sync` issue made from `.github/ISSUE_TEMPLATE/sync.md`
   (where it comes from, what it wants, how to know it is done). The watch
   reports `sync` issues even when the owner's own account opened them, and
   the receiving thread closes the issue once it has taken it into
   account, with a comment naming the pull request or to-do item that
   carries the work (`docs/coordinator.md`, section 10, items 4 to 6). A new project creates
   the `sync` label (`docs/method/bootstrap.md`).
9. The watch of the code host: a scheduled task a few times a day that
   reads the last check time from a state file, searches what changed
   (issues, pull request comments and reviews, `sync` issues), posts one
   numbered message, and never writes to the code host
   (`docs/coordinator.md`, section 10, item 1; set up in the first week,
   `docs/method/bootstrap.md`).
10. Link diagrams at a large project's size: the to-do diagram draws only
    the open items that wait on others and what they wait on; a diagram past
    Mermaid's limits (50,000 characters or 500 links) is named with its
    sizes instead of drawn, since GitHub would show an error box; an
    `--only` ID that names no diagram fails (exit code 1), and an AC
    selects its module; labels escape `#`, `<` and `>`; a `Related ADRs`
    row may name `ADR-NNNN to come` for a reserved number, which passes
    the check and is not drawn (`docs/traceability.md`, "Diagrams of the
    links").
11. Fix: in the link diagrams, two names that differ only by `-` and `_`
    (two test files, say) shared one box; each now has its own.

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
