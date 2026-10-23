import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import date

st.set_page_config(page_title="Seasonal Returns", page_icon="📈", layout="wide")
st.title("📈 Asset Seasonal Returns Dashboard")

# 1. Find all available CSV files
csv_files = [f for f in os.listdir(".") if f.endswith(".csv") and f != "requirements.txt"]
if not csv_files:
    st.error("No CSV files found in the repository!")
    st.stop()

# --- Complete Seasonal Dictionary ---
SEASONAL_DATA = {
    "copper.csv": {
        "bull": {"start": "11-22", "end": "05-05", "note": "Tactical: Nov 22 → Dec 01"},
        "bear": {"start": "06-10", "end": "08-25", "note": "Chop/Dip: Sep 25 → Oct 28"}
    },
    "mcxcopper.csv": {
        "bull": {"start": "11-22", "end": "05-05", "note": "Tactical: Nov 22 → Dec 01"},
        "bear": {"start": "06-10", "end": "08-25", "note": "Chop/Dip: Sep 25 → Oct 28"}
    },
    "lmecopper.csv": {
        "bull": {"start": "11-22", "end": "05-05", "note": "Tactical: Nov 22 → Dec 01"},
        "bear": {"start": "06-10", "end": "08-25", "note": "Chop/Dip: Sep 25 → Oct 28"}
    },
    "mcaluminium.csv": {
        "bull": {"start": "01-08", "end": "04-18", "note": ""},
        "bear": {"start": "05-12", "end": "06-28", "note": "Secondary: Dec 01 → Dec 24"}
    },
    "lmealuminium.csv": {
        "bull": {"start": "01-08", "end": "04-18", "note": ""},
        "bear": {"start": "05-12", "end": "06-28", "note": "Secondary: Dec 01 → Dec 24"}
    },
    "mczinc.csv": {
        "bull": {"start": "12-12", "end": "03-25", "note": ""},
        "bear": {"start": "05-05", "end": "07-20", "note": ""}
    },
    "lmezinc.csv": {
        "bull": {"start": "12-12", "end": "03-25", "note": ""},
        "bear": {"start": "05-05", "end": "07-20", "note": ""}
    },
    "gold.csv": {
        "bull": {"start": "12-22", "end": "02-10", "note": "Secondary: Jul 28 → Sep 12"},
        "bear": {"start": "02-24", "end": "05-15", "note": "Fall dip: Oct 10 → Nov 20"}
    },
    "silver.csv": {
        "bull": {"start": "12-16", "end": "02-25", "note": ""},
        "bear": {"start": "02-28", "end": "06-15", "note": ""}
    },
    "usoil.csv": {
        "bull": {"start": "02-15", "end": "04-28", "note": "Summer: Jun 25 → Aug 18"},
        "bear": {"start": "09-18", "end": "11-22", "note": ""}
    },
    "dxy.csv": {
        "bull": {"start": "01-04", "end": "02-28", "note": "Autumn: Sep 01 → Oct 31"},
        "bear": {"start": "04-10", "end": "06-05", "note": "Year-end: Nov 15 → Dec 28"}
    },
    "usdinr.csv": {
        "bull": {"start": "08-15", "end": "10-28", "note": "Pre-monsoon: May 10 → Jun 25"},
        "bear": {"start": "01-15", "end": "03-31", "note": "Winter: Nov 20 → Dec 31"}
    },
    "nifty.csv": {
        "bull": {"start": "10-25", "end": "01-05", "note": "Diwali/Santa rally; Secondary: Mar 26 → Apr 30"},
        "bear": {"start": "01-10", "end": "02-20", "note": "Union Budget risk; Secondary: Aug 20 → Sep 30"}
    },
    "nasdaq.csv": {
        "bull": {"start": "10-28", "end": "01-06", "note": "Year-end push; Summer: Jun 28 → Jul 22"},
        "bear": {"start": "02-12", "end": "03-15", "note": "Autumn: Sep 02 → Oct 12"}
    }
}

# --- CALLBACK FUNCTION FOR BUTTONS ---
def update_dates(start_str, end_str):
    s_month, s_day = map(int, start_str.split("-"))
    e_month, e_day = map(int, end_str.split("-"))
    
    # Set the session state variables that the date pickers look at
    st.session_state["entry_picker"] = date(2024, s_month, s_day)
    st.session_state["exit_picker"] = date(2025, e_month, e_day)

# Initialize defaults if they don't exist
if "entry_picker" not in st.session_state:
    st.session_state["entry_picker"] = date(2024, 11, 21)
