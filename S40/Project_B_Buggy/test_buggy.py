"""Unit tests for the buggy registration implementation.

The suite intentionally expects strict email validation so regressions surface as failures.
"""
from __future__ import annotations

import pytest

from registration_buggy import (
    DuplicateUserError,
    InMemoryUserStore,
    UserRegistrationService,
    ValidationError,
    register,
)


@pytest.fixture
def store() -> InMemoryUserStore:
    return InMemoryUserStore()


def test_successful_registration_with_provider(store: InMemoryUserStore) -> None:
    payload = {
        "email": "beta-user@example.com",
        "password": "VeryStrongPass1!",
        "provider": "oauth-google",
        "metadata": {"plan": "beta"},
    }
    result = register(payload, store=store)
    assert result["status"] == "success"
    assert result["provider"] == "oauth-google"


def test_invalid_email_formats_raise_error(store: InMemoryUserStore) -> None:
    service = UserRegistrationService(store=store)
    invalid_emails = [
        "user@@mail",
        "test@.com",
        "user@localhost",
        "user@example..com",
    ]
    for email in invalid_emails:
        with pytest.raises(ValidationError):
            service.register_user({"email": email, "password": "ValidPassword1!"})


def test_duplicate_registration_raises(store: InMemoryUserStore) -> None:
    payload = {"email": "dup@example.com", "password": "AnotherValid1!"}
    register(payload, store=store)
    with pytest.raises(DuplicateUserError):
        register(payload, store=store)
