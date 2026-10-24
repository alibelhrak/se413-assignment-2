# SE 413/513 Assignment 2: Coverage, Data-Flow Testing, and Test Doubles

**Student:** Ali Belhrak (GitHub: `alibelhrak`)
**Branch:** `assignment-2`

This repository contains a pytest suite for the Course Registration System.
`src/registration.py` is the provided starter code and is **unmodified**. The
suite targets the two new functions:

- `summarize_batch_registrations(requests)`, lines 62–89
- `enroll_student(current_credits, course_credits, prerequisite_met, notifier)`, lines 92–117

## Project layout

```
assignment-2/
|-- src/registration.py        provided, unmodified
|-- tests/test_registration.py all tests (Sections 4, 5, 6)
|-- tests/conftest.py          notifier Mock fixture (Section 6a)
|-- pyproject.toml             pytest + coverage configuration, markers
|-- .coveragerc-statement      statement-only coverage configuration (Section 4a)
|-- .gitignore
|-- README.md
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install pytest pytest-cov
```

All commands below are run from the project root. On Windows, `python -m pytest`
is used because the `pytest` script directory may not be on `PATH`.

---

## 1. Running the tests (Section 7)

### Full suite

```
python -m pytest -v
```

### Coverage commands (Section 4)

Branch coverage (statement + branch):

```
python -m pytest --cov --cov-branch --cov-report=term-missing
```

Statement-only coverage:

```
python -m pytest --cov --cov-config=.coveragerc-statement --cov-report=term-missing
```

> **Why a separate config file?** `pyproject.toml` sets `branch = true` under
> `[tool.coverage.run]`, so simply dropping `--cov-branch` still measures
> branches. `.coveragerc-statement` sets `branch = False` (and keeps
> `source = src`), producing a true statement-only report.

### Marker-filtered subsets

Every test carries the `unit` marker plus one of `positive`, `negative`, or
`boundary` (all registered in `pyproject.toml`).

```
python -m pytest -m negative -v          # rejection / failure scenarios (3 tests)
python -m pytest -m positive -v          # success scenarios (5 tests)
python -m pytest -m boundary -v          # empty-batch boundary (1 test)
python -m pytest -m "unit and not negative"
```

Example: `python -m pytest -m negative -v`

```
collected 9 items / 6 deselected / 3 selected
tests/test_registration.py::test_enroll_rejected_executes_rejection_path PASSED
tests/test_registration.py::test_batch_all_requests_rejected PASSED
tests/test_registration.py::test_enroll_rejected_sends_rejection_without_arguments PASSED
======================= 3 passed, 6 deselected =======================
```

### Test inventory

| Test | Markers | Section |
|---|---|---|
| `test_batch_single_approved_request` | unit, positive | 4a |
| `test_enroll_allowed_executes_success_path` | unit, positive | 4a |
| `test_enroll_rejected_executes_rejection_path` | unit, negative | 4a |
| `test_batch_empty_list_skips_loop` | unit, boundary | 4b |
| `test_batch_all_requests_rejected` | unit, negative | 4b |
| `test_batch_mixed_approved_and_rejected` | unit, positive | 4b |
| `test_batch_total_fees_loop_carried_du_pair` | unit, positive | 5c |
| `test_enroll_allowed_sends_confirmation_with_fee` | unit, positive | 6b |
| `test_enroll_rejected_sends_rejection_without_arguments` | unit, negative | 6c |

---

## 2. Statement and branch coverage (Section 4)

The report measures the whole file. Lines 15–59 belong to `can_register` and
`calculate_registration_fee`, which are **not** targets of this assignment.
Every entry left in the `Missing` column is inside that range; nothing from
line 62 onward is missing.

### 4(a) Final statement-only report

```
Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
src\registration.py      36      3    92%   28, 31, 50
---------------------------------------------------
TOTAL                    36      3    92%
============================== 9 passed ==============================
```

Lines 28, 31, and 50 are in `can_register` / `calculate_registration_fee`.
**`summarize_batch_registrations` and `enroll_student` have 0 missing statements.**

