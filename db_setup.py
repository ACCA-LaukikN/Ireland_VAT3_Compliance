"""
db_setup.py
Creates the SQLite database and all tables required for the Irish VAT3 
compliance tool. Seeds the vat_rates table with current Irish VAT rates.

Run this once to initialise vat3.db before using any other module.
"""

import sqlite3

DB_NAME = "vat3.db"


def get_connection():
    """Returns a connection and cursor to the VAT3 database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor


def create_tables(cursor):
    """Creates all tables required by the project if they don't already exist."""

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vat_rates (
            rate_id INTEGER PRIMARY KEY,
            rate_name TEXT NOT NULL,
            rate_percentage DECIMAL NOT NULL,
            effective_from DATE NOT NULL,
            effective_to DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            business_id INTEGER PRIMARY KEY,
            business_name TEXT NOT NULL,
            vat_registration_no TEXT NOT NULL,
            vat_period_type TEXT NOT NULL,
            accounting_basis TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vat_periods (
            period_id INTEGER PRIMARY KEY,
            business_id INTEGER NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            due_date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            FOREIGN KEY (business_id) REFERENCES businesses(business_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            business_id INTEGER NOT NULL,
            period_id INTEGER NOT NULL,
            transaction_date DATE NOT NULL,
            transaction_type TEXT NOT NULL,
            counterparty_name TEXT NOT NULL,
            counterparty_vat_no TEXT,
            net_amount DECIMAL NOT NULL,
            vat_rate_id INTEGER NOT NULL,
            vat_amount DECIMAL NOT NULL,
            gross_amount DECIMAL NOT NULL,
            invoice_number TEXT,
            supply_type TEXT NOT NULL,
            is_reverse_charge BOOLEAN DEFAULT 0,
            FOREIGN KEY (business_id) REFERENCES businesses(business_id),
            FOREIGN KEY (period_id) REFERENCES vat_periods(period_id),
            FOREIGN KEY (vat_rate_id) REFERENCES vat_rates(rate_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vat3_returns (
            return_id INTEGER PRIMARY KEY,
            period_id INTEGER NOT NULL,
            T1_vat_on_sales DECIMAL,
            T2_vat_on_purchases DECIMAL,
            T3_vat_payable DECIMAL,
            T4_vat_repayable DECIMAL,
            E1_intra_eu_sales DECIMAL,
            E2_intra_eu_purchases DECIMAL,
            generated_at DATETIME,
            FOREIGN KEY (period_id) REFERENCES vat_periods(period_id)
        )
    ''')


def seed_vat_rates(cursor):
    """Seeds the vat_rates table with current Irish VAT rates as per Revenue.ie"""

    irish_vat_rates = [
        (1, "Standard", 23.0, "2012-01-01", None),
        (2, "Reduced", 13.5, "1985-01-01", None),
        (3, "Second Reduced", 9.0, "2011-07-01", None),
        (4, "Livestock", 4.8, "1985-01-01", None),
        (5, "Zero Rated", 0.0, "1972-11-01", None),
        (6, "Exempt", 0.0, "1972-11-01", None),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO vat_rates 
        (rate_id, rate_name, rate_percentage, effective_from, effective_to)
        VALUES (?, ?, ?, ?, ?)
    ''', irish_vat_rates)


def initialise_database():
    """Main entry point - creates and seeds the database in one call."""
    conn, cursor = get_connection()
    create_tables(cursor)
    seed_vat_rates(cursor)
    conn.commit()
    print("Database initialised successfully — vat3.db ready")
    return conn, cursor


if __name__ == "__main__":
    initialise_database()
