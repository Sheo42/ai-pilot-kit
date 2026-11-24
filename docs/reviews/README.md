# Independent challenges

One file per challenge, `YYYY-MM-DD-<topic>-challenge.md`, and the author's
answers in `YYYY-MM-DD-<topic>-challenge-answers.md`. When and how a
challenge runs is in `docs/process.md`, "Independent challenge".

## Brief for the challenger

Paste this into a fresh session, on a different model than the author's
when possible, with nothing else from the discussion:

```
You are an independent reviewer. You took no part in this design. Read the
repository <name> on branch <branch>, starting with docs/process.md,
docs/project-definition.md and the PR <number>. Do not ask for the
discussion behind it.

Find what is wrong, missing or inconsistent: gaps between documents,
promises one document makes that another does not keep, rules with no
signal behind them ("how would the system know?"), plans that cannot be
done with the time available. Do not repeat findings already answered in
docs/reviews/.

Write docs/reviews/<date>-<topic>-challenge.md: numbered findings, each with
a severity (High, Medium, Low), where it is, why it matters, a fix, and a
suggested verdict (accept, defer, reject). End with numbered questions for
the owner, each with a suggested answer. Open a PR, or commit to <branch>.
```

## Answers file

| # | Severity | Call | Answer | Where |
|---|---|---|---|---|
| 1 | High | A | <what changes> | <files, to-do items> |

Call: A (accept), D (defer, with a phase), R (reject, with a one-line
reason). {{OWNER}}'s triage is recorded here, by number.
