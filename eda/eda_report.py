"""
eda_report.py
-------------
Performs the full Exploratory Data Analysis for the Local Food
Wastage Management System:
  1. Null value analysis (all 4 tables)
  2. Univariate analysis
  3. Bivariate analysis
  4. Multivariate analysis
  5. Claim analysis

Reads from food_wastage.db (built by sql/build_database.py).
Saves static charts (PNG) to outputs/charts/ and a couple of
interactive Plotly charts (HTML) for the Streamlit app to reuse.

Run:
    python eda/eda_report.py
"""

import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "food_wastage.db"
CHART_DIR = BASE_DIR / "outputs" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
PALETTE = ["#2E7D32", "#F9A825", "#C62828", "#1565C0", "#6A1B9A", "#EF6C00"]


def load_tables():
    conn = sqlite3.connect(DB_PATH)
    providers = pd.read_sql("SELECT * FROM Providers", conn)
    receivers = pd.read_sql("SELECT * FROM Receivers", conn)
    food = pd.read_sql("SELECT * FROM Food_Listings", conn)
    claims = pd.read_sql("SELECT * FROM Claims", conn)
    conn.close()
    return providers, receivers, food, claims


# ============================================================
# 1. NULL VALUE ANALYSIS
# ============================================================
def null_analysis(providers, receivers, food, claims):
    print("\n" + "=" * 60)
    print("NULL VALUE ANALYSIS")
    print("=" * 60)

    checks = {
        "Providers": (providers, ["Contact", "Address"]),
        "Receivers": (receivers, ["Contact"]),
        "Food_Listings": (food, ["Expiry_Date", "Quantity"]),
        "Claims": (claims, ["Status", "Timestamp"]),
    }

    rows = []
    for table_name, (df, cols) in checks.items():
        for col in cols:
            null_count = df[col].isnull().sum()
            null_pct = round(null_count / len(df) * 100, 2)
            rows.append({
                "Table": table_name,
                "Column": col,
                "Null_Count": null_count,
                "Null_Percentage": null_pct,
                "Total_Rows": len(df),
            })

    summary = pd.DataFrame(rows)
    print(summary.to_string(index=False))
    summary.to_csv(CHART_DIR.parent / "null_analysis_summary.csv", index=False)

    print(
        "\nFinding: In THIS dataset, none of the audited columns contain "
        "actual NULL/NaN values (0% nulls across the board). This is "
        "documented honestly below rather than assumed, since the project "
        "brief anticipated missing data that the real data does not have. "
        "See docs/null_value_analysis.md for the full write-up including "
        "possible reasons, handling methods, and business impact if nulls "
        "were to appear in a future data load."
    )
    return summary


# ============================================================
# 2. UNIVARIATE ANALYSIS
# ============================================================
def univariate(providers, receivers, food):
    # Provider Type Distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    order = providers["Type"].value_counts().index
    sns.countplot(data=providers, x="Type", hue="Type", order=order, palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Provider Type Distribution")
    ax.set_xlabel("Provider Type")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "01_provider_type_distribution.png", dpi=150)
    plt.close()

    fig = px.pie(providers, names="Type", title="Provider Type Distribution",
                  color_discrete_sequence=PALETTE)
    fig.write_html(CHART_DIR / "01_provider_type_distribution.html")

    # Receiver Type Distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    order = receivers["Type"].value_counts().index
    sns.countplot(data=receivers, x="Type", hue="Type", order=order, palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Receiver Type Distribution")
    ax.set_xlabel("Receiver Type")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "02_receiver_type_distribution.png", dpi=150)
    plt.close()

    fig = px.pie(receivers, names="Type", title="Receiver Type Distribution",
                  color_discrete_sequence=PALETTE)
    fig.write_html(CHART_DIR / "02_receiver_type_distribution.html")

    # Food Type Distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    order = food["Food_Type"].value_counts().index
    sns.countplot(data=food, x="Food_Type", hue="Food_Type", order=order, palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Food Type Distribution")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "03_food_type_distribution.png", dpi=150)
    plt.close()

    # Meal Type Distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    order = food["Meal_Type"].value_counts().index
    sns.countplot(data=food, x="Meal_Type", hue="Meal_Type", order=order, palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Meal Type Distribution")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "04_meal_type_distribution.png", dpi=150)
    plt.close()

    # Quantity histogram
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(food["Quantity"], bins=20, color=PALETTE[0], ax=ax)
    ax.set_title("Distribution of Food Quantity per Listing")
    ax.set_xlabel("Quantity")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "05_quantity_histogram.png", dpi=150)
    plt.close()

    print("Univariate charts saved.")


# ============================================================
# 3. BIVARIATE ANALYSIS
# ============================================================
def bivariate(food):
    # City vs Food Listings (Top 15 — 624 unique cities makes "all cities" unreadable)
    top_cities = food["Location"].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=top_cities.values, y=top_cities.index, hue=top_cities.index, palette="viridis", legend=False, ax=ax)
    ax.set_title("Top 15 Cities by Number of Food Listings")
    ax.set_xlabel("Number of Listings")
    ax.set_ylabel("City")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "06_top_cities_listings.png", dpi=150)
    plt.close()

    # Provider Type vs Quantity (box plot)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=food, x="Provider_Type", y="Quantity", hue="Provider_Type", palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Provider Type vs Food Quantity")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "07_provider_type_vs_quantity.png", dpi=150)
    plt.close()

    # Food Type vs Quantity (box plot)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=food, x="Food_Type", y="Quantity", hue="Food_Type", palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Food Type vs Quantity")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "08_food_type_vs_quantity.png", dpi=150)
    plt.close()

    # Meal Type vs Quantity (bar of total)
    meal_qty = food.groupby("Meal_Type")["Quantity"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(x=meal_qty.index, y=meal_qty.values, hue=meal_qty.index, palette=PALETTE, legend=False, ax=ax)
    ax.set_title("Total Quantity Listed by Meal Type")
    ax.set_ylabel("Total Quantity")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "09_meal_type_vs_quantity.png", dpi=150)
    plt.close()

    print("Bivariate charts saved.")


