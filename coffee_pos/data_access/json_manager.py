"""Low-level JSON file access with automatic recovery.

``JSONManager`` knows nothing about drinks or orders; it only guarantees that
a list of dicts can be loaded from / saved to a file safely:

* missing file      -> created from the default data (no crash)
* corrupt JSON      -> original is backed up as ``*.bak``, defaults restored
* write interrupted -> never leaves a half-written file (temp file + replace)
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, List

from coffee_pos.exceptions import DataFileError


class JSONManager:
    def __init__(self, path, default_factory: Callable[[], List[dict]] = list) -> None:
        self.path = Path(path)
        self._default_factory = default_factory
        self.events: List[str] = []  # human-readable recovery notices

    def load(self) -> List[dict]:
        """Return the list stored in the file, recovering if needed."""
        if not self.path.exists():
            self.events.append(f"{self.path.name} not found - created with default data.")
            return self._reset()
        try:
            text = self.path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return self._recover("is not valid UTF-8 text")
        except OSError as exc:
            raise DataFileError(f"Cannot read {self.path.name}: {exc}") from exc
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return self._recover("contains invalid JSON")
        if not isinstance(data, list):
            return self._recover("does not contain a JSON list")
        return data

    def save(self, data: List[dict]) -> None:
        """Atomically write ``data`` as pretty JSON."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                    json.dump(data, tmp, ensure_ascii=False, indent=2)
                os.replace(tmp_name, self.path)
            except BaseException:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
                raise
        except (OSError, TypeError, ValueError) as exc:
            raise DataFileError(f"Cannot save {self.path.name}: {exc}") from exc

    def backup(self, reason: str) -> Path:
        """Copy the current file to ``<name>.<timestamp>.bak`` and return its path."""
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        target = self.path.with_name(f"{self.path.name}.{stamp}.bak")
        try:
            shutil.copy2(self.path, target)
        except OSError as exc:
            raise DataFileError(f"Cannot back up {self.path.name}: {exc}") from exc
        self.events.append(f"{self.path.name} backed up to {target.name} ({reason}).")
        return target

    def _recover(self, reason: str) -> List[dict]:
        self.events.append(f"{self.path.name} {reason}.")
        self.backup(reason)
        return self._reset()

    def _reset(self) -> List[dict]:
        data = self._default_factory()
        self.save(data)
        return data
