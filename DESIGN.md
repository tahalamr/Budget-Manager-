# Design rationale

I kept the command-line style from the Session 12 example (argparse with one subcommand per action) and split the program into models, validation, services, storage and CLI so each file
has one job and the business rules can be tested without typing into a menu. The most
important choice is validating only at the boundaries: a transaction is checked once,
when it is built from user input or from a CSV row, and after that every other module
can trust it. Invalid data is rejected with a specific message (for example
"Row 6: amount must be > 0") instead of being silently corrected, because a silent
fix would hide a mistake from the user. Saving writes to a temporary file and then
swaps it in, so a crash cannot leave a half-written transactions file.
