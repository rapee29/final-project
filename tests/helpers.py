"""Shared test helpers."""

import shutil
import tempfile
import unittest
from datetime import datetime

from coffee_pos.services import build_service


class TempDirTestCase(unittest.TestCase):
    """Gives every test its own empty data folder."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class FakeClock:
    """Controllable clock so order timestamps are predictable."""

    def __init__(self, text="2026-10-12 09:00:00"):
        self.now = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")

    def set(self, text):
        self.now = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")

    def __call__(self):
        return self.now


def make_service(folder, clock=None):
    return build_service(folder, clock) if clock else build_service(folder)
