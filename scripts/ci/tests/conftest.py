"""Set-up shared by the CI scripts' tests: the `req` marker, as in the pytest.ini of the other packages."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "req(*ids): acceptance criterion IDs this test proves (docs/traceability.md)")
