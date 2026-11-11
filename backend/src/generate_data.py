
import csv
import random
from pathlib import Path
from datetime import date, timedelta

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def save_csv(filename, rows):
    with open(DATA_DIR / filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

customers = [
    {
        "customer_id": f"C{i:04}",
        "customer_name": f"Customer {i}",
        "city": random.choice(["Hyderabad", "Nandyal", "Chennai", "Bengaluru"])
    }
    for i in range(1, 501)
]

products = [
    {
        "product_id": f"P{i:03}",
        "product_name": f"Product {i}",
        "category": random.choice(["Electronics", "Clothing", "Home", "Books"])
    }
    for i in range(1, 51)
]

orders = []
order_items = []
start_date = date(2026, 1, 1)

for i in range(1, 3001):
    order_id = f"O{i:05}"

    orders.append({
        "order_id": order_id,
        "customer_id": random.choice(customers)["customer_id"],
        "order_date": (
            start_date + timedelta(days=random.randint(0, 300))
        ).isoformat()
    })

    for j in range(random.randint(1, 4)):
        product = random.choice(products)

        order_items.append({
            "order_item_id": f"OI{i:05}_{j+1}",
            "order_id": order_id,
            "product_id": product["product_id"],
         "quantity": random.randint(1, 5),
         "unit_price": round(random.uniform(50, 5000), 2),
         "discount": 0
        })

# Add invalid records for data-quality testing
order_items.append({
    "order_item_id": "BAD001",
    "order_id": "O00001",
    "product_id": "UNKNOWN",
    "quantity": 1,
    "unit_price": 100,
    "discount": 0
})

order_items.append({
    "order_item_id": "BAD002",
    "order_id": "O00002",
    "product_id": "P001",
    "quantity": -5,
    "unit_price": 100,
    "discount": 0
})

save_csv("customers.csv", customers)
save_csv("products.csv", products)
save_csv("orders.csv", orders)
save_csv("order_items.csv", order_items)

print("DATA GENERATION SUCCESSFUL")
print("Customers:", len(customers))
print("Products:", len(products))
print("Orders:", len(orders))
print("Order items:", len(order_items))
