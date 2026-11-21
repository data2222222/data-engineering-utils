"""Generate a SQL CREATE TABLE statement from a JSON field list.

Schema format:

    {
      "fields": [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "string"}
      ]
    }

Supported types: string, integer, number, boolean (anything else becomes TEXT).
"""
import argparse
import json

TYPE_MAP = {
    "postgresql": {"string": "VARCHAR", "integer": "INTEGER", "number": "DOUBLE PRECISION", "boolean": "BOOLEAN"},
    "mysql": {"string": "VARCHAR(255)", "integer": "INT", "number": "DOUBLE", "boolean": "BOOLEAN"},
}


def quote_identifier(name, dialect):
    # PostgreSQL uses "double quotes", MySQL uses `backticks`.
    if dialect == "mysql":
        return "`" + name.replace("`", "``") + "`"
    return '"' + name.replace('"', '""') + '"'


def schema_to_sql(schema, table_name, dialect="postgresql"):
    """Build the CREATE TABLE statement from an already-loaded schema dict."""
    type_map = TYPE_MAP[dialect]
    columns = []
    for field in schema.get("fields", []):
        sql_type = type_map.get(field.get("type", "string"), "TEXT")
        columns.append(f"  {quote_identifier(field['name'], dialect)} {sql_type}")

    table = quote_identifier(table_name, dialect)
    return f"CREATE TABLE {table} (\n" + ",\n".join(columns) + "\n);"


def main():
    parser = argparse.ArgumentParser(description="Generate SQL CREATE TABLE from a JSON schema")
    parser.add_argument("schema_path", help="Path to the JSON schema")
    parser.add_argument("table_name", help="Name of the table to create")
    parser.add_argument("--dialect", default="postgresql", choices=["postgresql", "mysql"], help="SQL dialect")
    args = parser.parse_args()

    with open(args.schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    print(schema_to_sql(schema, args.table_name, args.dialect))


if __name__ == "__main__":
    main()
