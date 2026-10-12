"""Local HTTP API used by the Coffee POS project and its demo client."""

from coffee_pos.api.client import CoffeeAPIClient
from coffee_pos.api.server import create_api_server

__all__ = ["CoffeeAPIClient", "create_api_server"]
