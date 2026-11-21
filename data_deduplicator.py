"""Remove duplicate rows from a CSV file, keeping the first occurrence.

Two rows are duplicates when they have the same values in all key columns.
"""
import argparse
import csv
import sys


def deduplicate_csv(input_path, output_path, key_columns):
    """Write unique rows to output_path. Returns (rows_read, rows_written)."""
    seen = set()
    rows_read = 0
    rows_written = 0

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames or []
        missing = [col for col in key_columns if col not in header]
        if missing:
            raise ValueError(f"Key column(s) not found in CSV header: {', '.join(missing)}")

        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()
            for row in reader:
                rows_read += 1
                key = tuple(row[col] for col in key_columns)
                if key in seen:
                    continue
                seen.add(key)
                writer.writerow(row)
                rows_written += 1

    return rows_read, rows_written


def main():
    parser = argparse.ArgumentParser(description="Deduplicate CSV rows based on key columns")
    parser.add_argument("input_csv", help="Input CSV file path")
    parser.add_argument("output_csv", help="Output CSV file path")
    parser.add_argument("--keys", nargs="+", required=True, help="Key columns used to detect duplicates")
    args = parser.parse_args()

    try:
        rows_read, rows_written = deduplicate_csv(args.input_csv, args.output_csv, args.keys)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    removed = rows_read - rows_written
    print(f"Read {rows_read} rows, removed {removed} duplicate(s), wrote {rows_written} to {args.output_csv}")


if __name__ == "__main__":
    main()
