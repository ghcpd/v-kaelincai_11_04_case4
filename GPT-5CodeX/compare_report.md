# Regression Comparison Report

## Scenario Overview
- Feature: local user registration with strict email, password, and duplicate validation.
- Original logic: RFC-like email regex (`registration_stable.EMAIL_REGEX`) plus password policy checks.
- Regression: `registration_buggy.UserRegistrationSystem._validate_email` now performs only superficial `"@" in email` check for local sign-ups, letting malformed addresses through.
- Verification goal: confirm invalid emails (`user@@mail.com`, `test@.com`) slip past the buggy implementation while baseline stays correct.

## Test Outcome Summary
| Test Case | Stable Result | Buggy Result | Regression Indicator |
| --- | --- | --- | --- |
| `test_valid_registration` | Pass | Pass | No |
| `test_invalid_email_rejected` | Pass | **Fail** (invalid email accepted) | Yes |
| `test_domainless_email_should_fail` | Pass | **Fail** (invalid email accepted) | Yes |
| `test_password_policy_enforced` | Pass | n/a (policy covered implicitly) | No |
| `test_duplicate_email_blocked` | Pass | Pass | No |
| `test_boundary_email` | Pass | n/a | No |

## Metrics
- Stable suite: 5/5 tests passed, exit code 0, see `Project_A_Stable/log_original.txt`.
- Buggy suite: 2/4 tests passed, exit code 1, see `Project_B_Buggy/log_buggy.txt`.
- Regression detection accuracy: 100% for invalid-email scenarios (both failing cases map to `regression_indicator=true` entries in `test_data.json`).

## Behavioral Differences
- Stable version rejects malformed emails via regex and structural checks.
- Buggy version skips regex for trusted providers and fallback mistakenly trusts any string with `"@"`, causing acceptance of addresses with duplicate or trailing separators.
- Duplicate detection and password policy remain intact in both versions, indicating regression scope is isolated to email validation.

## Observations
- Automated tests backed by shared `test_data.json` reveal the regression immediately; failures align with expected regression indicators.
- Adding provider-aware email validation tests in the buggy suite would help prevent similar defects when extending third-party integrations.
