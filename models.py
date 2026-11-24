"""Transaction schema (the data contract every other module relies on)."""
from dataclasses import dataclass

KINDS = ("expense", "income")
CATEGORIES = ("food", "rent", "transport", "salary", "leisure", "other")
CURRENCIES = ("EUR", "USD", "GBP", "MAD")


@dataclass(frozen=True)
class Transaction:
    id: str          # unique, e.g. "T001"
    date: str        # ISO format, e.g. "2026-09-04"
    kind: str        # "expense" or "income"
    category: str    # one of CATEGORIES
    amount: float    # positive, e.g. 18.50
    currency: str    # ISO code, e.g. "EUR"

    def to_row(self):
        return [self.id, self.date, self.kind, self.category,
                f"{self.amount:.2f}", self.currency]
