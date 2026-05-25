from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.data_engine import _ensure_nse_symbol, get_current_price


DEFAULT_DB_PATH = Path("data/portfolio.db")


def _connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                avg_price REAL NOT NULL CHECK(avg_price > 0),
                entry_date TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('BUY', 'SELL')),
                symbol TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_trade(symbol: str, qty: int, buy_price: float, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    if qty <= 0 or buy_price <= 0:
        raise ValueError("qty and buy_price must be positive")

    init_db(db_path)
    clean_symbol = _ensure_nse_symbol(symbol)
    now = datetime.utcnow().isoformat()

    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO holdings(symbol, quantity, avg_price, entry_date) VALUES(?, ?, ?, ?)",
            (clean_symbol, qty, float(buy_price), now),
        )
        holding_id = int(cur.lastrowid)
        cur.execute(
            "INSERT INTO transactions(type, symbol, price, quantity, timestamp) VALUES(?, ?, ?, ?, ?)",
            ("BUY", clean_symbol, float(buy_price), qty, now),
        )
        conn.commit()
    return holding_id


def remove_trade(trade_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    if trade_id <= 0:
        return False

    init_db(db_path)
    now = datetime.utcnow().isoformat()

    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT symbol, quantity, avg_price FROM holdings WHERE id = ?", (trade_id,))
        row = cur.fetchone()
        if row is None:
            return False

        symbol, quantity, avg_price = row
        cur.execute("DELETE FROM holdings WHERE id = ?", (trade_id,))
        cur.execute(
            "INSERT INTO transactions(type, symbol, price, quantity, timestamp) VALUES(?, ?, ?, ?, ?)",
            ("SELL", symbol, float(avg_price), int(quantity), now),
        )
        conn.commit()
    return True


def get_holdings(db_path: str | Path = DEFAULT_DB_PATH) -> List[Dict[str, object]]:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, symbol, quantity, avg_price, entry_date FROM holdings ORDER BY id ASC"
        )
        rows = cur.fetchall()

    output: List[Dict[str, object]] = []
    for row in rows:
        output.append(
            {
                "id": int(row[0]),
                "symbol": str(row[1]),
                "quantity": int(row[2]),
                "avg_price": float(row[3]),
                "entry_date": str(row[4]),
            }
        )
    return output


def get_portfolio_value(db_path: str | Path = DEFAULT_DB_PATH) -> Dict[str, object]:
    holdings = get_holdings(db_path)
    positions: List[Dict[str, object]] = []
    total_cost = 0.0
    total_market_value = 0.0

    for h in holdings:
        symbol = str(h["symbol"])
        qty = int(h["quantity"])
        avg_price = float(h["avg_price"])
        cost_value = qty * avg_price
        current_price: Optional[float] = get_current_price(symbol)
        market_value = (current_price * qty) if current_price is not None else 0.0
        pnl = market_value - cost_value if current_price is not None else None

        total_cost += cost_value
        if current_price is not None:
            total_market_value += market_value

        positions.append(
            {
                **h,
                "current_price": current_price,
                "cost_value": cost_value,
                "market_value": market_value if current_price is not None else None,
                "pnl": pnl,
            }
        )

    total_pnl = total_market_value - total_cost if total_market_value > 0 else None
    return {
        "positions": positions,
        "total_cost": total_cost,
        "total_market_value": total_market_value if total_market_value > 0 else None,
        "total_pnl": total_pnl,
    }
