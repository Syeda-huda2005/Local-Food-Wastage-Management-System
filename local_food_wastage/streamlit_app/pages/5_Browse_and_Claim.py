"""
Page 5 — Browse & Claim
Searchable food listing directory with provider contact info,
as called for in the original project brief.
"""

import streamlit as st
from utils import inject_css, run_query

st.set_page_config(page_title="Browse & Claim | Food Wastage System", page_icon="🔎", layout="wide")
inject_css()

st.title("Browse & Claim")
st.caption("Search active food listings and view provider contact details to coordinate a pickup.")

cities = run_query("SELECT DISTINCT Location FROM Food_Listings ORDER BY Location")["Location"].tolist()
food_types = run_query("SELECT DISTINCT Food_Type FROM Food_Listings ORDER BY Food_Type")["Food_Type"].tolist()
meal_types = run_query("SELECT DISTINCT Meal_Type FROM Food_Listings ORDER BY Meal_Type")["Meal_Type"].tolist()

c1, c2, c3, c4 = st.columns(4)
city_filter = c1.selectbox("City", ["All"] + cities)
food_filter = c2.selectbox("Food Type", ["All"] + food_types)
meal_filter = c3.selectbox("Meal Type", ["All"] + meal_types)
sort_by = c4.selectbox("Sort by", ["Expiry (soonest first)", "Quantity (highest first)"])

conditions, params = [], []
if city_filter != "All":
    conditions.append("f.Location = ?")
    params.append(city_filter)
if food_filter != "All":
    conditions.append("f.Food_Type = ?")
    params.append(food_filter)
if meal_filter != "All":
    conditions.append("f.Meal_Type = ?")
    params.append(meal_filter)

where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
order_clause = "f.Expiry_Date ASC" if sort_by.startswith("Expiry") else "f.Quantity DESC"

query = f"""
    SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, f.Food_Type, f.Meal_Type,
           f.Location AS City, p.Name AS Provider_Name, p.Type AS Provider_Type,
           p.Contact AS Provider_Contact, p.Address AS Provider_Address
    FROM Food_Listings f
    JOIN Providers p ON f.Provider_ID = p.Provider_ID
    {where_clause}
    ORDER BY {order_clause}
"""

results = run_query(query, tuple(params))

st.caption(f"**{len(results):,}** listing(s) match your filters.")
st.dataframe(
    results,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Food_ID": st.column_config.NumberColumn("ID", width="small"),
        "Provider_Contact": st.column_config.TextColumn("Contact"),
    },
)

st.download_button(
    "Download listing results as CSV",
    results.to_csv(index=False).encode("utf-8"),
    file_name="food_listings_filtered.csv",
    mime="text/csv",
)

st.divider()
st.markdown(
    """
    **Note on claiming:** This page surfaces real-time listing and provider contact
    data for coordination. In a production deployment, an in-app "Claim" button
    would insert a row into the `Claims` table — omitted here to keep the focus on
    the analytics layer that the project flow requires.
    """
)
