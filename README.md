# ⬡ NexusIQ — Analytics Intelligence Platform

<div align="center">

![NexusIQ Banner](https://img.shields.io/badge/NexusIQ-Analytics%20Intelligence-3b82f6?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsNSAyLjVNMjIgMTdsLTUgMi41TTIgMTJsNSAyLjVNMjIgMTJsLTUgMi41Ii8+PC9zdmc+)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Three.js](https://img.shields.io/badge/Three.js-r128-000000?style=flat-square&logo=threedotjs&logoColor=white)](https://threejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

**A full-stack business analytics dashboard with 3D visualizations, real-time KPIs, and Tableau export — built with Python, Pandas, Flask, and Three.js.**

[Live Demo](#) · [Report Bug](issues) · [Request Feature](issues)

</div>

---

## ✨ Features

- **3D Interactive Revenue Chart** — drag, rotate, and zoom powered by Three.js
- **Animated Particle Background** — dynamic canvas with WebGL-style network graph
- **5 Live KPI Cards** — Revenue, Profit, Customers, AOV, Churn Rate with sparklines
- **Real-time Filters** — All Time / Q1 / Q2 / Q3 / Q4 period switching
- **Sales Funnel Visualization** — stage-by-stage conversion with win rate
- **Regional Performance** — 5-market revenue breakdown with mix strip
- **Top Accounts Table** — filterable by segment with health status badges
- **Tableau Export** — one-click CSV export of all analytics datasets
- **REST API** — clean JSON endpoints for every data view
- **SQLite → PostgreSQL → MySQL** — works with any SQL database

---

## 🖥️ Screenshots

> Dashboard with 3D chart, animated particles, dark theme, and live KPI cards.

---

## 🗂️ Project Structure

```
NexusIQ/
├── app.py              ← Flask REST API (all /api/* routes)
├── analytics.py        ← Pandas KPI engine & Tableau exporter
├── seed_db.py          ← Database setup + sample data seeder
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment config template
├── static/
│   └── index.html      ← Full 3D frontend dashboard
├── sql/
│   ├── schema.sql      ← SQL schema (PostgreSQL / MySQL / SQLite)
│   └── queries.sql     ← All 7 KPI & reporting queries
├── exports/            ← Tableau CSV exports (auto-created)
└── SETUP.md            ← Detailed deployment guide
```

---

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ishika-pathak2317/nexusiq.git
cd nexusiq
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env if needed — SQLite works out of the box
```

### 5. Seed the database

```bash
python seed_db.py
```

### 6. Run the server

```bash
python app.py
```

Open **http://localhost:5000** 🎉

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard UI |
| GET | `/api/kpis?period=all\|q1\|q2\|q3\|q4` | KPI summary |
| GET | `/api/monthly` | Monthly revenue vs target |
| GET | `/api/segments` | Revenue by segment |
| GET | `/api/regions` | Revenue by region |
| GET | `/api/funnel` | Sales funnel stages |
| GET | `/api/accounts?segment=all\|enterprise\|smb` | Top accounts |
| GET | `/api/reps` | Sales rep leaderboard |
| GET | `/api/export` | Export CSVs for Tableau |
| GET | `/api/refresh` | Reload data from DB |

---

## 📊 Tableau Integration

### Option A — CSV (no server needed)
1. Click **Export for Tableau** in the dashboard
2. Open Tableau → **Connect → Text File**
3. Select `exports/orders_fact.csv`
4. Join other CSVs as needed

### Option B — Live Web Data Connector
1. Keep Flask server running
2. Tableau → **Connect → Web Data Connector**
3. Enter `http://localhost:5000/api/monthly`

---

## 🗄️ Database Support

| Database | Connection String |
|----------|-------------------|
| SQLite (default) | `sqlite:///./dashboard.db` |
| PostgreSQL | `postgresql://user:pass@localhost:5432/analytics_db` |
| MySQL | `mysql+pymysql://user:pass@localhost:3306/analytics_db` |

Set `DATABASE_URL` in your `.env` file.

---

## 🚀 Production Deployment

```bash
# Install Gunicorn (included in requirements.txt)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

See [SETUP.md](SETUP.md) for Nginx reverse proxy and systemd service setup.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.0 |
| Data | Pandas 2.2, NumPy |
| Database | SQLAlchemy (SQLite / PostgreSQL / MySQL) |
| 3D Viz | Three.js r128 |
| Charts | Chart.js 4.4 |
| Frontend | Vanilla JS, CSS3, HTML5 Canvas |
| Export | CSV (Tableau-ready) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made with ❤️ · <a href="https://github.com/YOUR_USERNAME/nexusiq">NexusIQ on GitHub</a>
</div>
