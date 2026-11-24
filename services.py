"""Budget logic only. No input(), no print(), no files."""
from collections import defaultdict

from .validation import ValidationError, build_transaction


def next_id(transactions):
    """T001, T002, ... always one more than the highest existing number."""
    numbers = [int(t.id[1:]) for t in transactions
               if t.id.startswith("T") and t.id[1:].isdigit()]
    return f"T{(max(numbers) + 1 if numbers else 1):03d}"


def add_transaction(transactions, raw_date, kind, category, raw_amount, currency="EUR"):
    """Return a NEW list with the validated transaction added."""
    new = build_transaction(next_id(transactions), raw_date, kind, category,
                            raw_amount, currency)
    return list(transactions) + [new]


def filter_transactions(transactions, kind=None, category=None, month=None):
    """month is 'YYYY-MM'. Any filter left as None is ignored."""
    result = []
    for t in transactions:
        if kind and t.kind != kind:
            continue
        if category and t.category != category:
            continue
        if month and not t.date.startswith(month):
            continue
        result.append(t)
    return result


def balance(transactions, currency="EUR"):
    """Income minus expenses for one currency (currencies are never mixed)."""
    total = 0.0
    for t in transactions:
        if t.currency != currency:
            continue
        total += t.amount if t.kind == "income" else -t.amount
    return round(total, 2)


def summary_by_category(transactions, currency="EUR"):
    """Expenses per category for one currency, largest first."""
    totals = defaultdict(float)
    for t in transactions:
        if t.kind == "expense" and t.currency == currency:
            totals[t.category] += t.amount
    return sorted(((c, round(v, 2)) for c, v in totals.items()),
                  key=lambda item: item[1], reverse=True)
