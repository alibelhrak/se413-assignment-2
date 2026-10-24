"""Test suite for src/registration.py (Assignment 2).

Targets summarize_batch_registrations() (lines 62-89) and
enroll_student() (lines 92-117).
"""

import pytest

from registration import enroll_student, summarize_batch_registrations


# ---------------------------------------------------------------------------
# Section 4(a): statement coverage
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.positive
def test_batch_single_approved_request():
    """One approved request executes lines 80-87 and 89.

    (10, 3, True): can_register -> True, total credits 13,
    fee = 12*100 + 1*75 = 1275.0.
    """
    assert summarize_batch_registrations([(10, 3, True)]) == (1, 1275.0)


@pytest.mark.unit
@pytest.mark.positive
def test_enroll_allowed_executes_success_path(notifier):
    """Allowed request executes lines 110-114."""
    assert enroll_student(10, 3, True, notifier) is True


@pytest.mark.unit
@pytest.mark.negative
def test_enroll_rejected_executes_rejection_path(notifier):
    """Prerequisite not met executes lines 110, 116-117."""
    assert enroll_student(10, 3, False, notifier) is False