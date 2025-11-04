"""Unit tests for the stable registration implementation."""
import json
import time

import pytest

from registration_stable import RegistrationError, UserRegistrationSystem


@pytest.fixture()
def system():
    return UserRegistrationSystem()


def test_successful_registration(system):
    payload = {
        "email": "valid.user@example.com",
        "password": "Str0ng!Passw0rd",
        "username": "validuser",
        "metadata": {"role": "tester"},
    }
    result = system.register_user(**payload)
    assert result["status"] == "success"
    assert result["user"]["email"] == payload["email"]
    assert json.loads(system.export_state())[0]["email"] == payload["email"]


def test_reject_duplicate_email(system):
    system.register_user(
        email="dupe@example.com",
        password="Val1d!Pass",
        username="unique",
    )
    with pytest.raises(RegistrationError, match="Email already registered"):
        system.register_user(
            email="Dupe@example.com",  # case-insensitive duplicate
            password="Another!Valid1",
            username="another",
        )


def test_reject_duplicate_username(system):
    system.register_user(
        email="first@example.com",
        password="Valid!Pass123",
        username="tester",
    )
    with pytest.raises(RegistrationError, match="Username already taken"):
        system.register_user(
            email="second@example.com",
            password="Stronger!234",
            username="Tester",  # case-insensitive duplicate
        )


def test_invalid_email_formats(system):
    invalid_emails = [
        "plainaddress",
        "missingatsign.com",
        "user@@example.com",
        "user@example",
        "user@.com",
        "user@invalid-.com",
        ".user@example.com",
        "user..dot@example.com",
    ]
    for email in invalid_emails:
        with pytest.raises(RegistrationError, match=r"Invalid email|Email .*cannot|Domain labels"):
            system.register_user(
                email=email,
                password="Valid!Pass123",
                username=f"user_{hash(email) & 0xffff}",
            )


def test_password_strength_rules(system):
    with pytest.raises(RegistrationError, match="at least 10 characters"):
        system.register_user(
            email="shortpass@example.com",
            password="S1mpl3!",
            username="shortpass",
        )

    with pytest.raises(RegistrationError, match="uppercase"):
        system.register_user(
            email="noupcase@example.com",
            password="lowercase1!",
            username="noupcase",
        )

    with pytest.raises(RegistrationError, match="lowercase"):
        system.register_user(
            email="nolowcase@example.com",
            password="UPPERCASE1!",
            username="nolowcase",
        )

    with pytest.raises(RegistrationError, match="digit"):
        system.register_user(
            email="nodigit@example.com",
            password="NoDigits!!",
            username="nodigit",
        )

    with pytest.raises(RegistrationError, match="special"):
        system.register_user(
            email="nospecial@example.com",
            password="ValidButNoSpecial1",
            username="nospecial",
        )


def test_password_length_upper_bound(system):
    long_password = "A!" + "a" * 130 + "1"
    with pytest.raises(RegistrationError, match="too long"):
        system.register_user(
            email="toolong@example.com",
            password=long_password,
            username="toolong",
        )


def test_registration_performance(system):
    start = time.perf_counter()
    for idx in range(200):
        system.register_user(
            email=f"user{idx}@example.com",
            password="StrongPass!123",
            username=f"user{idx}",
        )
    duration = time.perf_counter() - start
    # Ensure the registration loop is reasonably fast for in-memory operations.
    assert duration < 1.0, f"Registration performance degraded: {duration}s"
