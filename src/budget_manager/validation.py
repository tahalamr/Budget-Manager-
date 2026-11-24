"""Boundary checks. Every function returns a clean value or raises
ValidationError with a message the user can act on. Nothing is silently fixed."""
from datetime import date

from .models import CATEGORIES, CURRENCIES, KINDS, Transaction


class ValidationError(ValueError):
    pass


def validate_amount(raw):
    try:
        amount = float(raw)
    except (TypeError, ValueError):
        raise ValidationError(f"amount must be a number, got {raw!r}.")
    if amount != amount or amount in (float("inf"), float("-inf")):
        raise ValidationError("amount must be a finite number.")
    if amount <= 0:
        raise ValidationError(f"amount must be > 0, got {amount}.")
    return round(amount, 2)


def validate_date(raw):
    try:
        return date.fromisoformat(str(raw).strip()).isoformat()
    except ValueError:
        raise ValidationError(f"date must be YYYY-MM-DD (a real date), got {raw!r}.")


def validate_choice(name, raw, allowed):
    value = str(raw).strip().lower() if name != "currency" else str(raw).strip().upper()
    if value not in allowed:
        raise ValidationError(f"{name} must be one of {', '.join(allowed)}; got {raw!r}.")
    return value


def build_transaction(tid, raw_date, kind, category, raw_amount, currency):
    """Validate every field once, at the boundary, and return a Transaction."""
    tid = str(tid).strip()
    if not tid:
        raise ValidationError("id must not be empty.")
    return Transaction(
        id=tid,
        date=validate_date(raw_date),
        kind=validate_choice("kind", kind, KINDS),
        category=validate_choice("category", category, CATEGORIES),
        amount=validate_amount(raw_amount),
        currency=validate_choice("currency", currency, CURRENCIES),
    )
