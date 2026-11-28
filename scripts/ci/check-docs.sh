#!/usr/bin/env bash
# Document checks: unique REQ, TODO, ADR IDs and glossary terms; to-do range
# files well formed; relative links resolve; test tags name real ACs and every
# AC of a passed gate is covered (scripts/ci/trace.py --check).
# The to-do view (all of docs/todo/ as one list), the traceability matrix and
# the link diagrams (scripts/ci/links.py) go to the run summary first, so they
# are there even when a check fails.
# Needs: Python 3.10+ (standard library only).
set -euo pipefail
cd "$(dirname "$0")/../.."
# Phases whose gate has passed: their ACs must stay covered (docs/traceability.md,
# "What CI checks"). 0 until the first gate; the tester raises it in the pull
# request that passes a gate.
export TRACE_GATES_PASSED="${TRACE_GATES_PASSED:-0}"
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    python3 scripts/ci/todo_view.py . >> "$GITHUB_STEP_SUMMARY"
    if [ -n "$(ls docs/requirements/*.md 2>/dev/null | grep -v README.md)" ]; then
        python3 scripts/ci/trace.py . >> "$GITHUB_STEP_SUMMARY"
        python3 scripts/ci/links.py . >> "$GITHUB_STEP_SUMMARY"
    fi
fi
python3 scripts/ci/check_docs.py .
python3 scripts/ci/trace.py . --check
