"""Small reusable validators used by the domain models."""

import math

from coffee_pos.exceptions import ValidationError


def require_text(value, field: str, max_len: int = 60) -> str:
    """Return ``value`` stripped; reject non-strings, blanks and over-long text."""
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be text.")
    text = value.strip()
    if not text:
        raise ValidationError(f"{field} cannot be blank.")
    if len(text) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} characters.")
    return text


def require_int(value, field: str, minimum=None, maximum=None) -> int:
    """Return ``value`` if it is a real int (bool is rejected) within range."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field} must be a whole number.")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{field} must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ValidationError(f"{field} must be at most {maximum}.")
    return value


def require_number(value, field: str, minimum=None, maximum=None,
                   exclusive_min: bool = False) -> float:
    """Return ``value`` as float; reject bool, NaN, infinity and out-of-range."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field} must be a number.")
    number = float(value)
    if not math.isfinite(number):
        raise ValidationError(f"{field} must be a finite number.")
    if minimum is not None:
        if number < minimum or (exclusive_min and number == minimum):
            op = "greater than" if exclusive_min else "at least"
            raise ValidationError(f"{field} must be {op} {minimum}.")
    if maximum is not None and number > maximum:
        raise ValidationError(f"{field} must be at most {maximum}.")
    return number
