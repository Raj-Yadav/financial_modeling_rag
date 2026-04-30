"""
db/storage.py

Persists raw FMP API data (profile, metrics, ratios, price) to SQLite.
  → single `db/financial_data.db` file, one table per data type

Usage:
    from db.storage import save_raw_data, is_data_fresh, load_raw_from_sqlite
    save_raw_data(raw, symbol)
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# ── Path ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "db", "financial_data.db")


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS – normalise raw API payload into flat dicts
# ═══════════════════════════════════════════════════════════════════════════════

def _normalise_profile(raw: dict, symbol: str) -> list[dict]:
    p = raw.get("profile", [{}])
    p = p[0] if isinstance(p, list) and p else (p if isinstance(p, dict) else {})
    return [{
        "symbol":       symbol,
        "fetched_at":   datetime.utcnow().isoformat(),
        "company_name": p.get("companyName", ""),
        "industry":     p.get("industry", ""),
        "sector":       p.get("sector", ""),
        "market_cap":   p.get("marketCap"),
        "country":      p.get("country", ""),
        "exchange":     p.get("exchangeShortName", ""),
        "currency":     p.get("currency", ""),
        "website":      p.get("website", ""),
        "description":  p.get("description", ""),
    }]


def _normalise_metrics(raw: dict, symbol: str) -> list[dict]:
    rows = []
    for m in raw.get("metrics", []):
        rows.append({
            "symbol":                   symbol,
            "fetched_at":               datetime.utcnow().isoformat(),
            "date":                     m.get("date"),
            "period":                   m.get("period"),
            "revenue_per_share":        m.get("revenuePerShare"),
            "net_income_per_share":     m.get("netIncomePerShare"),
            "pe_ratio":                 m.get("peRatio"),
            "pb_ratio":                 m.get("pbRatio"),
            "debt_to_equity":           m.get("debtToEquity"),
            "roe":                      m.get("roe"),
            "roa":                      m.get("roa"),
            "ev_to_ebitda":             m.get("evToEbitda"),
            "dividend_yield":           m.get("dividendYield"),
            "free_cash_flow_per_share": m.get("freeCashFlowPerShare"),
        })
    return rows


def _normalise_ratios(raw: dict, symbol: str) -> list[dict]:
    rows = []
    for r in raw.get("ratios", []):
        rows.append({
            "symbol":                   symbol,
            "fetched_at":               datetime.utcnow().isoformat(),
            "date":                     r.get("date"),
            "period":                   r.get("period"),
            "gross_profit_margin":      r.get("grossProfitMargin"),
            "operating_profit_margin":  r.get("operatingProfitMargin"),
            "net_profit_margin":        r.get("netProfitMargin"),
            "current_ratio":            r.get("currentRatio"),
            "quick_ratio":              r.get("quickRatio"),
            "debt_equity_ratio":        r.get("debtEquityRatio"),
            "price_earnings_ratio":     r.get("priceEarningsRatio"),
            "price_to_book_ratio":      r.get("priceToBookRatio"),
            "price_to_sales_ratio":     r.get("priceToSalesRatio"),
            "return_on_equity":         r.get("returnOnEquity"),
            "return_on_assets":         r.get("returnOnAssets"),
            "dividend_yield":           r.get("dividendYield"),
        })
    return rows


def _normalise_prices(raw: dict, symbol: str) -> list[dict]:
    price_data = raw.get("price", [])
    if isinstance(price_data, dict):
        prices = price_data.get("historical", [])
    elif isinstance(price_data, list):
        prices = price_data
    else:
        prices = []

    rows = []
    for p in prices:
        rows.append({
            "symbol":     symbol,
            "fetched_at": datetime.utcnow().isoformat(),
            "date":       p.get("date"),
            "open":       p.get("open"),
            "high":       p.get("high"),
            "low":        p.get("low"),
            "close":      p.get("close"),
            "adj_close":  p.get("adjClose"),
            "volume":     p.get("volume"),
            "change":     p.get("change"),
            "change_pct": p.get("changePercent"),
        })
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
#  SQLite – schema
# ═══════════════════════════════════════════════════════════════════════════════

_CREATE_PROFILE = """
CREATE TABLE IF NOT EXISTS profile (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol       TEXT,
    fetched_at   TEXT,
    company_name TEXT,
    industry     TEXT,
    sector       TEXT,
    market_cap   REAL,
    country      TEXT,
    exchange     TEXT,
    currency     TEXT,
    website      TEXT,
    description  TEXT
);"""

_CREATE_METRICS = """
CREATE TABLE IF NOT EXISTS metrics (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol                   TEXT,
    fetched_at               TEXT,
    date                     TEXT,
    period                   TEXT,
    revenue_per_share        REAL,
    net_income_per_share     REAL,
    pe_ratio                 REAL,
    pb_ratio                 REAL,
    debt_to_equity           REAL,
    roe                      REAL,
    roa                      REAL,
    ev_to_ebitda             REAL,
    dividend_yield           REAL,
    free_cash_flow_per_share REAL
);"""

_CREATE_RATIOS = """
CREATE TABLE IF NOT EXISTS ratios (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol                  TEXT,
    fetched_at              TEXT,
    date                    TEXT,
    period                  TEXT,
    gross_profit_margin     REAL,
    operating_profit_margin REAL,
    net_profit_margin       REAL,
    current_ratio           REAL,
    quick_ratio             REAL,
    debt_equity_ratio       REAL,
    price_earnings_ratio    REAL,
    price_to_book_ratio     REAL,
    price_to_sales_ratio    REAL,
    return_on_equity        REAL,
    return_on_assets        REAL,
    dividend_yield          REAL
);"""

_CREATE_PRICE = """
CREATE TABLE IF NOT EXISTS price_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol      TEXT,
    fetched_at  TEXT,
    date        TEXT,
    open        REAL,
    high        REAL,
    low         REAL,
    close       REAL,
    adj_close   REAL,
    volume      INTEGER,
    change      REAL,
    change_pct  REAL
);"""


# ═══════════════════════════════════════════════════════════════════════════════
#  SQLite – internal helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for ddl in [_CREATE_PROFILE, _CREATE_METRICS, _CREATE_RATIOS, _CREATE_PRICE]:
        cur.execute(ddl)
    conn.commit()
    return conn


def _insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict]):
    if not rows:
        return
    cols         = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(cols))
    sql          = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    conn.executemany(sql, [list(r.values()) for r in rows])
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def save_raw_data(raw: dict, symbol: str):
    """
    Persist raw FMP API data to SQLite.

    Parameters
    ----------
    raw    : dict returned by fetch_all(symbol)
    symbol : stock ticker, e.g. "AAPL"
    """
    conn = _get_conn()
    try:
        _insert_rows(conn, "profile",       _normalise_profile(raw, symbol))
        _insert_rows(conn, "metrics",       _normalise_metrics(raw, symbol))
        _insert_rows(conn, "ratios",        _normalise_ratios(raw, symbol))
        _insert_rows(conn, "price_history", _normalise_prices(raw, symbol))
        print(f"[storage] ✅  Saved to SQLite → {DB_PATH}  (symbol={symbol})")
    finally:
        conn.close()


def is_data_fresh(symbol: str, max_age_hours: int = 24) -> bool:
    """
    Returns True if we already have data for this symbol fetched within
    max_age_hours, so we can skip the API call.
    """
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute(
            "SELECT fetched_at FROM profile WHERE symbol = ? ORDER BY fetched_at DESC LIMIT 1",
            (symbol.upper(),)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return False
        fetched_at = datetime.fromisoformat(row[0])
        return datetime.utcnow() - fetched_at < timedelta(hours=max_age_hours)
    except Exception:
        return False


def load_raw_from_sqlite(symbol: str) -> dict:
    """
    Reconstruct the raw-API-style dict from SQLite so the rest of the
    pipeline (build_documents, etc.) works without modification.

    Returns a dict with keys: profile, metrics, ratios, price
    """
    symbol = symbol.upper()
    conn   = _get_conn()

    def _rows(table: str) -> list[dict]:
        cur = conn.execute(
            f"SELECT * FROM {table} WHERE symbol = ? ORDER BY fetched_at DESC",
            (symbol,)
        )
        return [dict(r) for r in cur.fetchall()]

    # Profile
    profile_rows = _rows("profile")
    profile_out  = []
    if profile_rows:
        p = profile_rows[0]
        profile_out = [{
            "companyName":       p.get("company_name", ""),
            "industry":          p.get("industry", ""),
            "sector":            p.get("sector", ""),
            "marketCap":         p.get("market_cap"),
            "country":           p.get("country", ""),
            "exchangeShortName": p.get("exchange", ""),
            "currency":          p.get("currency", ""),
            "website":           p.get("website", ""),
            "description":       p.get("description", ""),
        }]

    # Metrics
    metrics_out = [{
        "date":                 r.get("date"),
        "period":               r.get("period"),
        "revenuePerShare":      r.get("revenue_per_share"),
        "netIncomePerShare":    r.get("net_income_per_share"),
        "peRatio":              r.get("pe_ratio"),
        "pbRatio":              r.get("pb_ratio"),
        "debtToEquity":         r.get("debt_to_equity"),
        "roe":                  r.get("roe"),
        "roa":                  r.get("roa"),
        "evToEbitda":           r.get("ev_to_ebitda"),
        "dividendYield":        r.get("dividend_yield"),
        "freeCashFlowPerShare": r.get("free_cash_flow_per_share"),
    } for r in _rows("metrics")]

    # Ratios
    ratios_out = [{
        "date":                  r.get("date"),
        "period":                r.get("period"),
        "grossProfitMargin":     r.get("gross_profit_margin"),
        "operatingProfitMargin": r.get("operating_profit_margin"),
        "netProfitMargin":       r.get("net_profit_margin"),
        "currentRatio":          r.get("current_ratio"),
        "quickRatio":            r.get("quick_ratio"),
        "debtEquityRatio":       r.get("debt_equity_ratio"),
        "priceEarningsRatio":    r.get("price_earnings_ratio"),
        "priceToBookRatio":      r.get("price_to_book_ratio"),
        "priceToSalesRatio":     r.get("price_to_sales_ratio"),
        "returnOnEquity":        r.get("return_on_equity"),
        "returnOnAssets":        r.get("return_on_assets"),
        "dividendYield":         r.get("dividend_yield"),
    } for r in _rows("ratios")]

    # Price history
    price_out = [{
        "date":          r.get("date"),
        "open":          r.get("open"),
        "high":          r.get("high"),
        "low":           r.get("low"),
        "close":         r.get("close"),
        "adjClose":      r.get("adj_close"),
        "volume":        r.get("volume"),
        "change":        r.get("change"),
        "changePercent": r.get("change_pct"),
    } for r in _rows("price_history")]

    conn.close()

    return {
        "profile": profile_out,
        "metrics": metrics_out,
        "ratios":  ratios_out,
        "price":   price_out,
    }


def load_from_sqlite(symbol: str, table: str) -> pd.DataFrame:
    """
    Read any table from the SQLite DB as a pandas DataFrame.

    Parameters
    ----------
    symbol : filter rows by ticker (pass None for all symbols)
    table  : one of  profile | metrics | ratios | price_history
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"No DB found at {DB_PATH}. Run the pipeline first.")

    conn  = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM {table}"
    if symbol:
        query += f" WHERE symbol = '{symbol.upper()}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df