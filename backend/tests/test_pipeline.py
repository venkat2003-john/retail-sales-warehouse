import csv
import unittest
import sqlite3
import tempfile
import shutil
from pathlib import Path

from src.pipeline import load_warehouse

ROOT = Path(__file__).resolve().parent.parent

class WarehouseTests(unittest.TestCase):

    def test_pipeline_and_data_quality(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            data = temp / "data"
            output = temp / "outputs"
            data.mkdir()

            for filename in [
                "customers.csv", "products.csv",
                "orders.csv", "order_items.csv"
            ]:
                shutil.copy(ROOT / "data" / filename, data / filename)

            db = output / "test.db"

            first = load_warehouse(data, db, output)

            self.assertEqual(first["status"], "SUCCESS")
            self.assertEqual(first["counts"]["rejected_rows"], 2)
            self.assertGreater(first["counts"]["accepted_fact_rows"], 0)

            connection = sqlite3.connect(db)

            fact_count = connection.execute(
                "SELECT COUNT(*) FROM fact_sales"
            ).fetchone()[0]

            self.assertEqual(
                fact_count, first["counts"]["accepted_fact_rows"]
            )

            foreign_key_errors = connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            self.assertEqual(foreign_key_errors, [])
            connection.close()

            # Rerun the same source and check repeatable results
            second = load_warehouse(data, db, output)

            self.assertEqual(
                first["counts"]["accepted_fact_rows"],
                second["counts"]["accepted_fact_rows"]
            )
            self.assertEqual(
                first["counts"]["net_sales_total"],
                second["counts"]["net_sales_total"]
            )

    def test_empty_input_files_are_rejected_or_handled(self):
        # An empty order-item batch must not silently create sales.
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            data = temp / "data"
            output = temp / "outputs"
            data.mkdir()

            for filename in [
                "customers.csv", "products.csv", "orders.csv"
            ]:
                shutil.copy(ROOT / "data" / filename, data / filename)

            (data / "order_items.csv").write_text(
                "order_item_id,order_id,product_id,quantity,unit_price,discount\n",
                encoding="utf-8"
            )

            report = load_warehouse(data, output / "empty.db", output)

            self.assertEqual(report["counts"]["accepted_fact_rows"], 0)
            self.assertEqual(report["counts"]["rejected_rows"], 0)

    def test_invalid_and_duplicate_records(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            data = temp / "data"
            output = temp / "outputs"
            data.mkdir()

            for filename in [
                "customers.csv", "products.csv",
                "orders.csv", "order_items.csv"
            ]:
                shutil.copy(ROOT / "data" / filename, data / filename)

            items_file = data / "order_items.csv"

            with open(items_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                first_valid_row = next(reader)

            extra_records = [
                first_valid_row,
                {
                    "order_item_id": "NULL001",
                    "order_id": "O00001",
                    "product_id": "P001",
                    "quantity": "",
                    "unit_price": "100",
                    "discount": "0"
                },
                {
                    "order_item_id": "BADNUM001",
                    "order_id": "O00001",
                    "product_id": "P001",
                    "quantity": "abc",
                    "unit_price": "100",
                    "discount": "0"
                },
                {
                    "order_item_id": "BADORDER001",
                    "order_id": "UNKNOWN_ORDER",
                    "product_id": "P001",
                    "quantity": "1",
                    "unit_price": "100",
                    "discount": "0"
                }
            ]

            with open(items_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerows(extra_records)

            report = load_warehouse(
                data, output / "edge_cases.db", output
            )

            self.assertEqual(report["status"], "SUCCESS")
            self.assertEqual(report["counts"]["rejected_rows"], 6)

            with open(
                output / "rejected_records.csv",
                newline="",
                encoding="utf-8"
            ) as f:
                rejected = list(csv.DictReader(f))

            reasons = [row["reason"] for row in rejected]

            self.assertTrue(any("Duplicate" in r for r in reasons))
            self.assertTrue(any("invalid literal" in r for r in reasons))
            self.assertTrue(any("Unknown or invalid order" in r for r in reasons))


    def test_sales_reconciliation(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            data = temp / "data"
            output = temp / "outputs"
            data.mkdir()

            for filename in [
                "customers.csv", "products.csv",
                "orders.csv", "order_items.csv"
            ]:
                shutil.copy(ROOT / "data" / filename, data / filename)

            db = output / "reconciliation.db"
            report = load_warehouse(data, db, output)

            connection = sqlite3.connect(db)

            result = connection.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(gross_sales), 0),
                    COALESCE(SUM(net_sales), 0),
                    COALESCE(SUM(quantity * unit_price), 0),
                    COALESCE(SUM(gross_sales - discount), 0)
                FROM fact_sales
            """).fetchone()

            connection.close()

            row_count, gross, net, calculated_gross, calculated_net = result

            self.assertEqual(
                row_count, report["counts"]["accepted_fact_rows"]
            )
            self.assertAlmostEqual(gross, calculated_gross, places=2)
            self.assertAlmostEqual(net, calculated_net, places=2)

if __name__ == "__main__":
    unittest.main()
