"""
Pytest configuration and fixtures.
"""

import pytest
import asyncio
from unittest.mock import patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_logging():
    """Mock logging to avoid side effects during tests."""
    with patch("app.core.logging.csv_logger") as mock_csv, \
         patch("app.core.logging.json_dumper") as mock_json:
        yield {"csv": mock_csv, "json": mock_json}
