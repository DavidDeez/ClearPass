import sqlite3
import json
from typing import Dict, Any, Optional

DB_FILE = "clearpass.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Verifications table for audit logs and caching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verifications (
            bvn TEXT PRIMARY KEY,
            trust_score INTEGER,
            verdict TEXT,
            details_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # API Keys for developer console
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            developer_name TEXT,
            active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def save_verification(bvn: str, result: Dict[str, Any]):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO verifications (bvn, trust_score, verdict, details_json)
        VALUES (?, ?, ?, ?)
    ''', (bvn, result.get("trust_score", 0), result.get("verdict", "BLOCK"), json.dumps(result)))
    conn.commit()
    conn.close()

def get_verification(bvn: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT details_json FROM verifications WHERE bvn = ?', (bvn,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def get_recent_verifications(limit: int = 10) -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT bvn, trust_score, verdict, timestamp FROM verifications ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"bvn": r[0], "trust_score": r[1], "verdict": r[2], "timestamp": r[3]} for r in rows]

init_db()
