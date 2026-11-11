import csv
import sqlite3
import json
import uuid
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def load_warehouse(source_dir, db_path, output_dir):
    source_dir = Path(source_dir)
    db_path = Path(db_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()
    counts = {}
    rejects = []
    start_time = datetime.now()

    customers = read_csv(source_dir / "customers.csv")
    products = read_csv(source_dir / "products.csv")
    orders = read_csv(source_dir / "orders.csv")
    items = read_csv(source_dir / "order_items.csv")

    counts["input_customers"] = len(customers)
    counts["input_products"] = len(products)
    counts["input_orders"] = len(orders)
    counts["input_order_items"] = len(items)

    customer_map = {}
    product_map = {}
    order_map = {}

    for row in customers:
        key = row.get("customer_id", "").strip()
        if key and key not in customer_map:
            customer_map[key] = row

    for row in products:
        key = row.get("product_id", "").strip()
        if key and key not in product_map:
            product_map[key] = row

    for row in orders:
        key = row.get("order_id", "").strip()
        if key and key not in order_map:
            order_map[key] = row

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")

    try:
        with con:
            con.executescript("""
                DROP TABLE IF EXISTS fact_sales;
                DROP TABLE IF EXISTS dim_customer;
                DROP TABLE IF EXISTS dim_product;
                DROP TABLE IF EXISTS dim_date;

                CREATE TABLE dim_customer (
                    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    city TEXT
                );

                CREATE TABLE dim_product (
                    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL UNIQUE,
                    product_name TEXT NOT NULL,
                    category TEXT
                );

                CREATE TABLE dim_date (
                    date_key INTEGER PRIMARY KEY,
                    full_date TEXT NOT NULL UNIQUE,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    day INTEGER NOT NULL
                );

                CREATE TABLE fact_sales (
                    sales_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_item_id TEXT NOT NULL UNIQUE,
                    order_id TEXT NOT NULL,
                    customer_key INTEGER NOT NULL,
                    product_key INTEGER NOT NULL,
                    date_key INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    discount REAL NOT NULL,
                    gross_sales REAL NOT NULL,
                    net_sales REAL NOT NULL,
                    FOREIGN KEY(customer_key) REFERENCES dim_customer(customer_key),
                    FOREIGN KEY(product_key) REFERENCES dim_product(product_key),
                    FOREIGN KEY(date_key) REFERENCES dim_date(date_key)
                );

                CREATE INDEX idx_sales_date ON fact_sales(date_key);
                CREATE INDEX idx_sales_customer ON fact_sales(customer_key);
                CREATE INDEX idx_sales_product ON fact_sales(product_key);
            """)

            for key, row in sorted(customer_map.items()):
                if not row.get("customer_name", "").strip():
                    continue
                con.execute(
                    "INSERT INTO dim_customer(customer_id,customer_name,city) VALUES(?,?,?)",
                    (key, row["customer_name"].strip(), row.get("city", ""))
                )

            for key, row in sorted(product_map.items()):
                if not row.get("product_name", "").strip():
                    continue
                con.execute(
                    "INSERT INTO dim_product(product_id,product_name,category) VALUES(?,?,?)",
                    (key, row["product_name"].strip(), row.get("category", ""))
                )

            customer_keys = dict(con.execute(
                "SELECT customer_id,customer_key FROM dim_customer"
            ))
            product_keys = dict(con.execute(
                "SELECT product_id,product_key FROM dim_product"
            ))

            valid_orders = {}
            for order_id, row in order_map.items():
                try:
                    customer_id = row["customer_id"].strip()
                    order_date = datetime.strptime(row["order_date"], "%Y-%m-%d").date()
                    if customer_id not in customer_keys:
                        raise ValueError("Unknown customer reference")
                    valid_orders[order_id] = (customer_id, order_date)
                    date_key = int(order_date.strftime("%Y%m%d"))
                    con.execute("""
                        INSERT OR IGNORE INTO dim_date
                        (date_key,full_date,year,month,day) VALUES(?,?,?,?,?)
                    """, (date_key, order_date.isoformat(),
                          order_date.year, order_date.month, order_date.day))
                except Exception as exc:
                    rejects.append({
                        "source_record": json.dumps(row),
                        "reason": f"Invalid order: {exc}"
                    })

            seen = set()
            accepted = 0
            for row in items:
                try:
                    item_id = row["order_item_id"].strip()
                    if not item_id:
                        raise ValueError("Missing order_item_id")
                    if item_id in seen:
                        raise ValueError("Duplicate order_item_id")
                    seen.add(item_id)

                    order_id = row["order_id"].strip()
                    product_id = row["product_id"].strip()
                    if order_id not in valid_orders:
                        raise ValueError("Unknown or invalid order reference")
                    if product_id not in product_keys:
                        raise ValueError("Unknown product reference")

                    quantity = int(row["quantity"])
                    unit_price = float(row["unit_price"])
                    discount = float(row["discount"])

                    if quantity <= 0:
                        raise ValueError("Quantity must be positive")
                    if unit_price < 0 or discount < 0:
                        raise ValueError("Price and discount cannot be negative")

                    customer_id, order_date = valid_orders[order_id]
                    gross = round(quantity * unit_price, 2)
                    if discount > gross:
                        raise ValueError("Discount cannot exceed gross sales")
                    net = round(gross - discount, 2)
                    date_key = int(order_date.strftime("%Y%m%d"))

                    con.execute("""
                        INSERT INTO fact_sales
                        (order_item_id,order_id,customer_key,product_key,date_key,
                         quantity,unit_price,discount,gross_sales,net_sales)
                        VALUES(?,?,?,?,?,?,?,?,?,?)
                    """, (
                        item_id, order_id, customer_keys[customer_id],
                        product_keys[product_id], date_key,
                        quantity, unit_price, discount, gross, net
                    ))
                    accepted += 1
                except Exception as exc:
                    rejects.append({
                        "source_record": json.dumps(row),
                        "reason": str(exc)
                    })

            counts["accepted_fact_rows"] = accepted
            counts["rejected_rows"] = len(rejects)
            counts["dimension_customers"] = con.execute(
                "SELECT COUNT(*) FROM dim_customer").fetchone()[0]
            counts["dimension_products"] = con.execute(
                "SELECT COUNT(*) FROM dim_product").fetchone()[0]
            counts["dimension_dates"] = con.execute(
                "SELECT COUNT(*) FROM dim_date").fetchone()[0]
            counts["warehouse_fact_rows"] = con.execute(
                "SELECT COUNT(*) FROM fact_sales").fetchone()[0]
            counts["net_sales_total"] = round(con.execute(
                "SELECT COALESCE(SUM(net_sales),0) FROM fact_sales"
            ).fetchone()[0], 2)

            fk_errors = con.execute("PRAGMA foreign_key_check").fetchall()
            if fk_errors:
                raise RuntimeError(f"Foreign key validation failed: {fk_errors}")

        ended = datetime.now(timezone.utc).isoformat()
        report = {
            "run_id": run_id,
            "status": "SUCCESS",
            "started_at": started,
            "ended_at": ended,
            "duration_seconds": round((datetime.now() - start_time).total_seconds(), 3),
            "counts": counts,
            "foreign_key_errors": 0
        }

        with open(output_dir / "rejected_records.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["source_record", "reason"])
            writer.writeheader()
            writer.writerows(rejects)

        with open(output_dir / "run_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logging.info("Run %s completed", run_id)
        logging.info("Accepted fact rows: %s", accepted)
        logging.info("Rejected rows: %s", len(rejects))
        logging.info("Net sales: %.2f", counts["net_sales_total"])
        return report

    except Exception:
        con.rollback()
        logging.exception("Pipeline failed")
        raise
    finally:
        con.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data")
    parser.add_argument("--db", default="outputs/retail_warehouse.db")
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()
    load_warehouse(args.data, args.db, args.output)
