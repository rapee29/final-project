import unittest

from coffee_pos.exceptions import (DuplicateError, EmptyCartError,
                                   InsufficientPaymentError, NotFoundError,
                                   ValidationError)
from tests.helpers import FakeClock, TempDirTestCase, make_service


class DrinkLogicTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.svc = make_service(self.tmp)

    def test_default_menu_matches_sprint1(self):
        self.assertEqual([(d.name, d.price) for d in self.svc.list_drinks()],
                         [("Espresso", 55), ("Americano", 60), ("Latte", 70),
                          ("Cappuccino", 70), ("Mocha", 75), ("Matcha Latte", 80)])

    def test_add_edit_delete_and_persist(self):
        new = self.svc.add_drink("Flat White", 85)
        self.assertEqual(new.drink_id, 7)
        self.svc.update_drink(7, price=90)
        self.svc.remove_drink(1)
        again = make_service(self.tmp)
        self.assertEqual(again.get_drink(7).price, 90.0)
        with self.assertRaises(NotFoundError):
            again.get_drink(1)

    def test_duplicate_name_and_bad_values(self):
        with self.assertRaises(DuplicateError):
            self.svc.add_drink("  latte ", 10)
        with self.assertRaises(DuplicateError):
            self.svc.update_drink(1, name="MOCHA")
        for name, price in [("", 10), ("X", 0), ("X", -1), ("X", "abc"), ("X", None)]:
            with self.subTest(name=name, price=price), self.assertRaises(ValidationError):
                self.svc.add_drink(name, price)
        self.assertEqual(len(self.svc.list_drinks()), 6)

    def test_delete_unknown_drink(self):
        with self.assertRaises(NotFoundError):
            self.svc.remove_drink(999)

    def test_search(self):
        self.assertEqual([d.name for d in self.svc.search_drinks("LATTE")],
                         ["Latte", "Matcha Latte"])
        self.assertEqual(self.svc.search_drinks("zzz"), [])
        for blank in ("", "   ", None):
            with self.subTest(blank=blank), self.assertRaises(ValidationError):
                self.svc.search_drinks(blank)

    def test_filter_price_range(self):
        names = [d.name for d in self.svc.filter_drinks(60, 75)]
        self.assertEqual(names, ["Americano", "Latte", "Cappuccino", "Mocha"])
        self.assertEqual(len(self.svc.filter_drinks()), 6)
        self.assertEqual(self.svc.filter_drinks(1000), [])
        for low, high in [(-5, 100), (100, 5), ("a", 5), (float("nan"), 5)]:
            with self.subTest(low=low, high=high), self.assertRaises(ValidationError):
                self.svc.filter_drinks(low, high)

    def test_sort(self):
        self.assertEqual([d.price for d in self.svc.sort_drinks(by="price")],
                         [55, 60, 70, 70, 75, 80])
        self.assertEqual(self.svc.sort_drinks(by="name", descending=True)[0].name,
                         "Mocha")
        with self.assertRaises(ValidationError):
            self.svc.sort_drinks(by="colour")

    def test_search_then_sort_chain(self):
        found = self.svc.search_drinks("a")
        ordered = self.svc.sort_drinks(found, by="price", descending=True)
        self.assertEqual(ordered[0].name, "Matcha Latte")


class MemberLogicTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.svc = make_service(self.tmp)

    def test_crud_and_search(self):
        self.svc.add_member("0811111111", "Mali", 0.2)
        self.svc.update_member("0811111111", name="Malee")
        self.assertEqual(make_service(self.tmp).get_member("0811111111").name, "Malee")
        self.assertEqual([m.name for m in self.svc.search_members("som")],
                         ["Somchai", "Somsri"])
        self.assertEqual([m.name for m in self.svc.search_members("98765")], ["Somsri"])
        self.svc.remove_member("0811111111")
        with self.assertRaises(NotFoundError):
            self.svc.get_member("0811111111")

    def test_invalid_member_input(self):
        with self.assertRaises(DuplicateError):
            self.svc.add_member("0812345678", "Dup")
        for args in [("12", "A"), ("0811111111", " "), ("0811111111", "A", 2)]:
            with self.subTest(args=args), self.assertRaises(ValidationError):
                self.svc.add_member(*args)
        with self.assertRaises(ValidationError):
            self.svc.search_members("")


class OrderLogicTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.clock = FakeClock("2026-10-12 09:00:00")
        self.svc = make_service(self.tmp, self.clock)

    def cart(self):
        return [self.svc.build_cart_item(2, "L", 3, "50%", 1),     # 60+20+15 = 95
                self.svc.build_cart_item(3, "m", 3, "100%", 1)]    # 70+10+15 = 95

    def test_cart_item_pricing_matches_sprint1(self):
        item = self.svc.build_cart_item(2, "L", 3, "50%", 1)
        self.assertEqual((item.unit_price, item.milk), (95.0, "Almond Milk"))

    def test_cart_item_rejects_bad_choices(self):
        bad = [dict(drink_id=99, size="S", milk_id=1, sweetness="0%", qty=1),
               dict(drink_id=1, size="XL", milk_id=1, sweetness="0%", qty=1),
               dict(drink_id=1, size="S", milk_id=9, sweetness="0%", qty=1),
               dict(drink_id=1, size="S", milk_id=1, sweetness="77%", qty=1),
               dict(drink_id=1, size="S", milk_id=1, sweetness="0%", qty=0),
               dict(drink_id=1, size="S", milk_id=1, sweetness="0%", qty=-3),
               dict(drink_id=1, size="S", milk_id=1, sweetness="0%", qty=100),
               dict(drink_id=1, size="S", milk_id=1, sweetness="0%", qty="2")]
        for kwargs in bad:
            with self.subTest(kwargs=kwargs), self.assertRaises((ValidationError, NotFoundError)):
                self.svc.build_cart_item(**kwargs)

    def test_guest_checkout(self):
        order = self.svc.checkout(self.cart(), 500)
        self.assertEqual((order.subtotal, order.discount, order.total, order.change),
                         (190.0, 0.0, 190.0, 310.0))
        self.assertEqual(order.member_name, "Guest")

    def test_member_gets_ten_percent(self):
        order = self.svc.checkout(self.cart(), 200, "0812345678")
        self.assertEqual((order.discount, order.total, order.change), (19.0, 171.0, 29.0))
        self.assertEqual(order.member_name, "Somchai")

    def test_unknown_member_raises(self):
        with self.assertRaises(NotFoundError):
            self.svc.checkout(self.cart(), 500, "0000000000")

    def test_payment_validation(self):
        with self.assertRaises(InsufficientPaymentError) as ctx:
            self.svc.checkout(self.cart(), 100)
        self.assertEqual(ctx.exception.shortfall, 90.0)
        for cash in (float("inf"), float("nan"), -5, "500", None, True):
            with self.subTest(cash=cash), self.assertRaises(ValidationError):
                self.svc.checkout(self.cart(), cash)
        self.assertEqual(self.svc.list_orders(), [])  # nothing saved on failure

    def test_exact_payment_has_zero_change(self):
        self.assertEqual(self.svc.checkout(self.cart(), 190).change, 0.0)

    def test_empty_cart(self):
        with self.assertRaises(EmptyCartError):
            self.svc.checkout([], 100)

    def test_orders_persist_and_ids_increase(self):
        self.svc.checkout(self.cart(), 500)
        self.svc.checkout(self.cart(), 500)
        again = make_service(self.tmp, self.clock)
        self.assertEqual([o.order_id for o in again.list_orders()], [1, 2])
        self.assertEqual(again.checkout(self.cart(), 500).order_id, 3)

    def test_daily_summary(self):
        self.assertEqual(self.svc.daily_summary().transactions, 0)
        self.svc.checkout(self.cart(), 500)
        self.svc.checkout([self.svc.build_cart_item(2, "S", 1, "0%", 3)], 500,
                          "0812345678")
        s = self.svc.daily_summary()
        self.assertEqual((s.transactions, s.cups), (2, 5))
        self.assertEqual(s.revenue, round(190 + 162.0, 2))
        self.assertEqual((s.top_drink, s.top_drink_cups), ("Americano", 4))
        with self.assertRaises(ValidationError):
            self.svc.daily_summary("12/10/2026")

    def test_history_filter_and_sort(self):
        self.svc.checkout(self.cart(), 500)                               # 190, 10-12
        self.clock.set("2026-10-13 10:00:00")
        self.svc.checkout([self.svc.build_cart_item(1, "S", 1, "0%", 1)], 100,
                          "0898765432")                                   # 49.5, 10-13
        self.assertEqual(len(self.svc.filter_orders()), 2)
        self.assertEqual([o.order_id for o in self.svc.filter_orders("2026-10-13")], [2])
        self.assertEqual([o.order_id for o in self.svc.filter_orders(date_to="2026-10-12")], [1])
        self.assertEqual([o.order_id for o in self.svc.filter_orders(min_total=100)], [1])
        by_member = self.svc.filter_orders(member_phone="0898765432")
        self.assertEqual([o.order_id for o in by_member], [2])
        self.assertEqual(self.svc.filter_orders("2027-01-01"), [])
        cheapest_first = self.svc.sort_orders(by="total", descending=False)
        self.assertEqual([o.order_id for o in cheapest_first], [2, 1])
        self.assertEqual([o.order_id for o in self.svc.sort_orders()], [2, 1])  # newest first
        for kwargs in [dict(date_from="bad"), dict(date_from="2026-10-13", date_to="2026-10-01"),
                       dict(min_total=-1), dict(min_total=10, max_total=5),
                       dict(member_phone="abc")]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValidationError):
                self.svc.filter_orders(**kwargs)
        with self.assertRaises(ValidationError):
            self.svc.sort_orders(by="nope")


class PerformanceTests(TempDirTestCase):
    def test_sort_and_filter_1000_drinks_under_50ms(self):           # TC-03
        import time
        svc = make_service(self.tmp)
        for i in range(1000):
            svc.add_drink(f"Drink {i}", 10 + (i * 7) % 90)
        start = time.perf_counter()
        ordered = svc.sort_drinks(by="price", descending=True)
        found = svc.filter_drinks(20, 60)
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.assertEqual(len(ordered), 1006)
        self.assertTrue(found)
        self.assertLess(elapsed_ms, 50)


if __name__ == "__main__":
    unittest.main()
