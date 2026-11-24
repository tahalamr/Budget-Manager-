"""Start the program with:  python run.py <command> ...   (see: python run.py --help)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from budget_manager.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
