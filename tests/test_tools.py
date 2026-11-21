import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from csv_schema_validator import validate_csv
from data_deduplicator import deduplicate_csv
from data_profiler import profile_csv
from schema_to_sql import schema_to_sql

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
CSV_PATH = os.path.join(EXAMPLES, "customers.csv")
SCHEMA_PATH = os.path.join(EXAMPLES, "schema.json")


def test_validator_finds_bad_rows():
    errors = validate_csv(CSV_PATH, SCHEMA_PATH)
    assert "Row 6: required column 'email' is empty" in errors
    assert "Row 6: column 'age' expected integer, got 'abc'" in errors
    assert len(errors) == 2


def test_validator_accepts_negative_integers(tmp_path):
    data = tmp_path / "data.csv"
    data.write_text("id\n-5\n")
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"properties": {"id": {"type": "integer"}}}))
    assert validate_csv(str(data), str(schema)) == []


def test_deduplicator_removes_duplicates(tmp_path):
    out = tmp_path / "out.csv"
    rows_read, rows_written = deduplicate_csv(CSV_PATH, str(out), ["id"])
    assert (rows_read, rows_written) == (5, 4)
    with open(out, newline="") as f:
        ids = [row["id"] for row in csv.DictReader(f)]
    assert ids == ["1", "2", "3", "4"]


def test_deduplicator_rejects_unknown_key(tmp_path):
    try:
        deduplicate_csv(CSV_PATH, str(tmp_path / "out.csv"), ["nope"])
    except ValueError as e:
        assert "nope" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_profiler_stats():
    total, stats = profile_csv(CSV_PATH)
    assert total == 5
    assert stats["balance"]["type"] == "numeric"
    assert stats["balance"]["max"] == 230.75
    assert stats["age"]["missing"] == 1
    assert stats["age"]["type"] == "text"  # 'abc' makes it non-numeric
    assert stats["name"]["distinct"] == 4


def test_schema_to_sql_postgres_and_mysql():
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    pg = schema_to_sql(schema, "customers")
    assert pg.startswith('CREATE TABLE "customers" (')
    assert '"balance" DOUBLE PRECISION' in pg
    my = schema_to_sql(schema, "customers", "mysql")
    assert "`name` VARCHAR(255)" in my
