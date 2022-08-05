from datetime import datetime
from itertools import chain
from sys import exit
from typing import List, Tuple

from click import confirm, echo
from psycopg2 import connect, errors, extras


def get_db_cursor(connection_string):
    """
    Connect to a database and get a cursor or exit if unable to connect
    """
    try:
        db = connect(connection_string)
        echo(f"Connected to database: {connection_string}")
        return db.cursor()
    except errors.Error as e:
        echo(f"Could not connect to database: {connection_string}\n{e}")
        exit(1)


def get_modified_date_stats(db) -> List[Tuple[str, datetime, datetime]]:
    """
    Print some stats about the modified_date column on all tables of a database
    """

    # Ensure the stat function exists
    db.execute(
        """
        CREATE OR REPLACE FUNCTION get_min_max_modified_date()
        RETURNS TABLE (table_name text,
                    max_value timestamp,
                    min_value timestamp)
        LANGUAGE plpgsql
        AS $$
            DECLARE
                r record;
            BEGIN
                FOR r IN
                    SELECT i.table_name, i.table_schema
                    FROM information_schema.tables i
                    WHERE i.table_name in (
                        SELECT c.table_name
                        FROM information_schema.columns c
                        WHERE c.table_schema = 'public'
                        AND c.column_name = 'modified_date'
                        GROUP BY c.table_name
                    )
                LOOP
                    execute format (
                        'SELECT min(modified_date) FROM %I.%I',
                        r.table_schema, r.table_name
                    ) INTO min_value;
                    execute format (
                        'SELECT max(modified_date) FROM %I.%I',
                        r.table_schema, r.table_name
                    ) INTO max_value;
                    table_name := r.table_name;
                    RETURN next;
                END LOOP;
            END
        $$;
        -- usage:
        -- SELECT * FROM get_min_max_modified_date()
    """
    )

    # Call the function
    db.callproc("get_min_max_modified_date")

    # Return only tables with existing modified_date values
    return [row for row in db.fetchall() if all(*row)]


def fix_modified_date(
    db,
    backup_db,
    bad_modified_date,
    table,
    ignore_count_mismatch=False,
) -> None:
    """
    Fix the modified_date column in a table by copying the original value from a backup instance
    """
    ids_query = f"SELECT id FROM {table} WHERE modified_date = %s"
    db.execute(ids_query, (bad_modified_date,))
    ids = tuple(chain(*db.fetchall()))

    if len(ids) == 0:
        echo(f"No rows found with modified_date = {bad_modified_date}")
        exit(0)

    # Get the original modified_date from the backup database
    dates_query = f"SELECT modified_date, id FROM {table} WHERE id IN %s"
    backup_db.execute(dates_query, (ids,))
    dates = backup_db.fetchall()

    if len(ids) != len(dates) and ignore_count_mismatch is False:
        echo(
            f"ID count mismatch between target and source databases in table `{table}`.\n"
            "This is likely to happen when rows have been deleted since the backup was taken.\n"
            "Run again with option --ignore-count-mismatch to ignore this error and continue."
        )
        exit(1)

    if not confirm(f"About to update {len(dates)} rows in table `{table}`. Continue?"):
        echo("Abotring...")
        exit(1)

    update_query = f"UPDATE {table} SET modified_date = %s WHERE id = %s"
    db.executemany(update_query, dates)

    echo(f"Done! Updated {len(dates)} rows in table `{table}`\n{{dates}}")
