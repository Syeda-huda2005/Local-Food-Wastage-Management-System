"""
Page 3 — SQL Insights
Runs every business query from sql/business_queries.sql live
against the database and displays results with business framing.
"""

import streamlit as st
import plotly.express as px
from utils import inject_css, run_query, CHART_SEQUENCE

st.set_page_config(page_title="SQL Insights | Food Wastage System", page_icon="🗄️", layout="wide")
inject_css()

st.title("SQL Insights")
st.caption("All queries run live against `food_wastage.db`. Full text also available in sql/business_queries.sql.")

# Each entry: title, business objective, SQL, business insight template (uses the result df)
QUERIES = [
    {
        "title": "1. Providers by City",
        "objective": "Identify which cities have the strongest provider presence.",
        "sql": "SELECT City, COUNT(*) AS Provider_Count FROM Providers GROUP BY City ORDER BY Provider_Count DESC LIMIT 15;",
        "chart": lambda df: px.bar(df, x="Provider_Count", y="City", orientation="h",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "2. Receivers by City",
        "objective": "Identify cities with the most receivers (demand concentration).",
        "sql": "SELECT City, COUNT(*) AS Receiver_Count FROM Receivers GROUP BY City ORDER BY Receiver_Count DESC LIMIT 15;",
        "chart": lambda df: px.bar(df, x="Receiver_Count", y="City", orientation="h",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "3. Most Contributing Providers (by quantity listed)",
        "objective": "Identify top donors for recognition and partnership retention.",
        "sql": """SELECT p.Provider_ID, p.Name, p.Type, SUM(f.Quantity) AS Total_Quantity_Listed
                  FROM Providers p JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
                  GROUP BY p.Provider_ID, p.Name, p.Type
                  ORDER BY Total_Quantity_Listed DESC LIMIT 10;""",
        "chart": lambda df: px.bar(df, x="Total_Quantity_Listed", y="Name", orientation="h",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "4. Most Claimed Food Item",
        "objective": "Understand which food types are in highest demand.",
        "sql": """SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
                  FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
                  GROUP BY f.Food_Name ORDER BY Claim_Count DESC;""",
        "chart": lambda df: px.bar(df, x="Food_Name", y="Claim_Count", color="Food_Name",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "5. Total Food Quantity Available",
        "objective": "Headline KPI for platform-wide food volume.",
        "sql": "SELECT SUM(Quantity) AS Total_Quantity_Available FROM Food_Listings;",
        "chart": None,
    },
    {
        "title": "6. Top Cities by Food Listing",
        "objective": "Identify the supply hotspots.",
        "sql": """SELECT Location AS City, COUNT(*) AS Listing_Count, SUM(Quantity) AS Total_Quantity
                  FROM Food_Listings GROUP BY Location ORDER BY Total_Quantity DESC LIMIT 10;""",
        "chart": lambda df: px.bar(df, x="Total_Quantity", y="City", orientation="h",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "7. Most Common Food Type",
        "objective": "Understand the dominant category of food being donated.",
        "sql": "SELECT Food_Type, COUNT(*) AS Listing_Count FROM Food_Listings GROUP BY Food_Type ORDER BY Listing_Count DESC;",
        "chart": lambda df: px.pie(df, names="Food_Type", values="Listing_Count", color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "8. Claims per Food Item (LEFT JOIN — includes zero-claim items)",
        "objective": "Spot food listings that are not being claimed at all (waste risk).",
        "sql": """SELECT f.Food_ID, f.Food_Name, f.Location, f.Quantity, COUNT(c.Claim_ID) AS Claim_Count
                  FROM Food_Listings f LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
                  GROUP BY f.Food_ID, f.Food_Name, f.Location, f.Quantity
                  ORDER BY Claim_Count ASC, f.Quantity DESC LIMIT 15;""",
        "chart": None,
    },
    {
        "title": "9. Providers with Most Successful Claims",
        "objective": "Identify providers whose donations convert into delivered food.",
        "sql": """SELECT p.Provider_ID, p.Name, p.Type, COUNT(c.Claim_ID) AS Completed_Claims
                  FROM Providers p JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
                  JOIN Claims c ON f.Food_ID = c.Food_ID
                  WHERE c.Status = 'Completed'
                  GROUP BY p.Provider_ID, p.Name, p.Type
                  ORDER BY Completed_Claims DESC LIMIT 10;""",
        "chart": lambda df: px.bar(df, x="Completed_Claims", y="Name", orientation="h",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "10. Claim Status Percentage",
        "objective": "Measure platform efficiency — what share of claims complete.",
        "sql": """SELECT Status, COUNT(*) AS Status_Count,
                         ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM Claims), 2) AS Percentage
                  FROM Claims GROUP BY Status ORDER BY Status_Count DESC;""",
        "chart": lambda df: px.pie(df, names="Status", values="Status_Count", color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "11. Average Quantity Claimed (Completed only)",
        "objective": "Typical donation size that successfully reaches a receiver.",
        "sql": """SELECT ROUND(AVG(f.Quantity),2) AS Avg_Quantity_Claimed
                  FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
                  WHERE c.Status = 'Completed';""",
        "chart": None,
    },
    {
        "title": "12. Most Claimed Meal Type",
        "objective": "Identify which meal occasion drives the most receiver demand.",
        "sql": """SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
                  FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
                  GROUP BY f.Meal_Type ORDER BY Claim_Count DESC;""",
        "chart": lambda df: px.bar(df, x="Meal_Type", y="Claim_Count", color="Meal_Type",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "13. Total Donated Quantity by Provider Type",
        "objective": "Compare contribution by provider category.",
        "sql": """SELECT Provider_Type, SUM(Quantity) AS Total_Donated_Quantity
                  FROM Food_Listings GROUP BY Provider_Type HAVING SUM(Quantity) > 0
                  ORDER BY Total_Donated_Quantity DESC;""",
        "chart": lambda df: px.bar(df, x="Provider_Type", y="Total_Donated_Quantity", color="Provider_Type",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "14. Top Receivers by Quantity Claimed (Window Function: RANK)",
        "objective": "Identify highest-impact receivers for partnership case studies.",
        "sql": """WITH receiver_totals AS (
                      SELECT r.Receiver_ID, r.Name, r.Type, SUM(f.Quantity) AS Total_Claimed
                      FROM Claims c JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
                      JOIN Food_Listings f ON c.Food_ID = f.Food_ID
                      WHERE c.Status = 'Completed'
                      GROUP BY r.Receiver_ID, r.Name, r.Type)
                  SELECT *, RANK() OVER (ORDER BY Total_Claimed DESC) AS Rank_By_Quantity
                  FROM receiver_totals ORDER BY Total_Claimed DESC LIMIT 10;""",
        "chart": lambda df: px.bar(df, x="Total_Claimed", y="Name", orientation="h",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "15. Daily Claim Trend (data spans Mar 1–21, 2025)",
        "objective": "Understand demand pattern over time to plan staffing/logistics.",
        "sql": """SELECT strftime('%Y-%m-%d', Timestamp) AS Claim_Date, COUNT(*) AS Claim_Count
                  FROM Claims GROUP BY Claim_Date ORDER BY Claim_Date;""",
        "chart": lambda df: px.line(df, x="Claim_Date", y="Claim_Count", markers=True,
                                     color_discrete_sequence=[CHART_SEQUENCE[0]]),
    },
    {
        "title": "16. Providers With Zero Successful Claims",
        "objective": "Surface donors whose listings aren't converting — candidates for outreach/support.",
        "sql": """SELECT p.Provider_ID, p.Name, p.Type, p.City FROM Providers p
                  WHERE p.Provider_ID NOT IN (
                      SELECT DISTINCT f.Provider_ID FROM Food_Listings f
                      JOIN Claims c ON f.Food_ID = c.Food_ID WHERE c.Status = 'Completed'
                  ) LIMIT 20;""",
        "chart": None,
    },
    {
        "title": "17. Listings Nearest Expiry With No Completed Claim",
        "objective": "Operational alert query — what's at the highest risk of being wasted right now.",
        "sql": """SELECT f.Food_ID, f.Food_Name, f.Location, f.Quantity, f.Expiry_Date
                  FROM Food_Listings f
                  WHERE f.Food_ID NOT IN (SELECT Food_ID FROM Claims WHERE Status = 'Completed')
                  ORDER BY f.Expiry_Date ASC LIMIT 15;""",
        "chart": None,
    },
    {
        "title": "18. Receiver Type Performance (Window Function: DENSE_RANK)",
        "objective": "Rank receiver types by total quantity successfully claimed.",
        "sql": """WITH type_totals AS (
                      SELECT r.Type, SUM(f.Quantity) AS Total_Claimed
                      FROM Claims c JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
                      JOIN Food_Listings f ON c.Food_ID = f.Food_ID
                      WHERE c.Status = 'Completed' GROUP BY r.Type)
                  SELECT *, DENSE_RANK() OVER (ORDER BY Total_Claimed DESC) AS Rank_Position
                  FROM type_totals;""",
        "chart": lambda df: px.bar(df, x="Type", y="Total_Claimed", color="Type",
                                    color_discrete_sequence=CHART_SEQUENCE),
    },
    {
        "title": "19. Top Provider Within Each City (Window Function: ROW_NUMBER + PARTITION BY)",
        "objective": "Find the leading donor per city for localized recognition programs.",
        "sql": """WITH provider_city_totals AS (
                      SELECT p.Provider_ID, p.Name, p.City, SUM(f.Quantity) AS Total_Quantity
                      FROM Providers p JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
                      GROUP BY p.Provider_ID, p.Name, p.City),
                  ranked AS (
                      SELECT *, ROW_NUMBER() OVER (PARTITION BY City ORDER BY Total_Quantity DESC) AS City_Rank
                      FROM provider_city_totals)
                  SELECT Provider_ID, Name, City, Total_Quantity, City_Rank FROM ranked
                  WHERE City_Rank = 1 ORDER BY Total_Quantity DESC LIMIT 15;""",
        "chart": None,
    },
    {
        "title": "20. Supply vs Demand by City (Full-Join Equivalent)",
        "objective": "Find cities with providers but no receivers, or vice versa — distribution gaps.",
        "sql": """SELECT COALESCE(p.City, r.City) AS City,
                         COUNT(DISTINCT p.Provider_ID) AS Provider_Count,
                         COUNT(DISTINCT r.Receiver_ID) AS Receiver_Count
                  FROM Providers p LEFT JOIN Receivers r ON p.City = r.City GROUP BY p.City
                  UNION
                  SELECT COALESCE(p.City, r.City) AS City,
                         COUNT(DISTINCT p.Provider_ID) AS Provider_Count,
                         COUNT(DISTINCT r.Receiver_ID) AS Receiver_Count
                  FROM Receivers r LEFT JOIN Providers p ON p.City = r.City GROUP BY r.City
                  ORDER BY Provider_Count DESC, Receiver_Count DESC LIMIT 20;""",
        "chart": None,
    },
]

search = st.text_input("Search queries", placeholder="e.g. 'expiry', 'provider', 'window function'")

for q in QUERIES:
    haystack = (q["title"] + q["objective"]).lower()
    if search and search.lower() not in haystack:
        continue
    with st.expander(q["title"], expanded=False):
        st.markdown(f"**Business objective:** {q['objective']}")
        st.code(q["sql"].strip(), language="sql")
        df = run_query(q["sql"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        if q["chart"] is not None and len(df) > 0:
            try:
                st.plotly_chart(q["chart"](df), use_container_width=True)
            except Exception:
                pass
        st.download_button(
            "Download results as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{q['title'].split('.')[0].strip()}_results.csv",
            mime="text/csv",
            key=f"dl_{q['title']}",
        )
