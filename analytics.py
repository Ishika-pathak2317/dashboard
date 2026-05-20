"""
analytics.py — Pandas-powered KPI engine
Reads from the database (via SQLAlchemy) or from CSV files,
computes every KPI shown on the dashboard, and exposes them
as clean Python dicts / DataFrames for the Flask API layer.
"""

import os
import warnings
from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

# ── Database connection ───────────────────────────────────────
DB_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dashboard.db"           # fallback to SQLite for local dev
)
engine = create_engine(DB_URL, echo=False)


# ── Helpers ───────────────────────────────────────────────────

def _load(query: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def _revenue_col(df: pd.DataFrame) -> pd.Series:
    """Compute net revenue from order columns."""
    return df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)


def load_orders() -> pd.DataFrame:
    """Load the full orders fact table with all joins."""
    query = """
        SELECT
            o.order_id, o.order_date, o.closed_date,
            o.quantity, o.unit_price, o.discount_pct,
            o.status,
            c.company_name, c.segment, c.nps_score,
            r.name  AS region, r.code AS region_code,
            p.name  AS product, p.category, p.cost_price,
            sr.full_name AS rep_name
        FROM orders o
        JOIN customers  c  ON o.customer_id = c.customer_id
        JOIN regions    r  ON c.region_id   = r.region_id
        JOIN products   p  ON o.product_id  = p.product_id
        JOIN sales_reps sr ON o.rep_id      = sr.rep_id
    """
    df = _load(query)
    df["order_date"]  = pd.to_datetime(df["order_date"])
    df["closed_date"] = pd.to_datetime(df["closed_date"])
    df["revenue"]     = _revenue_col(df)
    df["profit"]      = df["revenue"] - df["quantity"] * df["cost_price"]
    return df


# ── KPI Functions ─────────────────────────────────────────────

def kpi_summary(df: pd.DataFrame, period: str = "all") -> dict:
    """
    Return headline KPIs.
    period: 'all' | 'q1' | 'q2' | 'q3' | 'q4'
    """
    won = df[df["status"] == "closed_won"].copy()

    if period != "all":
        q = int(period[1])
        won = won[won["order_date"].dt.quarter == q]

    total_revenue   = won["revenue"].sum()
    gross_profit    = won["profit"].sum()
    active_customers = won["company_name"].nunique()
    aov             = won["revenue"].mean() if len(won) else 0

    # Churn: customers whose last order was > 90 days ago
    last_orders = (
        won.groupby("company_name")["order_date"].max()
        .reset_index(name="last_order")
    )
    cutoff = pd.Timestamp(date.today() - timedelta(days=90))
    churned = (last_orders["last_order"] < cutoff).sum()
    churn_rate = (churned / len(last_orders) * 100) if len(last_orders) else 0

    return {
        "total_revenue":    round(float(total_revenue), 2),
        "gross_profit":     round(float(gross_profit), 2),
        "active_customers": int(active_customers),
        "avg_order_value":  round(float(aov), 2),
        "churn_rate_pct":   round(float(churn_rate), 2),
        "gross_margin_pct": round(float(gross_profit / total_revenue * 100), 1)
                            if total_revenue else 0,
    }


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue, profit, and target (target = +10% PY, mocked here)."""
    won = df[df["status"] == "closed_won"].copy()
    won["month"] = won["order_date"].dt.to_period("M")
    monthly = (
        won.groupby("month")
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )
    monthly["month_str"] = monthly["month"].astype(str)
    monthly["target"]    = (monthly["revenue"] * 1.08).round(2)  # mock target
    monthly["revenue"]   = monthly["revenue"].round(2)
    monthly["profit"]    = monthly["profit"].round(2)
    return monthly[["month_str", "revenue", "profit", "target"]]


def revenue_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue split by business segment."""
    won = df[df["status"] == "closed_won"]
    seg = (
        won.groupby("segment")
        .agg(revenue=("revenue", "sum"), customers=("company_name", "nunique"))
        .reset_index()
    )
    seg["pct"] = (seg["revenue"] / seg["revenue"].sum() * 100).round(1)
    return seg.sort_values("revenue", ascending=False).reset_index(drop=True)


