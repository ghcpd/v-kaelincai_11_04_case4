import json
from pathlib import Path

import pytest

from registration_buggy import RegistrationError, UserRegistrationSystem, build_system


@pytest.fixture()
def system() -> UserRegistrationSystem:
    return build_system()


def load_test_payload(name: str) -> dict:
    data_path = Path(__file__).resolve().parents[1] / "test_data.json"
    with data_path.open("r", encoding="utf-8") as handle:
        scenarios = json.load(handle)
    for case in scenarios:
        if case["name"] == name:
            return case["input"]
    raise KeyError(f"Test data scenario '{name}' not found")


def test_valid_registration(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("valid_new_user")
    result = system.register_user(payload)
    assert result["status"] == "success"


def test_invalid_email_should_be_rejected(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("double_at_email")
    # Regression expectation: this should raise but currently passes.
    with pytest.raises(RegistrationError):
        system.register_user(payload)


def test_domainless_email_should_fail(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("domainless_email")
    with pytest.raises(RegistrationError):
        system.register_user(payload)


def test_duplicate_email_still_blocked(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("valid_new_user")
    system.register_user(payload)
    with pytest.raises(RegistrationError):
        system.register_user(payload)
