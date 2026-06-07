"""
app.py — Flask REST API for the Analytics Dashboard
Serves JSON endpoints consumed by the frontend (index.html).

Endpoints:
  GET /api/kpis?period=all|q1|q2|q3|q4
  GET /api/monthly
  GET /api/segments
  GET /api/regions
  GET /api/funnel
  GET /api/accounts?segment=all|enterprise|smb
  GET /api/reps
  GET /api/export          → triggers CSV export for Tableau
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from analytics import (
    load_orders,
    kpi_summary,
    monthly_revenue,
    revenue_by_segment,
    revenue_by_region,
    sales_funnel,
    top_accounts,
    rep_performance,
    period_comparison,
    export_for_tableau,
)

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # allow requests from any origin during development

# ── Cache the data in memory (reload on restart) ───────────────
_df = None

def get_df():
    global _df
    if _df is None:
        _df = load_orders()
    return _df


# ── Routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the dashboard HTML."""
    return send_from_directory("index.html")


@app.route("/api/kpis")
def api_kpis():
    period = request.args.get("period", "all").lower()
    if period not in ("all", "q1", "q2", "q3", "q4"):
        return jsonify({"error": "Invalid period"}), 400
    data = kpi_summary(get_df(), period=period)
    return jsonify(data)


@app.route("/api/monthly")
def api_monthly():
    df = monthly_revenue(get_df())
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/segments")
def api_segments():
    df = revenue_by_segment(get_df())
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/regions")
def api_regions():
    df = revenue_by_region(get_df())
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/funnel")
def api_funnel():
    df = sales_funnel(get_df())
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/accounts")
def api_accounts():
    segment = request.args.get("segment", "all").lower()
    df = get_df()
    if segment != "all":
        df = df[df["segment"].str.lower() == segment]
    accts = top_accounts(df, n=20)
    return jsonify(accts.to_dict(orient="records"))


@app.route("/api/reps")
def api_reps():
    df = rep_performance(get_df())
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/periods")
def api_periods():
    df = period_comparison(get_df())
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/export")
def api_export():
    """Export CSVs for Tableau and return file list."""
    files = export_for_tableau(get_df(), output_dir="./exports")
    return jsonify({"status": "ok", "files": files})


@app.route("/api/refresh")
def api_refresh():
    """Force-reload data from DB."""
    global _df
    _df = None
    _df = load_orders()
    return jsonify({"status": "refreshed", "rows": len(_df)})


# ── Error handlers ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e)}), 500


# ── Run ────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    print(f"🚀  Dashboard running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
