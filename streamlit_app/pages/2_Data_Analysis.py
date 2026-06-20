"""
Page 2 — Data Analysis
Interactive EDA: filters drive live SQL queries, charts render
with Plotly so they stay interactive inside the app.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils import inject_css, run_query, insight, CHART_SEQUENCE, COLORS

st.set_page_config(page_title="Data Analysis | Food Wastage System", page_icon="📊", layout="wide")
inject_css()

st.title("Data Analysis")
st.caption("Filter the dataset and explore univariate, bivariate, and multivariate patterns.")

# ----------------------------------------------------------------
# Filters (sidebar)
# ----------------------------------------------------------------
st.sidebar.header("Filters")

cities = run_query("SELECT DISTINCT Location FROM Food_Listings ORDER BY Location")["Location"].tolist()
provider_types = run_query("SELECT DISTINCT Provider_Type FROM Food_Listings ORDER BY Provider_Type")["Provider_Type"].tolist()
food_types = run_query("SELECT DISTINCT Food_Type FROM Food_Listings ORDER BY Food_Type")["Food_Type"].tolist()
meal_types = run_query("SELECT DISTINCT Meal_Type FROM Food_Listings ORDER BY Meal_Type")["Meal_Type"].tolist()

sel_cities = st.sidebar.multiselect("City", cities, default=[])
sel_provider_types = st.sidebar.multiselect("Provider Type", provider_types, default=provider_types)
sel_food_types = st.sidebar.multiselect("Food Type", food_types, default=food_types)
sel_meal_types = st.sidebar.multiselect("Meal Type", meal_types, default=meal_types)

# Build dynamic WHERE clause safely (values come from DISTINCT query results, not free text)
conditions = []
if sel_cities:
    placeholder = ",".join("?" * len(sel_cities))
    conditions.append(f"Location IN ({placeholder})")
if sel_provider_types:
    placeholder = ",".join("?" * len(sel_provider_types))
    conditions.append(f"Provider_Type IN ({placeholder})")
if sel_food_types:
    placeholder = ",".join("?" * len(sel_food_types))
    conditions.append(f"Food_Type IN ({placeholder})")
if sel_meal_types:
    placeholder = ",".join("?" * len(sel_meal_types))
    conditions.append(f"Meal_Type IN ({placeholder})")

where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
params = tuple(sel_cities + sel_provider_types + sel_food_types + sel_meal_types)

food_df = run_query(f"SELECT * FROM Food_Listings {where_clause}", params)

if food_df.empty:
    st.warning("No listings match the selected filters. Adjust filters in the sidebar.")
    st.stop()

st.caption(f"Showing **{len(food_df):,}** of 1,000 food listings based on current filters.")

tab1, tab2, tab3 = st.tabs(["Univariate", "Bivariate", "Multivariate"])

# ----------------------------------------------------------------
# Univariate
# ----------------------------------------------------------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Food Type Distribution")
        fig = px.pie(food_df, names="Food_Type", color_discrete_sequence=CHART_SEQUENCE, hole=0.35)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Meal Type Distribution")
        counts = food_df["Meal_Type"].value_counts().reset_index()
        counts.columns = ["Meal_Type", "Count"]
        fig = px.bar(counts, x="Meal_Type", y="Count", color="Meal_Type",
                     color_discrete_sequence=CHART_SEQUENCE)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Provider Type Distribution")
        counts = food_df["Provider_Type"].value_counts().reset_index()
        counts.columns = ["Provider_Type", "Count"]
        fig = px.bar(counts, x="Provider_Type", y="Count", color="Provider_Type",
                     color_discrete_sequence=CHART_SEQUENCE)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Quantity Distribution")
        fig = px.histogram(food_df, x="Quantity", nbins=20, color_discrete_sequence=[COLORS["terracotta"]])
        st.plotly_chart(fig, use_container_width=True)

    insight(
        f"The most common food type in the current filter is "
        f"**{food_df['Food_Type'].mode()[0]}** and the most common meal occasion is "
        f"**{food_df['Meal_Type'].mode()[0]}**. Use this to decide which categories "
        "need dedicated collection routes."
    )

# ----------------------------------------------------------------
# Bivariate
# ----------------------------------------------------------------
with tab2:
    st.subheader("Top 15 Cities by Number of Listings")
    top_cities = food_df["Location"].value_counts().head(15).reset_index()
    top_cities.columns = ["City", "Listings"]
    fig = px.bar(top_cities, x="Listings", y="City", orientation="h",
                 color="Listings", color_continuous_scale=["#EAE1CC", COLORS["terracotta"]])
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Provider Type vs Quantity")
        fig = px.box(food_df, x="Provider_Type", y="Quantity", color="Provider_Type",
                     color_discrete_sequence=CHART_SEQUENCE)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Food Type vs Quantity")
        fig = px.box(food_df, x="Food_Type", y="Quantity", color="Food_Type",
                     color_discrete_sequence=CHART_SEQUENCE)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Meal Type vs Total Quantity")
    meal_qty = food_df.groupby("Meal_Type")["Quantity"].sum().reset_index()
    fig = px.bar(meal_qty, x="Meal_Type", y="Quantity", color="Meal_Type",
                 color_discrete_sequence=CHART_SEQUENCE)
    st.plotly_chart(fig, use_container_width=True)

    top_city_name = top_cities.iloc[0]["City"] if not top_cities.empty else "N/A"
    insight(
        f"**{top_city_name}** leads in number of listings under the current filter. "
        "Box-plot spread shows some provider types donate consistent quantities "
        "while others vary widely — useful for forecasting pickup volumes."
    )

# ----------------------------------------------------------------
# Multivariate
# ----------------------------------------------------------------
with tab3:
    st.subheader("Quantity by City (Top 10) and Provider Type")
    top10 = food_df["Location"].value_counts().head(10).index
    sub = food_df[food_df["Location"].isin(top10)]
    pivot = sub.pivot_table(index="Location", columns="Provider_Type", values="Quantity",
                             aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=True, color_continuous_scale=["#F5EFE3", COLORS["terracotta"]],
                     aspect="auto")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Provider Type → Food Type (Treemap)")
        fig = px.treemap(food_df, path=["Provider_Type", "Food_Type"], values="Quantity",
                          color_discrete_sequence=CHART_SEQUENCE)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("City (Top 10) → Meal Type (Sunburst)")
        fig = px.sunburst(sub, path=["Location", "Meal_Type"], values="Quantity",
                           color_discrete_sequence=CHART_SEQUENCE)
        st.plotly_chart(fig, use_container_width=True)

    insight(
        "The heatmap highlights which city + provider-type combinations contribute "
        "the largest volumes — these are the highest-leverage partnerships to "
        "formalize with recurring pickup agreements."
    )
