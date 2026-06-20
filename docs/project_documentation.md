# Project Documentation
## Local Food Wastage Management System

---

## 1. Problem Statement

Restaurants, grocery stores, supermarkets, and catering services
regularly discard surplus food that is still safe to consume, while
NGOs, charities, shelters, and individuals in the same cities lack
reliable access to food. The core failure is not a shortage of food —
it's the absence of a system connecting the two sides:

1. Excess food is wasted daily.
2. Receivers don't know where or when food becomes available.
3. No centralized platform exists to list, discover, or track food.
4. Distribution is inefficient and ad hoc.
5. Providers and receivers have no structured way to connect.
6. No analytical layer exists to understand donation patterns, identify
   gaps, or measure what's working.

## 2. Objectives

- Provide a relational data model that cleanly separates Providers,
  Receivers, Food Listings, and Claims while preserving referential
  integrity.
- Perform a complete null-value audit before any other analysis.
- Run univariate, bivariate, and multivariate exploratory analysis to
  characterize the supply side (listings) and demand side (claims).
- Answer 15+ specific business questions in SQL using a full range of
  techniques (joins, subqueries, CTEs, window functions, aggregation).
- Deliver an interactive Streamlit application where every figure is
  sourced from a live SQL query against the database — not a
  pre-computed Python merge — so the dashboard stays consistent with
  the database as the source of truth.
- Translate findings into specific, data-grounded recommendations
  rather than generic advice.

## 3. Methodology

1. **Data ingestion & validation** — load the four CSVs, check dtypes,
   nulls, duplicate primary keys, and referential integrity (every
   `Food_Listings.Provider_ID` exists in `Providers`; every
   `Claims.Food_ID`/`Receiver_ID` exists in `Food_Listings`/`Receivers`).
   Result: 1,000 rows in each table, 0 orphaned foreign keys.
2. **Schema design** — four normalized tables with explicit primary and
   foreign keys (see Section 4), built via `sql/schema.sql`.
3. **Database build** — `sql/build_database.py` loads the CSVs into
   SQLite, normalizes date formats to ISO 8601 for reliable SQL date
   functions, and re-validates row counts and integrity post-load.
4. **EDA** — `eda/eda_report.py` performs the null audit, then 17
   visualizations spanning univariate, bivariate, multivariate, and
   claim-specific analysis, each saved to `outputs/charts/`.
5. **SQL business analysis** — 20 queries (15 required + 5 additional)
   in `sql/business_queries.sql`, each tested for execution correctness
   against the live database before being included in this submission.
6. **Application layer** — a 6-page Streamlit app where every page
   queries `food_wastage.db` directly at render time.

## 4. Database Design

### Schema (see `sql/schema.sql` for full DDL)

```
Providers
├── Provider_ID  (PK)
├── Name
├── Type           -- Supermarket / Grocery Store / Restaurant / Catering Service
├── Address
├── City
└── Contact

Receivers
├── Receiver_ID  (PK)
├── Name
├── Type           -- NGO / Charity / Shelter / Individual
├── City
└── Contact

Food_Listings
├── Food_ID  (PK)
├── Food_Name
├── Quantity
├── Expiry_Date
├── Provider_ID    (FK → Providers.Provider_ID)
├── Provider_Type
├── Location
├── Food_Type      -- Vegetarian / Non-Vegetarian / Vegan
└── Meal_Type       -- Breakfast / Lunch / Dinner / Snacks

Claims
├── Claim_ID  (PK)
├── Food_ID      (FK → Food_Listings.Food_ID)
├── Receiver_ID  (FK → Receivers.Receiver_ID)
├── Status         -- Pending / Completed / Cancelled
└── Timestamp
```

### ER Relationships

- **Providers (1) → Food_Listings (M)** via `Provider_ID` — one provider
  can list many food items.
- **Food_Listings (1) → Claims (M)** via `Food_ID` — a food item can be
  claimed (and re-claimed after a cancellation).
- **Receivers (1) → Claims (M)** via `Receiver_ID` — one receiver can
  make many claims.

