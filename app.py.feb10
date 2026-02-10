
import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import time

# ---------------- CONFIG ----------------
API_KEY = "YOUR_API_KEY"

with open("access_token.txt") as f:
    ACCESS_TOKEN = f.read().strip()

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

st.set_page_config(page_title="Top Gainers & Losers", layout="wide")
st.title("📊 Live Top Gainers & Losers")

# ---------------- LOAD INSTRUMENTS ----------------
df = pd.read_csv("instruments.csv", low_memory=False)
df = df[(df.exchange == "NSE") & (df.instrument_type == "EQ")]
symbol_token = dict(zip(df.tradingsymbol, df.instrument_token))

with open("watchlist.txt") as f:
    WATCHLIST = [x.strip() for x in f if x.strip()]

# ---------------- HELPERS ----------------
def fmt_vol(v):
    if v >= 1e7: return f"{v/1e7:.2f} Cr"
    if v >= 1e5: return f"{v/1e5:.2f} L"
    if v >= 1e3: return f"{v/1e3:.1f} K"
    return str(int(v))

# ---------------- DATA FETCH ----------------
rows = []
today = datetime.now().date()

tokens = [symbol_token[s] for s in WATCHLIST if s in symbol_token]
quotes = kite.quote(tokens)

for sym in WATCHLIST:
    try:
        token = symbol_token[sym]
        q = quotes[str(token)]

        ltp = q["last_price"]
        prev_close = q["ohlc"]["close"]
        pct = round(((ltp - prev_close) / prev_close) * 100, 2)
        total_vol = q.get("volume", 0)

        candles = kite.historical_data(token, today, today, "5minute")
        if not candles:
            continue

        c915 = candles[0]
        c10 = next((c for c in candles if c["date"].strftime("%H:%M")=="10:00"), None)
        c12 = next((c for c in candles if c["date"].strftime("%H:%M")=="12:00"), None)

        from_date = today - timedelta(days=15)
        vols = kite.historical_data(token, from_date, today - timedelta(days=1), "day")

        avg_raw = 0
        avg_vol = ""
        if len(vols) >= 7:
            avg_raw = sum(v["volume"] for v in vols[-7:]) / 7
            avg_vol = fmt_vol(avg_raw)

        today_vs = ""
        if avg_raw > 0:
            today_vs = f"{round(total_vol/avg_raw,2)}x"

        rows.append({
            "Symbol": sym,
            "LTP": round(ltp,2),
            "% Change": pct,
            "Avg Vol 7D": avg_vol,
            "Today Vs Avg": today_vs,
            "9:15 High %": round(((c915["high"]-prev_close)/prev_close)*100,2),
            "9:15 Low %": round(((c915["low"]-prev_close)/prev_close)*100,2),
            "10 High %": round(((c10["high"]-prev_close)/prev_close)*100,2) if c10 else "",
            "10 Low %": round(((c10["low"]-prev_close)/prev_close)*100,2) if c10 else "",
            "12 High %": round(((c12["high"]-prev_close)/prev_close)*100,2) if c12 else "",
            "12 Low %": round(((c12["low"]-prev_close)/prev_close)*100,2) if c12 else ""
        })

        time.sleep(0.2)
    except:
        pass

dfm = pd.DataFrame(rows)

gainers = dfm[dfm["% Change"] > 0].sort_values("% Change", ascending=False).head(20)
losers  = dfm[dfm["% Change"] < 0].sort_values("% Change").head(20)

# ---------------- DISPLAY ----------------
st.subheader("🟢 Top 20 Gainers")
st.dataframe(gainers, use_container_width=True)

st.subheader("🔴 Top 20 Losers")
st.dataframe(losers, use_container_width=True)

st.caption("Auto refresh page for latest data")

