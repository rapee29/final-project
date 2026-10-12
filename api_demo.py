"""Run a local API smoke demo: python api_demo.py"""

from threading import Thread
from tempfile import TemporaryDirectory

from coffee_pos.api import CoffeeAPIClient, create_api_server
from coffee_pos.services import build_service


def main() -> None:
    with TemporaryDirectory(prefix="coffee-pos-api-demo-") as folder:
        service = build_service(folder)
        server = create_api_server(service)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = server.server_address
            client = CoffeeAPIClient(f"http://{host}:{port}")
            menu = client.get_menu()
            print(f"GET /api/menu: {len(menu['items'])} drink(s)")
            order = client.create_order({
                "items": [{"drink_id": menu["items"][0]["drink_id"], "size": "S",
                           "milk_id": 1, "sweetness": "0%", "qty": 1}],
                "cash_received": 100,
            })
            print(f"POST /api/orders: created order #{order['order']['order_id']}")
            print(f"GET /api/orders: {len(client.get_orders()['items'])} order(s)")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    main()
