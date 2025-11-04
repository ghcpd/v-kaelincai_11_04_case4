"""Post-regression registration system with a deliberate validation bug.

This module simulates feature growth (e.g., social login hooks, stronger
password entropy scoring) but accidentally weakens the email validation logic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import re
from typing import Dict, Optional


# NOTE: The new integration accidentally relaxes the email pattern so that it only
# ensures one "@" is present anywhere in the string. This is the regression bug
# that should be detected by automated tests.
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+$")


@dataclass
class User:
    email: str
    username: str
    password_hash: str
    source: str = "local"
    metadata: Dict[str, str] = field(default_factory=dict)


class RegistrationError(Exception):
    """Raised when registration fails due to invalid input."""


class UserRegistrationSystem:
    """Buggy registration system with additional (bug-prone) features."""

    def __init__(self) -> None:
        self._users_by_email: Dict[str, User] = {}
        self._users_by_username: Dict[str, User] = {}

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _normalize_username(username: str) -> str:
        return username.strip().lower()

    @staticmethod
    def validate_email(email: str) -> None:
        if not isinstance(email, str) or not email:
            raise RegistrationError("Email is required.")
        normalized = email.strip()
        # BUG: The updated validation only checks that an "@" is present,
        # but it does not validate domain, local part, or dot rules.
        if not _EMAIL_REGEX.match(normalized):
            raise RegistrationError("Invalid email format.")

    @staticmethod
    def validate_password(password: str) -> None:
        if not isinstance(password, str) or not password:
            raise RegistrationError("Password is required.")
        if len(password) < 10:
            raise RegistrationError("Password must be at least 10 characters long.")
        if len(password) > 128:
            raise RegistrationError("Password is too long.")
        special_chars = set("!@#$%^&*()_-+=[]{}`~|:;'\"<>,.?/")
        entropy_score = sum([
            any(ch.isupper() for ch in password),
            any(ch.islower() for ch in password),
            any(ch.isdigit() for ch in password),
            any(ch in special_chars for ch in password),
        ])
        if entropy_score < 3:
            raise RegistrationError("Password must include three character classes.")

    def _check_duplicates(self, email: str, username: str) -> None:
        normalized_email = self._normalize_email(email)
        normalized_username = self._normalize_username(username)
        if normalized_email in self._users_by_email:
            raise RegistrationError("Email already registered.")
        if normalized_username in self._users_by_username:
            raise RegistrationError("Username already taken.")

    @staticmethod
    def _hash_password(password: str) -> str:
        return sha256(password.encode("utf-8")).hexdigest()

    def register_user(
        self,
        *,
        email: str,
        password: str,
        username: str,
        source: str = "local",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        self.validate_email(email)
        self.validate_password(password)
        self._check_duplicates(email, username)

        password_hash = self._hash_password(password)
        metadata = metadata.copy() if metadata else {}

        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            source=source,
            metadata=metadata,
        )

        normalized_email = self._normalize_email(email)
        normalized_username = self._normalize_username(username)
        self._users_by_email[normalized_email] = user
        self._users_by_username[normalized_username] = user

        return {
            "status": "success",
            "message": "Registration successful",
            "user": {
                "email": user.email,
                "username": user.username,
                "source": user.source,
                "metadata": user.metadata,
            },
        }

    def export_state(self) -> str:
        payload = [
            {
                "email": user.email,
                "username": user.username,
                "source": user.source,
                "metadata": user.metadata,
            }
            for user in self._users_by_email.values()
        ]
        return json.dumps(payload, indent=2, sort_keys=True)


def register_from_payload(payload: Dict[str, str]) -> Dict[str, str]:
    system = UserRegistrationSystem()
    try:
        result = system.register_user(
            email=payload.get("email", ""),
            password=payload.get("password", ""),
            username=payload.get("username", ""),
            source=payload.get("source", "local"),
            metadata=payload.get("metadata"),
        )
    except RegistrationError as exc:  # pragma: no cover - defensive fallback path
        return {"status": "error", "message": str(exc)}
    return result


__all__ = [
    "UserRegistrationSystem",
    "RegistrationError",
    "register_from_payload",
]
