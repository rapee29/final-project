"""Presentation Layer: the terminal interface (menus, prompts, printing).

This file only talks to the user and calls ``ShopService``. No pricing,
searching or file logic lives here. ``input_fn`` / ``output_fn`` can be
replaced so the whole UI can be tested with scripted input.
"""

from typing import Callable, List, Optional

from coffee_pos.exceptions import (CoffeePOSError, DataFileError,
                                   InsufficientPaymentError, NotFoundError,
                                   ValidationError)
from coffee_pos.models import CartItem, Drink, Member, Order
from coffee_pos.models.member import normalize_phone
from coffee_pos.models.options import (MAX_QUANTITY, MILK_OPTIONS, SIZE_OPTIONS,
                                       SWEETNESS_LEVELS)
from coffee_pos.models.validators import require_number
from coffee_pos.services import ShopService
from coffee_pos.services.sales_advisor import make_sales_advice

WIDTH = 45
CANCEL_WORD = "cancel"


class _Cancelled(Exception):
    """Raised when the user types 'cancel' at any prompt."""


class CoffeeCLI:
    def __init__(self, service: ShopService, input_fn: Callable[[str], str] = input,
                 output_fn: Callable[[str], None] = print) -> None:
        self.service = service
        self._input = input_fn
        self._print = output_fn

    # ============================================================ input helpers
    def _ask(self, prompt: str, allow_blank: bool = False) -> str:
        """Read a line. 'cancel' aborts the current action."""
        while True:
            text = self._input(prompt).strip()
            if text.lower() == CANCEL_WORD:
                raise _Cancelled()
            if text or allow_blank:
                return text
            self._print(" ⚠ Input cannot be empty.")

    def _ask_int(self, prompt: str, low: int, high: Optional[int] = None,
                 allow_blank: bool = False) -> Optional[int]:
        while True:
            text = self._ask(prompt, allow_blank)
            if text == "" and allow_blank:
                return None
            try:
                value = int(text)
            except ValueError:
                self._print(" ⚠ Please enter a whole number.")
                continue
            if value < low or (high is not None and value > high):
                limit = f"{low}-{high}" if high is not None else f"{low} or more"
                self._print(f" ⚠ Please enter a number {limit}.")
                continue
            return value

    def _ask_money(self, prompt: str, allow_blank: bool = False) -> Optional[float]:
        while True:
            text = self._ask(prompt, allow_blank)
            if text == "" and allow_blank:
                return None
            try:
                return float(text)
            except ValueError:
                self._print(" ⚠ Invalid amount.")

    def _ask_validated(self, ask: Callable[[], object], validate: Callable):
        """Keep asking the same question until ``validate`` accepts the answer."""
        while True:
            try:
                return validate(ask())
            except ValidationError as exc:
                self._print(f" ⚠ {exc}")

    def _ask_yes_no(self, prompt: str) -> bool:
        return self._ask(prompt + " (y/n): ", allow_blank=True).lower() == "y"

    def _line(self, char: str = "=") -> None:
        self._print(char * WIDTH)

    def _title(self, text: str, char: str = "=") -> None:
        self._print("\n" + char * WIDTH)
        self._print(text.center(WIDTH).rstrip())
        self._line(char)

    # ================================================================ main loop
    def run(self) -> None:
        for notice in self.service.notices:
            self._print(f" ℹ {notice}")
        actions = {"1": self.new_order, "2": self.show_daily_summary,
                   "3": self.manage_menu, "4": self.manage_members,
                   "5": self.show_order_history}
        while True:
            self._title("☕ SMART POS COFFEE TERMINAL SYSTEM ☕", "═")
            self._print("  [1] New Order (เปิดการสั่งซื้อใหม่)")
            self._print("  [2] Daily Sales Summary (สรุปยอดขายประจำวัน)")
            self._print("  [3] Manage Menu (จัดการเมนู)")
            self._print("  [4] Manage Members (จัดการสมาชิก)")
            self._print("  [5] Order History (ประวัติการขาย)")
            self._print("  [0] Exit System (ออกจากระบบ)")
            self._line("═")
            try:
                choice = self._input("Select option (0-5): ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if choice == "0":
                break
            action = actions.get(choice)
            if action is None:
                self._print(" ⚠ Invalid option. Please select 0-5.")
                continue
            try:
                self._safely(action)
            except (EOFError, KeyboardInterrupt):
                break  # input closed / Ctrl+C in the middle of an action
        self._print("\n Exiting POS System. Have a great day!")

    def _safely(self, action: Callable[[], None]) -> None:
        """Run a menu action; one bad input must never crash the program."""
        try:
            action()
        except _Cancelled:
            self._print(" ↩ Cancelled. Returning to menu.")
        except CoffeePOSError as exc:
            self._print(f" ⚠ {exc}")
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as exc:  # last-resort guard so the POS stays open
            self._print(f" ⚠ Unexpected error ({type(exc).__name__}): {exc}")

    # ================================================================ new order
    def new_order(self) -> None:
        cart: List[CartItem] = []
        while True:
            self._show_menu()
            drink_id = self._ask_int(
                "\nSelect item number (0 to finish ordering): ", 0)
            if drink_id == 0:
                break
            try:
                self.service.get_drink(drink_id)
            except NotFoundError:
                self._print(" ⚠ Invalid item selection.")
                continue
            cart.append(self._build_item(drink_id))
            if not self._ask_yes_no("\nAdd more items?"):
                break
        if not cart:
            self._print("Cart is empty. Returning to main menu.")
            return
        self._checkout(cart)

    def _build_item(self, drink_id: int) -> CartItem:
        self._print("\n--- Select Size ---")
        for code, info in SIZE_OPTIONS.items():
            self._print(f"  [{code}] {info['label']} (+฿{info['extra']})")
        while True:
            size = self._ask("Choose size (S/M/L): ").upper()
            if size in SIZE_OPTIONS:
                break
            self._print(" ⚠ Invalid size. Please choose S, M, or L.")

        self._print("\n--- Select Milk ---")
        for key, info in MILK_OPTIONS.items():
            self._print(f"  [{key}] {info['label']} (+฿{info['extra']})")
        milk_id = self._ask_int(f"Choose milk option (1-{len(MILK_OPTIONS)}): ",
                                1, len(MILK_OPTIONS))

        self._print("\n--- Select Sweetness Level ---")
        for idx, level in enumerate(SWEETNESS_LEVELS, 1):
            self._print(f"  [{idx}] {level}")
        sweet_idx = self._ask_int(f"Choose sweetness (1-{len(SWEETNESS_LEVELS)}): ",
                                  1, len(SWEETNESS_LEVELS))

        qty = self._ask_int(f"\nEnter quantity (1-{MAX_QUANTITY}): ", 1, MAX_QUANTITY)
        item = self.service.build_cart_item(
            drink_id, size, milk_id, SWEETNESS_LEVELS[sweet_idx - 1], qty)
        self._print(f"\n Added {item.qty}x {item.name} ({item.size}) to cart!")
        return item

    def _checkout(self, cart: List[CartItem]) -> None:
        phone = None
        if self._ask_yes_no("\nIs customer a member?"):
            candidate = self._ask("Enter member phone number: ")
            try:
                self.service.get_member(candidate)
                phone = candidate
            except NotFoundError:
                self._print(" Member phone number not found. Proceeding as Guest.")
        quote = self.service.price_cart(cart, phone)

        self._title("🛒 ORDER SUMMARY")
        for idx, item in enumerate(cart, 1):
            self._print(f"{idx}. {item.name} ({item.size}, {item.milk}, "
                        f"Sweet {item.sweetness})")
            self._print(f"   {item.qty} x ฿{item.unit_price:.2f} = ฿{item.total_price:.2f}")
        self._line("-")
        self._print(f"Subtotal: ฿{quote.subtotal:.2f}")
        if phone:
            self._print(f" Member found: Welcome {quote.member_name}! "
                        f"Discount: -฿{quote.discount:.2f}")
        self._print(f"Grand Total: ฿{quote.total:.2f}")
        self._line()

        while True:
            cash = self._ask_money("\nEnter cash received: ฿")
            try:
                order = self.service.checkout(cart, cash, phone)
                break
            except (InsufficientPaymentError, ValidationError) as exc:
                self._print(f" ⚠ {exc}")
            except DataFileError as exc:
                self._print(f" ⚠ Order NOT saved: {exc}")
                self._print("   Please check the data folder and try again.")
                return
        self._print_receipt(order)

    def _print_receipt(self, order: Order) -> None:
        self._print("\n" + "*" * WIDTH)
        self._print("           ☕ GROUP15 EXPRESS COFFEE ☕")
        self._print("             OFFICIAL RECEIPT")
        self._line("*")
        self._print(f"Order No.  : #{order.order_id:04d}")
        self._print(f"Date/Time  : {order.timestamp}")
        self._print(f"Customer   : {order.member_name}")
        self._line("-")
        for item in order.items:
            self._print(f"{item.qty}x {item.name:<15} [{item.size}] ฿{item.total_price:>8.2f}")
            self._print(f"   ({item.milk}, {item.sweetness})")
        self._line("-")
        self._print(f"Subtotal     : ฿{order.subtotal:>8.2f}")
        self._print(f"Discount     : -฿{order.discount:>7.2f}")
        self._print(f"Grand Total  : ฿{order.total:>8.2f}")
        self._print(f"Cash Received: ฿{order.cash_received:>8.2f}")
        self._print(f"Change       : ฿{order.change:>8.2f}")
        self._line("*")
        self._print("       Thank you for your order! ")
        self._line("*")

    # ============================================================ daily summary
    def show_daily_summary(self) -> None:
        text = self._ask("Date YYYY-MM-DD (blank = today): ", allow_blank=True)
        summary = self.service.daily_summary(text or None)
        self._title(f"DAILY SALES SUMMARY REPORT ({summary.day})")
        if summary.transactions == 0:
            self._print("No transactions recorded for this day.")
            self._line()
            return
        self._print(f"Total Transactions : {summary.transactions}")
        self._print(f"Total Drinks Sold  : {summary.cups} cups")
        self._print(f"Total Discounts    : ฿{summary.discounts:.2f}")
        self._print(f"Total Revenue      : ฿{summary.revenue:.2f}")
        self._print(f"Best Seller        : {summary.top_drink} ({summary.top_drink_cups} cups)")
        self._print(f"Sales Advisor      : {make_sales_advice(summary)}")
        self._line()

    # ================================================================ menu admin
    def _show_menu(self, drinks: Optional[List[Drink]] = None) -> None:
        drinks = self.service.list_drinks() if drinks is None else drinks
        self._title("☕ COFFEE SHOP MENU ☕")
        if not drinks:
            self._print("  (no drinks)")
        for drink in drinks:
            self._print(f"  [{drink.drink_id}] {drink.name:<20} ฿{drink.price:.2f}")
        self._line()

    def manage_menu(self) -> None:
        while True:
            self._title("MANAGE MENU (จัดการเมนู)", "-")
            self._print("  [1] List  [2] Add  [3] Edit  [4] Delete")
            self._print("  [5] Search by name  [6] Filter by price  [7] Sort")
            self._print("  [0] Back   (type 'cancel' to abort an action)")
            choice = self._input("Select option (0-7): ").strip()
            if choice == "0":
                return
            actions = {"1": self._menu_list, "2": self._menu_add, "3": self._menu_edit,
                       "4": self._menu_delete, "5": self._menu_search,
                       "6": self._menu_filter, "7": self._menu_sort}
            action = actions.get(choice)
            if action is None:
                self._print(" ⚠ Invalid option. Please select 0-7.")
                continue
            self._safely(action)

    def _menu_list(self) -> None:
        self._show_menu()

    def _menu_add(self) -> None:
        name = self._ask("Drink name: ")
        price = self._ask_validated(
            lambda: self._ask_money("Base price (฿): "),
            lambda v: require_number(v, "Price", minimum=0, exclusive_min=True))
        drink = self.service.add_drink(name, price)
        self._print(f" ✔ Added [{drink.drink_id}] {drink.name} ฿{drink.price:.2f}")

    def _menu_edit(self) -> None:
        self._show_menu()
        drink = self.service.get_drink(self._ask_int("Drink number to edit: ", 1))
        name = self._ask(f"New name (blank = keep '{drink.name}'): ", allow_blank=True)
        price = self._ask_money(f"New price (blank = keep ฿{drink.price:.2f}): ",
                                allow_blank=True)
        updated = self.service.update_drink(drink.drink_id, name or None, price)
        self._print(f" ✔ Updated [{updated.drink_id}] {updated.name} ฿{updated.price:.2f}")

    def _menu_delete(self) -> None:
        self._show_menu()
        drink = self.service.get_drink(self._ask_int("Drink number to delete: ", 1))
        if self._ask_yes_no(f"Delete '{drink.name}'?"):
            self.service.remove_drink(drink.drink_id)
            self._print(f" ✔ Deleted {drink.name}")
        else:
            self._print(" Not deleted.")

    def _menu_search(self) -> None:
        results = self.service.search_drinks(self._ask("Search keyword: "))
        self._print(f"\n{len(results)} result(s):")
        self._show_menu(results)

    def _menu_filter(self) -> None:
        low = self._ask_money("Minimum price (blank = none): ", allow_blank=True)
        high = self._ask_money("Maximum price (blank = none): ", allow_blank=True)
        results = self.service.filter_drinks(low, high)
        self._print(f"\n{len(results)} result(s):")
        self._show_menu(results)

    def _menu_sort(self) -> None:
        self._print("  [1] Name A-Z  [2] Name Z-A  [3] Price low-high  [4] Price high-low")
        choice = self._ask_int("Sort by (1-4): ", 1, 4)
        by, desc = {1: ("name", False), 2: ("name", True),
                    3: ("price", False), 4: ("price", True)}[choice]
        self._show_menu(self.service.sort_drinks(by=by, descending=desc))

    # ============================================================== member admin
    def _show_members(self, members: Optional[List[Member]] = None) -> None:
        members = self.service.list_members() if members is None else members
        self._title("MEMBERS (สมาชิก)", "-")
        if not members:
            self._print("  (no members)")
        for m in members:
            self._print(f"  {m.phone}  {m.name:<20} {m.discount_rate:.0%}")
        self._line("-")

    def manage_members(self) -> None:
        while True:
            self._title("MANAGE MEMBERS (จัดการสมาชิก)", "-")
            self._print("  [1] List  [2] Add  [3] Edit  [4] Delete  [5] Search")
            self._print("  [0] Back   (type 'cancel' to abort an action)")
            choice = self._input("Select option (0-5): ").strip()
            if choice == "0":
                return
            actions = {"1": self._member_list, "2": self._member_add,
                       "3": self._member_edit, "4": self._member_delete,
                       "5": self._member_search}
            action = actions.get(choice)
            if action is None:
                self._print(" ⚠ Invalid option. Please select 0-5.")
                continue
            self._safely(action)

    def _member_list(self) -> None:
        self._show_members()

    def _member_add(self) -> None:
        phone = self._ask_validated(
            lambda: self._ask("Phone number (9-10 digits): "), normalize_phone)
        name = self._ask("Name: ")
        percent = self._ask_money("Discount % (blank = 10): ", allow_blank=True)
        rate = 0.10 if percent is None else percent / 100
        member = self.service.add_member(phone, name, rate)
        self._print(f" ✔ Added {member.name} ({member.phone}) {member.discount_rate:.0%}")

    def _member_edit(self) -> None:
        member = self.service.get_member(self._ask("Phone number to edit: "))
        name = self._ask(f"New name (blank = keep '{member.name}'): ", allow_blank=True)
        percent = self._ask_money(
            f"New discount % (blank = keep {member.discount_rate:.0%}): ", allow_blank=True)
        updated = self.service.update_member(
            member.phone, name or None, None if percent is None else percent / 100)
        self._print(f" ✔ Updated {updated.name} ({updated.phone}) {updated.discount_rate:.0%}")

    def _member_delete(self) -> None:
        member = self.service.get_member(self._ask("Phone number to delete: "))
        if self._ask_yes_no(f"Delete member '{member.name}'?"):
            self.service.remove_member(member.phone)
            self._print(f" ✔ Deleted {member.name}")
        else:
            self._print(" Not deleted.")

    def _member_search(self) -> None:
        results = self.service.search_members(self._ask("Search name or phone: "))
        self._print(f"\n{len(results)} result(s):")
        self._show_members(results)

    # ============================================================ order history
    def show_order_history(self) -> None:
        self._print("Leave a field blank to skip that filter.")
        date_from = self._ask("From date YYYY-MM-DD: ", allow_blank=True) or None
        date_to = self._ask("To date   YYYY-MM-DD: ", allow_blank=True) or None
        min_total = self._ask_money("Minimum total ฿: ", allow_blank=True)
        max_total = self._ask_money("Maximum total ฿: ", allow_blank=True)
        phone = self._ask("Member phone: ", allow_blank=True) or None
        orders = self.service.filter_orders(date_from, date_to, min_total,
                                            max_total, phone)
        self._print("  [1] Newest first  [2] Oldest first  "
                    "[3] Highest total  [4] Lowest total")
        choice = self._ask_int("Sort by (1-4): ", 1, 4)
        by, desc = {1: ("time", True), 2: ("time", False),
                    3: ("total", True), 4: ("total", False)}[choice]
        orders = self.service.sort_orders(orders, by, desc)

        self._title(f"ORDER HISTORY ({len(orders)} order(s))")
        if not orders:
            self._print("No orders match.")
            self._line()
            return
        for o in orders:
            self._print(f"#{o.order_id:04d} {o.timestamp}  {o.member_name:<10} "
                        f"{o.cups} cups  ฿{o.total:>8.2f}")
        self._line("-")
        self._print(f"Sum of listed orders: ฿{sum(o.total for o in orders):.2f}")
        self._line()
