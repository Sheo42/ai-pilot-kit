# Roles

The team is one human product owner and seven AI roles, each a Claude Code
subagent defined in `.claude/agents/`. The project runs in one Claude
project: a coordinator talks with the owner and starts one thread per piece
of work (`docs/coordinator.md`); a thread uses the roles as subagents or
follows their checklists.

## The seven roles

| Role | Owns | Why it exists |
|---|---|---|
| Business analyst | Requirements: one need each, testable acceptance criteria, priority, phase | So nobody designs or codes an unclear need |
| Architect | ADRs, system and software views, interfaces, the split into to-do items, design review | So every costly decision is written, with its options, before code depends on it |
| Tester | Tests tagged with AC IDs, verification, defects, traceability, release report | So coverage is counted on acceptance criteria, not lines |
| Developer | Code and its tests, on a branch, through a PR | So code only starts from a ready to-do item |
| Security engineer | Threat models, security review of security-area PRs and ADRs | So the architect does not review their own security designs |
| PR reviewer | Correctness and completeness of every PR; the merge summary for the owner | So the owner can merge without reading every line |
| Chronicler | The record of how the project is built | So the method can be judged and reused |

Each role definition has the same shape: a "read first, every time" list,
numbered responsibilities, outputs, and boundaries (what the role must not
do). The boundaries matter most: the tester never changes product code, the
developer never weakens a test, nobody but the owner approves.

## Choices behind the set

1. One architect with two views (system, software) instead of two
   architects: a second role would split one design into two.
2. The security engineer is separate from the architect, to separate
   designing from attacking.
3. The PR reviewer exists from the first day; in the first project its first
   run found a merge conflict and contradictions left in the documents.
4. The chronicler records steps and lessons, not every decision or ID: it
   recorded too much at first.
5. The independent challenger is **not** a role: it is a fresh session on
   another model, on purpose, so it has no stake in the design and no
   shared context with the authors.

## What the first project found

In practice a thread plays most roles in sequence itself and calls a
subagent for a second opinion. The roles work best as **checklists and
boundaries**, less as separate actors handing work to each other. A
separate task format was dropped: a to-do item with "Covers" and "Blocked
by" is the task.
