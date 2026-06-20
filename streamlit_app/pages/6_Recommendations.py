"""
Page 6 — Business Recommendations
Recommendations derived from the actual query results in this
dataset, not generic boilerplate.
"""

import streamlit as st
from utils import inject_css, run_query, kpi_card, COLORS

st.set_page_config(page_title="Recommendations | Food Wastage System", page_icon="✅", layout="wide")
inject_css()

st.title("Business Recommendations")
st.caption("Each recommendation below is tied to a specific finding from the live data.")

# Pull supporting numbers live so the page can't drift out of sync with the data
completion = run_query("""
    SELECT ROUND(100.0*SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END)/COUNT(*),1) AS pct,
           ROUND(100.0*SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END)/COUNT(*),1) AS cancel_pct
    FROM Claims
""").iloc[0]

zero_claim_providers = run_query("""
    SELECT COUNT(*) AS n FROM Providers p WHERE p.Provider_ID NOT IN (
        SELECT DISTINCT f.Provider_ID FROM Food_Listings f
        JOIN Claims c ON f.Food_ID = c.Food_ID WHERE c.Status = 'Completed'
    )
""").iloc[0]["n"]

never_claimed_listings = run_query("""
    SELECT COUNT(*) AS n FROM Food_Listings f WHERE f.Food_ID NOT IN (SELECT Food_ID FROM Claims)
""").iloc[0]["n"]

top_provider_type = run_query("""
    SELECT Provider_Type, SUM(Quantity) AS t FROM Food_Listings
    GROUP BY Provider_Type ORDER BY t DESC LIMIT 1
""").iloc[0]

cancel_by_meal = run_query("""
    SELECT f.Meal_Type, COUNT(*) AS n FROM Claims c JOIN Food_Listings f ON c.Food_ID = f.Food_ID
    WHERE c.Status = 'Cancelled' GROUP BY f.Meal_Type ORDER BY n DESC LIMIT 1
""").iloc[0]

c1, c2, c3 = st.columns(3)
kpi_card("Claim Completion Rate", f"{completion['pct']}%", c1)
kpi_card("Providers w/ Zero Completed Claims", f"{zero_claim_providers:,} / 1,000", c2)
kpi_card("Listings Never Claimed", f"{never_claimed_listings:,} / 1,000", c3)

st.divider()

recommendations = [
    {
        "title": "1. Investigate and re-engage low-performing providers",
        "body": f"**{zero_claim_providers:,} of 1,000 providers (≈{zero_claim_providers/10:.0f}%)** have never had a "
                "completed claim. Before assuming the food itself is unwanted, audit whether the gap is "
                "discoverability (listings not surfaced to nearby receivers), pickup logistics, or listing quality "
                "(missing details, inconvenient timing).",
    },
    {
        "title": "2. Reduce the at-risk pool of unclaimed listings",
        "body": f"**{never_claimed_listings} listings ({never_claimed_listings/10:.1f}%)** have received zero claims of "
                "any status. Combined with the expiry-proximity query (SQL Insights #17), this is a concrete, "
                "queryable list — use it to trigger proactive outreach to nearby receivers before food expires.",
    },
    {
        "title": "3. Target the cancellation rate, not just completion rate",
        "body": f"**{completion['cancel_pct']}% of all claims are cancelled** after being made. Cancellations waste "
                "more than a non-claim, since the food was earmarked and unavailable to other receivers during "
                "that window. A short post-cancellation reason field would let the platform diagnose root causes "
                "(no-show, food no longer suitable, logistics failure).",
    },
    {
        "title": f"4. Address the elevated cancellation rate for {cancel_by_meal['Meal_Type']}",
        "body": f"**{cancel_by_meal['Meal_Type']}** listings show the highest cancellation count among meal types "
                "in this dataset. If this holds at scale, it may reflect timing mismatch — e.g. breakfast items "
                "being listed too close to spoilage for receivers to act on them.",
    },
    {
        "title": f"5. Formalize partnerships with {top_provider_type['Provider_Type']} providers",
        "body": f"**{top_provider_type['Provider_Type']}** contributes the largest total quantity "
                f"({top_provider_type['t']:,} units) of any provider type. Recurring pickup agreements with the "
                "top contributors in this category (see SQL Insights #3) would lock in the platform's largest "
                "supply source.",
    },
    {
        "title": "6. Build supply/demand maps at the city level",
        "body": "SQL Insights #20 (Supply vs Demand by City) surfaces cities with providers but few or no "
                "receivers, and vice versa. These are the clearest candidates for either new NGO outreach "
                "or new provider recruitment — not a one-size-fits-all expansion plan.",
    },
    {
        "title": "7. Set up expiry-based alerting",
        "body": "Combine SQL Insights #8 (claims per food item) and #17 (nearest-expiry, unclaimed) into a "
                "scheduled job that flags listings within 48 hours of expiry with zero completed claims, and "
                "push that list to nearby receivers automatically.",
    },
    {
        "title": "8. Recognize top-performing providers publicly",
        "body": "Use SQL Insights #3 and #9 (most contributed / most successfully claimed) to run a recurring "
                "\"Top Donor\" recognition — proven in food-rescue programs to increase retention of high-volume "
                "donors once they're identified and thanked.",
    },
    {
        "title": "9. Track receiver reliability alongside provider reliability",
        "body": "SQL Insights #14 and #18 rank receivers and receiver types by completed quantity. Pairing this "
                "with cancellation data (point 3) would let the platform identify and support receivers with "
                "high claim-but-low-completion patterns, rather than treating all receivers uniformly.",
    },
    {
        "title": "10. Re-evaluate the monthly-trend assumption in future data collection",
        "body": "This dataset's claim timestamps span only 21 days (Mar 1–21, 2025), which is too narrow for "
                "monthly seasonality analysis. Recommend the platform retain at least 6–12 months of claim "
                "history going forward so genuine seasonal patterns (holidays, semester breaks, etc.) become "
                "visible.",
    },
]

for rec in recommendations:
    st.markdown(
        f"""
        <div style="background-color:{COLORS['panel']}; border-radius:8px; padding:1rem 1.3rem; margin-bottom:0.8rem;">
            <p style="font-weight:700; margin-bottom:0.3rem; color:{COLORS['ink']};">{rec['title']}</p>
            <p style="margin:0; color:{COLORS['ink']};">{rec['body']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
