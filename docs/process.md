# Team process

How {{PROJECT}} is specified, designed, built, tested and documented. The
team is {{OWNER}} (product owner, final decision maker) plus seven AI roles
defined in `.claude/agents/`. Work runs in one Claude project: a
coordinator talks with {{OWNER}} and starts one thread per piece of work;
how it does that is in `docs/coordinator.md`.

## Who decides

Only {{OWNER}} approves a requirement, accepts an ADR, merges a pull request,
accepts a risk or deploys to production. Agents propose. Merging a PR
approves the requirements and accepts the ADRs it contains, unless
{{OWNER}} says otherwise in the PR.

Cost is counted in PRs and minutes of {{OWNER}}'s review, never in hours of
work. {{OWNER}} notes the minutes spent on each review (one number in the
merge comment), so the chronicler can report the real cost.

## The flow

```
Need ({{OWNER}})
  → business analyst: requirements with testable ACs
  → architect: ADR if needed; to-do items that cover the ACs
  → tester: test cases and failing tagged tests
  → developer: code on a branch, PR with the checklist below
  → reviews, by tier (below)
  → {{OWNER}}: triage findings by number, merge
  → chronicler: journal entry at the end of the session
```

Small changes (a typo, a dependency bump) skip the first three steps; CI
still runs.

**Exploratory POC.** Before the requirements of a new area, one throwaway
POC may be built without requirements or tracing, in `poc/`, to give
{{OWNER}} something to click. It ends when what {{OWNER}} says about it is
turned into requirements. POC code never becomes product code.

## Phases

The roadmap is cut into phases named after who uses the product at that
point (for example: simulator only, the owner's own lab, an internal
reviewer, a first customer). Each phase has a gate and a Must set of at most
<!-- choose: about 15 --> requirements. A new Must that does not fit pushes
another one out, by {{OWNER}}'s decision.

Phase 1 is a **walking skeleton**: the thinnest end-to-end version, with CI
green, built before most requirements are written.

Every gate needs: all Musts of the phase verified, no open P1 or P2
bug, the tester's `Go`, a global independent challenge, from the second gate after
the skeleton a mutation report with no untriaged survivor and no
untested mutant in the critical modules, the chronicler's phase entry, and
{{OWNER}}'s sign-off.

## Reviews, by tier

| Tier | Applies to | Reviews |
|---|---|---|
| 1 | Every code PR | Automated code review at medium effort in its own session, findings applied before asking {{OWNER}}, its full text kept in the PR as `docs/reviews/YYYY-MM-DD-<topic>-code-review.md` (every finding by number, with its answer) so a later challenger can compare against it; tester and PR reviewer |
| 2 | Contracts and hard-to-undo changes: interfaces, database schema, auth, access control, {{SECURITY_AREAS}} | Tier 1, plus the security engineer, plus an independent challenge |
| Docs | Requirements, ADRs, process | PR reviewer; architect when an ADR changes; independent challenge when listed below |

## Independent challenge

**When:** an ADR about security, access, data storage, hosting or an
external interface; a new requirements module or a batch of more than ten
requirements; a change to the roles or this process; a global pass before
each phase gate; whenever {{OWNER}} asks.

**How:**
1. A fresh session with no prior context, on a different model than the
   author when possible, reads only the repository and the PR, never the
   discussion behind it (brief in `docs/reviews/README.md`).
2. It writes `docs/reviews/YYYY-MM-DD-<topic>-challenge.md`: numbered
   findings, each with a severity (High, Medium, Low) and a suggested
   verdict (accept, defer, reject).
3. The author answers each finding by number.
4. {{OWNER}} triages by number ("all as suggested except 4"). Accepted
   findings become changes in the same PR, deferred ones a to-do item with a
   phase, rejected ones keep a one-line reason.
5. The PR under challenge stays in draft until the triage is applied, so it
   cannot be merged before its fixes.
6. Every review names the commit it reviewed; before the PR is marked
   ready, the PR reviewer checks that later commits are only the triaged
   fixes.

## Verification

From the Claude Code team's practice (Addy Osmani, "How the Claude Code
team thinks about verification", claude.dev blog, 2026-11-16).

1. **A `verify` skill** (`.claude/skills/verify/SKILL.md`): the checks a session runs before each commit,
   by kind of change (documents: document checks and lint; code: the tests
   of the parts touched; a page or the application's start: the real
   application booted and driven end to end, once before the PR leaves
   draft). It runs where the session is, never on the CI runner's machine;
   the full run is CI's, when the PR leaves draft. **Local test scope**:
   the session runs only the tests and end-to-end journeys its change
   touches, never the whole suite. The tests cost no tokens; setting up
   the stack and reading long output do. Screenshots for the UX
   walkthrough are still taken where the session is.
2. **The round limit**: count what is scarce, CI runs of the same failing
   job and review send-backs for the same finding. At three, a fresh look
   first (a new session with no context), then {{OWNER}} only for a
   decision, with numbered options.
