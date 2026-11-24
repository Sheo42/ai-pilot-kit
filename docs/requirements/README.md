# Requirements: conventions

Written by the `business-analyst` with `docs/templates/requirement.md`,
approved by {{OWNER}} when the PR merges. One file per module, named in
plain words (for example `access-control.md`); the module code is used in
IDs only.

## ID scheme

`REQ-<MODULE>-<NNN>`, for example `REQ-IAM-007`. Numbers are sequential per
module, never reused, never changed. Acceptance criteria are numbered inside
their requirement: `REQ-IAM-007.AC1`. The category is a field, not part of
the ID, so a requirement can be recategorised without breaking test links.

## Modules

| Code | Module | File | Phases |
|---|---|---|---|
| <!-- e.g. IAM --> | <!-- Users, roles, access --> | <!-- access-control.md --> | |

## Categories

| Code | Category |
|---|---|
| FUN | Functional: what the system does for a user |
| SEC | Security and privacy |
| PRF | Performance and capacity |
| REL | Reliability and availability |
| DAT | Data: model, quality, retention |
| INT | Interface and interoperability |
| UX | Usability and accessibility |
| OPS | Operability: monitoring, deployment, support |
| CMP | Compliance and regulation |
| TEC | Technical constraint imposed on the solution |

## Priority and phase

MoSCoW: **Must** (the phase fails without it), **Should** (can slip only by
{{OWNER}}'s decision), **Could**, **Won't (this phase)**. Each requirement
also names the phase by whose gate all its ACs must be verified
(`docs/process.md`, "Phases"). Each phase has a Must cap.

## Status lifecycle

```
Draft → Proposed → Approved → Implemented → Verified
                 ↘ Rejected      (any) → Deprecated
```

A PR sets its requirements to `Approved` before asking for the merge; the
merge makes it true. Changing an approved requirement bumps its version,
adds a change log line and sets it to `Approved` too: the merge re-approves
it. Never set it back to `Proposed` in the PR, because nothing sets it
forward after the merge. A CI check that refuses a bare `Draft` or `Proposed`
in every PR catches the ones left behind: the PR is the proposal, so its
requirements say `Approved` by the time it asks for review. Merging
approves every other document too, so documents other than requirements
and ADRs carry no status line: the merge history shows what was approved.

## Numbers in requirements

A number in a requirement is one of three kinds, and the
text says which when it is not obvious.

1. **A setting's default.** A time limit, threshold or count that decides
   what the platform does (an offline alarm after 5 minutes, a value fresh
   for 60 s, 3 retries in 10 minutes, escalation after 30 minutes). The code
   reads it as a setting with this default (the settings index), and the
   acceptance criterion is tested with the default and with a changed value.
2. **A target.** A measured promise (a chart in under 3 s, 99% of replies
   within 5 s, 10,000 devices). It is not a setting: it changes only by a new
   version of the requirement.
3. **A contract value.** Fixed by the device contract or the API (a field
   limit, a topic). It changes only with the contract's version.

A placeholder (a number not yet confirmed) is still one of the three; its
to-do says which.

## Verification methods

**Test** (automated, in CI; the default), **Demonstration**, **Inspection**,
**Analysis**. Every method other than Test states why automation is not
possible.
