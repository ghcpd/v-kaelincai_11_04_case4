"""
User Registration System - Stable Implementation
Correct email validation, password requirements, and duplicate checking
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple

class UserDatabase:
    """Simple in-memory user database"""
    def __init__(self):
        self.users = {}
    
    def user_exists(self, email: str) -> bool:
        return email.lower() in self.users
    
    def add_user(self, email: str, password: str) -> None:
        self.users[email.lower()] = {
            'password': password,
            'registered_at': datetime.now().isoformat()
        }
    
    def get_user_count(self) -> int:
        return len(self.users)

class RegistrationSystem:
    """User registration system with proper validation"""
    
    def __init__(self):
        self.db = UserDatabase()
        # Correct email regex pattern
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email format - STABLE VERSION"""
        if not email:
            return False, "Email cannot be empty"
        
        # Correct validation logic
        if not self.email_pattern.match(email):
            return False, "Invalid email format"
        
        # Check for common invalid patterns
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return False, "Invalid email format"
        
        if '@@' in email:
            return False, "Invalid email format"
        
        return True, "Email is valid"
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password requirements"""
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password too long (max 128 characters)"
        
        # Check for at least one uppercase, lowercase, and digit
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    def register_user(self, email: str, password: str) -> Dict:
        """Register a new user with validation"""
        # Validate email
        email_valid, email_msg = self.validate_email(email)
        if not email_valid:
            return {
                'success': False,
                'message': email_msg,
                'user': None
            }
        
        # Check for duplicate
        if self.db.user_exists(email):
            return {
                'success': False,
                'message': "User already exists",
                'user': None
            }
        
        # Validate password
        password_valid, password_msg = self.validate_password(password)
        if not password_valid:
            return {
                'success': False,
                'message': password_msg,
                'user': None
            }
        
        # Register user
        self.db.add_user(email, password)
        
        return {
            'success': True,
            'message': "Registration successful",
            'user': email
        }

if __name__ == "__main__":
    # Example usage
    system = RegistrationSystem()
    
    test_cases = [
        ("user@example.com", "Password123"),
        ("invalid@@email.com", "Password123"),
        ("test@.com", "Password123"),
        ("valid.user@company.org", "SecurePass1"),
    ]
    
    for email, password in test_cases:
        result = system.register_user(email, password)
        print(f"Email: {email} - Success: {result['success']} - Message: {result['message']}")