3. **A flaky test is a defect of a test**: a `Test` to-do item with its
   evidence (a CI run, or two failures of the same test); never retried,
   skipped or slowed to pass, never deleted without {{OWNER}}.
4. **A change that changes its judge says so**: one list of judge files (CI,
   test and lint settings, agents, skills, this process); a PR that changes
   one lists them, and the PR reviewer reports any change that weakens a
   check. Tests count too: deleted test files, added skip markers.
5. **Property and differential tests** where an invariant, a round-trip or
   an old version to compare with exists (decoders, migrations);
   deterministic in CI. **Mutation tests** (does a test notice a wrong
   line?) after a big feature and at phase gates, off the CI runner: a
   baseline at the first gate after the skeleton, for information, then
   at every later gate every survivor and every mutant no test reaches in
   the critical modules triaged, the noise cut in the tool, the verdicts
   kept in a ledger and a sample of them checked by a fresh session: the
   tests are written by the AI too, so they are checked by something that
   does not trust them, and so is the triage. (The first project's
   baseline found 227 real gaps among 364 survivors in its critical
   modules, with every test green.)
6. **Misses become rules**: a bug that reached main names the review that
   missed it; a miss seen in two PRs becomes a rule {{OWNER}} accepts or not.

## Stop the line

A red main branch or a stuck pull request (CI red, or conflicting, for more
than a day) is fixed before new work starts: no new thread opens until it is
green, and the fix is a P1 to-do item.

## Merge order

With one CI runner, each merge of `main` into a pull request starts its full
run again. So pull requests merge one at a time, in an order the coordinator
lists for {{OWNER}} (first what others wait for, then small and low-risk,
then by age). Only the next one merges `main` into its branch, once, just
before its turn; the others do not rebase after each merge. A PR that turns
red or conflicts goes back to its thread, and the next one takes its turn.
Drafts run only the fast CI checks; the full run starts when the PR is
marked ready for review.

