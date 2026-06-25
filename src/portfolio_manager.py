from __future__ import annotations

import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import contextmanager

from src.data_engine import _ensure_nse_symbol, get_current_price

DEFAULT_DB_PATH = Path("data/portfolio.db")

@contextmanager
def _connect(db_path: str | Path = DEFAULT_DB_PATH):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def hash_password(password: str) -> str:
    # Simple SHA-256 hash for demonstration
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db(db_path: str | Path = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        try:
            cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN ui_theme TEXT DEFAULT 'Sunset Glow (Light)'")
        except sqlite3.OperationalError:
            pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
        except sqlite3.OperationalError:
            pass
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                avg_price REAL NOT NULL CHECK(avg_price > 0),
                entry_date TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('BUY', 'SELL')),
                symbol TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                timestamp TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        # Seed admin user
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin", "sohommallick69@gmail.com", hash_password("123456"), "admin")
            )
        conn.commit()

def register_user(username: str, email: str, password: str, role: str = "user", db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, hash_password(password), role)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def verify_user(username: str, password: str, db_path: str | Path = DEFAULT_DB_PATH) -> Optional[Dict[str, object]]:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, role, ui_theme, profile_pic FROM users WHERE username = ? AND password_hash = ?",
            (username, hash_password(password))
        )
        row = cur.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "email": row[2], "role": row[3], "ui_theme": row[4] or "Sunset Glow (Light)", "profile_pic": row[5]}
    return None

def get_all_users(db_path: str | Path = DEFAULT_DB_PATH) -> List[Dict[str, object]]:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, role FROM users ORDER BY id ASC")
        rows = cur.fetchall()
    return [{"id": r[0], "username": r[1], "email": r[2], "role": r[3]} for r in rows]

def delete_user(user_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with _connect(db_path) as conn:
        cur = conn.cursor()
        # Ensure we don't delete the main admin
        cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if row and row[0] == "admin":
            return False
        
        cur.execute("DELETE FROM holdings WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return True

def add_trade(user_id: int, symbol: str, qty: int, buy_price: float, db_path: str | Path = DEFAULT_DB_PATH) -> int:
    if qty <= 0 or buy_price <= 0:
        raise ValueError("qty and buy_price must be positive")

    init_db(db_path)
    clean_symbol = _ensure_nse_symbol(symbol)
    now = datetime.utcnow().isoformat()

    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO holdings(user_id, symbol, quantity, avg_price, entry_date) VALUES(?, ?, ?, ?, ?)",
            (user_id, clean_symbol, qty, float(buy_price), now),
        )
        holding_id = int(cur.lastrowid)
        cur.execute(
            "INSERT INTO transactions(user_id, type, symbol, price, quantity, timestamp) VALUES(?, ?, ?, ?, ?, ?)",
            (user_id, "BUY", clean_symbol, float(buy_price), qty, now),
        )
        conn.commit()
    return holding_id

def remove_trade(user_id: int, trade_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    if trade_id <= 0:
        return False

    init_db(db_path)
    now = datetime.utcnow().isoformat()

    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT symbol, quantity, avg_price FROM holdings WHERE id = ? AND user_id = ?", (trade_id, user_id))
        row = cur.fetchone()
        if row is None:
            return False

        symbol, quantity, avg_price = row
        cur.execute("DELETE FROM holdings WHERE id = ?", (trade_id,))
        cur.execute(
            "INSERT INTO transactions(user_id, type, symbol, price, quantity, timestamp) VALUES(?, ?, ?, ?, ?, ?)",
            (user_id, "SELL", symbol, float(avg_price), int(quantity), now),
        )
        conn.commit()
    return True

def get_holdings(user_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> List[Dict[str, object]]:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, symbol, quantity, avg_price, entry_date FROM holdings WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
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

def get_portfolio_value(user_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> Dict[str, object]:
    holdings = get_holdings(user_id, db_path)
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

def update_user_theme(user_id: int, theme: str, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET ui_theme = ? WHERE id = ?", (theme, user_id))
        conn.commit()
        return True

def update_profile_picture(user_id: int, base64_data: Optional[str], db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (base64_data, user_id))
        conn.commit()
        return True

def get_user_email(username: str, db_path: str | Path = DEFAULT_DB_PATH) -> Optional[str]:
    with _connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return row[0] if row else None

def update_password(username: str, new_password: str, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    with _connect(db_path) as conn:
        cur = conn.cursor()
        pw_hash = hash_password(new_password)
        cur.execute("UPDATE users SET password_hash = ? WHERE username = ?", (pw_hash, username))
        conn.commit()
        return cur.rowcount > 0

def get_user_by_username(username: str, db_path: str | Path = DEFAULT_DB_PATH) -> Optional[dict]:
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, role, ui_theme, profile_pic FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None

def get_user_by_username_or_email(identifier: str, db_path: str | Path = DEFAULT_DB_PATH) -> Optional[dict]:
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, role FROM users WHERE username = ? OR email = ?", (identifier, identifier))
        row = cur.fetchone()
        return dict(row) if row else None
