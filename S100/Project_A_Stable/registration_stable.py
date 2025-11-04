"""Stable user registration system with robust validation.

This module implements the baseline registration logic that ensures:
- Proper email validation using a strict regular expression.
- Password strength checks (length, uppercase, lowercase, digit, special character).
- Duplicate user detection based on email and username (case-insensitive).
- Structured response objects to allow comparison across implementations.

The implementation avoids external services and focuses on deterministic behavior
for the purpose of regression testing experiments.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import re
from typing import Dict, Optional


_EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


@dataclass
class User:
    email: str
    username: str
    password_hash: str
    metadata: Dict[str, str] = field(default_factory=dict)


class RegistrationError(Exception):
    """Raised when registration fails due to invalid input."""


class UserRegistrationSystem:
    """Stable registration system with comprehensive validation."""

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
        if not _EMAIL_REGEX.fullmatch(normalized):
            raise RegistrationError("Invalid email format.")
        if ".." in normalized:
            raise RegistrationError("Email cannot contain consecutive dots.")
        local_part, domain_part = normalized.split("@", 1)
        if local_part.startswith(".") or local_part.endswith("."):
            raise RegistrationError("Email local part cannot start or end with dot.")
        if domain_part.startswith("-") or domain_part.endswith("-"):
            raise RegistrationError("Domain part cannot start or end with hyphen.")
        domain_labels = domain_part.split(".")
        if any(label == "" for label in domain_labels):
            raise RegistrationError("Domain labels cannot be empty.")
        for label in domain_labels:
            if label.startswith("-") or label.endswith("-"):
                raise RegistrationError("Domain labels cannot start or end with hyphen.")

    @staticmethod
    def validate_password(password: str) -> None:
        if not isinstance(password, str) or not password:
            raise RegistrationError("Password is required.")
        if len(password) < 10:
            raise RegistrationError("Password must be at least 10 characters long.")
        if len(password) > 128:
            raise RegistrationError("Password is too long.")
        checks = {
            "uppercase": any(ch.isupper() for ch in password),
            "lowercase": any(ch.islower() for ch in password),
            "digit": any(ch.isdigit() for ch in password),
            "special": any(ch in "!@#$%^&*()_-+=[]{}`~|:;\'\"<>,.?/" for ch in password),
        }
        for key, passed in checks.items():
            if not passed:
                raise RegistrationError(
                    f"Password must contain at least one {key} character."
                )

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
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Register a user after validating inputs.

        Returns a structured dictionary describing the registration outcome.
        """

        self.validate_email(email)
        self.validate_password(password)
        self._check_duplicates(email, username)

        password_hash = self._hash_password(password)
        metadata = metadata.copy() if metadata else {}
        user = User(email=email, username=username, password_hash=password_hash, metadata=metadata)

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
                "metadata": user.metadata,
            },
        }

    def export_state(self) -> str:
        """Serialize current users for reproducibility checks."""
        payload = [
            {
                "email": user.email,
                "username": user.username,
                "metadata": user.metadata,
            }
            for user in self._users_by_email.values()
        ]
        return json.dumps(payload, indent=2, sort_keys=True)


def register_from_payload(payload: Dict[str, str]) -> Dict[str, str]:
    """Convenience function for JSON-like registration payloads."""
    system = UserRegistrationSystem()
    try:
        result = system.register_user(
            email=payload.get("email", ""),
            password=payload.get("password", ""),
            username=payload.get("username", ""),
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
