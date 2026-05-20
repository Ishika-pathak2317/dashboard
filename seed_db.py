"""
seed_db.py — One-time script to create tables and insert sample data.
Uses SQLAlchemy so it works with SQLite, PostgreSQL, and MySQL.
Run once before starting the Flask server.

Usage:
    python seed_db.py
"""

import os
from datetime import date
from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric,
    Date, DateTime, ForeignKey, text
)
from sqlalchemy.orm import declarative_base, relationship, Session
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./dashboard.db")
engine = create_engine(DB_URL, echo=False)
Base   = declarative_base()

# ── Models ─────────────────────────────────────────────────────

class Region(Base):
    __tablename__ = "regions"
    region_id = Column(Integer, primary_key=True, autoincrement=True)
    name      = Column(String(60), nullable=False)
    code      = Column(String(10), unique=True, nullable=False)

class SalesRep(Base):
    __tablename__ = "sales_reps"
    rep_id     = Column(Integer, primary_key=True, autoincrement=True)
    full_name  = Column(String(100), nullable=False)
    email      = Column(String(120), unique=True, nullable=False)
    region_id  = Column(Integer, ForeignKey("regions.region_id"))
    hired_date = Column(Date, nullable=False)

class Product(Base):
    __tablename__ = "products"
    product_id  = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(120), nullable=False)
    category    = Column(String(60),  nullable=False)
    unit_price  = Column(Numeric(10, 2), nullable=False)
    cost_price  = Column(Numeric(10, 2), nullable=False)

class Customer(Base):
    __tablename__ = "customers"
    customer_id  = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(150), nullable=False)
    segment      = Column(String(40),  nullable=False)
    region_id    = Column(Integer, ForeignKey("regions.region_id"))
    nps_score    = Column(Integer)

class Order(Base):
    __tablename__ = "orders"
    order_id     = Column(Integer, primary_key=True, autoincrement=True)
    customer_id  = Column(Integer, ForeignKey("customers.customer_id"))
    product_id   = Column(Integer, ForeignKey("products.product_id"))
    rep_id       = Column(Integer, ForeignKey("sales_reps.rep_id"))
    quantity     = Column(Integer,       nullable=False, default=1)
    unit_price   = Column(Numeric(10,2), nullable=False)
    discount_pct = Column(Numeric(5,2),  default=0)
    status       = Column(String(20),    nullable=False, default="closed_won")
    order_date   = Column(Date, nullable=False)
    closed_date  = Column(Date)

# ── Seed Data ──────────────────────────────────────────────────

