-- ============================================================
--  ANALYTICS DASHBOARD — KPI & REPORTING QUERIES
-- ============================================================

-- ── KPI 1: Total Revenue (closed_won only) ───────────────────
SELECT
    ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS total_revenue
FROM orders
WHERE status = 'closed_won';

-- ── KPI 2: Gross Profit ──────────────────────────────────────
SELECT
    ROUND(SUM(
        o.quantity * (o.unit_price * (1 - o.discount_pct / 100.0) - p.cost_price)
    ), 2) AS gross_profit
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'closed_won';

-- ── KPI 3: Active Customers ──────────────────────────────────
SELECT COUNT(DISTINCT customer_id) AS active_customers
FROM orders
WHERE status = 'closed_won'
  AND order_date >= DATE_TRUNC('year', CURRENT_DATE);

-- ── KPI 4: Average Order Value ───────────────────────────────
SELECT
    ROUND(AVG(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS avg_order_value
FROM orders
WHERE status = 'closed_won';

-- ── KPI 5: Churn Rate (% customers with no order last 90 days) ─
SELECT
    ROUND(
        100.0 * COUNT(CASE WHEN last_order < CURRENT_DATE - 90 THEN 1 END)
              / NULLIF(COUNT(*), 0),
    2) AS churn_rate_pct
FROM (
    SELECT customer_id, MAX(order_date) AS last_order
    FROM orders WHERE status = 'closed_won'
    GROUP BY customer_id
) sub;

-- ── REPORT 1: Monthly Revenue vs Target ──────────────────────
SELECT
    DATE_TRUNC('month', order_date) AS month,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct / 100.0)), 2) AS revenue,
    ROUND(SUM(o.quantity * (o.unit_price * (1 - o.discount_pct/100.0) - p.cost_price)), 2) AS profit
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'closed_won'
  AND o.order_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY 1
ORDER BY 1;

-- ── REPORT 2: Revenue by Segment ─────────────────────────────
SELECT
    c.segment,
    ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount_pct/100.0)), 2) AS revenue,
    COUNT(DISTINCT o.customer_id) AS num_customers
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'closed_won'
GROUP BY c.segment
ORDER BY revenue DESC;

-- ── REPORT 3: Revenue by Region ──────────────────────────────
SELECT
    r.name  AS region,
    r.code,
    ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount_pct/100.0)), 2) AS revenue,
    COUNT(DISTINCT o.customer_id) AS customers
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions  r ON c.region_id   = r.region_id
WHERE o.status = 'closed_won'
GROUP BY r.region_id, r.name, r.code
ORDER BY revenue DESC;

-- ── REPORT 4: Sales Funnel ───────────────────────────────────
SELECT
    status,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM orders
GROUP BY status
ORDER BY
    CASE status
        WHEN 'leads'        THEN 1
        WHEN 'qualified'    THEN 2
        WHEN 'proposal'     THEN 3
        WHEN 'negotiation'  THEN 4
        WHEN 'closed_won'   THEN 5
        WHEN 'lost'         THEN 6
    END;

-- ── REPORT 5: Top Accounts ───────────────────────────────────
SELECT
    c.company_name,
    c.segment,
    r.code AS region,
    ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount_pct/100.0)), 2) AS revenue,
    COUNT(o.order_id) AS num_orders,
    c.nps_score,
    CASE
        WHEN c.nps_score >= 70                              THEN 'Healthy'
        WHEN c.nps_score BETWEEN 50 AND 69                  THEN 'At Risk'
        ELSE                                                     'Churn Risk'
    END AS health_status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions   r ON c.region_id   = r.region_id
WHERE o.status = 'closed_won'
GROUP BY c.customer_id, c.company_name, c.segment, r.code, c.nps_score
ORDER BY revenue DESC
LIMIT 20;

-- ── REPORT 6: Rep Performance ────────────────────────────────
SELECT
    sr.full_name,
    r.name AS region,
    COUNT(CASE WHEN o.status = 'closed_won' THEN 1 END) AS won,
    COUNT(CASE WHEN o.status = 'lost'       THEN 1 END) AS lost,
    ROUND(
        100.0 * COUNT(CASE WHEN o.status = 'closed_won' THEN 1 END)
              / NULLIF(COUNT(CASE WHEN o.status IN ('closed_won','lost') THEN 1 END), 0),
    1) AS win_rate_pct,
    ROUND(SUM(CASE WHEN o.status = 'closed_won'
        THEN o.quantity * o.unit_price * (1 - o.discount_pct/100.0)
        ELSE 0 END), 2) AS revenue
FROM orders o
JOIN sales_reps sr ON o.rep_id     = sr.rep_id
JOIN regions    r  ON sr.region_id = r.region_id
GROUP BY sr.rep_id, sr.full_name, r.name
ORDER BY revenue DESC;

-- ── REPORT 7: Period Comparison (YoY / QoQ) ──────────────────
SELECT
    EXTRACT(YEAR  FROM order_date) AS yr,
    EXTRACT(QUARTER FROM order_date) AS qtr,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS revenue,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(order_id) AS orders
FROM orders
WHERE status = 'closed_won'
GROUP BY 1, 2
ORDER BY 1, 2;
