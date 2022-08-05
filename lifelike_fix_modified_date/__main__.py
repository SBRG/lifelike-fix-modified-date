"""
lifelike-fix-modified-date

Fixes all modified_date columns in a database to match the values in a backup database.
This is useful when a database migration updates modified_date column in a table unintentionally.

Usage:
  lifelike-fix-modified-date (-h | --help | --version)
  lifelike-fix-modified-date stats --database=<uri>
  lifelike-fix-modified-date fix <bad_modified_date> --database=<uri> --backup-database=<uri>
                                                     [--table=<table>] [--ignore-count-mismatch]

Generic options:
  -h --help                 Show this screen.
  --version                 Show version.
  --database=<uri>          Postgres URI of the target database.

Fix options:
  --backup-database=<uri>   Postgres URI of the backup (source) database.
  --table=<table>           Table name to fix. [default: files]
  --ignore-coount-mismatch  Ignore row count mismatch between backup source and target databases
                            (e.g. if there are deleted rows since the backup was taken).

Examples:
  lifelike-fix-modified-date stats --database=postgres://user:pass@localhost:5432/db
  lifelike-fix-modified-date fix "2022-08-03 18:21:49.498104" --database=postgres://user:pass@host:5432/db --backup-database=postgres://user:pass@backup-host:5432/db
"""
from sys import exit

from click import echo
from docopt import docopt
from psycopg2 import errors

from . import get_db_cursor, get_modified_date_stats, fix_modified_date
from .__about__ import __version__

args = docopt(__doc__, version=__version__)

# Connect to the Postgres database
db = get_db_cursor(args["--database"])

if args["stats"]:
    stats = get_modified_date_stats(db)

    if len(stats) == 0:
        echo("No tables with modified_date values found. Empty database?")
    else:
        echo(
            "Stats about modified_date column in target database:\n\n"
            f"{'Table':<30} {'Min modified_date':<30} {'Max modified_date':30}\n{'-' * 90}\n"
            + "\n".join(
                ["{:<30} {:<30} {:<30}".format(*map(str, row)) for row in stats]
            )
        )

elif args["fix"]:
    echo(f"Connecting to backup database: {args['--backup-database']}\n")
    backup_db = get_db_cursor(args["--backup-database"])

    try:
        fix_modified_date(
            db,
            backup_db,
            args["<bad_modified_date>"],
            args["--table"],
            ignore_count_mismatch=args["--ignore-count-mismatch"],
        )
    except errors.InvalidDatetimeFormat:
        echo(f"Invalid datetime provided: {args['<bad_modified_date>']}")
        exit(1)
    except errors.UndefinedTable:
        echo(f"Provided table does not exist: {args['--table']}")
        exit(1)
    except errors.Error as e:
        echo(f"Database Error: {e}")
        exit(1)
