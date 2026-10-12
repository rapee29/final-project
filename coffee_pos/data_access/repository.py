"""Generic in-memory repository that is written through to a JSON file.

State management rule (Sprint 3): memory and file never disagree.
Every change is saved immediately; if saving fails the in-memory change is
rolled back and ``DataFileError`` is raised.
"""

from typing import Callable, Dict, Generic, Hashable, List, TypeVar

from coffee_pos.data_access.json_manager import JSONManager
from coffee_pos.exceptions import (CoffeePOSError, DataFileError, DuplicateError,
                                   NotFoundError)

T = TypeVar("T")


class JSONRepository(Generic[T]):
    def __init__(self, manager: JSONManager, model_cls, key_attr: str,
                 entity_name: str) -> None:
        self._manager = manager
        self._model_cls = model_cls
        self._key_attr = key_attr
        self._entity = entity_name
        self._items: Dict[Hashable, T] = {}
        self.notices: List[str] = []
        self._load()

    # ---------------------------------------------------------------- reading
    def all(self) -> List[T]:
        return list(self._items.values())

    def get(self, key) -> T:
        try:
            return self._items[key]
        except (KeyError, TypeError):
            raise NotFoundError(self._entity, key) from None

    def exists(self, key) -> bool:
        return key in self._items

    def __len__(self) -> int:
        return len(self._items)

    # ---------------------------------------------------------------- writing
    def add(self, item: T) -> T:
        key = getattr(item, self._key_attr)
        if key in self._items:
            raise DuplicateError(self._entity, key)
        self._items[key] = item
        self._commit(lambda: self._items.pop(key, None))
        return item

    def update(self, item: T) -> T:
        key = getattr(item, self._key_attr)
        old = self.get(key)
        self._items[key] = item
        self._commit(lambda: self._items.__setitem__(key, old))
        return item

    def delete(self, key) -> T:
        old = self.get(key)
        del self._items[key]
        self._commit(lambda: self._items.__setitem__(key, old))
        return old

    # --------------------------------------------------------------- internal
    def _commit(self, rollback: Callable[[], None]) -> None:
        try:
            self._manager.save([i.to_dict() for i in self._items.values()])
        except DataFileError:
            rollback()
            raise

    def _load(self) -> None:
        skipped = 0
        for record in self._manager.load():
            try:
                item = self._model_cls.from_dict(record)
            except (CoffeePOSError, KeyError, TypeError, ValueError, AttributeError):
                skipped += 1
                continue
            key = getattr(item, self._key_attr)
            if key in self._items:
                skipped += 1
                continue
            self._items[key] = item
        if skipped:
            self._manager.backup(f"{skipped} invalid record(s) skipped")
            self.notices.append(f"{self._entity}: skipped {skipped} invalid record(s).")
            self._manager.save([i.to_dict() for i in self._items.values()])
        self.notices = self._manager.events + self.notices
