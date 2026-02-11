import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime

# ================= CONFIG =================
API_KEY = "YOUR_API_KEY"

st.set_page_config(page_title="MoneyAssure Dashboard", layout="wide")
st.title("📊 MoneyAssure Dashboard")

# ================= LOAD TOKEN =================
with open("access_token.txt") as f:
    ACCESS_TOKEN = f.read().strip()

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ================= SESSION STATE =================
if "rank_map" not in st.session_state:
    st.session_state.rank_map = {}

# ================= FETCH DATA =================
def get_top_gainers():

    instruments = kite.instruments("NSE")
    df_inst = pd.DataFrame(instruments)

    symbols = df_inst[
        (df_inst["exchange"] == "NSE") &
        (df_inst["instrument_type"] == "EQ")
    ].head(300)

    rows = []

    for _, row in symbols.iterrows():
        try:
            q = kite.quote(f"NSE:{row['tradingsymbol']}")
            q = q[f"NSE:{row['tradingsymbol']}"]

            ltp = q["last_price"]
            prev_close = q["ohlc"]["close"]
            change = ((ltp - prev_close) / prev_close) * 100

            rows.append({
                "Symbol": row["tradingsymbol"],
                "LTP": round(ltp, 2),
                "% Change": round(change, 2)
            })
        except:
            pass

    return pd.DataFrame(rows)

# ================= FREEZE RANK =================
def apply_freeze_rank(df):
    rank_map = st.session_state.rank_map

    for sym in df["Symbol"]:
        if sym not in rank_map:
            rank_map[sym] = len(rank_map) + 1

    df["Rank"] = df["Symbol"].map(rank_map)
    return df

# ================= MAIN =================
df = get_top_gainers()

if not df.empty:

    # Sort only by % change
    df["% Change"] = pd.to_numeric(df["% Change"], errors="coerce")
    df = df.sort_values(by="% Change", ascending=False).reset_index(drop=True)

    # Apply frozen rank
    df = apply_freeze_rank(df)

    # Top 20
    df = df.head(20)

    st.subheader("🟢 Top 20 Gainers (High Levels)")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("No data available")


