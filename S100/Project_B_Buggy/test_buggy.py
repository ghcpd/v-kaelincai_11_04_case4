"""Regression-focused tests for the buggy implementation.

These tests mirror the stable suite but highlight the broken email validation.
At least one test is expected to fail, demonstrating the regression.
"""
import json
import pytest

from registration_buggy import RegistrationError, UserRegistrationSystem


@pytest.fixture()
def system():
    return UserRegistrationSystem()


def test_successful_registration(system):
    payload = {
        "email": "valid.user@example.com",
        "password": "Str0ng!Passw0rd",
        "username": "validuser",
        "source": "local",
        "metadata": {"role": "tester"},
    }
    result = system.register_user(**payload)
    assert result["status"] == "success"
    assert json.loads(system.export_state())[0]["email"] == payload["email"]


def test_detect_invalid_email_regression(system):
    # This test documents the regression: invalid emails should fail but do not.
    with pytest.raises(RegistrationError, match="Invalid email"):
        system.register_user(
            email="user@@example.com",
            password="ValidPass!234",
            username="bademail",
        )


def test_detect_invalid_email_missing_domain(system):
    with pytest.raises(RegistrationError, match="Invalid email"):
        system.register_user(
            email="test@.com",
            password="Another1!Good",
            username="missingdomain",
        )


def test_duplicate_checks_remain(system):
    system.register_user(
        email="first@example.com",
        password="ValidPass!123",
        username="tester",
    )
    with pytest.raises(RegistrationError, match="already registered"):
        system.register_user(
            email="first@example.com",
            password="AnotherPass!123",
            username="another",
        )


def test_password_policy(system):
    with pytest.raises(RegistrationError, match="character classes"):
        system.register_user(
            email="entropy@example.com",
            password="alllowercase",
            username="lowentropy",
        )
