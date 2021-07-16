"""pytest markers."""
import os
from typing import Any, Callable

import pytest

"""
Skip a test if no test database is defined.

This marker should be used on all tests that require a database. The marker checks
whether the environment variable SDB_DSN is defined and its value is not an empty
string. This is the variable used by the db fixture to create a database connection.
"""
nodatabase: Callable[..., Any] = pytest.mark.skipif(
    not os.getenv("SDB_DSN"),
    reason="No test database defined. See the tests.markers package for details.",
)
