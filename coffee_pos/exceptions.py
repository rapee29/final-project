"""Custom exceptions shared by every layer.

All application errors derive from ``CoffeePOSError`` so the UI layer can
catch one base class and show a friendly message instead of crashing.
"""


class CoffeePOSError(Exception):
    """Base class for all expected application errors."""


class ValidationError(CoffeePOSError, ValueError):
    """Raised when a value fails validation (wrong type, out of range, blank)."""


class NotFoundError(CoffeePOSError):
    """Raised when a record (drink, member, order) does not exist."""

    def __init__(self, entity: str, key) -> None:
        self.entity = entity
        self.key = key
        super().__init__(f"{entity} '{key}' not found.")


class DuplicateError(CoffeePOSError):
    """Raised when adding a record whose key or name already exists."""

    def __init__(self, entity: str, key) -> None:
        self.entity = entity
        self.key = key
        super().__init__(f"{entity} '{key}' already exists.")


class EmptyCartError(CoffeePOSError):
    """Raised when checking out an empty cart."""

    def __init__(self) -> None:
        super().__init__("Cart is empty.")


class InsufficientPaymentError(CoffeePOSError):
    """Raised when the cash received is less than the amount due."""

    def __init__(self, shortfall: float) -> None:
        self.shortfall = shortfall
        super().__init__(f"Insufficient amount. Still need ฿{shortfall:.2f}")


class DataFileError(CoffeePOSError):
    """Raised when a data file cannot be read or written."""


class DatabaseError(CoffeePOSError):
    """Raised when the configured database cannot be reached or updated."""


class APIError(CoffeePOSError):
    """Raised when the Coffee POS HTTP API cannot complete a request."""
