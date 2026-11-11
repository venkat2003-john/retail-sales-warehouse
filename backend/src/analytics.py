
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "outputs" / "retail_warehouse.db"
SQL_FILE = ROOT / "sql" / "analytics.sql"

def run_analytics():
    if not DB.exists():
        raise FileNotFoundError(f"Warehouse database not found: {DB}")

    connection = sqlite3.connect(DB)

    try:
        sql_text = SQL_FILE.read_text(encoding="utf-8")

        queries = [
            query.strip()
            for query in sql_text.split(";")
            if query.strip()
        ]

        for number, query in enumerate(queries, start=1):
            print(f"\n{'=' * 55}")
            print(f"ANALYTICAL REPORT {number}")
            print("=" * 55)

            cursor = connection.execute(query)
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()

            print(" | ".join(columns))
            print("-" * 55)

            for row in rows:
                print(" | ".join(str(value) for value in row))

    finally:
        connection.close()

if __name__ == "__main__":
    run_analytics()
