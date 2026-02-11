import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import time, json, os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="MoneyAssure Dashboard", layout="wide")
st.title("📊 MoneyAssure Dashboard")

# ---------------- FLASH CSS ----------------
st.markdown("""
<style>
.flash-green {
    animation: flashGreen 1s infinite;
    font-weight: bold;
}
.flash-red {
    animation: flashRed 1s infinite;
    font-weight: bold;
}
@keyframes flashGreen {
    0% { background:#002b00; }
    50% { background:#00ff44; }
    100% { background:#002b00; }
}
@keyframes flashRed {
    0% { background:#330000; }
    50% { background:#ff3333; }
    100% { background:#330000; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- SECRETS ----------------
API_KEY = st.secrets["API_KEY"]
ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

RANK_FILE = "open_rank.json"

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

def flash_val(val, threshold, mode):
    try:
        v = float(val)
        if mode == "gainer" and v < threshold:
            return f'<span class="flash-green">{v}</span>'
        if mode == "loser" and v > -threshold:
            return f'<span class="flash-red">{v}</span>'
        return str(v)
    except:
        return ""

# ---------------- RANK MEMORY ----------------
def is_new_day():
    if not os.path.exists(RANK_FILE):
        return True
    d = datetime.fromtimestamp(os.path.getmtime(RANK_FILE)).date()
    return d != datetime.now().date()

def load_ranks():
    if os.path.exists(RANK_FILE):
        with open(RANK_FILE) as f:
            return json.load(f)
    return {"gainers":{}, "losers":{}}

def save_ranks(r):
    with open(RANK_FILE,"w") as f:
        json.dump(r,f)


# ---------------- FETCH DATA ----------------
rows = []
today = datetime.now().date()

tokens = [symbol_token[s] for s in WATCHLIST if s in symbol_token]
quotes = kite.quote(tokens)

progress = st.progress(0)
total = len(WATCHLIST)

for i, sym in enumerate(WATCHLIST):
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
        c10 = next((c for c in candles if c["date"].strftime("%H:%M") == "10:00"), None)
        c12 = next((c for c in candles if c["date"].strftime("%H:%M") == "12:00"), None)

        from_date = today - timedelta(days=15)
        vols = kite.historical_data(token, from_date, today - timedelta(days=1), "day")

        avg_raw = 0
        avg_vol = ""
        if len(vols) >= 7:
            avg_raw = sum(v["volume"] for v in vols[-7:]) / 7
            avg_vol = fmt_vol(avg_raw)

        today_vs = ""
        if avg_raw > 0:
            today_vs = f"{round(total_vol / avg_raw, 2)}x"

        rows.append({
            "Symbol": sym,
            "LTP": round(ltp, 2),
            "% Change": pct,
            "Avg Vol 7D": avg_vol,
            "Today Vs Avg": today_vs,
            "9:15 High %": round(((c915["high"] - prev_close) / prev_close) * 100, 2),
            "10 High %": round(((c10["high"] - prev_close) / prev_close) * 100, 2) if c10 else "",
            "12 High %": round(((c12["high"] - prev_close) / prev_close) * 100, 2) if c12 else "",
            "9:15 Low %": round(((c915["low"] - prev_close) / prev_close) * 100, 2),
            "10 Low %": round(((c10["low"] - prev_close) / prev_close) * 100, 2) if c10 else "",
            "12 Low %": round(((c12["low"] - prev_close) / prev_close) * 100, 2) if c12 else ""
        })

        progress.progress((i + 1) / total)
        time.sleep(0.15)
    except:
        pass

dfm = pd.DataFrame(rows)

# ---------------- APPLY RANK ----------------
if is_new_day():
    ranks = {"gainers":{}, "losers":{}}
else:
    ranks = load_ranks()

gainers_tmp = dfm[dfm["% Change"] > 0].sort_values("% Change", ascending=False)
losers_tmp  = dfm[dfm["% Change"] < 0].sort_values("% Change")

for i,r in enumerate(gainers_tmp.itertuples(),1):
    if r.Symbol not in ranks["gainers"]:
        ranks["gainers"][r.Symbol] = i

for i,r in enumerate(losers_tmp.itertuples(),1):
    if r.Symbol not in ranks["losers"]:
        ranks["losers"][r.Symbol] = i

save_ranks(ranks)


dfm["Rank"] = dfm.apply(
    lambda x: ranks["gainers"].get(x["Symbol"])
    if x["% Change"] > 0
    else ranks["losers"].get(x["Symbol"]),
    axis=1
)

# ---------------- SPLIT ----------------
gainers = dfm[dfm["% Change"] > 0].sort_values("Rank").head(20)
losers  = dfm[dfm["% Change"] < 0].sort_values("Rank").head(20)

gainers = gainers.drop(columns=["9:15 Low %","10 Low %","12 Low %"])
losers  = losers.drop(columns=["9:15 High %","10 High %","12 High %"])

# ---------------- DISPLAY ----------------
st.subheader("🟢 Top 20 Gainers (High Levels)")
g = gainers.copy()
g["9:15 High %"] = g["9:15 High %"].apply(lambda x: flash_val(x,1.5,"gainer"))
g["10 High %"]   = g["10 High %"].apply(lambda x: flash_val(x,1.5,"gainer"))
g["12 High %"]   = g["12 High %"].apply(lambda x: flash_val(x,1.0,"gainer"))
st.markdown(g.to_html(escape=False, index=False), unsafe_allow_html=True)

st.subheader("🔴 Top 20 Losers (Low Levels)")
l = losers.copy()
l["9:15 Low %"] = l["9:15 Low %"].apply(lambda x: flash_val(x,1.5,"loser"))
l["10 Low %"]   = l["10 Low %"].apply(lambda x: flash_val(x,1.5,"loser"))
l["12 Low %"]   = l["12 Low %"].apply(lambda x: flash_val(x,1.0,"loser"))
st.markdown(l.to_html(escape=False, index=False), unsafe_allow_html=True)

st.caption("⚡ Flash: 9:15 & 10 ≥ 1.5% | 12 ≥ 1%")
