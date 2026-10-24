"""Shared pytest fixtures for the Assignment 2 test suite."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def notifier():
    """A plain Mock standing in for the notifier collaborator of enroll_student().

    It acts as a stub (its methods accept any call, so enroll_student() runs
    without a real email/push service) and as a spy (it records every call,
    so tests can verify which method was called and with which arguments).
    A fresh Mock is created per test, so call records never leak between tests.
    """
    return Mock()