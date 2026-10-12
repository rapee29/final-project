"""Cart items, completed orders and report value objects."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from coffee_pos.exceptions import ValidationError
from coffee_pos.models.options import MAX_QUANTITY, SIZE_OPTIONS, SWEETNESS_LEVELS
from coffee_pos.models.validators import require_int, require_number, require_text

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
GUEST_NAME = "Guest"


@dataclass
class CartItem:
    """One customised line in a cart / order."""

    drink_id: int
    name: str
    size: str
    milk: str
    sweetness: str
    qty: int
    unit_price: float

    def __post_init__(self) -> None:
        self.drink_id = require_int(self.drink_id, "Drink id", minimum=1)
        self.name = require_text(self.name, "Drink name")
        if self.size not in SIZE_OPTIONS:
            raise ValidationError("Size must be S, M or L.")
        self.milk = require_text(self.milk, "Milk")
        if self.sweetness not in SWEETNESS_LEVELS:
            raise ValidationError("Invalid sweetness level.")
        self.qty = require_int(self.qty, "Quantity", minimum=1, maximum=MAX_QUANTITY)
        self.unit_price = round(
            require_number(self.unit_price, "Unit price", minimum=0), 2)

    @property
    def total_price(self) -> float:
        return round(self.unit_price * self.qty, 2)

    def to_dict(self) -> dict:
        return {"drink_id": self.drink_id, "name": self.name, "size": self.size,
                "milk": self.milk, "sweetness": self.sweetness, "qty": self.qty,
                "unit_price": self.unit_price, "total_price": self.total_price}

    @classmethod
    def from_dict(cls, data: dict) -> "CartItem":
        return cls(data["drink_id"], data["name"], data["size"], data["milk"],
                   data["sweetness"], data["qty"], data["unit_price"])


@dataclass(frozen=True)
class Quote:
    """Price breakdown of a cart before payment."""

    subtotal: float
    discount: float
    total: float
    member_name: str = GUEST_NAME
    member_phone: Optional[str] = None


@dataclass
class Order:
    """A paid transaction. This is what gets saved in orders.json."""

    order_id: int
    timestamp: str
    items: List[CartItem]
    subtotal: float
    discount: float
    total: float
    cash_received: float
    change: float
    member_phone: Optional[str] = None
    member_name: str = GUEST_NAME

    def __post_init__(self) -> None:
        self.order_id = require_int(self.order_id, "Order id", minimum=1)
        try:
            datetime.strptime(self.timestamp, TIMESTAMP_FORMAT)
        except (TypeError, ValueError):
            raise ValidationError("Invalid order timestamp.") from None
        if not self.items:
            raise ValidationError("An order needs at least one item.")
        for name in ("subtotal", "discount", "total", "cash_received", "change"):
            setattr(self, name, round(
                require_number(getattr(self, name), name, minimum=0), 2))
        if self.member_phone is not None:
            self.member_phone = require_text(self.member_phone, "Member phone", 20)
        self.member_name = require_text(self.member_name, "Member name")

    @property
    def day(self) -> date:
        return datetime.strptime(self.timestamp, TIMESTAMP_FORMAT).date()

    @property
    def cups(self) -> int:
        return sum(item.qty for item in self.items)

    def to_dict(self) -> dict:
        return {"order_id": self.order_id, "timestamp": self.timestamp,
                "items": [i.to_dict() for i in self.items],
                "subtotal": self.subtotal, "discount": self.discount,
                "total": self.total, "cash_received": self.cash_received,
                "change": self.change, "member_phone": self.member_phone,
                "member_name": self.member_name}

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        items = [CartItem.from_dict(i) for i in data["items"]]
        return cls(data["order_id"], data["timestamp"], items, data["subtotal"],
                   data["discount"], data["total"], data["cash_received"],
                   data["change"], data.get("member_phone"),
                   data.get("member_name", GUEST_NAME))


@dataclass(frozen=True)
class DailySummary:
    """Aggregated sales for one calendar day."""

    day: date
    transactions: int
    cups: int
    revenue: float
    discounts: float
    top_drink: Optional[str] = None
    top_drink_cups: int = 0
