"""Files only: load/save the transactions as JSON, back them up, import a CSV."""
import csv
import json
from pathlib import Path

from .models import Transaction
from .validation import ValidationError, build_transaction

CSV_HEADER = ["id", "date", "kind", "category", "amount", "currency"]


def load(file):
    """Read the JSON file and return a list of Transaction objects.
    A missing file simply means 'no transactions yet'."""
    file = Path(file)
    if not file.exists():
        return []
    try:
        rows = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ValidationError(f"{file} is not valid JSON ({err.msg}, line {err.lineno}).")
    if not isinstance(rows, list):
        raise ValidationError(f"{file} must contain a JSON list.")
    transactions = []
    for number, row in enumerate(rows, start=1):
        try:
            transactions.append(build_transaction(
                row["id"], row["date"], row["kind"], row["category"],
                row["amount"], row["currency"]))
        except (KeyError, TypeError):
            raise ValidationError(f"{file}, entry {number}: missing or malformed fields.")
        except ValidationError as err:
            raise ValidationError(f"{file}, entry {number}: {err}")
    return transactions


def save(file, transactions):
    """Write to a temporary file first and then swap it in, so a crash can
    never leave a half-written transactions file."""
    file = Path(file)
    if file.parent != Path("."):
        file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_name(file.name + ".tmp")
    rows = [t.__dict__ for t in transactions]
    temporary.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    temporary.replace(file)


def backup(file, destination):
    """Copy the current data to a NEW file. Mode "x" refuses to overwrite an
    older backup (it raises FileExistsError)."""
    transactions = load(file)
    with open(destination, "x", encoding="utf-8") as output:
        json.dump([t.__dict__ for t in transactions], output, indent=2)
    return len(transactions)


def read_csv(path):
    """Read a CSV and return (valid_rows, errors). Bad rows are skipped and
    reported as 'Row N: message' so the user can fix them."""
    path = Path(path)
    if not path.exists():
        raise ValidationError(f"file not found: {path}")
    good, errors = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != CSV_HEADER:
            raise ValidationError(f"Row 1: header must be {','.join(CSV_HEADER)}.")
        for number, row in enumerate(reader, start=2):
            if len(row) != len(CSV_HEADER):
                errors.append(f"Row {number}: expected {len(CSV_HEADER)} columns, got {len(row)}.")
                continue
            try:
                good.append(build_transaction(*row))
            except ValidationError as err:
                errors.append(f"Row {number}: {err}")
    return good, errors
