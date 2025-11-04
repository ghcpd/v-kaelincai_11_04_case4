"""Stable user registration module with robust validation logic."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


EMAIL_REGEX = re.compile(
    r"^(?=.{3,254}$)(?!.*\.\.)[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
)


class RegistrationError(Exception):
    """Base exception for registration failures."""


class ValidationError(RegistrationError):
    """Raised when input validation fails."""


class DuplicateUserError(RegistrationError):
    """Raised when attempting to register an existing user."""


@dataclass(frozen=True)
class User:
    email: str
    password_hash: str
    metadata: Dict[str, str] = field(default_factory=dict)


class InMemoryUserStore:
    """Simple in-memory user store providing duplicate checks."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def add_user(self, user: User) -> None:
        key = user.email.lower()
        if key in self._users:
            raise DuplicateUserError(f"User with email '{user.email}' already exists")
        self._users[key] = user

    def exists(self, email: str) -> bool:
        return email.lower() in self._users

    def list_users(self) -> Iterable[User]:
        return self._users.values()


class UserRegistrationService:
    """Service responsible for validating and registering users."""

    def __init__(self, store: Optional[InMemoryUserStore] = None) -> None:
        self.store = store or InMemoryUserStore()

    @staticmethod
    def _validate_email(email: str) -> None:
        if not isinstance(email, str) or not email:
            raise ValidationError("Email is required")
        if not EMAIL_REGEX.match(email):
            raise ValidationError("Invalid email format")

    @staticmethod
    def _validate_password(password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValidationError("Password is required")
        if len(password) < 10:
            raise ValidationError("Password must be at least 10 characters long")
        if len(password) > 128:
            raise ValidationError("Password exceeds maximum length of 128 characters")
        if " " in password:
            raise ValidationError("Password must not contain spaces")
        checks = {
            "uppercase": re.search(r"[A-Z]", password),
            "lowercase": re.search(r"[a-z]", password),
            "digit": re.search(r"\d", password),
            "symbol": re.search(r"[^A-Za-z0-9]", password),
        }
        missing = [name for name, passed in checks.items() if not passed]
        if missing:
            raise ValidationError(
                "Password missing required character types: " + ", ".join(missing)
            )

    def register_user(self, payload: Dict[str, str]) -> Dict[str, str]:
        if not isinstance(payload, dict):
            raise ValidationError("Payload must be a dictionary")
        email = payload.get("email", "")
        password = payload.get("password", "")
        metadata = payload.get("metadata", {})
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")

        self._validate_email(email)
        self._validate_password(password)
        if self.store.exists(email):
            raise DuplicateUserError(f"User with email '{email}' already exists")

        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        user = User(email=email, password_hash=password_hash, metadata=metadata)
        self.store.add_user(user)
        return {"status": "success", "message": "Registration successful"}


def register(payload: Dict[str, str], store: Optional[InMemoryUserStore] = None) -> Dict[str, str]:
    """Convenience function used by tests and scripts."""
    service = UserRegistrationService(store=store)
    return service.register_user(payload)


__all__ = [
    "DuplicateUserError",
    "InMemoryUserStore",
    "RegistrationError",
    "User",
    "UserRegistrationService",
    "ValidationError",
    "register",
]
