"""
Page 4 — Claim Analysis
Claim status distribution, top receivers, top providers.
"""

import streamlit as st
import plotly.express as px
from utils import inject_css, run_query, insight, kpi_card, CHART_SEQUENCE

st.set_page_config(page_title="Claim Analysis | Food Wastage System", page_icon="📦", layout="wide")
inject_css()

st.title("Claim Analysis")
st.caption("How effectively listed food converts into successful claims.")

status_df = run_query("""
    SELECT Status, COUNT(*) AS Count,
           ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM Claims), 1) AS Pct
    FROM Claims GROUP BY Status ORDER BY Count DESC
""")

c1, c2, c3 = st.columns(3)
for col, row in zip([c1, c2, c3], status_df.itertuples()):
    kpi_card(row.Status, f"{row.Count:,} ({row.Pct}%)", col)

st.divider()

col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Claim Status Distribution")
    fig = px.pie(status_df, names="Status", values="Count", color_discrete_sequence=CHART_SEQUENCE, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Claims Over Time (Daily)")
    trend = run_query("""
        SELECT strftime('%Y-%m-%d', Timestamp) AS Claim_Date, Status, COUNT(*) AS Count
        FROM Claims GROUP BY Claim_Date, Status ORDER BY Claim_Date
    """)
    fig = px.line(trend, x="Claim_Date", y="Count", color="Status", markers=True,
                  color_discrete_sequence=CHART_SEQUENCE)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)
with col3:
    st.subheader("Top 10 Receivers (Completed Claims)")
    top_recv = run_query("""
        SELECT r.Name, r.Type, r.City, COUNT(*) AS Completed_Claims, SUM(f.Quantity) AS Total_Quantity
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
        ORDER BY Total_Quantity DESC LIMIT 10
    """)
    st.dataframe(top_recv, use_container_width=True, hide_index=True)
    fig = px.bar(top_recv, x="Total_Quantity", y="Name", orientation="h",
                 color_discrete_sequence=[CHART_SEQUENCE[0]])
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Top 10 Providers (Completed Claims)")
    top_prov = run_query("""
        SELECT p.Name, p.Type, p.City, COUNT(*) AS Completed_Claims, SUM(f.Quantity) AS Total_Quantity
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID, p.Name, p.Type, p.City
        ORDER BY Total_Quantity DESC LIMIT 10
    """)
    st.dataframe(top_prov, use_container_width=True, hide_index=True)
    fig = px.bar(top_prov, x="Total_Quantity", y="Name", orientation="h",
                 color_discrete_sequence=[CHART_SEQUENCE[1]])
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

pending_pct = status_df.loc[status_df["Status"] == "Pending", "Pct"]
cancelled_pct = status_df.loc[status_df["Status"] == "Cancelled", "Pct"]
insight(
    f"Pending claims sit at {pending_pct.values[0] if len(pending_pct) else 0}% and "
    f"cancelled claims at {cancelled_pct.values[0] if len(cancelled_pct) else 0}% — together "
    "these represent food that is listed but not reliably reaching a receiver. "
    "Reducing cancellations even by a few points would meaningfully raise the "
    "platform's effective food-rescue rate."
)
