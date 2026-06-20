"""
app.py
------
Local Food Wastage Management System — Streamlit Application
Page 1: Overview

Run with:
    streamlit run app.py
(from inside the streamlit_app/ directory)
"""

import subprocess
import sys
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "food_wastage.db"
if not DB_PATH.exists():
    build_script = Path(__file__).resolve().parent.parent / "sql" / "build_database.py"
    subprocess.run([sys.executable, str(build_script)], check=True)

from utils import inject_css, kpi_card, run_query, insight, COLORS
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🌾",
    layout="wide",
)
inject_css()

# ----------------------------------------------------------------
# Header
# ----------------------------------------------------------------
st.markdown(
    f"""
    <div style="padding: 0.5rem 0 1.2rem 0;">
        <p style="text-transform:uppercase; letter-spacing:0.15em; color:{COLORS['terracotta']};
                  font-size:0.8rem; margin-bottom:0.2rem; font-weight:600;">
            Local Food Wastage Management System
        </p>
        <h1 style="margin:0; font-size:2.4rem;">Connecting Surplus to Need</h1>
        <p style="color:{COLORS['muted']}; font-size:1.05rem; max-width:700px; margin-top:0.4rem;">
            A data platform linking restaurants, grocery stores, supermarkets, and
            caterers with NGOs, shelters, charities, and individuals — so surplus
            food gets redistributed instead of wasted.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ----------------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------------
total_providers = run_query("SELECT COUNT(*) AS n FROM Providers").iloc[0]["n"]
total_receivers = run_query("SELECT COUNT(*) AS n FROM Receivers").iloc[0]["n"]
total_listings = run_query("SELECT COUNT(*) AS n FROM Food_Listings").iloc[0]["n"]
total_claims = run_query("SELECT COUNT(*) AS n FROM Claims").iloc[0]["n"]
total_quantity = run_query("SELECT SUM(Quantity) AS q FROM Food_Listings").iloc[0]["q"]
completed_pct = run_query(
    "SELECT ROUND(100.0*SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END)/COUNT(*),1) AS pct FROM Claims"
).iloc[0]["pct"]

c1, c2, c3, c4 = st.columns(4)
kpi_card("Total Providers", f"{total_providers:,}", c1)
kpi_card("Total Receivers", f"{total_receivers:,}", c2)
kpi_card("Food Listings", f"{total_listings:,}", c3)
kpi_card("Total Claims", f"{total_claims:,}", c4)

c5, c6 = st.columns(2)
kpi_card("Total Food Quantity Listed (units)", f"{total_quantity:,}", c5)
kpi_card("Claim Completion Rate", f"{completed_pct}%", c6)

st.divider()

# ----------------------------------------------------------------
# Business Objective
# ----------------------------------------------------------------
left, right = st.columns([3, 2])

with left:
    st.subheader("Business Objective")
    st.write(
        """
        Every day, restaurants, grocery stores, and supermarkets discard food that
        is still safe to eat, while NGOs and individuals nearby struggle to access
        meals. This platform closes that gap by giving providers a place to list
        surplus food and giving receivers a way to find and claim it — all backed
        by a relational database and analyzed for trends that drive smarter
        food-rescue decisions.
        """
    )
    st.subheader("Who Uses This Platform")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**Food Providers**")
        st.markdown("- Restaurants\n- Grocery Stores\n- Supermarkets\n- Catering Services")
    with cc2:
        st.markdown("**Food Receivers**")
        st.markdown("- NGOs\n- Charities\n- Shelters\n- Individuals")

with right:
    st.subheader("How to Navigate")
    st.markdown(
        """
        Use the **sidebar** to move between pages:

        - **Data Analysis** — EDA charts with filters
        - **SQL Insights** — all 20 business SQL queries
        - **Claim Analysis** — claim status & top performers
        - **Browse & Claim** — search listings, view provider contacts
        - **Recommendations** — data-driven action items
        """
    )

insight(
    f"A {completed_pct}% claim completion rate means a meaningful share of listed "
    "food is not converting into a delivered claim. See the SQL Insights and "
    "Recommendations pages for where to focus improvement efforts."
)
