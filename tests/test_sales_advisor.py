"""Tests for the explainable sales-advice automation."""

from datetime import date
from unittest import TestCase

from coffee_pos.models import DailySummary
from coffee_pos.services.sales_advisor import make_sales_advice


class SalesAdvisorTests(TestCase):
    def test_advises_on_top_seller(self):
        summary = DailySummary(date(2026, 10, 12), 4, 8, 520, 20, "Latte", 5)
        self.assertIn("Promote Latte", make_sales_advice(summary))

    def test_advises_when_there_are_no_sales(self):
        summary = DailySummary(date(2026, 10, 12), 0, 0, 0, 0)
        self.assertIn("No sales today yet", make_sales_advice(summary))
