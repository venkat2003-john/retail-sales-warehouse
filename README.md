# Retail Sales Analytics Warehouse

## 1. Project Overview

The **Retail Sales Analytics Warehouse** is a Python-based data engineering project that transforms retail transaction data into a structured data warehouse for business analysis.

The solution uses an ETL (Extract, Transform, Load) pipeline to process customer, product, order, and order-item data. It validates records, handles invalid data, loads accepted records into a SQLite database using a Star Schema, and presents business insights through a Streamlit dashboard.

### Project Objectives

- Build an end-to-end retail data processing pipeline.
- Implement data validation and quality checks.
- Design a dimensional data warehouse using a Star Schema.
- Store rejected records separately for auditing.
- Generate execution reports.
- Provide SQL-based business analytics.
- Display sales insights through an interactive dashboard.

## 2. System Architecture

The project follows this workflow:

```text
CSV Source Data
      |
      v
Python Data Generation
      |
      v
Data Validation and ETL
      |
      +----------------------+
      |                      |
      v                      v
Valid Records          Invalid Records
      |                      |
      v                      v
SQLite Warehouse       Rejected Records CSV
      |
      v
Star Schema
      |
      v
SQL Analytics
      |
      v
Streamlit Dashboard
      |
      v
Business Insights
```

For detailed architecture, see [architecture/architecture.md](architecture/architecture.md).

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Data Processing | Python CSV, Pandas |
| Database | SQLite |
| Query Language | SQL |
| Dashboard | Streamlit |
| Data Visualization | Streamlit Charts |
| Testing | Python unittest |
| Source Data | CSV files |
| Version Control | Git and GitHub |

## 4. Source Data

The project uses four CSV source files:

- `customers.csv` – Customer details and city.
- `products.csv` – Product details and categories.
- `orders.csv` – Customer orders and order dates.
- `order_items.csv` – Individual products, quantities, prices, and discounts.

The data generator creates sample retail transaction data and includes deliberately invalid records to test data quality validation.

## 5. Data Warehouse Design

The warehouse follows a **Star Schema** design.

### Dimension Tables

| Table | Description |
|---|---|
| dim_customer | Customer information |
| dim_product | Product information |
| dim_date | Calendar and date information |

### Fact Table

| Table | Description |
|---|---|
| fact_sales | Retail sales transactions at order-item level |

**Fact table grain:** One row represents one product line within one customer order.

### Measures

- Quantity
- Unit price
- Discount
- Gross sales
- Net sales

## 6. Data Quality and Validation

The ETL pipeline performs validation checks for:

- Required fields.
- Customer and product references.
- Valid order references.
- Duplicate order-item identifiers.
- Positive quantities.
- Non-negative prices and discounts.
- Discounts not exceeding gross sales.
- Foreign-key integrity.

Invalid records are excluded from the fact table and stored separately in:

`backend/outputs/rejected_records.csv`

## 7. ETL Pipeline and Monitoring

The backend pipeline performs the following operations:

1. Reads the four source CSV files.
2. Validates customer and product information.
3. Creates dimension tables.
4. Validates orders and order-item records.
5. Loads valid transactions into the fact table.
6. Stores rejected records separately.
7. Checks foreign-key integrity.
8. Generates a JSON execution report.

The execution report is saved at:

`backend/outputs/run_report.json`

The report contains:

- Run ID and timestamps.
- Execution status.
- Accepted and rejected record counts.
- Dimension and fact table counts.
- Total net sales.
- Execution duration.
- Foreign-key validation results.

**Loading strategy:** The current implementation uses a full-refresh approach. It rebuilds the warehouse from the source CSV files whenever the pipeline runs.

## 8. SQL Analytics

The SQL analytics module provides business insights, including:

1. Overall sales performance.
2. Top 10 products by revenue.
3. Revenue by customer city.
4. Monthly revenue trends.

SQL queries are maintained in:

`backend/sql/analytics.sql`

## 9. Streamlit Dashboard

The frontend is developed using Streamlit and connects directly to the SQLite warehouse.