def seed():
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        if s.query(Region).count() > 0:
            print("⚠️  Database already seeded. Skipping.")
            return

        regions = [
            Region(name="North America",              code="NAMER"),
            Region(name="Europe Middle East Africa",  code="EMEA"),
            Region(name="Asia Pacific",               code="APAC"),
            Region(name="Latin America",              code="LATAM"),
            Region(name="Middle East Africa",         code="MEA"),
        ]
        s.add_all(regions); s.flush()

        reps = [
            SalesRep(full_name="Alice Monroe",  email="alice@co.com", region_id=1, hired_date=date(2021,3,15)),
            SalesRep(full_name="Bruno Silva",   email="bruno@co.com", region_id=2, hired_date=date(2020,7,1)),
            SalesRep(full_name="Chen Wei",      email="chen@co.com",  region_id=3, hired_date=date(2022,1,10)),
            SalesRep(full_name="Diana Patel",   email="diana@co.com", region_id=4, hired_date=date(2023,4,20)),
            SalesRep(full_name="Ethan Müller",  email="ethan@co.com", region_id=2, hired_date=date(2019,11,5)),
        ]
        s.add_all(reps); s.flush()

        products = [
            Product(name="Analytics Pro",      category="SaaS",       unit_price=299.00, cost_price=45.00),
            Product(name="Enterprise Suite",   category="Enterprise",  unit_price=1499.00,cost_price=320.00),
            Product(name="SMB Starter Pack",   category="SMB",        unit_price=99.00,  cost_price=18.00),
            Product(name="Data Connector API", category="SaaS",       unit_price=199.00, cost_price=30.00),
            Product(name="Custom Integration", category="Other",      unit_price=799.00, cost_price=200.00),
        ]
        s.add_all(products); s.flush()

        customers = [
            Customer(company_name="Meridian Corp",       segment="Enterprise", region_id=1, nps_score=74),
            Customer(company_name="Bluewave Systems",    segment="Enterprise", region_id=2, nps_score=68),
            Customer(company_name="Fortis Analytics",    segment="Enterprise", region_id=1, nps_score=55),
            Customer(company_name="Kinara Technologies", segment="SMB",        region_id=3, nps_score=81),
            Customer(company_name="Vantage Retail",      segment="SMB",        region_id=2, nps_score=49),
            Customer(company_name="Crestline Media",     segment="Enterprise", region_id=1, nps_score=38),
            Customer(company_name="Luminate SaaS",       segment="SMB",        region_id=4, nps_score=88),
            Customer(company_name="Syntech Partners",    segment="SMB",        region_id=1, nps_score=72),
        ]
        s.add_all(customers); s.flush()

        orders = [
            Order(customer_id=1,product_id=2,rep_id=1,quantity=1,unit_price=1499,discount_pct=5, status="closed_won", order_date=date(2024,1,10),closed_date=date(2024,2,14)),
            Order(customer_id=2,product_id=2,rep_id=2,quantity=1,unit_price=1499,discount_pct=0, status="closed_won", order_date=date(2024,1,22),closed_date=date(2024,3,1)),
            Order(customer_id=3,product_id=1,rep_id=1,quantity=3,unit_price=299, discount_pct=10,status="closed_won", order_date=date(2024,2,5), closed_date=date(2024,3,20)),
            Order(customer_id=4,product_id=3,rep_id=3,quantity=5,unit_price=99,  discount_pct=0, status="closed_won", order_date=date(2024,3,11),closed_date=date(2024,4,2)),
            Order(customer_id=5,product_id=3,rep_id=2,quantity=2,unit_price=99,  discount_pct=0, status="negotiation",order_date=date(2024,4,15),closed_date=None),
            Order(customer_id=6,product_id=4,rep_id=1,quantity=1,unit_price=199, discount_pct=15,status="closed_won", order_date=date(2024,5,1), closed_date=date(2024,5,28)),
            Order(customer_id=7,product_id=3,rep_id=4,quantity=4,unit_price=99,  discount_pct=0, status="closed_won", order_date=date(2024,6,18),closed_date=date(2024,7,10)),
            Order(customer_id=8,product_id=1,rep_id=1,quantity=2,unit_price=299, discount_pct=5, status="closed_won", order_date=date(2024,7,22),closed_date=date(2024,8,15)),
            Order(customer_id=1,product_id=5,rep_id=5,quantity=1,unit_price=799, discount_pct=0, status="closed_won", order_date=date(2024,8,3), closed_date=date(2024,9,1)),
            Order(customer_id=2,product_id=4,rep_id=2,quantity=2,unit_price=199, discount_pct=0, status="closed_won", order_date=date(2024,9,10),closed_date=date(2024,10,5)),
            Order(customer_id=3,product_id=2,rep_id=1,quantity=1,unit_price=1499,discount_pct=10,status="lost",       order_date=date(2024,10,1),closed_date=date(2024,10,30)),
            Order(customer_id=4,product_id=1,rep_id=3,quantity=6,unit_price=299, discount_pct=0, status="closed_won", order_date=date(2024,11,5),closed_date=date(2024,12,1)),
            Order(customer_id=7,product_id=2,rep_id=4,quantity=1,unit_price=1499,discount_pct=0, status="proposal",   order_date=date(2024,12,1),closed_date=None),
            Order(customer_id=8,product_id=5,rep_id=1,quantity=1,unit_price=799, discount_pct=5, status="closed_won", order_date=date(2024,12,15),closed_date=date(2024,12,28)),
        ]
        s.add_all(orders)
        s.commit()
        print(f"✅  Seeded {len(regions)} regions, {len(reps)} reps, {len(products)} products, "
              f"{len(customers)} customers, {len(orders)} orders.")

if __name__ == "__main__":
    seed()
