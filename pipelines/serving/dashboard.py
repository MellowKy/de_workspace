import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from deltalake import DeltaTable
import duckdb
import pandas as pd

st.set_page_config(
    page_title="Medallion Lakehouse Analytics",
    page_icon="🧊",
    layout="wide"
)

st.title("🧊 Medallion Data Lakehouse Analytics")
st.subheader("Real-Time Gold Tier Sales Metrics")

GOLD_DELTA_PATH = PROJECT_ROOT / "data/gold/daily_sales_delta"

@st.cache_data(ttl=5)
def load_gold_data():
    if not GOLD_DELTA_PATH.exists():
        return pd.DataFrame()

    dt = DeltaTable(str(GOLD_DELTA_PATH))
    arrow_table = dt.to_pyarrow_table()  # noqa: F841

    con = duckdb.connect()
    df = con.execute("""
        SELECT
            CAST(sales_date AS DATE) AS sales_date,
            currency,
            total_orders,
            total_revenue
        FROM arrow_table
        ORDER BY sales_date DESC
    """).df()
    con.close()
    return df

df_sales = load_gold_data()

if df_sales.empty:
    st.warning("Gold Delta Lake table is empty or uninitialized. Materialize pipeline assets first.")
else:
    st.sidebar.header("Filter Options")
    currencies = st.sidebar.multiselect(
        "Select Currency",
        options=df_sales["currency"].unique().tolist(),
        default=df_sales["currency"].unique().tolist()
    )

    filtered_df = df_sales[df_sales["currency"].isin(currencies)]

    col1, col2, col3, col4 = st.columns(4)
    total_rev = filtered_df["total_revenue"].sum()
    total_ord = filtered_df["total_orders"].sum()
    aov = total_rev / total_ord if total_ord > 0 else 0.0

    col1.metric("Total Revenue", f"${total_rev:,.2f}")
    col2.metric("Total Orders", f"{total_ord:,}")
    col3.metric("Avg Order Value (AOV)", f"${aov:,.2f}")
    col4.metric("Active Currency", ", ".join(currencies))

    st.markdown("---")

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Daily Revenue Aggregates")
        st.dataframe(filtered_df, use_container_width=True)

    with right_col:
        st.subheader("Revenue by Sales Date")
        if not filtered_df.empty:
            chart_data = filtered_df.groupby("sales_date")["total_revenue"].sum().reset_index()
            st.bar_chart(chart_data.set_index("sales_date"))
