# Retail Sales Analytics Warehouse

## 1. Project Overview

The Retail Sales Analytics Warehouse is a Python-based data engineering project that transforms transactional retail data into a dimensional data warehouse for business analysis.

The project uses a Star Schema design and SQLite to store sales facts and related dimensions. It includes data generation, validation, transformation, loading, automated testing, and SQL-based analytical reporting.

## 2. Architecture

CSV Transactional Sources  
→ Python Data Generation  
→ Data Validation and ETL  
→ SQLite Star Schema Warehouse  
→ SQL Analytics and Business Reports

## 3. Technology Stack

- Python 3
- SQLite
- SQL
- Pandas / Python CSV processing
- Unittest
- PowerShell

## 4. Data Sources

The project uses four transactional CSV files:

- customers.csv
- products.csv
- orders.csv
- order_items.csv

A data generator creates sample retail data and includes deliberately invalid records to test data quality rules.

## 5. Dimensional Data Model

The warehouse uses a Star Schema.

**Dimension tables:**
- dim_customer — customer information and customer surrogate keys.
- dim_product — product information and product surrogate keys.
- dim_date — calendar information and date keys.

**Fact table:**
- fact_sales — sales transactions at order-item level.

**Fact grain:** One row represents one product line within one customer order.

**Measures:**
- Quantity
- Unit price
- Discount
- Gross sales
- Net sales

## 6. Data Quality and Validation

The pipeline validates:
- Required fields.
- Customer and product references.
- Duplicate order-item identifiers.
- Positive quantities.
- Valid prices and discounts.
- Foreign-key integrity.

Invalid records are stored in `outputs/rejected_records.csv`.

## 7. Idempotency and Monitoring

The pipeline uses a full-refresh approach: it rebuilds the warehouse from the same source files on each run.

It generates a run report containing:
- Run ID and timestamps.
- Accepted and rejected record counts.
- Dimension record counts.
- Net sales.
- Execution duration.

Run details are stored in `outputs/run_report.json`.

## 8. Analytical Reports

The SQL analytics module provides:

1. Overall sales performance.
2. Top 10 products by revenue.
3. Sales by customer city.
4. Monthly revenue analysis.

## 9. Project Execution

Run these commands from the project root directory:

```powershell
python .\src\generate_data.py
python .\src\pipeline.py
python -m unittest discover -s tests -v
python .\src\analytics.py
```

## 10. Project Structure

```text
retail-sales-warehouse/
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
│
├── src/
│   ├── generate_data.py
│   ├── pipeline.py
│   └── analytics.py
│
├── sql/
│   └── analytics.sql
│
├── tests/
│   └── test_pipeline.py
│
├── outputs/
│   ├── retail_warehouse.db
│   ├── rejected_records.csv
│   └── run_report.json
│
└── README.md
```

## 11. Testing

Automated tests use Python's unittest framework to verify:
- Pipeline execution and data quality.
- Handling of empty input files.
- Repeat-run consistency.
- Warehouse foreign-key integrity.

## 12. Conclusion

This project demonstrates an end-to-end retail data engineering workflow, including dimensional modelling, ETL processing, data quality validation, automated testing, and analytical reporting.