"""Run the Coffee POS website and its local API."""

import os

from coffee_pos.api import create_api_server
from coffee_pos.services import build_service


def main() -> int:
    host = os.environ.get("COFFEE_POS_HOST", "127.0.0.1")
    port = int(os.environ.get("COFFEE_POS_PORT", "8000"))
    try:
        server = create_api_server(build_service(), host=host, port=port)
    except OSError as exc:
        print(f"Cannot start Coffee POS web app on {host}:{port}: {exc}")
        return 1

    print(f"Coffee POS is ready at http://{host}:{port}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCoffee POS web app stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
