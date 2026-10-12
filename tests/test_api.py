"""End-to-end tests for the self-made Coffee POS HTTP API."""

import json
from threading import Thread
from unittest import TestCase
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from coffee_pos.api import CoffeeAPIClient, create_api_server
from coffee_pos.exceptions import APIError
from tests.helpers import make_service


class CoffeeAPITests(TestCase):
    def setUp(self):
        import tempfile

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.service = make_service(self.temp_dir.name)
        self.server = create_api_server(self.service)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self._close_server)
        host, port = self.server.server_address
        self.client = CoffeeAPIClient(f"http://{host}:{port}")

    def _close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_get_menu_and_post_order_persist(self):
        menu = self.client.get_menu()
        self.assertEqual(len(menu["items"]), 6)
        order = self.client.create_order({
            "items": [{"drink_id": 1, "size": "S", "milk_id": 1,
                       "sweetness": "0%", "qty": 1}],
            "cash_received": 100,
        })["order"]
        self.assertEqual(order["total"], 55.0)
        self.assertEqual(len(self.client.get_orders()["items"]), 1)

    def test_post_invalid_order_returns_clear_api_error(self):
        with self.assertRaisesRegex(APIError, "400 Client Error"):
            self.client.create_order({"items": [], "cash_received": 100})

    def test_malformed_json_body_returns_400(self):
        host, port = self.server.server_address
        request = Request(f"http://{host}:{port}/api/orders", data=b"{bad",
                          headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(HTTPError) as result:
            urlopen(request)
        self.assertEqual(result.exception.code, 400)
        body = json.loads(result.exception.read())
        self.assertIn("error", body)

    def test_unknown_endpoint_returns_404(self):
        host, port = self.server.server_address
        request = Request(f"http://{host}:{port}/api/missing")
        with self.assertRaises(HTTPError) as result:
            urlopen(request)
        self.assertEqual(result.exception.code, 404)