if "exit_picker" not in st.session_state:
    st.session_state["exit_picker"] = date(2025, 2, 21)

# 2. Create the dropdowns
col1, col2, col3 = st.columns(3)
with col1:
    selected_file = st.selectbox("Select Asset", csv_files)

# --- Display Suggestions and Quick-Select Buttons ---
if selected_file in SEASONAL_DATA:
    data = SEASONAL_DATA[selected_file]
    
    st.markdown("---")
    st.subheader(f"💡 Suggested Seasonal Windows for {selected_file}")
    
    tab1, tab2 = st.tabs(["📈 Bullish Window", "📉 Bearish Window"])
    
    with tab1:
        st.success(f"**Optimal Window:** {data['bull']['start']} to {data['bull']['end']}")
        if data['bull']['note']:
            st.caption(f"💡 {data['bull']['note']}")
            
        # Using on_click callback to fix the date update issue
        st.button(
            "Load Bullish Dates", 
            on_click=update_dates, 
            args=(data['bull']['start'], data['bull']['end'])
        )
            
    with tab2:
        st.error(f"**Optimal Window:** {data['bear']['start']} to {data['bear']['end']}")
        if data['bear']['note']:
            st.caption(f"💡 {data['bear']['note']}")
            
        st.button(
            "Load Bearish Dates", 
            on_click=update_dates, 
            args=(data['bear']['start'], data['bear']['end'])
        )
    
    st.markdown("---")

# 3. Date Pickers
# We remove the 'value=' argument and rely entirely on 'key=' tied to session_state
with col2:
    entry_date = st.date_input("Entry Date (Month-Day)", key="entry_picker")
with col3:
    exit_date = st.date_input("Exit Date (Month-Day)", key="exit_picker")


# 4. The logic to calculate returns
def load_data(filename):
    df = pd.read_csv(filename)
    df.columns = [c.strip().lower() for c in df.columns]
    dc = next((c for c in df.columns if c in ("time","date")), None)
    pc = next((c for c in df.columns if c in ("close","close price","settle")), None)
    
    for fmt in ("%d-%m-%Y","%Y-%m-%d","%m/%d/%Y"):
        try:
            df[dc] = pd.to_datetime(df[dc], format=fmt)
            break
        except Exception:
            continue
    return df.rename(columns={dc:"time", pc:"close"}).sort_values("time").reset_index(drop=True)

def snap(df, s):
    c = df[df["time"] >= pd.Timestamp(s)]
    return c.iloc[0] if len(c) else None

if st.button("Run Backtest", type="primary"):
    df = load_data(selected_file)
    
    emd = entry_date.strftime("%m-%d")
    xmd = exit_date.strftime("%m-%d")
    cross_year = exit_date.month < entry_date.month

    rows = []
    for y in range(df["time"].dt.year.min(), df["time"].dt.year.max() + 1):
        e = snap(df, f"{y}-{emd}")
        x = snap(df, f"{y + int(cross_year)}-{xmd}")
        if e is None or x is None or x["time"] <= e["time"]: continue
        
        r = (x["close"]/e["close"] - 1) * 100
        rows.append({"Year":y,"Entry":e["time"].date(),"In$":e["close"],
                     "Exit":x["time"].date(),"Out$":x["close"],"Return%":r})

    if not rows:
        st.warning("No trades found for this window.")
    else:
        out = pd.DataFrame(rows)
        
        # Show the metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Win Rate", f"{(out['Return%']>0).mean()*100:.1f}%")
        m2.metric("Average Return", f"{out['Return%'].mean():.2f}%")
        m3.metric("Best Year", f"{out['Return%'].max():.2f}%")
        m4.metric("Worst Year", f"{out['Return%'].min():.2f}%")
        
        # Show the Chart with RED/GREEN logic
        st.subheader("Year-by-Year Returns")
        
        out["Color"] = out["Return%"].apply(lambda x: "Positive" if x >= 0 else "Negative")
        
        chart = alt.Chart(out).mark_bar().encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("Return%:Q", title="Return (%)"),
            color=alt.Color("Color:N", scale=alt.Scale(domain=["Positive", "Negative"], range=["#00C853", "#FF1744"]), legend=None),
            tooltip=["Year", alt.Tooltip("Return%:Q", format=".2f")]
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
        
        # Show the Table
        st.subheader("Trade Details")
        st.dataframe(out.style.format({"Return%": "{:.2f}%", "In$": "{:.4f}", "Out$": "{:.4f}"}), width="stretch")