"""Validate a CSV file against a simple JSON schema.

The schema uses a small subset of JSON Schema:

    {
      "required": ["id", "name"],
      "properties": {
        "id":    {"type": "integer"},
        "price": {"type": "number"},
        "name":  {"type": "string"}
      }
    }

Exits with status 1 if any row fails validation.
"""
import argparse
import csv
import json
import sys


def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_csv(csv_path, schema_path):
    """Return a list of error messages. An empty list means the file is valid."""
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    required_columns = schema.get("required", [])
    column_types = schema.get("properties", {})

    errors = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        header = reader.fieldnames or []

        for col in required_columns:
            if col not in header:
                errors.append(f"Header: required column '{col}' is missing")

        # Row 1 is the header, so data starts at row 2 (matches spreadsheet numbering).
        for row_num, row in enumerate(reader, start=2):
            for col in required_columns:
                if col in header and row.get(col, "") == "":
                    errors.append(f"Row {row_num}: required column '{col}' is empty")

            for col, info in column_types.items():
                value = row.get(col)
                if value is None or value == "":
                    continue
                expected = info.get("type")
                if expected == "integer" and not is_integer(value):
                    errors.append(f"Row {row_num}: column '{col}' expected integer, got '{value}'")
                elif expected == "number" and not is_number(value):
                    errors.append(f"Row {row_num}: column '{col}' expected number, got '{value}'")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate a CSV file against a JSON schema")
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument("schema_path", help="Path to the JSON schema file")
    args = parser.parse_args()

    errors = validate_csv(args.csv_path, args.schema_path)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print("CSV validation passed.")


if __name__ == "__main__":
    main()
