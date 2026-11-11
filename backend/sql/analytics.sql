
-- 1. Overall sales performance
SELECT
    COUNT(*) AS total_order_lines,
    SUM(quantity) AS units_sold,
    ROUND(SUM(gross_sales), 2) AS gross_revenue,
    ROUND(SUM(net_sales), 2) AS net_revenue
FROM fact_sales;

-- 2. Top 10 products by revenue
SELECT
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.net_sales), 2) AS revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- 3. Sales by customer city
SELECT
    c.city,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY c.city
ORDER BY revenue DESC;

-- 4. Monthly revenue trend
SELECT
    d.year,
    d.month,
    ROUND(SUM(f.net_sales), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
