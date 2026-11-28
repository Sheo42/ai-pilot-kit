# Mutation tests

How to run the mutation tests that `docs/process.md` asks for
("Verification", item 5, and "Phases", the gate), and how to keep their
verdicts. A mutation tool changes one line of the code on purpose (a `<`
becomes `<=`, a condition becomes `true`, a call is removed) and runs the
tests: a test should fail. Each changed copy is a **mutant**. The tests, like
the code, were written by the AI, so this is how the project checks that the
tests notice a wrong line.

One file per run in this folder, `YYYY-MM-DD-<scope>.md` (for example
`2026-03-02-gate-2.md` or `2026-02-10-billing-feature.md`), copied from
[the ledger template](../templates/mutation-ledger.md).

## When

1. After a big feature, on the modules it changed.
2. At each phase gate, on the critical modules. At the first gate after the
   walking skeleton the run is a **baseline**, for information: it is
   triaged, but it does not block the gate. From the second gate after the
   skeleton, the gate needs a ledger with no survivor and no unreached
   mutant left without a verdict in the critical modules.
3. Never on the CI runner: a run takes long and the CI runner is shared.
   It runs where long runs go in this project (`docs/coordinator.md`,
   "Rhythm"). The result is a document, the ledger, in a pull request.

## Critical modules

The modules where a wrong line costs most: {{SECURITY_AREAS}}, access
control, and the code that writes data that cannot be rebuilt. The architect
proposes the list with the security engineer; the pull request that changes
it is merged by {{OWNER}}, which accepts it.

| Module | Path | Why it is critical |
|---|---|---|
| <!-- adapt: module name --> | <!-- adapt: src/... --> | <!-- adapt: one line --> |

## The tool

1. The architect picks a mutation tool for the stack, in an ADR when it is
   a new dependency. Any tool that lists each mutant with its file, line,
   change and result will do.
2. Its settings are checked in (the file is named in each ledger) and are a
   judge file (`docs/process.md`, "Verification", item 4): a change that
   excludes code from the run is read for weakening.
3. **Noise is cut in the tool, not in the ledger.** A kind of mutant that
   can never matter (a log message, a debug-only branch, generated code) is
   excluded in the settings, with a comment saying why, so it does not come
   back at every run. A mutant is noise only if no user, caller or stored
   record can ever see the change.
4. Each mutant gets a time limit; a mutant that hangs counts as killed
   (the tests noticed something) and is listed with the count.

## The run and the triage

1. The tester runs the tool on the named commit and fills the ledger's
   header and counts per module: killed, survived, not reached (no test
   runs that line), timed out, errors.
2. Every survivor and every unreached mutant in the scope gets one row and
   one verdict:

   | Verdict | Meaning | What follows |
   |---|---|---|
   | Gap | A test should notice this change and none does | A test, in the same PR or a `Test` to-do item with its phase |
   | Bug | The mutant is right and the code is wrong | A `Bug` to-do item (`docs/process.md`, "Bugs") |
   | Equivalent | The change cannot alter any result (the same value is computed another way) | The reason, in one line; if it is a pattern, it is cut in the tool next time |
   | Accepted | The change alters a result nobody relies on | The reason, in one line; {{OWNER}} sees each one in the PR |

3. A test written for a Gap is shown to kill its mutant (run the tool on
   that line again, or apply the change by hand and see the test fail).
4. A gap in a non-critical module is triaged the same way when the run
   covers it, but does not block the gate.

## The sample check

The verdicts are written by an AI too, so a fresh session that does not
trust them checks a sample:

1. A new session with no context, on a different model than the triage
   when possible, gets the ledger and the commit, never the discussion.
2. It re-judges a random sample: every `Accepted` row, and of the other
   verdicts 20 rows or all of them if fewer, drawn with the seed written in
   the ledger so anyone can draw the same rows again.
3. It fills the ledger's sample table. Each disagreement is settled by
   {{OWNER}} by number, like a challenge finding.
4. More than two disagreements in the sample means the triage of that
   verdict is done again, then a new sample is checked.

Assumption (2026-11-28): the sample size of 20 and the limit of two
disagreements are first values, not measured ones; a project changes them
after its first gate and says so in its chronicle.

## The pull request

One pull request per run: the ledger, the tool's settings if they changed,
the tests written for Gaps and the new to-do items. Its description gives
the score per critical module, the number of rows per verdict, and the
sample check's result.
