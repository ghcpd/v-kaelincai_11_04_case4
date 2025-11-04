import re
from typing import Dict, List

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

class RegistrationError(Exception):
    pass

class RegistrationSystem:
    def __init__(self) -> None:
        self._users: List[Dict[str, str]] = []

    def _validate_email(self, email: str) -> None:
        if not isinstance(email, str) or not email:
            raise RegistrationError("Email is required")
        if len(email) > 254:
            raise RegistrationError("Email too long")
        if not EMAIL_REGEX.fullmatch(email):
            raise RegistrationError("Invalid email format")

    def _validate_password(self, password: str) -> None:
        if not isinstance(password, str) or not password:
            raise RegistrationError("Password is required")
        if len(password) < 8:
            raise RegistrationError("Password too short")
        if len(password) > 64:
            raise RegistrationError("Password too long")
        if ' ' in password:
            raise RegistrationError("Password cannot contain spaces")
        if not re.search(r'[A-Z]', password):
            raise RegistrationError("Password must contain uppercase")
        if not re.search(r'[a-z]', password):
            raise RegistrationError("Password must contain lowercase")
        if not re.search(r'[0-9]', password):
            raise RegistrationError("Password must contain digit")
        if not re.search(r'[!@#$%^&*()_+\-={}[\]|;:,.<>?]', password):
            raise RegistrationError("Password must contain special char")

    def _check_duplicate(self, email: str) -> None:
        for u in self._users:
            if u['email'].lower() == email.lower():
                raise RegistrationError("Duplicate email")

    def register(self, payload: Dict[str, str]) -> Dict[str, str]:
        email = payload.get('email', '')
        password = payload.get('password', '')
        try:
            self._validate_email(email)
            self._validate_password(password)
            self._check_duplicate(email)
        except RegistrationError as e:
            return {"ok": False, "message": str(e)}
        self._users.append({"email": email, "password": password})
        return {"ok": True, "message": "Registration successful"}

if __name__ == "__main__":
    import json, sys
    data = json.loads(sys.stdin.read())
    rs = RegistrationSystem()
    print(json.dumps(rs.register(data)))
