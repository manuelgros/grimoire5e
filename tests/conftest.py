"""
Shared fixtures.

The unit tests in test_entry_format.py need no data and always run. The corpus
tests in test_render_sweep.py walk every entry of a real 5etools download; they
skip unless a data directory is available, so the suite still passes on a clean
checkout or in CI without network access.

Point them at a specific download with:

    GRIMOIRE_TEST_DATA=/path/to/data pytest

Otherwise they fall back to the data directory the app itself uses.
"""

import os
from pathlib import Path

import pytest

from grimoire.config import get_data_dir


def _resolve_data_dir():
    env = os.environ.get("GRIMOIRE_TEST_DATA")
    candidates = [Path(env)] if env else []
    candidates += [get_data_dir(), Path("data")]
    for path in candidates:
        if path.is_dir() and any(path.glob("*.json")):
            return path
    return None


@pytest.fixture(scope="session")
def data_dir():
    path = _resolve_data_dir()
    if path is None:
        pytest.skip(
            "no 5etools data found — run grimoire to download it, or set "
            "GRIMOIRE_TEST_DATA to a data directory"
        )
    return path


@pytest.fixture(scope="session")
def loader(data_dir):
    from grimoire.services.data_loader import DataLoader

    return DataLoader(data_dir)
