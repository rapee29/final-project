"""End-to-end tests: scripted keyboard input through the real CLI + service + files."""

import json
import unittest
from pathlib import Path
from unittest import mock

from coffee_pos.exceptions import DataFileError
from coffee_pos.ui import CoffeeCLI
from tests.helpers import FakeClock, TempDirTestCase, make_service


class CLITestCase(TempDirTestCase):
    def run_cli(self, *inputs, service=None):
        """Feed ``inputs`` to the CLI; running out of input behaves like Ctrl+D."""
        feed = iter(inputs)

        def fake_input(prompt=""):
            try:
                return next(feed)
            except StopIteration:
                raise EOFError from None

        out = []
        svc = service or make_service(self.tmp, FakeClock())
        CoffeeCLI(svc, fake_input, out.append).run()
        return "\n".join(out), svc


class MainMenuTests(CLITestCase):
    def test_exit(self):
        out, _ = self.run_cli("0")
        self.assertIn("Exiting POS System", out)

    def test_invalid_main_choices_do_not_crash(self):
        out, _ = self.run_cli("", "abc", "99", "-1", "1.5", " 0 ")
        self.assertEqual(out.count("Invalid option"), 5)

    def test_eof_and_ctrl_c_exit_gracefully(self):
        out, _ = self.run_cli()  # no input at all
        self.assertIn("Have a great day", out)

        def ctrl_c(prompt=""):
            raise KeyboardInterrupt

        out = []
        CoffeeCLI(make_service(self.tmp), ctrl_c, out.append).run()
        self.assertIn("Have a great day", "\n".join(out))

    def test_startup_notice_when_files_missing(self):
        out, _ = self.run_cli("0")
        self.assertIn("menu.json not found", out)

    def test_corrupt_data_files_at_startup(self):
        for name in ("menu.json", "members.json", "orders.json"):
            (Path(self.tmp) / name).write_text("<<<garbage>>>", encoding="utf-8")
        out, svc = self.run_cli("0", service=make_service(self.tmp))
        self.assertIn("invalid JSON", out)
        self.assertEqual(len(svc.list_drinks()), 6)       # defaults restored
        self.assertEqual(len(list(Path(self.tmp).glob("*.bak"))), 3)


class NewOrderTests(CLITestCase):
    def test_full_guest_order_with_receipt_and_persistence(self):
        out, svc = self.run_cli(
            "1", "2", "L", "3", "3", "1", "y",     # Americano L almond 50%
            "3", "M", "3", "4", "1", "n",          # Latte M almond 100%
            "n", "500", "0")
        self.assertIn("Subtotal: ฿190.00", out)
        self.assertIn("Change       : ฿  310.00", out)
        self.assertIn("Order No.  : #0001", out)
        saved = json.loads((Path(self.tmp) / "orders.json").read_text(encoding="utf-8"))
        self.assertEqual(saved[0]["total"], 190.0)
        self.assertEqual(len(make_service(self.tmp).list_orders()), 1)

    def test_member_discount_and_unknown_member(self):
        out, _ = self.run_cli("1", "2", "L", "3", "3", "1", "n",
                              "y", "0812345678", "500", "0")
        self.assertIn("Welcome Somchai", out)
        self.assertIn("Grand Total: ฿85.50", out)
        out, _ = self.run_cli("1", "1", "S", "1", "1", "1", "n",
                              "y", "0000000000", "500", "0")
        self.assertIn("not found. Proceeding as Guest", out)

    def test_every_invalid_input_is_retried(self):
        out, svc = self.run_cli(
            "1",
            "abc", "-3", "99",            # bad item number -> text, negative, unknown id
            "1",
            "XL", "", "s",                # bad size, blank, valid (lower case)
            "9", "x", "1",                # bad milk
            "0", "5", "1",                # bad sweetness
            "0", "-2", "abc", "100", "2.5", "2",   # bad quantity (size/milk NOT asked again)
            "n", "n",
            "abc", "nan", "inf", "-5", "50", "200",   # bad payments
            "0")
        for text in ("Please enter a whole number", "Invalid item selection",
                     "Invalid size", "Input cannot be empty", "Invalid amount",
                     "Insufficient amount"):
            self.assertIn(text, out)
        self.assertEqual(out.count("--- Select Size ---"), 1)  # size not asked again
        self.assertEqual(len(svc.list_orders()), 1)
        self.assertEqual(svc.list_orders()[0].items[0].qty, 2)

    def test_empty_cart_returns_to_menu(self):
        out, svc = self.run_cli("1", "0", "0")
        self.assertIn("Cart is empty", out)
        self.assertEqual(svc.list_orders(), [])

    def test_cancel_abandons_order(self):
        out, svc = self.run_cli("1", "1", "S", "cancel", "0")
        self.assertIn("Cancelled", out)
        self.assertEqual(svc.list_orders(), [])

    def test_eof_in_the_middle_of_an_order(self):
        out, svc = self.run_cli("1", "1", "S")
        self.assertIn("Have a great day", out)
        self.assertEqual(svc.list_orders(), [])

    def test_save_failure_does_not_crash_or_record_order(self):
        svc = make_service(self.tmp, FakeClock())
        with mock.patch.object(svc._orders._manager, "save",
                               side_effect=DataFileError("disk full")):
            out, _ = self.run_cli("1", "1", "S", "1", "1", "1", "n", "n", "100", "0",
                                  service=svc)
        self.assertIn("Order NOT saved", out)
        self.assertEqual(svc.list_orders(), [])


