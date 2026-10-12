import unittest

from coffee_pos.exceptions import ValidationError
from coffee_pos.models import CartItem, Drink, Member, Order


class DrinkTests(unittest.TestCase):
    def test_valid_drink_is_normalised(self):
        d = Drink(1, "  Latte ", 70)
        self.assertEqual((d.name, d.price), ("Latte", 70.0))

    def test_invalid_values_rejected(self):
        for args in [(0, "x", 10), (1, "", 10), (1, "   ", 10), (1, "x", 0),
                     (1, "x", -5), (1, "x", float("nan")), (1, "x", float("inf")),
                     (1, "x", "10"), (1, "x", True), (True, "x", 10), (1, 5, 10)]:
            with self.subTest(args=args), self.assertRaises(ValidationError):
                Drink(*args)

    def test_round_trip(self):
        d = Drink(3, "Mocha", 75)
        self.assertEqual(Drink.from_dict(d.to_dict()), d)


class MemberTests(unittest.TestCase):
    def test_discount(self):
        self.assertEqual(Member("0812345678", "A").discount_for(190), 19.0)

    def test_invalid_phone_and_rate(self):
        for args in [("abc", "A"), ("123", "A"), ("08123456789012", "A"),
                     ("0812345678", ""), ("0812345678", "A", -0.1),
                     ("0812345678", "A", 1.5)]:
            with self.subTest(args=args), self.assertRaises(ValidationError):
                Member(*args)


class OrderTests(unittest.TestCase):
    def item(self, **kw):
        base = dict(drink_id=1, name="Latte", size="M", milk="Soy Milk",
                    sweetness="50%", qty=2, unit_price=80)
        base.update(kw)
        return CartItem(**base)

    def test_cart_item_total_and_validation(self):
        self.assertEqual(self.item().total_price, 160.0)
        for bad in [dict(size="XL"), dict(qty=0), dict(qty=-1), dict(qty=1000),
                    dict(qty=1.5), dict(sweetness="75%"), dict(unit_price=-1)]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                self.item(**bad)

    def test_order_round_trip_and_bad_timestamp(self):
        order = Order(1, "2026-10-12 09:00:00", [self.item()], 160, 0, 160, 200, 40)
        self.assertEqual(Order.from_dict(order.to_dict()), order)
        with self.assertRaises(ValidationError):
            Order(1, "yesterday", [self.item()], 160, 0, 160, 200, 40)
        with self.assertRaises(ValidationError):
            Order(1, "2026-10-12 09:00:00", [], 0, 0, 0, 0, 0)


if __name__ == "__main__":
    unittest.main()