### 4(b) Final branch-coverage report

```
Name                  Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------
src\registration.py      36      3     18      3    89%   28, 31, 50
-----------------------------------------------------------------
TOTAL                    36      3     18      3    89%
============================== 9 passed ==============================
```

No `a->b` arcs are listed, and the three partial branches are the decisions
leading to lines 28, 31, and 50 (outside the targets).
**Both target functions have no missing branches.** The arc `84->83` was the
only gap after Section 4(a); it was closed by the rejected-request tests below.

### 4(b) Which tests exercise each decision outcome

| Decision | Outcome | Exercised by |
|---|---|---|
| `for` loop, line 83 | Body entered (83→84) | `test_batch_single_approved_request`, `test_batch_all_requests_rejected`, and `test_batch_mixed_approved_and_rejected` each iterate over at least one request. |
| `for` loop, line 83 | Loop exits (83→89) | `test_batch_empty_list_skips_loop` exits without entering the body, and every non-empty batch test also exits after its last request. |
| `if can_register(...)`, line 84 | True (84→85) | `test_batch_single_approved_request` and `test_batch_mixed_approved_and_rejected` include the approved request `(10, 3, True)`. |
| `if can_register(...)`, line 84 | False (84→83) | `test_batch_all_requests_rejected` (out-of-range credits and missing prerequisite) and the second request of `test_batch_mixed_approved_and_rejected`. |
| `if can_register(...)`, line 110 | True (110→111) | `test_enroll_allowed_executes_success_path` and `test_enroll_allowed_sends_confirmation_with_fee` call `enroll_student(10, 3, True, ...)`. |
| `if can_register(...)`, line 110 | False (110→116) | `test_enroll_rejected_executes_rejection_path` and `test_enroll_rejected_sends_rejection_without_arguments` call `enroll_student(10, 3, False, ...)`. |

Note: coverage.py marks 83→89 as covered by any non-empty batch, because every
loop exits through that arc. The empty-batch test is still included because it
is the only one that verifies the initial accumulator values reach the
`return` unchanged (DU pair 2 below).

---

## 3. Data-flow testing: `total_fees` (Section 5)

```python
81    total_fees = 0.0                                                         # d1
83    for current_credits, course_credits, prerequisite_met in requests:
84        if can_register(current_credits, course_credits, prerequisite_met):
85            approved_count = approved_count + 1
86            total_credits = current_credits + course_credits
87            total_fees = total_fees + calculate_registration_fee(total_credits)  # u1, then d2
89    return approved_count, total_fees                                        # u2
```

### 5(a) Definitions and uses

| ID | Line | Statement | Kind |
|---|---|---|---|
| **d1** | 81 | `total_fees = 0.0` | Definition: initialization before the loop |
| **d2** | 87 | `total_fees = total_fees + ...` (left-hand side) | Definition: accumulation inside the loop |
| **u1** | 87 | `total_fees + calculate_registration_fee(...)` (right-hand side) | c-use (computation) |
| **u2** | 89 | `return approved_count, total_fees` | c-use (returned value) |

`total_fees` has **no p-uses**: the predicates on lines 83 and 84 test
`requests` and `can_register(...)`, never `total_fees`. On line 87 the
right-hand side is evaluated before the assignment, so u1 always reads a value
defined *earlier* (by d1, or by d2 on a previous iteration).

### 5(b) DU-pair table

A rejected iteration does not assign `total_fees`, so a path through one or
more rejected iterations is still def-clear.