def revenue_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue split by region."""
    won = df[df["status"] == "closed_won"]
    reg = (
        won.groupby(["region", "region_code"])
        .agg(revenue=("revenue", "sum"), customers=("company_name", "nunique"))
        .reset_index()
    )
    reg["pct"] = (reg["revenue"] / reg["revenue"].sum() * 100).round(1)
    return reg.sort_values("revenue", ascending=False).reset_index(drop=True)


def sales_funnel(df: pd.DataFrame) -> pd.DataFrame:
    """Funnel stage counts and conversion rates."""
    stage_order = ["leads", "qualified", "proposal",
                   "negotiation", "closed_won", "lost"]
    funnel = (
        df.groupby("status")
        .size()
        .reindex(stage_order, fill_value=0)
        .reset_index(name="count")
    )
    total = funnel["count"].sum()
    funnel["pct"] = (funnel["count"] / total * 100).round(1)
    # Conversion vs top of funnel (closed_won / leads)
    top = funnel.loc[funnel["status"] == "leads", "count"].values
    funnel["conversion_from_top"] = (
        (funnel["count"] / top[0] * 100).round(1) if len(top) and top[0] else 0
    )
    return funnel


def top_accounts(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N accounts by revenue with health status."""
    won = df[df["status"] == "closed_won"]
    accts = (
        won.groupby(["company_name", "segment", "region_code", "nps_score"])
        .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
        .reset_index()
    )
    accts["growth_pct"] = np.random.uniform(-10, 45, len(accts)).round(1)  # mock
    accts["health"] = accts["nps_score"].apply(
        lambda s: "Healthy" if s >= 70 else ("At Risk" if s >= 50 else "Churn Risk")
    )
    return accts.sort_values("revenue", ascending=False).head(n).reset_index(drop=True)


def rep_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Sales rep win rate and revenue leaderboard."""
    closed = df[df["status"].isin(["closed_won", "lost"])]
    reps = closed.groupby("rep_name").apply(lambda g: pd.Series({
        "won":      (g["status"] == "closed_won").sum(),
        "lost":     (g["status"] == "lost").sum(),
        "revenue":  g.loc[g["status"] == "closed_won", "revenue"].sum().round(2),
    })).reset_index()
    reps["win_rate"] = (reps["won"] / (reps["won"] + reps["lost"]) * 100).round(1)
    return reps.sort_values("revenue", ascending=False).reset_index(drop=True)


def period_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Quarter-over-quarter revenue comparison."""
    won = df[df["status"] == "closed_won"].copy()
    won["year"]    = won["order_date"].dt.year
    won["quarter"] = won["order_date"].dt.quarter
    qoq = (
        won.groupby(["year", "quarter"])
        .agg(revenue=("revenue", "sum"), orders=("order_id", "count"),
             customers=("company_name", "nunique"))
        .reset_index()
    )
    qoq["label"] = qoq.apply(lambda r: f"Q{int(r.quarter)} {int(r.year)}", axis=1)
    return qoq


# ── Tableau Export ────────────────────────────────────────────

def export_for_tableau(df: pd.DataFrame, output_dir: str = "./exports") -> dict:
    """
    Export analysis-ready CSVs that Tableau can connect to directly.
    Returns dict with file paths.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    files = {}

    # 1. Raw orders (main data source)
    path = os.path.join(output_dir, "orders_fact.csv")
    df.to_csv(path, index=False)
    files["orders_fact"] = path

    # 2. Monthly summary
    path = os.path.join(output_dir, "monthly_revenue.csv")
    monthly_revenue(df).to_csv(path, index=False)
    files["monthly_revenue"] = path

    # 3. Regional
    path = os.path.join(output_dir, "regional.csv")
    revenue_by_region(df).to_csv(path, index=False)
    files["regional"] = path

    # 4. Segment
    path = os.path.join(output_dir, "segment.csv")
    revenue_by_segment(df).to_csv(path, index=False)
    files["segment"] = path

    # 5. Funnel
    path = os.path.join(output_dir, "funnel.csv")
    sales_funnel(df).to_csv(path, index=False)
    files["funnel"] = path

    # 6. Accounts
    path = os.path.join(output_dir, "accounts.csv")
    top_accounts(df, n=50).to_csv(path, index=False)
    files["accounts"] = path

    print(f"✅  Exported {len(files)} files to '{output_dir}':")
    for k, v in files.items():
        print(f"    {k:20s} → {v}")

    return files


# ── CLI quick-check ───────────────────────────────────────────

if __name__ == "__main__":
    print("Loading data…")
    df = load_orders()
    print(f"  {len(df)} rows loaded\n")

    print("── KPI Summary (All time) ──")
    for k, v in kpi_summary(df).items():
        print(f"  {k:<25} {v}")

    print("\n── Monthly Revenue ──")
    print(monthly_revenue(df).to_string(index=False))

    print("\n── Sales Funnel ──")
    print(sales_funnel(df).to_string(index=False))

    print("\n── Top Accounts ──")
    print(top_accounts(df).to_string(index=False))

    print("\n── Exporting for Tableau… ──")
    export_for_tableau(df)
