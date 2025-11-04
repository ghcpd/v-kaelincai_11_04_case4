# Regression Comparison Report

Generated: 2025-11-04T06:15:41+00:00

## Scenario Overview

- **Feature:** User registration with email and password validation.
- **Stable logic:** Uses anchored RFC-style regex, disallows consecutive separators, enforces domain labels, and blocks duplicates.
- **Regression change:** Introduced OAuth provider support with email sanitisation and a relaxed regex (`^[A-Za-z0-9._%+-]+@[^\s]+$`), allowing malformed emails such as `user@@mail` and `test@.com`.
- **Verification goal:** Detect divergence in validation accuracy by re-running the original negative email cases and confirming failures in the buggy build.

## Test Result Summary

5 passed in 0.02s
1 failed, 1 passed in 0.10s

| Metric | Project A (Stable) | Project B (Buggy) |
| --- | --- | --- |
| Passed | 5 | 1 |
| Failed | 0 | 1 |
| Skipped | 0 | 0 |
| Warnings | 0 | 0 |

- **Execution time (stable):** 0.782778 seconds
- **Execution time (buggy):** 0.839942 seconds
- **Regression-focused cases:** 3 (`case-002, case-003, case-004`)
- **Exit codes:**
  - Stable exit code: 0
  - Buggy exit code: 1

## Observations

1. The stable suite passes all assertions, confirming baseline correctness.
2. The buggy suite exits with a non-zero status because invalid emails are no longer rejected, evidencing the regression.
3. Duplicate user protection and password complexity remain intact across both versions, isolating the fault to email validation.
4. Providers can now be attached to registrations in the buggy build, but the relaxed sanitisation inadvertently normalises malformed addresses.

## Recommended Next Steps

- Reinstate the strict regex (`^(?=.{3,254}$)(?!.*\.\.)[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$`) and remove the `@@` collapsing logic.
- Extend CI pipelines to execute the shared `test_data.json` scenarios on every commit.
- Add property-based tests for email parsing to cover unusual separators and provider-specific payloads.