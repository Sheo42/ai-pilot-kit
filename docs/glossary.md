# Glossary

Every term, acronym and standard used in the project, in plain words. Every
role adds a term the first time it uses it, in the same change. Sorted
alphabetically within each section.

## Domain

| Term | Meaning |
|---|---|

## Project process

| Term | Meaning |
|---|---|
| AC | Acceptance criterion: one testable Given / When / Then condition of a requirement |
| ADR | Architecture Decision Record: a short document recording one decision, its options and consequences |
| AI pilot kit | The template repository this project started from: the rules, roles, templates and checks of the method. `KIT_VERSION` says which version; general improvements go back to it (`docs/process.md`, "The kit") |
| Bug, bug priority | A to-do row with the category `Bug`; its priority comes from impact × likelihood: P1 blocks a user journey or breaks security, P2 has a workaround, P3 is cosmetic |
| CI queue | Full CI runs take turns on a single runner, in an order the coordinator writes in one issue (the owner can change it); a run that must wait cancels itself and is started again when its turn comes |
| Claim test | A check that compares what a document says with what the code does, so the two cannot drift apart |
| Coordinator, thread | The Claude session that talks with the owner in the project chat, and the separate sessions it starts, one per piece of work |
| Coordinator playbook | The kit's `docs/coordinator.md`: how the coordinator starts threads, chooses each pull request's reviews and the merge order, and talks with the owner, written so another project does not have to rebuild it from project memory |
| Differential test | A test that runs the old and the new version of something on the same input and compares the results (for example, database migrations run in two orders) |
| Draft pull request | A pull request marked as not ready: it cannot be merged, and CI runs only its fast checks until it is marked ready for review |
| Exploratory POC | A throwaway proof of concept built without requirements, to give the owner something to try; closed by turning the feedback into requirements |
| Independent challenge | A review of a big decision by a fresh session on another model, reading only the repository, with numbered findings the owner triages one by one |
| Judge file | A file that decides whether a change is good: CI, test and lint settings, agents, skills, the process, the tests themselves. A PR that changes one says so, and the PR reviewer reads the change for weakening |
| Local test scope | A session runs only the tests and end-to-end journeys its change touches; the full suite is CI's run. The tests cost no tokens; setting up the stack and reading its output do |
| Link diagram, Mermaid | A picture of the links between documents (use case to ACs and tests, requirement to requirement and ADR, to-do to to-do), written in Mermaid, a text format GitHub draws as a diagram; made by `scripts/ci/links.py` (`docs/traceability.md`, "Diagrams of the links") |
| Merge batch | Two or three low-risk pull requests merged together into one branch with the newest `main`, tested by one CI run, merged by the owner as one |
| Merge order | The order, listed for the owner, in which open pull requests merge one at a time; only the next one merges `main` into its branch, just before its turn |
| Merge summary | The PR reviewer's short, plain summary of a PR and its review verdicts, for the owner |
| MoSCoW | Priority scale: Must, Should, Could, Won't |
| Mutation test, mutant, survivor | A tool changes one line of the code on purpose (a mutant) and runs the tests; a mutant no test notices is a survivor, one no test runs is not reached. Each one in a critical module gets a verdict: Gap, Bug, Equivalent or Accepted (`docs/mutation/README.md`) |
| Mutation ledger | The file of one mutation run, `docs/mutation/YYYY-MM-DD-<scope>.md`: its counts, a verdict per survivor and unreached mutant, and a fresh session's check of a sample of them |
| Number range | A block of to-do, requirement, ADR or migration numbers the coordinator reserves for one thread when it starts, so parallel branches never write the same ID; unused numbers stay unused |
| Phase gate | The checks that end a roadmap phase; the next phase starts only when they pass |
| Range file | The file of the to-do list that holds one number range, `docs/todo/540-549.md`; created by the thread that got the range, so parallel pull requests never add rows at the same place |
| Ratchet | A CI check on a number (suppressions, coverage, a file's size) whose baseline may only improve |
| Repository variable, `CI_RUNS_ON` | A setting of the GitHub repository that workflows read; `CI_RUNS_ON` names the runner labels `docs.yml` runs on, hosted runners when unset (`docs/method/ci-runners.md`) |
| Round limit | How many CI runs of the same failing job, or review send-backs for the same finding, a session takes before it gets a fresh look and then asks the owner (`docs/process.md`, "Verification") |
| Self-hosted runner | A machine of the owner's that runs CI jobs for a repository, instead of GitHub's hosted runners; never used by a public repository (`docs/method/ci-runners.md`) |
| Stop the line | A red main branch or a stuck pull request is fixed before new work starts |
| Skill, verify skill | A packaged set of instructions a Claude session loads for one kind of task (`.claude/skills/<name>/SKILL.md`); the `verify` skill holds the checks run before each commit |
| Subagent (role) | A role defined in `.claude/agents/` that a session can call for a task, with its own instructions and tools |
| Sync issue | An issue one project opens on another project's repository (or the kit's) to ask for something, labelled `sync` and made from the "Sync request" template: where it comes from, what it wants, how to know it is done. The watch reports it even when the owner's own account opened it; the pull request that does the work closes it (`docs/coordinator.md`, section 10) |
| Traceability | The link from each requirement and AC to the tests that prove it, generated from the test tags, never edited by hand |
| Triage | The owner's call on each finding or question, by number: accept, defer (with a phase) or reject (with a reason) |
| Use case, UC | One person's whole task across features, step by step: actor, goal, starting state, main steps with what the person sees, other paths, the requirement ACs it crosses and its test. `UC-NN` in `docs/use-cases.md`; each one is a browser journey or an integration scenario tagged `uc: UC-NN` (`docs/process.md`, "Use cases") |
| Walking skeleton | The thinnest version of the whole system that runs end to end, built first so every later feature hangs on a working chain |