Indexes were added on all foreign-key and city/location columns
(`idx_food_provider`, `idx_claims_food`, `idx_claims_receiver`,
`idx_food_city`, `idx_provider_city`, `idx_receiver_city`) since the
business queries are JOIN- and GROUP BY-heavy.

## 5. EDA Report Summary

Full charts are in `outputs/charts/`; this section summarizes what each
analysis tier found.

### Null Value Analysis
Zero nulls found across all eight audited columns. Full write-up,
including the handling methodology that would apply to future data with
real nulls, is in `docs/null_value_analysis.md`.

### Univariate Analysis
- **Provider Type:** fairly even split — Supermarket (262), Grocery
  Store (256), Restaurant (246), Catering Service (236).
- **Receiver Type:** NGO (274) leads, followed by Charity (263),
  Shelter (246), Individual (217).
- **Food Type:** near-even three-way split — Vegetarian (336), Vegan
  (334), Non-Vegetarian (330).
- **Meal Type:** Breakfast (254) and Snacks (253) slightly ahead of
  Lunch (248) and Dinner (245).
- **Quantity:** ranges 1–50 units per listing, mean ≈25.8, no extreme
  outliers — a healthy, well-bounded distribution.

### Bivariate Analysis
- **City vs Listings:** 624 unique cities in the data; listing counts
  are thin per city (top city has only 6 listings), meaning supply is
  geographically dispersed rather than concentrated — a logistics
  challenge for centralized pickup routes.
- **Provider Type vs Quantity:** box plots show broadly similar
  quantity ranges across provider types, with no single type
  dominating per-listing size.
- **Meal Type vs Total Quantity:** Breakfast listings carry the
  largest cumulative quantity, consistent with it also being the most
  common meal type by count.

### Multivariate Analysis
- The City × Provider Type heatmap (top 10 cities) shows that most
  cities are served by only one or two provider types, not a full mix
  — a sign that provider diversity within a city is still shallow at
  this stage of the platform.
- The Provider Type × Food Type treemap and City × Meal Type sunburst
  give a navigable view of where volume concentrates, used directly in
  the Streamlit Data Analysis page for interactive drill-down.

### Claim Analysis
- **Status split:** Completed 339 (33.9%), Cancelled 336 (33.6%),
  Pending 325 (32.5%) — nearly an even three-way split, meaning exactly
  as many claims fail (cancelled) as succeed.
- **Most claimed food item:** Rice (122 claims), followed by Soup
  (114) and Dairy (110).
- **Top receiver by completed quantity:** Derek Potter (Charity), 99
  units.
- **Top provider by completed quantity:** Barry Group (Restaurant),
  140 units claimed successfully.

## 6. SQL Analysis Report

