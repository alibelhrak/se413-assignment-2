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


# ---------------------------------------------------------------------------
# Section 4(b): branch coverage
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.boundary
def test_batch_empty_list_skips_loop():
    """Empty batch: the for loop (line 83) is never entered (83->89).

    Both accumulators keep their initial values.
    """
    assert summarize_batch_registrations([]) == (0, 0.0)


@pytest.mark.unit
@pytest.mark.negative
def test_batch_all_requests_rejected():
    """Every request rejected: the if on line 84 is only False (84->83).

    (16, 3, True) fails the current-credits range; (10, 3, False) fails
    the prerequisite. Neither contributes to the count or the fees.
    """
    assert summarize_batch_registrations([(16, 3, True), (10, 3, False)]) == (0, 0.0)


@pytest.mark.unit
@pytest.mark.positive
def test_batch_mixed_approved_and_rejected():
    """Both outcomes of line 84 in one batch: True (84->85) then False (84->83).

    Only the approved request (10, 3, True) adds its fee of 1275.0.
    """
    assert summarize_batch_registrations([(10, 3, True), (10, 3, False)]) == (1, 1275.0)

# ---------------------------------------------------------------------------
# Section 5(c): data-flow testing -- loop-carried DU pair of total_fees
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.positive
def test_batch_total_fees_loop_carried_du_pair():
    """Exercises the loop-carried DU pair (def @ line 87, use @ line 87).

    Iteration 1 approves (10, 3, True): total 13 credits, fee 1275.0, and
    line 87 defines total_fees = 0.0 + 1275.0.
    Iteration 2 approves (10, 2, True): total 12 credits, fee 1200.0, and
    line 87 reads the total_fees defined on iteration 1:
    total_fees = 1275.0 + 1200.0 = 2475.0.

    A version of line 87 that overwrote instead of accumulating would
    return 1200.0 here, but would still pass every single-approval test.
    """
    approved_count, total_fees = summarize_batch_registrations(
        [(10, 3, True), (10, 2, True)]
    )

    assert approved_count == 2
    assert total_fees == 1275.0 + 1200.0  # 2475.0
    
    


# ---------------------------------------------------------------------------
# Section 6: test doubles for the notifier collaborator
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.positive
def test_enroll_allowed_sends_confirmation_with_fee(notifier):
    """Allowed case: state verification + behavior verification on the Mock.

    (10, 3, True): can_register -> True, total 13 credits,
    fee = 12*100 + 1*75 = 1275.0.
    """
    result = enroll_student(10, 3, True, notifier)

    # State verification: the function's own observable output.
    assert result is True

    # Behavior verification: how enroll_student talked to its collaborator.
    notifier.send_confirmation.assert_called_once_with(1275.0)
    notifier.send_rejection.assert_not_called()


@pytest.mark.unit
@pytest.mark.negative
def test_enroll_rejected_sends_rejection_without_arguments(notifier):
    """Rejected case (prerequisite not met): state + behavior verification."""
    result = enroll_student(10, 3, False, notifier)

    # State verification
    assert result is False

    # Behavior verification
    notifier.send_rejection.assert_called_once_with()
    notifier.send_confirmation.assert_not_called()