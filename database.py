import sqlite3
from pathlib import Path
import pandas as pd

DB=Path("drought_history.db")

def conn():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS runs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        waktu TEXT NOT NULL, tema TEXT, wilayah TEXT, jumlah INTEGER,
        risiko_rata REAL)""")
    c.commit()
    return c

def save_run(df,theme,region):
    c=conn()
    try:
        c.execute("INSERT INTO runs(waktu,tema,wilayah,jumlah,risiko_rata) VALUES(datetime('now','localtime'),?,?,?,?)",
                  (theme,region,len(df),float(df["Skor Risiko"].mean()) if not df.empty else 0))
        c.commit()
    finally: c.close()

def load_history():
    c=conn()
    try:
        return pd.read_sql_query("SELECT waktu AS Waktu, tema AS Tema, wilayah AS Wilayah, jumlah AS Konten, risiko_rata AS Risiko_Rata2 FROM runs ORDER BY id DESC LIMIT 500",c)
    finally: c.close()