All 20 queries live in `sql/business_queries.sql` and are re-runnable
live in the Streamlit app's **SQL Insights** page. Each was executed
against `food_wastage.db` and verified to return correct, non-empty
results before inclusion (see the verification log retained in this
project's build history). Technique coverage:

| Technique | Queries using it |
|---|---|
| WHERE / ORDER BY | 1, 2, 6, 8, 17 |
| GROUP BY / HAVING | 1–7, 12, 13, 18 |
| INNER JOIN | 3, 4, 9, 11, 12, 14, 18, 19 |
| LEFT JOIN | 8, 16, 17, 20 |
| CASE WHEN | 10 |
| Subquery | 10, 16, 17 |
| CTE (WITH) | 14, 18, 19 |
| Window functions (RANK / DENSE_RANK / ROW_NUMBER) | 14, 18, 19 |
| UNION (FULL JOIN equivalent) | 20 |

## 7. Business Insights

**Food Availability — which city has the highest food availability?**
South Kathryn leads by total quantity listed (179 units across 6
listings), narrowly ahead of New Carol (167 units). However, with 624
distinct cities in the dataset, supply is highly dispersed rather than
concentrated in a few hubs.

**Food Waste — which meal type gets wasted the most?**
Using claims data as a proxy (a listing that is never completed-claimed
represents food at high risk of waste), Breakfast listings have the
highest cancellation count (99) among meal types, suggesting timing or
shelf-life mismatch is most acute for breakfast items.

**Provider Analysis — which provider contributes the most food?**
Barry Group (Restaurant) tops total quantity listed (179 units) and
also leads in successfully completed claims (140 units claimed),
making it the platform's most reliable high-volume donor in this
dataset.

**Receiver Analysis — which receiver claims the most food?**
Derek Potter (Charity) leads completed claims by quantity (99 units),
followed by Steven Griffin (NGO, 89 units) and Peter Gonzalez (Shelter,
83 units).

**Claims Analysis — what percentage of claims are completed?**
33.9% (339 of 1,000). Cancelled claims are nearly as common (33.6%),
meaning the platform currently loses about as much claimed food to
cancellation as it successfully delivers.

**Demand Analysis — which city has the highest food demand?**
By receiver count, New Christopher leads with 3 registered receivers,
though — as with supply — receiver presence is thinly spread across
966 distinct cities rather than concentrated.

## 8. Business Recommendations

See the live, data-grounded version of these in the Streamlit app's
**Recommendations** page (numbers recalculate from the database each
run). Summary:

1. Investigate and re-engage the 749 of 1,000 providers with zero
   completed claims — diagnose discoverability, logistics, or listing
   quality before assuming the food itself is unwanted.
2. Proactively target the 353 listings that have never received any
   claim, especially as they approach expiry.
3. Treat the 33.6% cancellation rate as a first-class metric, not an
   afterthought next to completion rate — cancelled claims waste a
   pickup window other receivers could have used.
4. Investigate Breakfast's elevated cancellation count specifically —
   likely a timing/shelf-life issue worth testing.
5. Formalize recurring pickup agreements with top-contributing
   Restaurant-type providers, the platform's largest supply category
   by total quantity (6,923 units).
6. Use the Supply vs Demand by City query to target NGO outreach or
   provider recruitment city-by-city, rather than a blanket expansion
   strategy.
7. Build automated expiry-proximity alerts using the existing
   "nearest-expiry, unclaimed" query as the alert trigger.
8. Run a recurring public recognition program for top donors, sourced
   directly from the Most Contributing Provider query.
9. Track receiver-side reliability (claim-to-completion ratio) the
   same way provider reliability is tracked.
10. Extend future data collection to 6–12 months of claim history; the
    current 21-day window is too narrow to detect genuine seasonal
    demand patterns.

## 9. Architecture Diagram (description)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ providers   │     │ receivers   │     │food_listings│     │   claims    │
│   .csv      │     │   .csv      │     │   .csv      │     │   .csv      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       └───────────────────┴─────────┬─────────┴───────────────────┘
                                      │
                          sql/build_database.py
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │  food_wastage.db      │
                          │  (SQLite, 4 tables,   │
                          │   FK constraints,     │
                          │   indexes)            │
                          └──────────┬────────────┘
                                     │
                  ┌──────────────────┼──────────────────┐
                  ▼                  ▼                   ▼
        eda/eda_report.py   sql/business_queries.sql  streamlit_app/
        (charts → outputs/) (validated query bank)    (6-page live app,
                                                         queries DB directly)
```

## 10. Data Flow Diagram (description)

```
Provider lists food  →  Food_Listings row created
                              │
                              ▼
Receiver searches/browses (Streamlit "Browse & Claim" page,
queries Food_Listings JOIN Providers live)
                              │
                              ▼
Receiver claims food  →  Claims row created (Status = Pending)
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
           Completed     Cancelled       (stays Pending)
                │             │
                ▼             ▼
     Counted in claim-success   Counted in cancellation-rate
     KPIs and top-receiver/        analysis (Recommendation #3)
     top-provider rankings
```

## 11. Conclusion

The dataset supports a fully functional, end-to-end food-rescue
analytics platform: a normalized SQL schema with verified referential
integrity, a complete EDA covering null analysis through multivariate
claim analysis, 20 validated business SQL queries spanning the full
range of required SQL techniques, and a 6-page Streamlit application
where every number is computed live from the database rather than
hardcoded. The most actionable finding is structural rather than
cosmetic: nearly three-quarters of providers (74.9%) have never had a
successful claim, and over a third of claims that do get made end in
cancellation. The recommendations in Section 8 are written to address
that gap directly rather than offer generic "increase awareness"
advice.