| # | DU pair | Def-clear path | Meaning | Exercised by |
|---|---|---|---|---|
| 1 | (d1, u1): 81 → 87 | 81 → 83 → 84 → 85 → 86 → 87 | The first approved request reads the initial `0.0` | `test_batch_single_approved_request`, `test_batch_mixed_approved_and_rejected`, `test_batch_total_fees_loop_carried_du_pair` |
| 2 | (d1, u2): 81 → 89 | 81 → 83 → 89 (directly, or after rejected iterations only) | No request is approved, so `0.0` is returned | `test_batch_empty_list_skips_loop`, `test_batch_all_requests_rejected` |
| 3 | (d2, u2): 87 → 89 | 87 → 83 → 89 (directly, or after later rejected iterations) | The last accumulated total is returned | `test_batch_single_approved_request`, `test_batch_mixed_approved_and_rejected`, `test_batch_total_fees_loop_carried_du_pair` |
| 4 | **(d2, u1): 87 → 87, loop-carried** | 87 → 83 → 84 → 85 → 86 → 87 on a later iteration | A later approved request reads the running total from an earlier one | `test_batch_total_fees_loop_carried_du_pair` |

### 5(c) Loop-carried pair test

`test_batch_total_fees_loop_carried_du_pair` runs the batch
`[(10, 3, True), (10, 2, True)]`. Both requests are approved: the first adds
1275.0 (13 credits = 12 × 100 + 1 × 75), and the second reads that running total
on line 87 and adds 1200.0 (12 credits). The test asserts
`approved_count == 2` and `total_fees == 2475.0`.

**Why zero or one approval cannot exercise this pair:** with zero approved
requests line 87 never executes, and with exactly one it executes once, so the
value defined by d2 can only reach the `return` (u2) and never a later
execution of the use on line 87 (u1). All-Defs is already satisfied by pairs 1
and 3 (each definition reaches some use), but All-Uses also requires pair 4.
That pair is the only one that would detect line 87 overwriting `total_fees`
instead of accumulating it: such a bug returns 1200.0 here but still passes
every single-approval test.

---

## 4. Test doubles for the notifier (Section 6)

### 6(a) Fixture

`tests/conftest.py` defines a `notifier` fixture that returns a plain
`unittest.mock.Mock()`. A fresh Mock is created for each test. It serves as:

- a **stub**: it accepts `send_confirmation(fee)` and `send_rejection()` calls
  without a real email or push service, so `enroll_student()` runs in isolation;
- a **spy**: it records every call and its arguments, so tests can verify how
  `enroll_student()` interacted with its collaborator.

### 6(b) Positive test: `test_enroll_allowed_sends_confirmation_with_fee`

`enroll_student(10, 3, True, notifier)`

| Verification | Assertion |
|---|---|
| State | `result is True` |
| Behavior | `notifier.send_confirmation.assert_called_once_with(1275.0)` |
| Behavior | `notifier.send_rejection.assert_not_called()` |

### 6(c) Negative test: `test_enroll_rejected_sends_rejection_without_arguments`

`enroll_student(10, 3, False, notifier)` (prerequisite not met)

| Verification | Assertion |
|---|---|
| State | `result is False` |
| Behavior | `notifier.send_rejection.assert_called_once_with()` (called once, with no arguments) |
| Behavior | `notifier.send_confirmation.assert_not_called()` |

---

## 5. Evidence the full suite passes (Section 7b)

`python -m pytest -v` from the project root:

```
collected 9 items

tests/test_registration.py::test_batch_single_approved_request PASSED                  [ 11%]
tests/test_registration.py::test_enroll_allowed_executes_success_path PASSED           [ 22%]
tests/test_registration.py::test_enroll_rejected_executes_rejection_path PASSED        [ 33%]
tests/test_registration.py::test_batch_empty_list_skips_loop PASSED                    [ 44%]
tests/test_registration.py::test_batch_all_requests_rejected PASSED                    [ 55%]
tests/test_registration.py::test_batch_mixed_approved_and_rejected PASSED              [ 66%]
tests/test_registration.py::test_batch_total_fees_loop_carried_du_pair PASSED          [ 77%]
tests/test_registration.py::test_enroll_allowed_sends_confirmation_with_fee PASSED     [ 88%]
tests/test_registration.py::test_enroll_rejected_sends_rejection_without_arguments PASSED [100%]

===================================== 9 passed =====================================
```