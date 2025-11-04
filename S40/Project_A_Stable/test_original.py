"""Unit tests for the stable registration implementation."""
from __future__ import annotations

import pytest

from registration_stable import (
    DuplicateUserError,
    InMemoryUserStore,
    UserRegistrationService,
    ValidationError,
    register,
)


@pytest.fixture
def store() -> InMemoryUserStore:
    return InMemoryUserStore()


def test_successful_registration(store: InMemoryUserStore) -> None:
    payload = {
        "email": "user@example.com",
        "password": "ValidPass!2",
        "metadata": {"plan": "free"},
    }
    result = register(payload, store=store)
    assert result == {"status": "success", "message": "Registration successful"}


def test_duplicate_registration_raises(store: InMemoryUserStore) -> None:
    payload = {"email": "dup@example.com", "password": "Another1!A"}
    register(payload, store=store)
    with pytest.raises(DuplicateUserError):
        register(payload, store=store)


def test_invalid_email_formats(store: InMemoryUserStore) -> None:
    service = UserRegistrationService(store=store)
    invalid_emails = [
        "user@@example.com",
        "userexample.com",
        "user@.com",
        "user@localhost",
        "user@example..com",
    ]
    for email in invalid_emails:
        with pytest.raises(ValidationError):
            service.register_user({"email": email, "password": "ValidPass!2"})


def test_password_policy_requires_complexity(store: InMemoryUserStore) -> None:
    service = UserRegistrationService(store=store)
    bad_passwords = [
        "short1!A",
        "nouppercase1!",
        "NOLOWERCASE1!",
        "NoDigits!!",
        "NoSymbols123",
        "contains space1!A",
    ]
    for password in bad_passwords:
        with pytest.raises(ValidationError):
            service.register_user({"email": "pass@example.com", "password": password})


def test_password_max_length(store: InMemoryUserStore) -> None:
    service = UserRegistrationService(store=store)
    long_password = "A" * 120 + "a1!"
    assert len(long_password) > 120
    service.register_user({"email": "long@example.com", "password": long_password})

    too_long_password = "Aa1!" + "Z" * 200
    with pytest.raises(ValidationError):
        service.register_user({"email": "toolong@example.com", "password": too_long_password})
