"""SQLite integration coverage for migration and persistent POS workflows."""

import json
import os
from pathlib import Path
import threading
from urllib.request import Request, urlopen
from unittest.mock import patch

from coffee_pos.exceptions import InsufficientPaymentError
from coffee_pos.api import create_api_server
from coffee_pos.services import build_service
from tests.helpers import FakeClock, TempDirTestCase


class SQLiteStorageTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.database_path = str(Path(self.tmp) / "coffee_pos.sqlite3")
        self.environment = patch.dict(os.environ, {
            "SQLITE_DATABASE": self.database_path,
            "COFFEE_POS_STORAGE": "sqlite",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def service(self, clock=None):
        return build_service(self.tmp, clock or FakeClock(), storage="sqlite")

    def test_migrates_legacy_json_and_preserves_source_files(self):
        menu_path = Path(self.tmp) / "menu.json"
        menu_path.write_text(json.dumps([
            {"drink_id": 1, "name": "Legacy Espresso", "price": 55}
        ]), encoding="utf-8")

        service = self.service()

        self.assertEqual([(d.name, d.price) for d in service.list_drinks()],
                         [("Legacy Espresso", 55.0)])
        self.assertTrue(menu_path.exists())
        self.assertTrue(any("migrated 1 record(s)" in note for note in service.notices))

    def test_checkout_and_crud_persist_after_reopening_service(self):
        service = self.service()
        service.add_drink("Flat White", 85)
        service.update_drink(7, price=90)
        cart = [service.build_cart_item(7, "M", 1, "50%", 1)]
        order = service.checkout(cart, 110)
        service.remove_drink(1)

        reopened = self.service()

        self.assertEqual(reopened.get_drink(7).price, 90.0)
        self.assertEqual([item.order_id for item in reopened.list_orders()], [order.order_id])
        self.assertEqual(reopened.get_order(order.order_id).change, 10.0)
        self.assertEqual(len(reopened.list_drinks()), 6)

    def test_failed_payment_does_not_persist_an_order(self):
        service = self.service()
        cart = [service.build_cart_item(1, "S", 1, "0%", 1)]

        with self.assertRaises(InsufficientPaymentError):
            service.checkout(cart, 1)

        self.assertEqual(self.service().list_orders(), [])

    def test_api_checkout_writes_order_to_sqlite(self):
        service = self.service()
        server = create_api_server(service, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.shutdown)

        payload = json.dumps({
            "items": [{"drink_id": 1, "size": "M", "milk_id": 1,
                       "sweetness": "50%", "qty": 1}],
            "cash_received": 70,
        }).encode("utf-8")
        request = Request(
            f"http://127.0.0.1:{server.server_address[1]}/api/orders",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=3) as response:
            body = json.loads(response.read().decode("utf-8"))

        reopened = self.service()
        self.assertEqual(response.status, 201)
        self.assertEqual(body["order"]["order_id"], 1)
        self.assertEqual([order.order_id for order in reopened.list_orders()], [1])


if __name__ == "__main__":
    import unittest
    unittest.main()
