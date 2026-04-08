import sqlite3

conn = sqlite3.connect("detections.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    label TEXT NOT NULL,
    confidence REAL NOT NULL,
    frames_analyzed INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database initialized successfully.")
