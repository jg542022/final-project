import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ---------------- CONFIG ----------------

DATASET_DIR = "archive"
META_FILE = os.path.join(DATASET_DIR, "symbols_valid_meta.csv")
PRICES_DIR = os.path.join(DATASET_DIR, "stocks")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sinatra1",
    "database": "cs3260-project",
}

# ----------------------------------------


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def import_companies_and_stocks(conn):
    """
    symbols_valid_meta.csv columns (relevant):
    - Symbol
    - Security Name
    """
    df = pd.read_csv(META_FILE)

    cursor = conn.cursor()

    company_id = 1
    symbol_to_company = {}

    for _, row in df.iterrows():
        ticker = row["Symbol"]
        name = row["Security Name"]

        symbol_to_company[ticker] = company_id

        cursor.execute(
            """
            INSERT IGNORE INTO companies (company_id, name)
            VALUES (%s, %s)
            """,
            (company_id, name),
        )

        cursor.execute(
            """
            INSERT IGNORE INTO stocks (ticker, company_id)
            VALUES (%s, %s)
            """,
            (ticker, company_id),
        )

        company_id += 1

    conn.commit()
    cursor.close()
    print("✓ Companies and stocks imported")


def import_prices(conn):
    """
    Reads each prices/<TICKER>.csv
    Uses only:
    - Date
    - Close
    """
    cursor = conn.cursor()

    for filename in os.listdir(PRICES_DIR):
        if not filename.endswith(".csv"):
            continue

        ticker = filename.replace(".csv", "")
        path = os.path.join(PRICES_DIR, filename)

        df = pd.read_csv(path, usecols=["Date", "Close"])
        df.dropna(inplace=True)

        for _, row in df.iterrows():
            date = row["Date"]
            close_price = int(round(row["Close"]))

            cursor.execute(
                """
                INSERT IGNORE INTO prices (ticker, time, dollars)
                VALUES (%s, %s, %s)
                """,
                (ticker, f"{date} 00:00:00", close_price),
            )

        print(f"✓ Imported prices for {ticker}")

    conn.commit()
    cursor.close()


def main():
    try:
        conn = get_connection()
        import_companies_and_stocks(conn)
        import_prices(conn)
    except Error as e:
        print("Database error:", e)
    finally:
        if conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()

