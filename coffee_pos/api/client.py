"""HTTP client for the self-made Coffee POS API."""

from typing import Any, Dict
from urllib.parse import urljoin

import requests

from coffee_pos.exceptions import APIError


class CoffeeAPIClient:
    """Call the menu and checkout endpoints with timeout and error handling."""

    def __init__(self, base_url: str, timeout: float = 3.0) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def get_menu(self) -> Dict[str, Any]:
        return self._request("GET", "api/menu")

    def get_orders(self) -> Dict[str, Any]:
        return self._request("GET", "api/orders")

    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "api/orders", json=payload)

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        try:
            response = requests.request(
                method, urljoin(self.base_url, path), timeout=self.timeout, **kwargs)
            response.raise_for_status()
            body = response.json()
        except requests.Timeout as exc:
            raise APIError("Coffee API request timed out.") from exc
        except requests.RequestException as exc:
            raise APIError(f"Coffee API request failed: {exc}") from exc
        except ValueError as exc:
            raise APIError("Coffee API returned invalid JSON.") from exc
        if not isinstance(body, dict):
            raise APIError("Coffee API returned an unexpected JSON response.")
        return body
