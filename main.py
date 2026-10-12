"""Entry point: python main.py"""

import sys

from coffee_pos.exceptions import CoffeePOSError
from coffee_pos.services import build_service
from coffee_pos.ui import CoffeeCLI


def main() -> int:
    try:
        service = build_service()
    except CoffeePOSError as exc:
        print(f"Cannot start the POS: {exc}")
        return 1
    try:
        CoffeeCLI(service).run()
    except KeyboardInterrupt:
        print("\n Exiting POS System. Have a great day!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