class AdminTests(CLITestCase):
    def test_menu_crud_search_filter_sort(self):
        out, svc = self.run_cli(
            "3",
            "2", "Flat White", "85",            # add
            "2", "Latte", "10",                 # duplicate name
            "2", "Bad", "-4", "abc", "cancel",  # invalid price re-asked, then cancel
            "3", "7", "", "90",                 # edit price only
            "5", "latte",                       # search
            "6", "60", "75",                    # filter
            "7", "4",                           # sort price high-low
            "4", "7", "y",                      # delete
            "4", "99",                          # delete unknown
            "5", "   ", "x",                    # blank search is re-asked
            "9",                                # invalid option
            "0", "0")
        self.assertIn("Added [7] Flat White", out)
        self.assertIn("already exists", out)
        self.assertIn("must be greater than 0", out)
        self.assertIn("Updated [7] Flat White ฿90.00", out)
        self.assertIn("2 result(s)", out)
        self.assertIn("4 result(s)", out)
        self.assertIn("Deleted Flat White", out)
        self.assertIn("Drink '99' not found", out)
        self.assertIn("Input cannot be empty", out)
        self.assertIn("Cancelled", out)
        self.assertEqual(len(svc.list_drinks()), 6)

    def test_member_crud(self):
        out, svc = self.run_cli(
            "4",
            "2", "123", "abcdefghij", "0811111111", "Mali", "20",   # bad phones re-asked
            "2", "0811111111", "Dup", "",                           # duplicate phone
            "3", "0811111111", "Malee", "",
            "5", "mal",
            "4", "0811111111", "y",
            "4", "0811111111",                      # now unknown
            "0", "0")
        self.assertIn("Added Mali", out)
        self.assertEqual(out.count("Phone number must be 9-10 digits"), 2)
        self.assertIn("already exists", out)
        self.assertIn("Updated Malee", out)
        self.assertIn("1 result(s)", out)
        self.assertIn("Deleted Malee", out)
        self.assertIn("not found", out)
        self.assertEqual(len(svc.list_members()), 2)

    def test_summary_and_history(self):
        order = ("1", "2", "S", "1", "1", "2", "n", "n", "500")
        out, _ = self.run_cli(*order, "0")
        out, _ = self.run_cli(
            "2", "",                              # today's summary
            "2", "not-a-date",                    # bad date
            "5", "", "", "", "", "", "1",         # history no filters
            "5", "2027-01-01", "", "", "", "", "1",   # no match
            "5", "2026-10-12", "2026-10-01", "1", "0",  # reversed dates
            "0")
        self.assertIn("Total Transactions : 1", out)
        self.assertIn("Total Revenue      : ฿120.00", out)
        self.assertIn("YYYY-MM-DD format", out)
        self.assertIn("ORDER HISTORY (1 order(s))", out)
        self.assertIn("No orders match", out)


if __name__ == "__main__":
    unittest.main()
