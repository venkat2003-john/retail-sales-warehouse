# Retail Sales Analytics Warehouse

## 1. Project Overview

The **Retail Sales Analytics Warehouse** is a Python-based data engineering project designed to transform raw retail data into a structured data warehouse for business analysis.

The project implements an ETL pipeline that extracts data from CSV files, validates and cleans records, and loads the processed data into a SQLite database using a Star Schema.

It also includes SQL analytics, automated testing, and a Streamlit dashboard for visualizing retail business performance.

## 2. Project Objectives

- Build an end-to-end ETL pipeline.
- Validate and clean raw retail data.
- Design a Star Schema data warehouse.
- Store structured data using SQLite.
- Generate business insights using SQL.
- Visualize sales performance through a dashboard.
- Test data quality and pipeline reliability.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | ETL pipeline and data processing |
| Pandas | Data analysis and dashboard data handling |
| SQLite | Data warehouse |
| SQL | Business analytics |
| Streamlit | Interactive dashboard |
| Unittest | Automated testing |
| Git & GitHub | Version control |

## 4. Project Architecture

```text
CSV Source Files
       |
       v
Data Generation
       |
       v
ETL Pipeline
       |
       v
Data Validation
       |
       v
SQLite Data Warehouse
       |
       v
SQL Analytics
       |
       v
Streamlit Dashboard
```

## 5. Source Data

The project uses four CSV files:

- `customers.csv` – Customer information.
- `products.csv` – Product information.
- `orders.csv` – Order information.
- `order_items.csv` – Individual products purchased in each order.

Synthetic sample data is generated using Python.

## 6. Data Warehouse Design

The warehouse follows a Star Schema.

### Dimension Tables

- `dim_customer`
- `dim_product`
- `dim_date`

### Fact Table

- `fact_sales`

**Fact Table Grain:** One record represents one product line within a customer order.

## 7. ETL Pipeline

The ETL pipeline performs the following operations:

1. Extracts data from CSV files.
2. Validates required fields.
3. Checks invalid and duplicate records.
4. Applies data cleaning rules.
5. Loads valid records into SQLite.
6. Stores rejected records separately.
7. Generates a pipeline execution report.

The current implementation uses a full-refresh loading strategy.

## 8. Data Quality Checks

The pipeline includes:

- Required field validation.
- Duplicate record detection.
- Invalid customer and product checks.
- Quantity and price validation.
- Rejected record tracking.

## 9. SQL Analytics

The SQL analytics module provides insights such as:

- Total revenue.
- Total orders.
- Units sold.
- Top-performing products.
- Revenue by city.
- Monthly sales trends.

## 10. Streamlit Dashboard

The interactive dashboard displays:

- Total revenue.
- Total orders.
- Units sold.
- Total customers.
- Top 10 products.
- Revenue by city.
- Monthly revenue trends.
- Product-level details.

## 11. Project Structure

```text
retail-sales-warehouse/
│
├── architecture/
│   └── architecture.md
│
├── backend/
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
└── README.md
```

## 12. Installation and Execution

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

From the project root:

```powershell
cd backend
python .\src\generate_data.py
```

### Step 4: Run the ETL Pipeline

From the `backend` directory:

```powershell
python .\src\pipeline.py
```

### Step 5: Run Unit Tests

```powershell
python -m unittest discover -s tests -v
```

### Step 6: Run SQL Analytics

```powershell
python .\src\analytics.py
```

### Step 7: Launch the Dashboard

Return to the project root:

```powershell
cd ..
python -m streamlit run frontend/app.py
```

The dashboard will open in your web browser.

## 13. Current Limitations

- Uses synthetic retail data.
- Uses SQLite as the database.
- Implements full-refresh loading rather than incremental CDC.
- Designed as a local demonstration project.

## 14. Future Enhancements

- Implement incremental data loading.
- Integrate a cloud-based database.
- Add real-time data processing.
- Improve dashboard filtering and reporting.
- Add advanced sales forecasting.

## 15. Conclusion

This project demonstrates an end-to-end retail data engineering workflow, covering data generation, ETL processing, data quality validation, warehouse design, SQL analytics, automated testing, and dashboard visualization.

**GitHub Repository:**

https://github.com/venkat2003-john/retail-sales-warehouse
