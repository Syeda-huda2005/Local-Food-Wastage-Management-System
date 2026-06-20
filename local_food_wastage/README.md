# Local Food Wastage Management System

A data analytics platform that connects food providers (restaurants, grocery
stores, supermarkets, catering services) with food receivers (NGOs, charities,
shelters, individuals) to reduce food wastage — built on a SQL database,
analyzed with Python EDA, and deployed as an interactive Streamlit dashboard.

## Project Structure

```
local_food_wastage/
├── database/                    # Source CSV datasets
│   ├── providers_data.csv
│   ├── receivers_data.csv
│   ├── food_listings_data.csv
│   └── claims_data.csv
├── sql/
│   ├── schema.sql                # CREATE TABLE statements, keys, indexes
│   ├── build_database.py         # Builds food_wastage.db from the CSVs
│   └── business_queries.sql      # 20 validated business SQL queries
├── eda/
│   └── eda_report.py             # Null analysis + univariate/bivariate/
│                                  # multivariate/claim analysis charts
├── outputs/
│   ├── charts/                   # 17 generated PNG/HTML charts
│   └── null_analysis_summary.csv
├── streamlit_app/
│   ├── app.py                    # Page 1: Overview
│   ├── utils.py                  # Shared DB connection, styling, KPI cards
│   ├── .streamlit/config.toml    # Custom theme
│   └── pages/
│       ├── 2_Data_Analysis.py    # Filters + live EDA charts
│       ├── 3_SQL_Insights.py     # All 20 SQL queries, live + downloadable
│       ├── 4_Claim_Analysis.py   # Claim status, top providers/receivers
│       ├── 5_Browse_and_Claim.py # Searchable listings + provider contacts
│       └── 6_Recommendations.py  # Data-grounded recommendations
├── docs/
│   ├── project_documentation.md  # Full write-up: problem, methodology,
│   │                              # architecture, EDA report, SQL report,
│   │                              # insights, recommendations, conclusion
│   ├── null_value_analysis.md    # Detailed null analysis with business impact
│   └── viva_questions.md         # 80 Q&A for project defense
├── food_wastage.db               # Built SQLite database (generated)
├── requirements.txt
└── README.md
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Build the database
```bash
cd sql
python build_database.py
```
This reads the four CSVs from `database/`, creates `food_wastage.db` in the
project root, and prints row counts plus a referential-integrity check.

### 3. Run the EDA script (optional — regenerates charts)
```bash
cd eda
python eda_report.py
```
Charts are saved to `outputs/charts/` as PNG (static) and HTML (interactive
Plotly) files.

### 4. Launch the Streamlit app
```bash
cd streamlit_app
streamlit run app.py
```
Open the local URL Streamlit prints (typically `http://localhost:8501`).
The app connects directly to `food_wastage.db` — make sure step 2 has been
run first so the database file exists in the project root.

## Tech Stack

- **Database:** SQLite (portable; schema also documented for MySQL/Postgres
  with minor type adjustments)
- **EDA:** pandas, numpy, matplotlib, seaborn, plotly
- **App:** Streamlit, with all dashboard data sourced from live SQL queries
  (no data merging in Python — joins are done in SQL per project rules)

## A Note on the Data

The brief anticipated missing values (null contacts, addresses, expiry
dates, etc.). The actual CSVs provided contain **zero nulls** across every
audited column — see `docs/null_value_analysis.md` for the full, honest
write-up of this finding plus the handling methodology that would apply if
nulls appeared in a future data load. Likewise, all claim timestamps fall
within a 21-day window (Mar 1–21, 2025), so the "monthly trend" query was
implemented as a **daily** trend instead — a monthly grouping would
collapse to a single bar and add no insight. This is documented inline in
`sql/business_queries.sql`.

## Key Findings (see docs/project_documentation.md for full detail)

- 1,000 providers, 1,000 receivers, 1,000 food listings, 1,000 claims
- Claim completion rate: **33.9%** (339 completed / 1,000 total)
- **749 of 1,000 providers** have never had a completed claim
- **353 listings** have never received any claim at all
- Top food item by claims: **Rice** (122 claims)
- Restaurants contribute the most total quantity (6,923 units)
