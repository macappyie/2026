import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime
import os

# ================= CONFIG =================
API_KEY = "YOUR_API_KEY"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

st.set_page_config(page_title="MoneyAssure Dashboard", layout="wide")
st.title("📊 MoneyAssure Dashboard")

# ================= KITE SETUP =================
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ================= FETCH DATA FUNCTION =================
def get_top_gainers():
    instruments = kite.instruments("NSE")
    df_inst = pd.DataFrame(instruments)

    # Example: Top 200 stocks (modify if needed)
    symbols = df_inst[df_inst["segment"] == "NSE"][:200]

    data = []

    for _, row in symbols.iterrows():
        try:
            ltp_data = kite.ltp(f"NSE:{row['tradingsymbol']}")
            ltp = ltp_data[f"NSE:{row['tradingsymbol']}"]["last_price"]
            change = ltp_data[f"NSE:{row['tradingsymbol']}"]["change"]

            data.append({
                "Symbol": row["tradingsymbol"],
                "LTP": round(ltp, 2),
                "% Change": round(change, 2)
            })
        except:
            continue

    df = pd.DataFrame(data)
    return df


# ================= MAIN LOGIC =================
df = get_top_gainers()

if not df.empty:

    # -------- FIX SORTING --------
    df["% Change"] = pd.to_numeric(df["% Change"], errors="coerce")
    df = df.sort_values(by="% Change", ascending=False).reset_index(drop=True)

    # -------- RANK UPDATE --------
    df["Rank"] = df.index + 1

    # -------- TOP 20 ONLY --------
    df = df.head(20)

    # -------- FLASH LOGIC (OPTIONAL) --------
    def highlight_row(row):
        if row["% Change"] > 5:
            return ['background-color: #0f5132; color: white'] * len(row)
        return [''] * len(row)

    st.subheader("🟢 Top 20 Gainers (High Levels)")
    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

else:
    st.warning("No data available.")

