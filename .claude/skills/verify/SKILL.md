---
name: verify
description: Check a change on {{PROJECT}} before committing it or marking a pull request ready - runs the fast checks of the parts it touches, or boots the whole application and drives it end to end.
---

# Verify a change

Run this before every commit, at the level of the change. CI is the proof,
not the place to find out (`docs/process.md`, "Verification"). It runs where
the session is, never on the CI runner's machine; the full run is CI's, when
the PR leaves draft.

## 1. The level, by kind of change

| The change | Level | When | What it runs |
|---|---|---|---|
| Documents only | `docs` | Each commit, and before the PR leaves draft | The document checks (`scripts/ci/check_docs.py`) and the Markdown lint |
| Code | `quick` | Each commit | `docs`, the linters, and the tests of each part the change touches |
| A page, the application's start, or a journey | `smoke` | Once before the PR leaves draft | Builds and starts the real application, drives the journeys the change touches end to end (browser, API harness or simulator); the full set is CI's |

Fill in, for this project, the command of each level and the table "changed
path → tests to run".

## 2. When it fails

1. Find the cause and fix it. Never skip, retry, or add a sleep to make a
   check pass. Re-run only what failed; these re-runs are free.
2. A test that failed and then passed on the same tree may be flaky: a
   `Test` to-do item once there is evidence (a CI run, or two failures).
3. CI runs of the same failing job and review send-backs count towards the
   round limit (`docs/process.md`, "Verification", item 2).
