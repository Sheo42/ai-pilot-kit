<!-- kit-note -->
> **This is the kit repository, not a project.** If you are a Claude
> session here, you are maintaining the kit: read `KIT.md` first, and do
> not fill the placeholders. `scripts/kit/init.py` removes this note when a
> new project is made from the kit.
<!-- /kit-note -->

# {{PROJECT}}

{{PRODUCT}} Project definition: `docs/project-definition.md`.

## How to work in this repository

The team process is in `docs/process.md`. Read it before starting any task.
The coordinator of the project also follows `docs/coordinator.md`.
Work is done through seven roles, defined in `.claude/agents/`:

| When the work is about | Delegate to |
|---|---|
| A new need, a change of scope, writing or changing a requirement | `business-analyst` |
| A design choice, an ADR, a design review | `architect` |
| Test cases, verifying a PR, coverage, defects, release check | `tester` |
| Implementing a to-do item or fixing a defect | `developer` |
| Attacking a design or PR touching {{SECURITY_AREAS}}; threat models | `security-engineer` |
| Reviewing any pull request before merge; writing the merge summary | `pr-reviewer` |
| Recording how the project is built, after a session or a process change | `chronicler` |

Rules that apply to every role:
1. {{OWNER}} is the product owner: only {{OWNER}} approves requirements,
   accepts ADRs, merges pull requests and deploys to production. Merging a
   PR approves the requirements and accepts the ADRs it contains.
2. Cost is counted in pull requests and minutes of {{OWNER}}'s review,
   never in hours or days of work.
3. Number every question and list item for {{OWNER}}, and give a suggested
   answer, so {{OWNER}} can answer by number ("1 yes, 2 as suggested").
4. Every piece of code traces to a requirement ID; every acceptance
   criterion traces to a test (`docs/traceability.md`).
5. Never skip, disable or weaken a test to get a green build.
6. Never commit on `main`; one branch and one PR per task.
7. Before each commit, run the `verify` skill where you are, never on the
   CI runner's machine, and only the tests and journeys your change
   touches: the full suite is CI's. At the round limit on the same failure, get a fresh
   look, then ask {{OWNER}} for the decision (`docs/process.md`,
   "Verification").
8. At the start of a task, close the to-do items of PRs merged since the
   previous task, and reserve a number range if the task adds requirements or
   to-do items (`docs/process.md`, "Parallel threads").
9. At the end of a task, update the to-do list in `docs/todo/` (new items in
   your range's file, closed ones set to Done in place); a PR closes its own items.
   Never add a "review PR #N" item.
10. A new term, acronym or standard goes into `docs/glossary.md` in the same
    change.
11. Write assumptions down, dated, in the document that makes them; never
    let an assumption pass as a fact.
12. Summarise and cite third-party documents; never copy them into the
    repository.
13. A change to the process, this file, an agent or a CI script that is not
    specific to this domain is also proposed to the kit (`docs/process.md`,
    "The kit").
14. End each work session by asking the `chronicler` for the journal entry.
