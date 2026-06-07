-- ============================================================
--  ANALYTICS DASHBOARD — DATABASE SCHEMA & SEED DATA
--  Compatible with: PostgreSQL 14+ / MySQL 8+ / SQLite 3
-- ============================================================

-- ── 1. DROP & CREATE ─────────────────────────────────────────

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS sales_reps;

CREATE TABLE regions (
    region_id   SERIAL PRIMARY KEY,
    name        VARCHAR(60) NOT NULL,
    code        VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE sales_reps (
    rep_id      SERIAL PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(120) UNIQUE NOT NULL,
    region_id   INT REFERENCES regions(region_id),
    hired_date  DATE NOT NULL
);

CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    name         VARCHAR(120) NOT NULL,
    category     VARCHAR(60)  NOT NULL,   -- SaaS / Enterprise / SMB / Other
    unit_price   NUMERIC(10,2) NOT NULL,
    cost_price   NUMERIC(10,2) NOT NULL
);

CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    segment      VARCHAR(40)  NOT NULL,   -- Enterprise / SMB / Startup
    region_id    INT REFERENCES regions(region_id),
    created_at   TIMESTAMP DEFAULT NOW(),
    nps_score    INT CHECK (nps_score BETWEEN 0 AND 100)
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT  REFERENCES customers(customer_id),
    product_id   INT  REFERENCES products(product_id),
    rep_id       INT  REFERENCES sales_reps(rep_id),
    quantity     INT  NOT NULL DEFAULT 1,
    unit_price   NUMERIC(10,2) NOT NULL,
    discount_pct NUMERIC(5,2)  DEFAULT 0,
    status       VARCHAR(20)   NOT NULL DEFAULT 'closed_won',
                                        -- leads / qualified / proposal /
                                        -- negotiation / closed_won / lost
    order_date   DATE NOT NULL,
    closed_date  DATE
);

-- ── 2. INDEXES ───────────────────────────────────────────────

CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status   ON orders(status);
CREATE INDEX idx_customers_seg   ON customers(segment);
CREATE INDEX idx_customers_reg   ON customers(region_id);

-- ── 3. SEED DATA ─────────────────────────────────────────────

INSERT INTO regions (name, code) VALUES
  ('North America', 'NAMER'),
  ('Europe Middle East Africa', 'EMEA'),
  ('Asia Pacific', 'APAC'),
  ('Latin America', 'LATAM'),
  ('Middle East Africa', 'MEA');

INSERT INTO sales_reps (full_name, email, region_id, hired_date) VALUES
  ('Alice Monroe',    'alice@company.com',   1, '2021-03-15'),
  ('Bruno Silva',     'bruno@company.com',   2, '2020-07-01'),
  ('Chen Wei',        'chen@company.com',    3, '2022-01-10'),
  ('Diana Patel',     'diana@company.com',   4, '2023-04-20'),
  ('Ethan Müller',    'ethan@company.com',   2, '2019-11-05');

INSERT INTO products (name, category, unit_price, cost_price) VALUES
  ('Analytics Pro',       'SaaS',       299.00, 45.00),
  ('Enterprise Suite',    'Enterprise', 1499.00, 320.00),
  ('SMB Starter Pack',    'SMB',         99.00, 18.00),
  ('Data Connector API',  'SaaS',       199.00, 30.00),
  ('Custom Integration',  'Other',      799.00, 200.00);

INSERT INTO customers (company_name, segment, region_id, nps_score) VALUES
  ('Meridian Corp',        'Enterprise', 1, 74),
  ('Bluewave Systems',     'Enterprise', 2, 68),
  ('Fortis Analytics',     'Enterprise', 1, 55),
  ('Kinara Technologies',  'SMB',        3, 81),
  ('Vantage Retail',       'SMB',        2, 49),
  ('Crestline Media',      'Enterprise', 1, 38),
  ('Luminate SaaS',        'SMB',        4, 88),
  ('Syntech Partners',     'SMB',        1, 72);

-- Sample orders spread across FY 2024 (add more as needed)
INSERT INTO orders (customer_id, product_id, rep_id, quantity, unit_price, discount_pct, status, order_date, closed_date) VALUES
  (1, 2, 1, 1, 1499.00, 5,  'closed_won',  '2024-01-10', '2024-02-14'),
  (2, 2, 2, 1, 1499.00, 0,  'closed_won',  '2024-01-22', '2024-03-01'),
  (3, 1, 1, 3, 299.00,  10, 'closed_won',  '2024-02-05', '2024-03-20'),
  (4, 3, 3, 5, 99.00,   0,  'closed_won',  '2024-03-11', '2024-04-02'),
  (5, 3, 2, 2, 99.00,   0,  'negotiation', '2024-04-15', NULL),
  (6, 4, 1, 1, 199.00,  15, 'closed_won',  '2024-05-01', '2024-05-28'),
  (7, 3, 4, 4, 99.00,   0,  'closed_won',  '2024-06-18', '2024-07-10'),
  (8, 1, 1, 2, 299.00,  5,  'closed_won',  '2024-07-22', '2024-08-15'),
  (1, 5, 5, 1, 799.00,  0,  'closed_won',  '2024-08-03', '2024-09-01'),
  (2, 4, 2, 2, 199.00,  0,  'closed_won',  '2024-09-10', '2024-10-05'),
  (3, 2, 1, 1, 1499.00, 10, 'lost',        '2024-10-01', '2024-10-30'),
  (4, 1, 3, 6, 299.00,  0,  'closed_won',  '2024-11-05', '2024-12-01'),
  (7, 2, 4, 1, 1499.00, 0,  'proposal',    '2024-12-01', NULL),
  (8, 5, 1, 1, 799.00,  5,  'closed_won',  '2024-12-15', '2024-12-28');
