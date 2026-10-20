"""Small self-made HTTP API backed by the existing ShopService."""

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from coffee_pos.exceptions import CoffeePOSError, NotFoundError
from coffee_pos.services.sales_advisor import make_sales_advice

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"


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

        def _send_web_file(self, relative_path):
            root = WEB_ROOT.resolve()
            target = (root / relative_path).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                self._send_json(404, {"error": "Page not found."})
                return
            content = target.read_bytes()
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if content_type.startswith("text/") or content_type in ("application/javascript",):
                content_type += "; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

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
            if path == "/":
                self._send_web_file("portal.html")
            elif path == "/user":
                self._send_web_file("index.html")
            elif path == "/admin":
                self._send_web_file("admin.html")
            elif path.startswith("/assets/"):
                self._send_web_file(path.lstrip("/"))
            elif path.startswith("/api/admin/"):
                resource = path.removeprefix("/api/admin/")
                if resource == "summary":
                    summary = service.daily_summary()
                    self._send_json(200, {
                        "day": summary.day.isoformat(),
                        "transactions": summary.transactions,
                        "cups": summary.cups,
                        "revenue": summary.revenue,
                        "discounts": summary.discounts,
                        "top_drink": summary.top_drink,
                        "top_drink_cups": summary.top_drink_cups,
                        "advice": make_sales_advice(summary),
                    })
                elif resource == "menu":
                    self._send_json(200, {"items": [d.to_dict() for d in service.list_drinks()]})
                elif resource == "orders":
                    self._send_json(200, {"items": [o.to_dict() for o in service.list_orders()]})
                else:
                    self._send_json(404, {"error": "Admin endpoint not found."})
            elif path == "/api/menu":
                self._send_json(200, {"items": [d.to_dict() for d in service.list_drinks()]})
            elif path == "/api/members":
                self._send_json(200, {"items": [m.to_dict() for m in service.list_members()]})
            elif path == "/api/summary":
                summary = service.daily_summary()
                self._send_json(200, {
                    "day": summary.day.isoformat(),
                    "transactions": summary.transactions,
                    "cups": summary.cups,
                    "revenue": summary.revenue,
                    "discounts": summary.discounts,
                    "top_drink": summary.top_drink,
                    "top_drink_cups": summary.top_drink_cups,
                    "advice": make_sales_advice(summary),
                })
            elif path == "/api/orders":
                self._send_json(200, {"items": [o.to_dict() for o in service.list_orders()]})
            else:
                self._send_json(404, {"error": "Endpoint not found."})

        def do_POST(self):
            path = urlsplit(self.path).path
            if path == "/api/admin/menu":
                try:
                    payload = self._read_json()
                    drink = service.add_drink(payload.get("name"), payload.get("price"))
                    self._send_json(201, {"item": drink.to_dict()})
                except (KeyError, TypeError, ValueError, CoffeePOSError) as exc:
                    self._send_json(400, {"error": str(exc)})
                return
            if path != "/api/orders":
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

        def do_PUT(self):
            path = urlsplit(self.path).path
            prefix = "/api/admin/menu/"
            if not path.startswith(prefix):
                self._send_json(404, {"error": "Endpoint not found."})
                return
            try:
                drink_id = int(path.removeprefix(prefix))
                payload = self._read_json()
                drink = service.update_drink(
                    drink_id, name=payload.get("name"), price=payload.get("price"))
                self._send_json(200, {"item": drink.to_dict()})
            except (KeyError, TypeError, ValueError, CoffeePOSError) as exc:
                status = 404 if isinstance(exc, NotFoundError) else 400
                self._send_json(status, {"error": str(exc)})

        def do_DELETE(self):
            path = urlsplit(self.path).path
            prefix = "/api/admin/menu/"
            if not path.startswith(prefix):
                self._send_json(404, {"error": "Endpoint not found."})
                return
            try:
                drink_id = int(path.removeprefix(prefix))
                drink = service.remove_drink(drink_id)
                self._send_json(200, {"item": drink.to_dict()})
            except (TypeError, ValueError, CoffeePOSError) as exc:
                status = 404 if isinstance(exc, NotFoundError) else 400
                self._send_json(status, {"error": str(exc)})

    return ThreadingHTTPServer((host, port), CoffeeAPIHandler)
