
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# Database location
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "backend" / "outputs" / "retail_warehouse.db"

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Retail Sales Dashboard")
st.caption("Insights from the Retail Sales Analytics Warehouse")

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()


@st.cache_data
def load_data():
    with sqlite3.connect(DB_PATH) as con:
        summary = pd.read_sql_query("""
            SELECT
                COUNT(DISTINCT order_id) AS total_orders,
                SUM(quantity) AS total_units,
                ROUND(SUM(net_sales), 2) AS total_revenue,
                COUNT(DISTINCT customer_key) AS total_customers
            FROM fact_sales
        """, con)

        products = pd.read_sql_query("""
            SELECT p.product_name,
                   ROUND(SUM(f.net_sales), 2) AS revenue
            FROM fact_sales f
            JOIN dim_product p
              ON f.product_key = p.product_key
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 10
        """, con)

        cities = pd.read_sql_query("""
            SELECT c.city,
                   ROUND(SUM(f.net_sales), 2) AS revenue
            FROM fact_sales f
            JOIN dim_customer c
              ON f.customer_key = c.customer_key
            GROUP BY c.city
            ORDER BY revenue DESC
        """, con)

        monthly = pd.read_sql_query("""
            SELECT d.year, d.month,
                   ROUND(SUM(f.net_sales), 2) AS revenue
            FROM fact_sales f
            JOIN dim_date d
              ON f.date_key = d.date_key
            GROUP BY d.year, d.month
            ORDER BY d.year, d.month
        """, con)

    return summary, products, cities, monthly


summary, products, cities, monthly = load_data()

# KPI cards
row = st.columns(4)
row[0].metric("Total Revenue", f"₹{summary.iloc[0]['total_revenue']:,.2f}")
row[1].metric("Total Orders", f"{summary.iloc[0]['total_orders']:,}")
row[2].metric("Units Sold", f"{summary.iloc[0]['total_units']:,}")
row[3].metric("Customers", f"{summary.iloc[0]['total_customers']:,}")

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("Top 10 Products by Revenue")
    st.bar_chart(products.set_index("product_name")["revenue"])

with right:
    st.subheader("City-wise Revenue")
    st.bar_chart(cities.set_index("city")["revenue"])

st.subheader("Monthly Revenue Trend")
monthly["month_name"] = monthly["month"].apply(
    lambda m: pd.Timestamp(2026, int(m), 1).strftime("%b")
)
monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month_name"]
st.line_chart(monthly.set_index("period")["revenue"])

st.divider()
st.subheader("Top Products Details")
st.dataframe(products, width="stretch")

st.caption("Data source: SQLite Retail Sales Warehouse")
