"""
Input Validation Utilities — KisanSathi
Centralizes all input sanitisation and validation rules.

Author: Rustam Ali
"""

import re
from typing import Any


def sanitize_string(value: str, max_len: int = 256) -> str:
    """Strip leading/trailing whitespace and truncate to max_len."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_len]


def is_valid_email(email: str) -> bool:
    """Return True if email matches a basic RFC-5321 pattern."""
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, email or ""))


def is_valid_mobile(mobile: str) -> bool:
    """Return True for a 10-digit Indian mobile number."""
    return bool(re.match(r"^\d{10}$", str(mobile or "")))


def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Requirements: ≥8 chars, uppercase, lowercase, digit.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_soil_params(data: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate soil parameter ranges for ML models.
    Returns (is_valid, error_message).
    """
    ranges = {
        "N":           (0, 200),
        "P":           (0, 200),
        "K":           (0, 200),
        "temperature": (-10, 55),
        "humidity":    (0, 100),
        "ph":          (0, 14),
        "rainfall":    (0, 5000),
    }
    for field, (lo, hi) in ranges.items():
        if field not in data:
            return False, f"Missing required field: {field}"
        try:
            val = float(data[field])
        except (TypeError, ValueError):
            return False, f"Field '{field}' must be a number."
        if not (lo <= val <= hi):
            return False, f"Field '{field}' must be between {lo} and {hi}."
    return True, ""


def validate_location(location: str) -> bool:
    """Return True if location string is non-empty and not too long."""
    loc = sanitize_string(location, 128)
    return bool(loc) and len(loc) >= 2
