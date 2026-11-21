# Data Engineering Utils

Small command-line tools for everyday CSV and database chores: validating files, profiling columns, removing duplicates, generating table DDL, and loading data into PostgreSQL incrementally.

Each tool is a single Python script built on the standard library (only the PostgreSQL loader needs `psycopg2`). They can also be imported and used as functions.

| Tool | What it does |
|------|--------------|
| `csv_schema_validator.py` | Checks a CSV against a JSON schema (required columns, integer/number types) |
| `data_profiler.py` | Prints missing values, distinct counts, and min/max/mean for each column |
| `data_deduplicator.py` | Removes duplicate rows based on one or more key columns |
| `schema_to_sql.py` | Generates a `CREATE TABLE` statement for PostgreSQL or MySQL |
| `incremental_csv_loader.py` | Inserts only new rows (by unique key) into a PostgreSQL table |

## Setup

```bash
git clone https://github.com/data2222222/data-engineering-utils.git
cd data-engineering-utils
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Requires Python 3.9+. The `examples/` folder has a sample CSV and schema you can try every command with.

## Usage

### Validate a CSV against a schema

```bash
python csv_schema_validator.py examples/customers.csv examples/schema.json
```
```
Validation failed with 2 error(s):
  - Row 6: required column 'email' is empty
  - Row 6: column 'age' expected integer, got 'abc'
```
Exits with status 1 on failure, so it can be used as a check in a pipeline.

### Profile a CSV

```bash
python data_profiler.py examples/customers.csv
```
```
Column: balance (numeric)
  Missing:  0
  Distinct: 4
  Min:      12.3
  Max:      230.75
  Mean:     114.3
```

### Remove duplicates

```bash
python data_deduplicator.py examples/customers.csv customers_deduped.csv --keys id
```
The first occurrence of each key is kept. Pass several columns to `--keys` for a composite key.

### Generate SQL from a schema

```bash
python schema_to_sql.py examples/schema.json customers --dialect postgresql
```
```sql
CREATE TABLE "customers" (
  "id" INTEGER,
  "name" VARCHAR,
  "email" VARCHAR,
  "age" INTEGER,
  "balance" DOUBLE PRECISION
);
```

### Load new rows into PostgreSQL

```bash
export PGPASSWORD=your_password
python incremental_csv_loader.py --host localhost --user postgres --dbname mydb \
    examples/customers.csv customers id
```
Rows whose `id` already exists in the table (or appears earlier in the file) are skipped, so running it twice is safe. Table and column names are quoted with `psycopg2.sql`, and all inserts run in one transaction.

## Schema format

```json
{
  "required": ["id", "name"],
  "properties": { "id": {"type": "integer"}, "balance": {"type": "number"} },
  "fields": [ {"name": "id", "type": "integer"}, {"name": "balance", "type": "number"} ]
}
```
`required` and `properties` are used by the validator; `fields` is used by `schema_to_sql.py`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
