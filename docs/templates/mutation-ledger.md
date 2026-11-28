<!-- Copy to docs/mutation/YYYY-MM-DD-<scope>.md for each mutation run. How to fill it: docs/mutation/README.md. -->

# Mutation ledger: <scope, e.g. gate 2, or the billing feature>

| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| Kind | Gate \| Baseline (first gate after the skeleton, for information) \| Feature |
| Phase | <phase number and name, from docs/process.md> |
| Commit | <full commit hash the tool ran on> |
| Scope | <the modules run, with their paths> |
| Tool | <tool and version> |
| Settings | <path of the tool's settings file, as of that commit> |
| Command | `<the exact command>` |
| Run by | <role: tester> |
| Sample seed | <a number, for the sample check> |
| Checked by | <fresh session, its model, date> |

## Counts

Critical modules first. A timed-out mutant counts as killed. Score = (killed + timed out) / (killed + timed out + survived + not reached).

| Module | Critical | Killed | Survived | Not reached | Timed out | Errors | Score |
|---|---|---|---|---|---|---|---|
| <module> | Yes | 0 | 0 | 0 | 0 | 0 | 0% |

Verdicts: Gap 0, Bug 0, Equivalent 0, Accepted 0, none missing.

## Verdicts

One row per survivor and per unreached mutant in the scope. Numbers are
forever in this file, like review findings.

| # | Module | Where | Change | Result | Verdict | Reason | Follow-up |
|---|---|---|---|---|---|---|---|
| 1 | <module> | `<path>:<line>` | `<` → `<=` | Survived | Gap | <what a test should notice> | <test name in this PR, or TODO-NNN> |
| 2 | <module> | `<path>:<line>` | condition → `true` | Not reached | Gap | <no test runs this line> | <test name, or TODO-NNN> |

Result: Survived or Not reached. Verdict: Gap, Bug, Equivalent or Accepted
(`docs/mutation/README.md`, "The run and the triage").

## Sample check

Filled by the fresh session. Rows drawn: every Accepted row, and 20 others
(or all of them) drawn with the sample seed.

| Row | Verdict given | Checker's verdict | Agrees | Note | {{OWNER}}'s call |
|---|---|---|---|---|---|
| 1 | Gap | Gap | Yes | | |

Disagreements: 0. Triage done again: no.
