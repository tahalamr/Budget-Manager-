"""Run with:  python -m unittest discover -s tests -v"""
import contextlib
import io
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from budget_manager import cli, services, storage                  # noqa: E402
from budget_manager.validation import ValidationError, validate_amount  # noqa: E402

SAMPLE = os.path.join(HERE, "..", "data", "sample_transactions.csv")


def run_cli(*argv):
    """Run the CLI and return (printed text, exit code)."""
    out, code = io.StringIO(), 0
    with contextlib.redirect_stdout(out):
        try:
            cli.main(list(argv))
        except SystemExit as exit_:
            code = exit_.code
    return out.getvalue(), code


class NormalCase(unittest.TestCase):
    """Normal case: add an income and an expense, then check balance and summary."""

    def test_add_list_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            data = os.path.join(folder, "t.json")
            run_cli("--file", data, "add", "2026-09-01", "income", "salary", "1000")
            text, code = run_cli("--file", data, "add", "2026-09-02", "expense", "food", "18.50")
            self.assertEqual((text.strip(), code), ("Added T002.", 0))
            summary, _ = run_cli("--file", data, "summary")
            self.assertIn("Balance: 981.50 EUR", summary)
            self.assertIn("food", summary)


class BoundaryCases(unittest.TestCase):
    """Boundary 1: amounts at and around zero. Boundary 2: malformed input."""

    def test_amount_boundaries(self):
        self.assertEqual(validate_amount("0.01"), 0.01)        # smallest valid
        for bad in ("0", "-5", "abc", "", "nan", "inf"):
            with self.assertRaises(ValidationError, msg=bad):
                validate_amount(bad)

    def test_invalid_input_gives_error_and_saves_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            data = os.path.join(folder, "t.json")
            for args in (("2026-13-45", "expense", "food", "5"),   # impossible date
                         ("2026-09-01", "gift", "food", "5"),      # unknown kind
                         ("2026-09-01", "expense", "pizza", "5"),  # unknown category
                         ("2026-09-01", "expense", "food", "-5")): # negative amount
                text, code = run_cli("--file", data, "add", *args)
                self.assertEqual(code, 1)
                self.assertTrue(text.startswith("Error:"))
            self.assertFalse(os.path.exists(data))


class Persistence(unittest.TestCase):
    def test_save_load_round_trip(self):
        data = services.add_transaction([], "2026-09-01", "income", "salary", "10")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "t.json")
            storage.save(path, data)
            self.assertEqual(storage.load(path), data)

    def test_import_sample_reports_bad_rows_and_backup_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            data = os.path.join(folder, "t.json")
            text, _ = run_cli("--file", data, "import", SAMPLE)
            self.assertIn("Skipped: Row 6: amount must be > 0", text)
            self.assertIn("Imported 4 rows, skipped 5.", text)
            target = os.path.join(folder, "b.json")
            self.assertEqual(run_cli("--file", data, "backup", target)[1], 0)
            self.assertEqual(run_cli("--file", data, "backup", target)[1], 1)  # exists


if __name__ == "__main__":
    unittest.main()
