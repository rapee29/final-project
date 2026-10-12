"""Member domain model (customer with a phone-number membership)."""

from dataclasses import dataclass

from coffee_pos.exceptions import ValidationError
from coffee_pos.models.validators import require_number, require_text


def normalize_phone(value) -> str:
    """Return a phone number made of 9-10 digits, or raise ValidationError."""
    phone = require_text(value, "Phone number", max_len=20)
    if not phone.isdigit() or not 9 <= len(phone) <= 10:
        raise ValidationError("Phone number must be 9-10 digits.")
    return phone


@dataclass
class Member:
    """A member identified by phone number who receives a percentage discount."""

    phone: str
    name: str
    discount_rate: float = 0.10

    def __post_init__(self) -> None:
        self.phone = normalize_phone(self.phone)
        self.name = require_text(self.name, "Member name")
        self.discount_rate = require_number(
            self.discount_rate, "Discount rate", minimum=0, maximum=1)

    def discount_for(self, subtotal: float) -> float:
        """Return the discount in baht for a given subtotal."""
        return round(subtotal * self.discount_rate, 2)

    def to_dict(self) -> dict:
        return {"phone": self.phone, "name": self.name,
                "discount_rate": self.discount_rate}

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        return cls(data["phone"], data["name"], data["discount_rate"])
