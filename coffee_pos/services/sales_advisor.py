"""Deterministic sales automation based on the shop's daily summary."""


def make_sales_advice(summary) -> str:
    """Return a short, explainable action from today's recorded sales."""
    if summary.transactions == 0:
        return "No sales today yet: promote the daily special to start activity."
    if summary.top_drink:
        return (f"Promote {summary.top_drink}: it leads today's sales with "
                f"{summary.top_drink_cups} cup(s).")
    return "Review today's orders and feature a drink with a clear value offer."
