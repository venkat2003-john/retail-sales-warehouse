
# Retail Sales Warehouse - Data Dictionary

## 1. Fact Table: fact_sales

**Grain:** One row represents one product line in one customer order.

| Column | Description |
|---|---|
| sales_key | Unique surrogate key for each sales record |
| order_item_id | Unique source order item identifier |
| order_id | Source order identifier |
| customer_key | Foreign key to dim_customer |
| product_key | Foreign key to dim_product |
| date_key | Foreign key to dim_date |
| quantity | Number of products sold |
| unit_price | Price per product |
| discount | Discount amount |
| gross_sales | Quantity multiplied by unit price |
| net_sales | Gross sales minus discount |

## 2. Dimension Table: dim_customer

| Column | Description |
|---|---|
| customer_key | Customer surrogate primary key |
| customer_id | Original customer identifier |
| customer_name | Customer name |
| city | Customer city |

## 3. Dimension Table: dim_product

| Column | Description |
|---|---|
| product_key | Product surrogate primary key |
| product_id | Original product identifier |
| product_name | Product name |
| category | Product category |

## 4. Dimension Table: dim_date

| Column | Description |
|---|---|
| date_key | Date key in YYYYMMDD format |
| full_date | Complete calendar date |
| year | Calendar year |
| month | Calendar month |
| day | Day of month |

## 5. Business Measures

- Gross Sales = Quantity × Unit Price
- Net Sales = Gross Sales − Discount
- Total Revenue = Sum of Net Sales
- Total Quantity Sold = Sum of Quantity

## 6. Warehouse Design

- Architecture: Star Schema
- Database: SQLite
- ETL Language: Python
- Source Format: CSV
- Load Strategy: Full Refresh
- Data Quality: Validation and rejected-record logging