Two or three low-risk pull requests (reviewed, no protocol, schema, sign-in,
tenancy or CI change, never a dependency bot's) can share one full run: a
merge batch. A branch from the newest `main` merges each one's head, its
pull request (not a draft) gets the full run while the members stay drafts,
and the owner merges that one with a merge commit, which marks them all
merged. A check before the merge fails when `main` or a member moved since
the batch was built. Red: drop the member at fault, or merge them one by one.

With one runner, full CI runs take turns: a run that would run the heavy
jobs while another is going cancels itself and is started again when its
turn comes, in the order the coordinator writes in one issue, which the owner can
change from a phone. Otherwise the runner takes one job of each run in turn and every run
finishes late.

## Owner's rulings

When {{OWNER}} decides, the ruling is quoted word for word, with its date
and where it was said, in the to-do item, ADR or requirement it decides; a
paraphrase may follow it, never replace it.

## Pull request checklist

Every PR description has:
1. What it covers: requirement, AC, ADR and to-do IDs.
2. What was done, with links; tests added.
3. Assumptions made (dated) and open questions, numbered, each with a
   suggested answer.
4. The reviews run and their verdicts; the merge summary.
5. `docs/todo/`, `docs/glossary.md`, the test tags (`docs/traceability.md`) and the
   architecture views updated where needed.
6. Values a person may want to change (time limits, thresholds, retry
   counts, password rules, addresses) are settings with a default and a
   documented name, not constants in code; what must not change says so.
   One settings index lists where each part's settings are. A number in a
   requirement says whether it is a setting's default, a target or a
   contract value (requirements README, "Numbers in requirements").
   No silent fallback: an invalid value, or a missing value with no safe
   default (a secret, an address), stops the service at start-up with an
   error naming the setting.
7. Every suppressed finding of a static analysis tool (a `noqa`, a
   `type: ignore`, an entry in an ignore file) carries its reason on the
   same line or entry.
8. A PR that changes what a user sees has a UX walkthrough (below).

## Use cases

A requirement tests one feature; a use case is one person's whole task
across features: actor, goal, starting state, main steps (what the person
does and what they see), other paths (error, refusal), the requirement ACs
it crosses and its test. Kept in `docs/use-cases.md` (`UC-NN`) by the
business analyst, linked to requirements, never repeating them. Each use
case is tested by browser journeys or integration scenarios whose files carry
`uc: UC-NN`; the list of use cases is the list of key journeys. A PR that
changes a journey updates its use case. A step no requirement covers is a
gap: a to-do item until a requirement covers it.

## UX walkthrough

Reviews and unit tests check the code, not what a person sees after each
action. Before a PR that changes a page asks for {{OWNER}}'s review, the
tester drives the changed pages in a real browser at the PR's commit, does
each main action (normal path, one error, a role that may not do it), looks
at them on a phone and in dark mode, and checks the tester role's UX
checklist. The PR description gets a numbered table: action, what the user
sees, result, screenshot (screenshots kept outside the repository). A failed
check is a defect. Each main action also gets a test asserting what the user
sees after it, in browser end-to-end tests of the key journeys once they
exist. {{OWNER}}'s own feedback sessions stay the last check.

## Parallel threads

1. Every number a thread may write is reserved before it writes it: to-do
   items (a block of 10 starting on a ten, for example TODO-300 to 309),
   requirements per module, ADR numbers, migration numbers and use case numbers. Branches
   see only what is merged, so "the next free number" is the same for two
   threads.
   1. The coordinator gives the range when it starts the thread, picked
      above the highest number on `main`, in open PRs and in ranges
      already reserved. It keeps the list of reservations and the next
      free number in its own notes (project memory), not in a file of the
      repository, which changes only at merge.
   2. A thread that needs more asks for a second range; it never takes the
      numbers just above its own.
   3. Unused numbers stay unused: no placeholder rows; CI checks for
      duplicates, not gaps.
   4. The PR writes its to-do items in a file named after its range,
      `docs/todo/300-309.md`, and lists the numbers it used in its
      description. No document carries an "Updated" line or a history
      of its changes: git keeps them, and a line every PR edits makes
      every pair of PRs conflict.
   5. A migration that merges after a higher-numbered one is checked for
      dependencies on it, and renamed to a new number if there are any; a
      merged migration is never renamed or edited.
   6. Without a coordinator, take the next block above everything on
      `main` and in open PRs, and write it in the PR description first.
2. A thread whose work depends on another's says so in its PR ("Blocked
   by") and rebases when the other merges.
3. At the start of each task, the thread closes, in place, the to-do items
   of PRs merged since the previous task.

## The to-do list

The to-do list is the single open list, kept in `docs/todo/` as one file per
reserved range so parallel PRs never add rows at the same place (rules in
`docs/todo/README.md`). Its view (`scripts/ci/todo_view.py`, also in the CI
run summary) shows "Waiting on {{OWNER}}" for decisions and questions only
{{OWNER}} can answer, "Team work" for the rest, "Done" for closed items. Rows
never move: closing sets the status to `Done YYYY-MM-DD` in place. Each item has a category, a priority (P1 blocks the next
step, P2 current phase, P3 later); team work also has an owner and
"Blocked by". IDs are never reused; duplicates are closed as "Dropped:
merged into TODO-NNN". A PR closes its own items; no "review PR #N" item.
A to-do item that covers ACs is the task: there is no separate task format.

## Bugs

A bug is a to-do row with the category `Bug` and a priority from impact ×
likelihood: P1 when it blocks a user journey, loses or leaks data, or breaks
security, in normal use (any use for security); P2 when the journey works
with a workaround or wrong information, or a P1 impact in a rare case; P3
for cosmetic bugs and other rare cases. The tester reports defects with
this priority. Before merge, the PR reviewer lists in the merge summary the
open bugs the PR touches, those it closes and those it adds; a PR does not
merge leaving a new P1 open. A bug found by a PR's tests in code already on
`main` is fixed in that PR, or the tests merge first and the fix is the
next task, never left waiting in the unmerged PR. The open `Bug` rows are
the bug list: the to-do view prints them first, under "Bugs" (`--bugs`
prints them alone), and no other file repeats them.

## Lessons

Every lesson or proposal the chronicler writes becomes a to-do item in the
same change. At each phase gate, the chronicler lists those not applied, and
{{OWNER}} keeps, changes or drops them. A rule nobody follows is removed or
made checkable by CI.

## The kit

This process comes from the AI pilot kit, version in `KIT_VERSION`. The
project keeps its own copy and adapts it freely. A change to this file,
`docs/coordinator.md`, `CLAUDE.md`, an agent or a CI script that is not
specific to this domain is also proposed to the kit, by a pull request on
the kit repository or, when that cannot be done in the same task, a
`Process` to-do item. When the kit gains a rule this project wants, a pull
request takes it and updates `KIT_VERSION` only if it takes the whole
release.

## Branches and commits

One branch and one PR per task; never a commit on `main`. Branch names come
from the tool that opens them. The PR title carries the IDs it covers;
commit messages say what changed and reference IDs.

## Where things live

```
CLAUDE.md                     rules for every session, role table
KIT_VERSION                   the kit version this project started from
.claude/agents/               the seven roles
docs/process.md               this file
docs/coordinator.md           coordinator playbook: threads, reviews, merge order, talking with the owner
docs/project-definition.md    scope, roadmap, open questions
docs/todo/                    the to-do list, one file per range
docs/glossary.md              every term, in plain words
docs/requirements/            one file per module, plain names; README = conventions
docs/use-cases.md             use cases UC-NN, one per key journey
docs/adr/                     decisions and their index
docs/architecture/            system and software views
docs/interfaces/              versioned interface specs
docs/traceability.md          how the requirements ↔ tests matrix is generated
docs/reviews/                 independent challenges, code reviews and answers
docs/security/                threat models
docs/verification/            manual verification records
docs/chronicle/               how the project is built
docs/templates/               requirement and ADR templates
scripts/ci/                   CI checks, runnable on any computer
```
