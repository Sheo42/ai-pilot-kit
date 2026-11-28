# Traceability matrix

Links every requirement and acceptance criterion (AC) to the tests and
proofs that verify it. Nobody edits it by hand: `scripts/ci/trace.py` builds it from the requirements and the test
tags, and CI prints it in the run summary. A hand-kept matrix and its
coverage counts make every parallel pull request conflict.

## Tagging a test

1. Python: `@pytest.mark.req("REQ-XXX-NNN.AC1")` on the test (register the
   `req` marker in `pytest.ini`).
2. TypeScript: the AC ID in the test title, `it("REQ-XXX-NNN.AC1: ...")`.
3. A whole file: a `# req:` or `// req:` line naming the ACs.
4. Check scripts: the AC ID in the message the check prints, or a
   `# req:` comment.
5. Inspection, demonstration, analysis, or an AC proved only in part: one
   file per proof in `docs/verification/` with a `Criterion` row (the ACs)
   and a `Result` row (`Pass`, `Partial: what is missing`, `Not run`).

## Diagrams of the links

`scripts/ci/links.py` draws the links as Mermaid diagrams, which GitHub
shows as pictures, on a phone too: one per use case (its ACs and their
tests), one per module (the requirements, their `Related` requirements and
`Related ADRs`), and one of the to-do items that block others. Each AC and
requirement is coloured by its coverage here: green covered, orange partly,
red not at all. CI puts them in the run summary, after the matrix; the PR
reviewer pastes the ones a PR changes into its merge summary
(`links.py --only UC-03,MON,TODO`). `scripts/ci/check_docs.py` fails on a
`Related` or `Related ADRs` row naming a requirement, an AC or an ADR that
does not exist.

## What CI checks

`scripts/ci/trace.py --check` fails on a tag naming no AC, and on an AC of
a passed phase gate that is not fully covered. `TRACE_GATES_PASSED` in
`scripts/ci/check-docs.sh` starts at 0; give `PHASES` in `trace.py` your
phase names.
