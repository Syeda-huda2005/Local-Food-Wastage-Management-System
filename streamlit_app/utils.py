"""
utils.py
--------
Shared helpers for the Local Food Wastage Management System
Streamlit app: database connection, custom styling, and a
reusable KPI card component.
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "food_wastage.db"

# Brand palette — used consistently across charts and CSS
COLORS = {
    "ink": "#1B2E1F",        # deep charcoal-green, headers/text
    "cream": "#F5EFE3",      # page background
    "panel": "#EAE1CC",      # card background
    "terracotta": "#C76B3F", # primary accent / actions
    "gold": "#C8963E",       # secondary accent / highlights
    "leaf": "#4F7942",       # success / positive
    "rust": "#9C4221",       # warning / negative
    "muted": "#8A8270",      # captions, gridlines
}

CHART_SEQUENCE = ["#C76B3F", "#4F7942", "#C8963E", "#1B2E1F", "#9C4221", "#8A8270"]


@st.cache_resource
def get_connection():
    """Cached SQLite connection, shared across pages in a session."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=300)
def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Run a read-only SQL query and return a DataFrame. Cached for 5 minutes."""
    conn = get_connection()
    return pd.read_sql(query, conn, params=params)


def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLORS['cream']};
        }}
        h1, h2, h3 {{
            font-family: 'Georgia', 'Times New Roman', serif;
            color: {COLORS['ink']};
            letter-spacing: -0.01em;
        }}
        p, li, span, label, div {{
            color: {COLORS['ink']};
        }}
        [data-testid="stSidebar"] {{
            background-color: {COLORS['ink']};
        }}
        [data-testid="stSidebar"] * {{
            color: {COLORS['cream']} !important;
        }}
        .kpi-card {{
            background-color: {COLORS['panel']};
            border-left: 4px solid {COLORS['terracotta']};
            border-radius: 6px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 0.5rem;
        }}
        .kpi-label {{
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {COLORS['muted']};
            margin: 0;
        }}
        .kpi-value {{
            font-family: 'Georgia', serif;
            font-size: 2.1rem;
            font-weight: 700;
            color: {COLORS['ink']};
            margin: 0.1rem 0 0 0;
        }}
        .insight-box {{
            background-color: #FFF8EC;
            border-left: 4px solid {COLORS['gold']};
            border-radius: 6px;
            padding: 0.9rem 1.2rem;
            margin: 0.8rem 0 1.4rem 0;
            font-size: 0.95rem;
        }}
        .insight-box b {{
            color: {COLORS['rust']};
        }}
        hr {{
            border-color: {COLORS['panel']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value, col=None):
    target = col if col is not None else st
    target.markdown(
        f"""
        <div class="kpi-card">
            <p class="kpi-label">{label}</p>
            <p class="kpi-value">{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(text: str):
    st.markdown(f'<div class="insight-box"><b>Insight:</b> {text}</div>', unsafe_allow_html=True)
