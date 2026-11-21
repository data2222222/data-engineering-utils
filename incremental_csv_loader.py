"""Incrementally load a CSV file into a PostgreSQL table.

Only rows whose unique key is not already in the table are inserted, so the
same file can be loaded repeatedly without creating duplicates.

The password is read from the PGPASSWORD environment variable so it doesn't
end up in your shell history.
"""
import argparse
import csv
import os
import sys

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values


def load_incremental_csv(db_config, csv_path, table_name, unique_key):
    """Insert new rows and return how many were inserted."""
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        columns = reader.fieldnames or []
        if unique_key not in columns:
            raise ValueError(f"Unique key column '{unique_key}' not found in CSV header")
        rows = list(reader)

    conn = psycopg2.connect(**db_config)
    try:
        with conn, conn.cursor() as cur:
            # Identifiers are quoted with psycopg2.sql to avoid SQL injection.
            cur.execute(
                sql.SQL("SELECT {} FROM {}").format(sql.Identifier(unique_key), sql.Identifier(table_name))
            )
            # Compare as strings: CSV values are text, database values may be ints.
            existing_keys = {str(r[0]) for r in cur.fetchall()}

            new_rows = []
            seen_in_file = set()
            for row in rows:
                key = row[unique_key]
                if key in existing_keys or key in seen_in_file:
                    continue
                seen_in_file.add(key)
                new_rows.append(tuple(row[col] if row[col] != "" else None for col in columns))

            if new_rows:
                insert = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                    sql.Identifier(table_name),
                    sql.SQL(", ").join(sql.Identifier(c) for c in columns),
                )
                execute_values(cur, insert.as_string(cur), new_rows)
    finally:
        conn.close()

    return len(new_rows)


def main():
    parser = argparse.ArgumentParser(description="Incrementally load a CSV file into PostgreSQL")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--user", required=True)
    parser.add_argument("--dbname", required=True)
    parser.add_argument("csv_path", help="CSV file path")
    parser.add_argument("table_name", help="Target table name")
    parser.add_argument("unique_key", help="Unique key column name")
    args = parser.parse_args()

    db_config = {
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "password": os.environ.get("PGPASSWORD"),
        "dbname": args.dbname,
    }
    try:
        inserted = load_incremental_csv(db_config, args.csv_path, args.table_name, args.unique_key)
    except (ValueError, psycopg2.Error) as e:
        print(f"Error: {e}")
        sys.exit(1)

    if inserted:
        print(f"Inserted {inserted} new row(s) into {args.table_name}.")
    else:
        print("No new rows to insert.")


if __name__ == "__main__":
    main()
