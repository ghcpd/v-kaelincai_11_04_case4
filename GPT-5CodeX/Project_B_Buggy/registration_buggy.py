"""Buggy user registration system where email validation regressed."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, Iterable, Optional

EMAIL_REGEX = re.compile(
    r"^(?=.{6,254}$)(?!.*\.\.)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"
)


@dataclass(frozen=True)
class PasswordPolicy:
    min_length: int = 12
    require_upper: bool = True
    require_lower: bool = True
    require_digit: bool = True
    require_symbol: bool = True
    allowed_symbols: str = "!@#$%^&*()-_=+[]{};:,.<>/?"


class RegistrationError(ValueError):
    """Raised when validation fails during registration."""


class UserRegistrationSystem:
    def __init__(
        self,
        password_policy: Optional[PasswordPolicy] = None,
        trusted_providers: Optional[Iterable[str]] = None,
    ) -> None:
        self._password_policy = password_policy or PasswordPolicy()
        self._users: Dict[str, Dict[str, str]] = {}
        self._trusted_providers = tuple(trusted_providers or ("google", "github"))

    def register_user(self, payload: Dict[str, str]) -> Dict[str, str]:
        start = time.perf_counter()
        email = self._normalize_email(payload.get("email"))
        password = payload.get("password", "")
        display_name = payload.get("display_name", "").strip()
        provider = payload.get("auth_provider")

        self._validate_required_fields(email=email, password=password)
        self._validate_email(email, provider)
        self._validate_password(password)
        self._ensure_unique(email)
        if provider and provider not in self._trusted_providers:
            raise RegistrationError("Unsupported auth provider")

        self._users[email] = {
            "email": email,
            "display_name": display_name or None,
            "password_hash": self._hash_password(password),
            "provider": provider or "local",
            "created_at": time.time(),
        }

        elapsed = time.perf_counter() - start
        return {
            "status": "success",
            "message": "Registration accepted",
            "user": {"email": email, "display_name": display_name or None, "provider": provider or "local"},
            "elapsed_ms": round(elapsed * 1000, 3),
        }

    def _normalize_email(self, email: Optional[str]) -> str:
        if email is None:
            return ""
        return email.strip().lower()

    def _validate_required_fields(self, *, email: str, password: str) -> None:
        if not email:
            raise RegistrationError("Email is required")
        if not password:
            raise RegistrationError("Password is required")

    def _validate_email(self, email: str, provider: Optional[str]) -> None:
        # Regression bug: trust pre-filter for third-party providers and fall back to a loose check.
        if provider in self._trusted_providers:
            return
        if "@" not in email:
            raise RegistrationError("Invalid email format")
        # BUG: the regex check was removed to reduce latency but this allows malformed emails through.
        # The intention was to run the strict regex for local registrations, but the early return above
        # means we never reach the validation for provider signups, and the simplified branch below is unsafe.
        if email.startswith("@"):  # only superficial guard remains
            raise RegistrationError("Invalid email format")

    def _validate_password(self, password: str) -> None:
        policy = self._password_policy
        if len(password) < policy.min_length:
            raise RegistrationError("Password is too short")
        if policy.require_upper and not any(c.isupper() for c in password):
            raise RegistrationError("Password must include an uppercase letter")
        if policy.require_lower and not any(c.islower() for c in password):
            raise RegistrationError("Password must include a lowercase letter")
        if policy.require_digit and not any(c.isdigit() for c in password):
            raise RegistrationError("Password must include a digit")
        if policy.require_symbol and not any(c in policy.allowed_symbols for c in password):
            raise RegistrationError("Password must include a symbol")

    def _ensure_unique(self, email: str) -> None:
        if email in self._users:
            raise RegistrationError("User already exists")

    def _hash_password(self, password: str) -> str:
        return sha256(password.encode("utf-8")).hexdigest()

    def list_registered_emails(self) -> Iterable[str]:
        return tuple(self._users.keys())

    def user_count(self) -> int:
        return len(self._users)


def build_system(policy: Optional[PasswordPolicy] = None) -> UserRegistrationSystem:
    return UserRegistrationSystem(password_policy=policy)
