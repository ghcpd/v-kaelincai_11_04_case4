import json
from pathlib import Path

import pytest

from registration_stable import RegistrationError, UserRegistrationSystem, build_system


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
    assert payload["email"].lower() in system.list_registered_emails()


def test_invalid_email_rejected(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("double_at_email")
    with pytest.raises(RegistrationError):
        system.register_user(payload)


def test_password_policy_enforced(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("missing_symbol")
    with pytest.raises(RegistrationError) as exc:
        system.register_user(payload)
    assert "symbol" in str(exc.value)


def test_duplicate_email_blocked(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("valid_new_user")
    system.register_user(payload)
    with pytest.raises(RegistrationError):
        system.register_user(payload)


def test_boundary_email(system: UserRegistrationSystem) -> None:
    payload = load_test_payload("boundary_email")
    result = system.register_user(payload)
    assert result["status"] == "success"
    assert system.user_count() == 1
