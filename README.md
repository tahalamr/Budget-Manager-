# Budget Manager (Release 1)

A small command-line tool to record income and expenses, see your balance and see
where your money goes. It follows the Session 12 command-line pattern (argparse
commands, JSON file, backup in "x" mode). Python 3.9+, no extra packages.

## Setup
1. Install Python 3.9 or newer.
2. Unzip the project and open a terminal inside the `budget-manager` folder.

## Run
```
python run.py --help
python run.py import data/sample_transactions.csv
python run.py add 2026-09-20 expense food 23.40
python run.py list
python run.py list --kind expense --month 2026-09
python run.py summary
python run.py backup backup.json
```
Data is saved in `transactions.json` in the current folder (change it with
`--file other.json`, placed before the command).

## Example
The sample file has 4 valid rows and 5 deliberately invalid ones:
```
$ python run.py import data/sample_transactions.csv
Skipped: Row 6: amount must be > 0, got -5.0.
Skipped: Row 7: category must be one of food, rent, transport, salary, leisure, other; got 'pizza'.
Skipped: Row 8: date must be YYYY-MM-DD (a real date), got '2026-13-45'.
Skipped: Row 9: amount must be a number, got 'abc'.
Skipped: Row 10: expected 6 columns, got 4.
Imported 4 rows, skipped 5.
$ python run.py add 2026-09-20 expense food 23.40
Added T005.
$ python run.py summary
Transactions: 5
Balance: 746.10 EUR
  rent          700.00 EUR
  food           41.90 EUR
  transport      12.00 EUR
```
Invalid input prints an actionable error and exits with code 1, for example
`Error: date must be YYYY-MM-DD (a real date), got '2026-13-45'.`

## Test
```
python -m unittest discover -s tests -v
```
5 tests: 1 normal case (add, list, summary), 2 boundary cases (amounts at and around
zero; malformed input is rejected and nothing is saved), a save/load round trip, and
a sample-file import plus the backup that never overwrites.

## Project layout
| File | Responsibility |
|---|---|
| `src/budget_manager/models.py` | Transaction record and allowed values |
| `src/budget_manager/validation.py` | All input checks, clear error messages |
| `src/budget_manager/services.py` | Add, filter, balance, summary (no input/output) |
| `src/budget_manager/storage.py` | JSON load/save, backup, CSV import |
| `src/budget_manager/cli.py` | argparse commands only |

## Known limitations
- Currencies are never converted: the balance and summary show EUR only.
- Transactions cannot be edited or deleted (the undo stretch challenge is not done).
- Allowed categories and currencies are fixed in `models.py`.
- `import` skips bad CSV rows instead of repairing them; fix the CSV and import again.
- Importing the same CSV twice adds the rows twice (new ids each time).
