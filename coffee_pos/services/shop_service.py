"""Business Logic Layer: everything the shop can do, with no print()/input().

The UI calls these methods; this class talks to the repositories (Data Access
Layer). It never prints, so it can be unit-tested without a terminal.
"""

from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Union

from coffee_pos.data_access import JSONManager, JSONRepository
from coffee_pos.exceptions import (DuplicateError, EmptyCartError,
                                   InsufficientPaymentError, NotFoundError,
                                   ValidationError)
from coffee_pos.models import CartItem, DailySummary, Drink, Member, Order, Quote
from coffee_pos.models.member import normalize_phone
from coffee_pos.models.options import (MAX_QUANTITY, MILK_OPTIONS, SIZE_OPTIONS,
                                       SWEETNESS_LEVELS)
from coffee_pos.models.order import GUEST_NAME, TIMESTAMP_FORMAT
from coffee_pos.models.validators import require_int, require_number, require_text

DateLike = Union[str, date, None]

DRINK_SORT_KEYS = ("id", "name", "price")
ORDER_SORT_KEYS = ("id", "time", "total")


def _default_drinks() -> List[dict]:
    seed = [("Espresso", 55), ("Americano", 60), ("Latte", 70),
            ("Cappuccino", 70), ("Mocha", 75), ("Matcha Latte", 80)]
    return [Drink(i, name, price).to_dict() for i, (name, price) in enumerate(seed, 1)]


def _default_members() -> List[dict]:
    return [Member("0812345678", "Somchai").to_dict(),
            Member("0898765432", "Somsri").to_dict()]


