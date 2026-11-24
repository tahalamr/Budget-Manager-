"""Command-line tool, same style as the Session 12 example (argparse + subparsers).
It only talks to the user. All rules live in services/validation, all files in storage.

Examples (run from the project folder):
  python run.py add 2026-09-04 expense food 18.50
  python run.py list
  python run.py list --kind expense --month 2026-09
  python run.py summary
  python run.py backup backup.json
  python run.py import data/sample_transactions.csv
  python run.py --help
"""
import argparse
import sys

from . import services, storage
from .models import CATEGORIES, CURRENCIES, KINDS
from .validation import ValidationError

DEFAULT_FILE = "transactions.json"


def build_parser():
    parser = argparse.ArgumentParser(description="Personal Budget Manager")
    parser.add_argument("--file", default=DEFAULT_FILE,
                        help=f"data file to use (default: {DEFAULT_FILE})")

    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="record a transaction")
    add.add_argument("date", help="YYYY-MM-DD")
    add.add_argument("kind", help="/".join(KINDS))
    add.add_argument("category", help="/".join(CATEGORIES))
    add.add_argument("amount", help="positive number, e.g. 18.50")
    add.add_argument("--currency", default="EUR", help="/".join(CURRENCIES))

    listing = commands.add_parser("list", help="show transactions")
    listing.add_argument("--kind")
    listing.add_argument("--category")
    listing.add_argument("--month", help="YYYY-MM")

    commands.add_parser("summary", help="balance and expenses by category")

    backup = commands.add_parser("backup", help="copy the data to a new file")
    backup.add_argument("destination")

    imp = commands.add_parser("import", help="add the valid rows of a CSV file")
    imp.add_argument("csv_file")
    return parser


def run(args):
    transactions = storage.load(args.file)

    if args.command == "add":
        transactions = services.add_transaction(
            transactions, args.date, args.kind, args.category,
            args.amount, args.currency)
        storage.save(args.file, transactions)
        print(f"Added {transactions[-1].id}.")

    elif args.command == "list":
        chosen = services.filter_transactions(
            transactions,
            kind=args.kind.lower() if args.kind else None,
            category=args.category.lower() if args.category else None,
            month=args.month)
        for t in chosen:
            print(f"{t.id}  {t.date}  {t.kind:<8} {t.category:<10} "
                  f"{t.amount:>9.2f} {t.currency}")

    elif args.command == "summary":
        print(f"Transactions: {len(transactions)}")
        print(f"Balance: {services.balance(transactions):.2f} EUR")
        for category, total in services.summary_by_category(transactions):
            print(f"  {category:<10} {total:>9.2f} EUR")

    elif args.command == "backup":
        count = storage.backup(args.file, args.destination)
        print(f"Backed up {count} transactions to {args.destination}.")

    elif args.command == "import":
        rows, errors = storage.read_csv(args.csv_file)
        for row in rows:
            transactions = services.add_transaction(
                transactions, row.date, row.kind, row.category,
                row.amount, row.currency)
        storage.save(args.file, transactions)
        for message in errors:
            print(f"Skipped: {message}")
        print(f"Imported {len(rows)} rows, skipped {len(errors)}.")


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        run(args)
    except ValidationError as err:
        print(f"Error: {err}")
        sys.exit(1)
    except FileExistsError:
        print(f"Error: {args.destination} already exists; choose a new name.")
        sys.exit(1)


if __name__ == "__main__":
    main()