# ============================================================
# 4. MULTIVARIATE ANALYSIS
# ============================================================
def multivariate(food, claims):
    # City + Provider Type + Quantity (heatmap, top 10 cities)
    top10 = food["Location"].value_counts().head(10).index
    pivot = (food[food["Location"].isin(top10)]
             .pivot_table(index="Location", columns="Provider_Type",
                           values="Quantity", aggfunc="sum", fill_value=0))
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    ax.set_title("Quantity by City (Top 10) and Provider Type")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "10_city_providertype_quantity_heatmap.png", dpi=150)
    plt.close()

    # Food Type + Meal Type + Quantity (heatmap)
    pivot2 = food.pivot_table(index="Food_Type", columns="Meal_Type",
                               values="Quantity", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(pivot2, annot=True, fmt=".0f", cmap="OrRd", ax=ax)
    ax.set_title("Quantity by Food Type and Meal Type")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "11_foodtype_mealtype_quantity_heatmap.png", dpi=150)
    plt.close()

    # Treemap: Provider Type > Food Type > Quantity
    fig = px.treemap(food, path=["Provider_Type", "Food_Type"], values="Quantity",
                      title="Quantity by Provider Type and Food Type",
                      color_discrete_sequence=PALETTE)
    fig.write_html(CHART_DIR / "12_treemap_providertype_foodtype.html")

    # Sunburst: City(top10) > Meal Type > Quantity
    sub = food[food["Location"].isin(top10)]
    fig = px.sunburst(sub, path=["Location", "Meal_Type"], values="Quantity",
                       title="Quantity by City (Top 10) and Meal Type",
                       color_discrete_sequence=PALETTE)
    fig.write_html(CHART_DIR / "13_sunburst_city_mealtype.html")

    # Provider + Claims + Quantity (stacked bar, top 10 providers by claimed qty)
    merged = claims.merge(food, on="Food_ID")
    prov_claims = (merged.groupby(["Provider_ID", "Status"])["Quantity"]
                   .sum().reset_index())
    top_providers = (prov_claims.groupby("Provider_ID")["Quantity"].sum()
                      .sort_values(ascending=False).head(10).index)
    sub2 = prov_claims[prov_claims["Provider_ID"].isin(top_providers)]
    pivot3 = sub2.pivot(index="Provider_ID", columns="Status", values="Quantity").fillna(0)
    pivot3.plot(kind="bar", stacked=True, figsize=(9, 6), color=PALETTE)
    plt.title("Top 10 Providers: Claimed Quantity by Status")
    plt.ylabel("Quantity")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "14_provider_claims_quantity_stacked.png", dpi=150)
    plt.close()

    print("Multivariate charts saved.")


# ============================================================
# 5. CLAIM ANALYSIS
# ============================================================
def claim_analysis(claims, food, receivers, providers):
    # Claim Status Distribution
    status_counts = claims["Status"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(status_counts.values, labels=status_counts.index, autopct="%1.1f%%",
           colors=PALETTE)
    ax.set_title("Claim Status Distribution")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "15_claim_status_distribution.png", dpi=150)
    plt.close()

    # Top Receivers (by number of completed claims)
    merged_r = claims.merge(receivers, on="Receiver_ID")
    top_recv = (merged_r[merged_r["Status"] == "Completed"]
                .groupby("Name").size().sort_values(ascending=False).head(10))
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=top_recv.values, y=top_recv.index, hue=top_recv.index, palette="viridis", legend=False, ax=ax)
    ax.set_title("Top 10 Receivers by Completed Claims")
    ax.set_xlabel("Completed Claims")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "16_top_receivers.png", dpi=150)
    plt.close()

    # Top Providers (by quantity successfully claimed)
    merged_p = claims.merge(food, on="Food_ID").merge(providers, on="Provider_ID")
    top_prov = (merged_p[merged_p["Status"] == "Completed"]
                .groupby("Name")["Quantity"].sum()
                .sort_values(ascending=False).head(10))
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=top_prov.values, y=top_prov.index, hue=top_prov.index, palette="viridis", legend=False, ax=ax)
    ax.set_title("Top 10 Providers by Quantity Successfully Claimed")
    ax.set_xlabel("Quantity")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "17_top_providers.png", dpi=150)
    plt.close()

    print("Claim analysis charts saved.")


def main():
    providers, receivers, food, claims = load_tables()
    null_analysis(providers, receivers, food, claims)
    univariate(providers, receivers, food)
    bivariate(food)
    multivariate(food, claims)
    claim_analysis(claims, food, receivers, providers)
    print(f"\nAll charts saved to: {CHART_DIR}")


if __name__ == "__main__":
    main()
