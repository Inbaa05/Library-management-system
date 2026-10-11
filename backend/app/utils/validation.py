"""Request validation utilities."""
import re
from typing import Any, Dict, List, Optional, Tuple


def validate_email(email: str) -> bool:
    """Check whether an email address is in a valid format."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Tuple[bool, str]:
    """Enforce password strength requirements. Returns (is_valid, reason)."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit'
    return True, ''


def validate_required_fields(data: Dict[str, Any], fields: List[str]) -> Optional[str]:
    """Return an error message if any required field is missing or empty."""
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"'{field}' is required and cannot be empty"
    return None


def sanitize_string(value: str, max_length: int = 10000) -> str:
    """Strip whitespace and truncate a string to a safe maximum length."""
    return str(value).strip()[:max_length]
