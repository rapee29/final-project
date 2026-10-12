"""Small self-made HTTP API backed by the existing ShopService."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from coffee_pos.exceptions import CoffeePOSError, NotFoundError


def create_api_server(service, host="127.0.0.1", port=0):
    """Create a testable local API server; port 0 asks the OS for a free port."""

    class CoffeeAPIHandler(BaseHTTPRequestHandler):
        def log_message(self, _format, *_args):
            return

        def _send_json(self, status, body):
            encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _read_json(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 64_000:
                    raise ValueError("Request body must be between 1 and 64000 bytes.")
                value = json.loads(self.rfile.read(length))
                if not isinstance(value, dict):
                    raise ValueError("JSON body must be an object.")
                return value
            except (ValueError, json.JSONDecodeError) as exc:
                raise ValueError("Request body must contain a valid JSON object.") from exc

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/api/menu":
                self._send_json(200, {"items": [d.to_dict() for d in service.list_drinks()]})
            elif path == "/api/orders":
                self._send_json(200, {"items": [o.to_dict() for o in service.list_orders()]})
            else:
                self._send_json(404, {"error": "Endpoint not found."})

        def do_POST(self):
            if urlsplit(self.path).path != "/api/orders":
                self._send_json(404, {"error": "Endpoint not found."})
                return
            try:
                payload = self._read_json()
                lines = payload.get("items")
                if not isinstance(lines, list) or not lines:
                    raise ValueError("items must be a non-empty list.")
                cart = [service.build_cart_item(
                    line["drink_id"], line["size"], line["milk_id"],
                    line["sweetness"], line["qty"]) for line in lines]
                order = service.checkout(
                    cart, payload.get("cash_received"), payload.get("member_phone"))
                self._send_json(201, {"order": order.to_dict()})
            except (KeyError, TypeError, ValueError) as exc:
                self._send_json(400, {"error": str(exc)})
            except NotFoundError as exc:
                self._send_json(404, {"error": str(exc)})
            except CoffeePOSError as exc:
                self._send_json(400, {"error": str(exc)})

    return ThreadingHTTPServer((host, port), CoffeeAPIHandler)
