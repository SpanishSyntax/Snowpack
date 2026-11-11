"""Shared fixtures for Snowpack tests."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Provides an isolated workspace directory."""
    return tmp_path
