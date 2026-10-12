"""Drink domain model (one item on the menu)."""

from dataclasses import dataclass

from coffee_pos.models.validators import require_int, require_number, require_text


@dataclass
class Drink:
    """A menu item with a unique id, a name and a base price in baht."""

    drink_id: int
    name: str
    price: float

    def __post_init__(self) -> None:
        self.drink_id = require_int(self.drink_id, "Drink id", minimum=1)
        self.name = require_text(self.name, "Drink name")
        self.price = round(
            require_number(self.price, "Price", minimum=0, maximum=100_000,
                           exclusive_min=True), 2)

    def to_dict(self) -> dict:
        return {"drink_id": self.drink_id, "name": self.name, "price": self.price}

    @classmethod
    def from_dict(cls, data: dict) -> "Drink":
        return cls(data["drink_id"], data["name"], data["price"])
