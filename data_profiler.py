"""Print a quick profile of every column in a CSV file.

For each column: missing values, distinct values, and (for numeric columns)
min, max and mean.
"""
import argparse
import csv


def profile_csv(csv_path):
    """Return (total_rows, stats) where stats maps column name to a dict of metrics."""
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        columns = reader.fieldnames or []
        stats = {}
        for col in columns:
            stats[col] = {"missing": 0, "distinct": set(), "numbers": [], "non_numeric": 0}

        total_rows = 0
        for row in reader:
            total_rows += 1
            for col in columns:
                value = row.get(col) or ""
                s = stats[col]
                if value == "":
                    s["missing"] += 1
                    continue
                s["distinct"].add(value)
                try:
                    s["numbers"].append(float(value))
                except ValueError:
                    s["non_numeric"] += 1

    result = {}
    for col in columns:
        s = stats[col]
        numbers = s["numbers"]
        is_numeric = len(numbers) > 0 and s["non_numeric"] == 0
        result[col] = {
            "missing": s["missing"],
            "distinct": len(s["distinct"]),
            "type": "numeric" if is_numeric else "text",
            "min": min(numbers) if is_numeric else None,
            "max": max(numbers) if is_numeric else None,
            "mean": sum(numbers) / len(numbers) if is_numeric else None,
        }
    return total_rows, result


def main():
    parser = argparse.ArgumentParser(description="Profile the columns of a CSV file")
    parser.add_argument("csv_path", help="Path to the CSV file")
    args = parser.parse_args()

    total_rows, result = profile_csv(args.csv_path)
    print(f"Total rows: {total_rows}\n")
    for col, s in result.items():
        print(f"Column: {col} ({s['type']})")
        print(f"  Missing:  {s['missing']}")
        print(f"  Distinct: {s['distinct']}")
        if s["type"] == "numeric":
            print(f"  Min:      {s['min']:g}")
            print(f"  Max:      {s['max']:g}")
            print(f"  Mean:     {s['mean']:.4g}")
        print()


if __name__ == "__main__":
    main()
