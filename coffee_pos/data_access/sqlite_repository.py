"""SQLite-backed repository implementing the ShopService repository interface."""

import json
import sqlite3

from coffee_pos.exceptions import DatabaseError, DuplicateError, NotFoundError


class SQLiteRepository:
    def __init__(self, database, entity, model_cls, key_attr):
        self._database = database
        self._entity = entity
        self._model_cls = model_cls
        self._key_attr = key_attr
        self.notices = []

    def _from_row(self, row):
        if self._entity == "Drink":
            record = {"drink_id": row[0], "name": row[1], "price": row[2]}
        elif self._entity == "Member":
            record = {"phone": row[0], "name": row[1], "discount_rate": row[2]}
        else:
            record = json.loads(row[0])
        return self._model_cls.from_dict(record)

    def all(self):
        queries = {
            "Drink": "SELECT drink_id, name, price FROM drinks ORDER BY drink_id",
            "Member": "SELECT phone, name, discount_rate FROM members ORDER BY name",
            "Order": "SELECT payload FROM orders ORDER BY order_id",
        }
        try:
            with self._database.session() as connection:
                return [self._from_row(row) for row in connection.execute(queries[self._entity])]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot read {self._entity} records from SQLite: {exc}") from exc

    def get(self, key):
        columns = {
            "Drink": "drink_id, name, price",
            "Member": "phone, name, discount_rate",
            "Order": "payload",
        }[self._entity]
        try:
            with self._database.session() as connection:
                row = connection.execute(
                    f"SELECT {columns} FROM {self._table()} "
                    f"WHERE {self._key_column()} = ?", (key,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot read {self._entity} from SQLite: {exc}") from exc
        if row is None:
            raise NotFoundError(self._entity, key)
        return self._from_row(row)

    def exists(self, key):
        try:
            self.get(key)
            return True
        except NotFoundError:
            return False

    def __len__(self):
        try:
            with self._database.session() as connection:
                return connection.execute(
                    f"SELECT COUNT(*) FROM {self._table()}"
                ).fetchone()[0]
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot count {self._entity} records: {exc}") from exc

    def add(self, item):
        query, values = self._insert(item)
        try:
            with self._database.session() as connection:
                connection.execute(query, values)
            return item
        except sqlite3.IntegrityError as exc:
            raise DuplicateError(self._entity, getattr(item, self._key_attr)) from exc
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot save {self._entity} to SQLite: {exc}") from exc

    def import_many(self, items):
        """Import a legacy collection in one transaction, skipping duplicate rows."""
        imported = skipped = 0
        try:
            with self._database.session() as connection:
                for item in items:
                    query, values = self._insert(item)
                    try:
                        connection.execute(query, values)
                        imported += 1
                    except sqlite3.IntegrityError:
                        skipped += 1
            return imported, skipped
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot migrate {self._entity} records to SQLite: {exc}") from exc

    def update(self, item):
        key = getattr(item, self._key_attr)
        query, values = self._update(item)
        try:
            with self._database.session() as connection:
                cursor = connection.execute(query, (*values, key))
                if cursor.rowcount == 0 and connection.execute(
                    f"SELECT 1 FROM {self._table()} WHERE {self._key_column()} = ?", (key,)
                ).fetchone() is None:
                    raise NotFoundError(self._entity, key)
            return item
        except sqlite3.IntegrityError as exc:
            raise DuplicateError(self._entity, key) from exc
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot update {self._entity} in SQLite: {exc}") from exc

    def delete(self, key):
        old = self.get(key)
        try:
            with self._database.session() as connection:
                connection.execute(
                    f"DELETE FROM {self._table()} WHERE {self._key_column()} = ?", (key,)
                )
            return old
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot delete {self._entity} from SQLite: {exc}") from exc

    def _table(self):
        return {"Drink": "drinks", "Member": "members", "Order": "orders"}[self._entity]

    def _key_column(self):
        return {"Drink": "drink_id", "Member": "phone", "Order": "order_id"}[self._entity]

    def _insert(self, item):
        record = item.to_dict()
        if self._entity == "Drink":
            return "INSERT INTO drinks (drink_id, name, price) VALUES (?, ?, ?)", (
                record["drink_id"], record["name"], record["price"])
        if self._entity == "Member":
            return "INSERT INTO members (phone, name, discount_rate) VALUES (?, ?, ?)", (
                record["phone"], record["name"], record["discount_rate"])
        return "INSERT INTO orders (order_id, timestamp, total, payload) VALUES (?, ?, ?, ?)", (
            record["order_id"], record["timestamp"], record["total"],
            json.dumps(record, ensure_ascii=False, separators=(",", ":")))

    def _update(self, item):
        record = item.to_dict()
        if self._entity == "Drink":
            return "UPDATE drinks SET name = ?, price = ? WHERE drink_id = ?", (
                record["name"], record["price"])
        if self._entity == "Member":
            return "UPDATE members SET name = ?, discount_rate = ? WHERE phone = ?", (
                record["name"], record["discount_rate"])
        return "UPDATE orders SET timestamp = ?, total = ?, payload = ? WHERE order_id = ?", (
            record["timestamp"], record["total"],
            json.dumps(record, ensure_ascii=False, separators=(",", ":")))
