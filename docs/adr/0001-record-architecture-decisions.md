# ADR-0001: Record architecture decisions as ADRs

| Field | Value |
|---|---|
| Status | Accepted |
| Date | {{DATE}} |
| Deciders | {{OWNER}} (accepts), architect (proposes) |
| Related requirements | none |
| Supersedes | none |

## Context

The product is built by one person with AI agents that start each session
without memory of earlier ones. Decisions that live only in conversations
get lost, re-discussed or silently contradicted.

## Decision

We will record every significant architecture decision as a short Markdown
ADR in `docs/adr/`, using `docs/templates/adr.md`. A decision is significant
if it is costly to reverse, crosses modules, adds a technology, changes a
public interface or affects security. The architect proposes, {{OWNER}}
accepts by merging.

## Options considered

| Option | Pros | Cons |
|---|---|---|
| ADRs in the repository (chosen) | Versioned with the code, readable by agents, reviewed in PRs | Needs discipline |
| A design section in the project definition | Already exists | Not versioned per decision, grows unreadable |
| No written decisions | No effort | Agents re-open settled questions |

## Consequences

- Positive: every agent can read why the system is shaped as it is.
- Negative: each ADR costs a review; keep them short.
- Revisit if ADRs are skipped or no longer read in reviews.

## Compliance

The architect's review checks that a PR introducing a significant decision
references an accepted ADR. CI checks that ADR numbers are unique.
