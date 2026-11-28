# Workflow

The full rules are in [`docs/process.md`](../process.md). This page explains
the shape of the flow and the reasons behind each step.

## 1. From a need to a merge

```
Need (owner, any form)
  → requirement(s) with testable ACs          business analyst
  → ADR if a costly decision is involved      architect (+ security engineer)
  → tests for each AC                         tester
  → code on a branch, PR with handoff note    developer
  → reviews sized to the PR                   tester, PR reviewer, architect, security engineer
  → independent challenge if the PR is big    fresh session, other model
  → owner triages findings, then merges       owner
  → chronicle entry                           chronicler
```

Why this order: a need written as a testable requirement is cheap to change;
the same need discovered in code review is not. Each arrow is a place where
an AI role can stop and ask the owner a numbered question instead of
guessing.

Two shortcuts, both written into the process:

1. **Exploratory POC.** A throwaway proof of concept in `poc/`, built
   without requirements or tracing, to give the owner something to click.
   In the first project it produced sharper feedback than any question list.
2. **Small changes** (a typo, a dependency bump) skip the requirement and
   design steps but still run the checks.

## 2. Thread organisation

- One coordinator in the project chat; one thread per piece of work, each
  on its own branch, opening its own PR.
- Threads run in parallel. They share the repository, the project memory
  and a shared files folder. A branch sees only what is merged, so two
  threads would pick the same "next" number: the coordinator reserves a
  range of to-do, requirement, ADR and migration numbers for each thread
  when it starts it, and keeps the list in project memory. Each PR writes
  its to-do items in a file of its own range (`docs/todo/540-549.md`), so
  parallel PRs never add rows at the same place.
- Each PR closes its own to-do items. Open PRs are the owner's review queue,
  so there is never a "review PR #N" to-do.

## 3. Reviews, sized to the change

Not every PR gets every reviewer: the tiers are in `docs/process.md` and
`docs/coordinator.md`, section 4. Documents get the PR reviewer; code gets
an automated code review at medium effort, the tester and the PR reviewer;
pages add a UX walkthrough; contracts, schemas, sign-in, tenancy and the
security areas add the security engineer and a blind challenge.

## 4. The independent challenge

**When:** security, tenancy, connectivity, storage or hosting ADRs; a new
requirements module or a large batch; a process change; a global pass
before each phase gate; or whenever the owner asks.

**How:**
1. A fresh session with no prior context, on a different model than the
   author, reads only the repository and the PR.
2. It writes numbered findings, each with a severity and a suggested
   verdict (accept, defer, reject), in `docs/reviews/`.
3. The author answers each finding by number.
4. The owner triages by number. Accepted findings become changes in the
   same PR; deferred ones a to-do with a phase; rejected ones keep a
   one-line reason.

In the first project, the first four challenges each found at least one
High finding that the authors and reviewers had missed, usually in the gap
between two documents rather than inside one.

## 5. Triage: the owner's real job

The owner's main work is answering numbered lists:
- requirement questions ("1 yes, 2 no, 3 as proposed"),
- challenge findings ("all as suggested except 10"),
- decisions in the to-do list ("Waiting on" the owner).

The method works when each question in a list arrives with a suggested
answer, so the owner can confirm most items in a word and spend time only
on the few that need judgement. Plain steps and instructions are numbered
too, but carry no suggested answer: there is nothing to answer.

## 6. Closing a session

Every task ends by updating the to-do list in `docs/todo/` (open what is
new in the range's own file, close what is done in place) and the glossary;
every session ends with a chronicle entry.
