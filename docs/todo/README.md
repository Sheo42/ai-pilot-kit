# To-do items

The one list of what is open, split into one file per reserved number range
so that parallel pull requests never add rows at the same place. Every role
updates it at the end of each task: add what the task opened in its range's
file, close what it resolved in place. {{OWNER}} reads the view to know what
is waiting on them.

## Reading the list

`python3 scripts/ci/todo_view.py` prints the view: "Bugs" (open items of the
category `Bug`, the bug list), "Waiting on {{OWNER}}" (open items owned
by {{OWNER}}, bugs too), "Team work" (the other open items, bugs left out), each sorted by
priority then number, and "Done"; `--bugs` prints the bug list alone. CI writes it to the run summary
of the document checks. Set `TODO_OWNER={{OWNER}}` in the CI job, or pass
`--owner {{OWNER}}`.

## The files

1. One file per reserved range, named after it: `000-009.md` holds TODO-000
   to TODO-009 and nothing else. The thread that got the range creates the
   file in its pull request.
2. Rows never move. Closing an item sets its Status to `Done YYYY-MM-DD`.
3. Rows are sorted by number. CI checks the file name, the range, the
   order, the columns and that open items have a category and a priority
   (`scripts/ci/check_docs.py`).
4. No shared "Updated" line: the PR description says which range it used.

## Columns

| Column | What goes in it |
|---|---|
| ID | `TODO-NNN`, three digits or more, never reused |
| Item | What is to be done or answered, in plain words |
| Category | Decision, Question (facts only {{OWNER}} knows), Review, Requirements, Architecture, Security, Test, Bug (`docs/process.md`, "Bugs"), Process |
| Priority | P1: blocks the next step. P2: needed in the current phase. P3: later |
| Owner | `{{OWNER}}` for a decision or question waiting on them; otherwise the roles |
| Blocked by | The items that must be done first, "—" when none |
| Status | Open, Not started, In progress, or `Done YYYY-MM-DD`; CI refuses any other value |
| Where | The document, requirement or ADR it belongs to, "—" when none |

A duplicate is closed as done with "Dropped: merged into TODO-NNN" in its
item, never deleted.

## Order of work

1. TODO-003 (walking skeleton) is the only P1 path.