The dashboard displays:

- Total Revenue.
- Total Orders.
- Total Units Sold.
- Total Customers.
- Top 10 Products by Revenue.
- City-wise Revenue.
- Monthly Revenue Trend.
- Top Products Details.

The dashboard source file is:

`frontend/app.py`

The database is located at:

`backend/outputs/retail_warehouse.db`

## 10. Project Structure

```text
retail-sales-warehouse/
│
├── architecture/
│   └── architecture.md
│
├── backend/
│   │
│   ├── data/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   │
│   ├── src/
│   │   ├── generate_data.py
│   │   ├── pipeline.py
│   │   ├── analytics.py
│   │   └── benchmark.py
│   │
│   ├── sql/
│   │   └── analytics.sql
│   │
│   ├── tests/
│   │   └── test_pipeline.py
│   │
│   └── outputs/
│       ├── retail_warehouse.db
│       ├── rejected_records.csv
│       └── run_report.json
│
├── docs/
│   └── data_dictionary.md
│
├── frontend/
│   └── app.py
│
├── .gitignore
│
└── README.md
```

## 11. Installation and Execution

### Prerequisites

- Python 3.10 or newer.
- pip package manager.
- Git (optional, for cloning the repository).

### Step 1: Clone the Repository

```bash
git clone https://github.com/venkat2003-john/retail-sales-warehouse.git
cd retail-sales-warehouse
```

### Step 2: Install Dependencies

```bash
python -m pip install pandas streamlit
```

### Step 3: Generate Sample Data (Optional)

Open a terminal in the project root and navigate to the backend:

```powershell
cd backend
```

Run:

```powershell
python .\src\generate_data.py
```

This regenerates the four sample CSV files in `backend/data/`.

**Note:** Run this only when you want to regenerate the sample source data.

### Step 4: Execute the ETL Pipeline

From the `backend` directory:

```powershell
python .\src\pipeline.py
```

The pipeline creates or refreshes:

- `outputs/retail_warehouse.db`
- `outputs/rejected_records.csv`
- `outputs/run_report.json`

### Step 5: Run Automated Tests

Remain in the `backend` directory:

```powershell
python -m unittest discover -s tests -v
```

### Step 6: Run SQL Analytics

From the `backend` directory:

```powershell
python .\src\analytics.py
```

### Step 7: Launch the Dashboard

Return to the project root:

```powershell
cd ..
```

Start Streamlit:

```powershell
python -m streamlit run frontend/app.py
```

The dashboard will open in your default browser.

**Note:** The committed SQLite database is already included in the repository, so the dashboard can be launched without regenerating data or rerunning the pipeline.

## 12. Automated Testing

The project includes automated tests using Python's unittest framework.

The tests validate:

- Pipeline execution and data quality.
- Handling of empty input files.
- Invalid and duplicate records.
- Sales reconciliation.
- Warehouse foreign-key integrity.
- Repeat-run consistency.

Run the tests from the `backend` directory:

```powershell
python -m unittest discover -s tests -v
```

## 13. Current Limitations

- The pipeline uses full-refresh loading instead of incremental processing.
- SQLite is used as a lightweight local warehouse.
- The project uses generated sample retail data rather than a live production data source.
- The dashboard depends on the locally available SQLite database.

## 14. Future Enhancements

Potential improvements include:

- Incremental data loading.
- Change Data Capture (CDC) integration.
- Scheduling automated ETL jobs.
- Additional data quality monitoring.
- More advanced dashboard filters.
- Integration with cloud-based data warehouses.

## 15. Conclusion

The Retail Sales Analytics Warehouse demonstrates an end-to-end data engineering workflow covering source data generation, ETL processing, data quality validation, dimensional modelling, SQLite warehouse management, automated testing, SQL analytics, and dashboard development.

The project provides a foundation for understanding how transactional retail data can be transformed into structured information for business reporting and decision-making.

## Repository

GitHub: https://github.com/venkat2003-john/retail-sales-warehouse