def parse_date(value: DateLike, field: str = "Date") -> Optional[date]:
    """Accept ``None``, a ``date`` or a ``YYYY-MM-DD`` string."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(f"{field} must be in YYYY-MM-DD format.") from None


def _check_range(low, high, label: str) -> None:
    if low is not None and high is not None and low > high:
        raise ValidationError(f"Minimum {label} cannot be greater than maximum.")


class ShopService:
    def __init__(self, drinks: JSONRepository, members: JSONRepository,
                 orders: JSONRepository,
                 clock: Callable[[], datetime] = datetime.now) -> None:
        self._drinks = drinks
        self._members = members
        self._orders = orders
        self._clock = clock

    @property
    def notices(self) -> List[str]:
        """Recovery messages produced while loading the data files."""
        return self._drinks.notices + self._members.notices + self._orders.notices

    # ================================================================ drinks
    def list_drinks(self) -> List[Drink]:
        return self.sort_drinks(self._drinks.all(), "id")

    def get_drink(self, drink_id: int) -> Drink:
        return self._drinks.get(drink_id)

    def add_drink(self, name: str, price) -> Drink:
        name = require_text(name, "Drink name")
        self._ensure_unique_name(name)
        next_id = max((d.drink_id for d in self._drinks.all()), default=0) + 1
        return self._drinks.add(Drink(next_id, name, price))

    def update_drink(self, drink_id: int, name: Optional[str] = None,
                     price=None) -> Drink:
        current = self.get_drink(drink_id)
        new_name = current.name if name is None else require_text(name, "Drink name")
        if new_name.casefold() != current.name.casefold():
            self._ensure_unique_name(new_name)
        new_price = current.price if price is None else price
        return self._drinks.update(Drink(drink_id, new_name, new_price))

    def remove_drink(self, drink_id: int) -> Drink:
        return self._drinks.delete(drink_id)

    def search_drinks(self, keyword: str) -> List[Drink]:
        """Case-insensitive substring search on the drink name."""
        keyword = require_text(keyword, "Search keyword").casefold()
        return [d for d in self.list_drinks() if keyword in d.name.casefold()]

    def filter_drinks(self, min_price=None, max_price=None) -> List[Drink]:
        """Drinks whose base price is within [min_price, max_price]."""
        if min_price is not None:
            min_price = require_number(min_price, "Minimum price", minimum=0)
        if max_price is not None:
            max_price = require_number(max_price, "Maximum price", minimum=0)
        _check_range(min_price, max_price, "price")
        return [d for d in self.list_drinks()
                if (min_price is None or d.price >= min_price)
                and (max_price is None or d.price <= max_price)]

    def sort_drinks(self, drinks: Optional[Iterable[Drink]] = None,
                    by: str = "name", descending: bool = False) -> List[Drink]:
        if by not in DRINK_SORT_KEYS:
            raise ValidationError(f"Sort key must be one of: {', '.join(DRINK_SORT_KEYS)}.")
        source = self._drinks.all() if drinks is None else list(drinks)
        keys = {"id": lambda d: d.drink_id,
                "name": lambda d: (d.name.casefold(), d.drink_id),
                "price": lambda d: (d.price, d.name.casefold())}
        return sorted(source, key=keys[by], reverse=descending)

    def _ensure_unique_name(self, name: str) -> None:
        if any(d.name.casefold() == name.casefold() for d in self._drinks.all()):
            raise DuplicateError("Drink", name)

    # =============================================================== members
    def list_members(self) -> List[Member]:
        return sorted(self._members.all(), key=lambda m: (m.name.casefold(), m.phone))

    def get_member(self, phone: str) -> Member:
        return self._members.get(str(phone).strip())

    def add_member(self, phone: str, name: str, discount_rate: float = 0.10) -> Member:
        return self._members.add(Member(phone, name, discount_rate))

    def update_member(self, phone: str, name: Optional[str] = None,
                      discount_rate: Optional[float] = None) -> Member:
        current = self.get_member(phone)
        return self._members.update(Member(
            current.phone,
            current.name if name is None else name,
            current.discount_rate if discount_rate is None else discount_rate))

    def remove_member(self, phone: str) -> Member:
        return self._members.delete(str(phone).strip())

    def search_members(self, keyword: str) -> List[Member]:
        """Case-insensitive search on name or phone number."""
        keyword = require_text(keyword, "Search keyword").casefold()
        return [m for m in self.list_members()
                if keyword in m.name.casefold() or keyword in m.phone]

    # ================================================================ orders
    def build_cart_item(self, drink_id: int, size: str, milk_id: int,
                        sweetness: str, qty: int) -> CartItem:
        """Validate the choices and price one customised line."""
        drink = self.get_drink(drink_id)
        size = str(size).strip().upper()
        if size not in SIZE_OPTIONS:
            raise ValidationError("Size must be S, M or L.")
        if milk_id not in MILK_OPTIONS:
            raise ValidationError("Milk option must be 1, 2 or 3.")
        if sweetness not in SWEETNESS_LEVELS:
            raise ValidationError("Invalid sweetness level.")
        qty = require_int(qty, "Quantity", minimum=1, maximum=MAX_QUANTITY)
        unit_price = (drink.price + SIZE_OPTIONS[size]["extra"]
                      + MILK_OPTIONS[milk_id]["extra"])
        return CartItem(drink.drink_id, drink.name, size,
                        MILK_OPTIONS[milk_id]["label"], sweetness, qty, unit_price)

    def price_cart(self, cart: List[CartItem],
                   member_phone: Optional[str] = None) -> Quote:
        """Compute subtotal, member discount and total (no side effects)."""
        if not cart:
            raise EmptyCartError()
        subtotal = round(sum(item.total_price for item in cart), 2)
        discount, name, phone = 0.0, GUEST_NAME, None
        if member_phone:
            member = self.get_member(member_phone)  # NotFoundError if unknown
            discount = member.discount_for(subtotal)
            name, phone = member.name, member.phone
        return Quote(subtotal, discount, round(subtotal - discount, 2), name, phone)

    def checkout(self, cart: List[CartItem], cash_received,
                 member_phone: Optional[str] = None) -> Order:
        """Take payment, save the order and return it (with change)."""
        quote = self.price_cart(cart, member_phone)
        cash = require_number(cash_received, "Cash received", minimum=0)
        if cash < quote.total:
            raise InsufficientPaymentError(round(quote.total - cash, 2))
        order = Order(
            order_id=max((o.order_id for o in self._orders.all()), default=0) + 1,
            timestamp=self._clock().strftime(TIMESTAMP_FORMAT),
            items=list(cart), subtotal=quote.subtotal, discount=quote.discount,
            total=quote.total, cash_received=cash,
            change=round(cash - quote.total, 2),
            member_phone=quote.member_phone, member_name=quote.member_name)
        return self._orders.add(order)

    def list_orders(self) -> List[Order]:
        return self.sort_orders(self._orders.all(), "id", descending=False)

    def get_order(self, order_id: int) -> Order:
        return self._orders.get(order_id)

    def filter_orders(self, date_from: DateLike = None, date_to: DateLike = None,
                      min_total=None, max_total=None,
                      member_phone: Optional[str] = None) -> List[Order]:
        """Combine any of: date range, total range, member phone."""
        start = parse_date(date_from, "Start date")
        end = parse_date(date_to, "End date")
        _check_range(start, end, "date")
        if min_total is not None:
            min_total = require_number(min_total, "Minimum total", minimum=0)
        if max_total is not None:
            max_total = require_number(max_total, "Maximum total", minimum=0)
        _check_range(min_total, max_total, "total")
        phone = normalize_phone(member_phone) if member_phone else None
        return [o for o in self.list_orders()
                if (start is None or o.day >= start)
                and (end is None or o.day <= end)
                and (min_total is None or o.total >= min_total)
                and (max_total is None or o.total <= max_total)
                and (phone is None or o.member_phone == phone)]

    def sort_orders(self, orders: Optional[Iterable[Order]] = None,
                    by: str = "time", descending: bool = True) -> List[Order]:
        if by not in ORDER_SORT_KEYS:
            raise ValidationError(f"Sort key must be one of: {', '.join(ORDER_SORT_KEYS)}.")
        source = self._orders.all() if orders is None else list(orders)
        keys = {"id": lambda o: o.order_id,
                "time": lambda o: (o.timestamp, o.order_id),
                "total": lambda o: (o.total, o.order_id)}
        return sorted(source, key=keys[by], reverse=descending)

    def daily_summary(self, day: DateLike = None) -> DailySummary:
        target = parse_date(day) or self._clock().date()
        orders = [o for o in self._orders.all() if o.day == target]
        by_drink = Counter()
        for order in orders:
            for item in order.items:
                by_drink[item.name] += item.qty
        top = min(by_drink.items(), key=lambda kv: (-kv[1], kv[0])) if by_drink else None
        return DailySummary(
            day=target, transactions=len(orders),
            cups=sum(o.cups for o in orders),
            revenue=round(sum(o.total for o in orders), 2),
            discounts=round(sum(o.discount for o in orders), 2),
            top_drink=top[0] if top else None,
            top_drink_cups=top[1] if top else 0)


def build_service(data_dir=None,
                  clock: Callable[[], datetime] = datetime.now) -> ShopService:
    """Wire the three layers together using JSON files in ``data_dir``."""
    folder = Path(data_dir) if data_dir else Path(__file__).resolve().parents[2] / "data"
    drinks = JSONRepository(JSONManager(folder / "menu.json", _default_drinks),
                            Drink, "drink_id", "Drink")
    members = JSONRepository(JSONManager(folder / "members.json", _default_members),
                             Member, "phone", "Member")
    orders = JSONRepository(JSONManager(folder / "orders.json", list),
                            Order, "order_id", "Order")
    return ShopService(drinks, members, orders, clock)
