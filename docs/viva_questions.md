# Viva Preparation — Local Food Wastage Management System

Answers reference this project's actual implementation, not generic
textbook answers, so they hold up under follow-up questions.

---

## Section A: Project Viva Questions (30)

**1. What problem does this project solve?**
It connects food providers with surplus food to receivers who need it,
replacing an ad hoc, disconnected process with a tracked, queryable
platform — reducing both food waste and food insecurity.

**2. Who are the two user groups in this system?**
Providers (Restaurants, Grocery Stores, Supermarkets, Catering
Services) and Receivers (NGOs, Charities, Shelters, Individuals).

**3. What are the four core entities in your data model?**
Providers, Receivers, Food_Listings, and Claims.

**4. How are these four entities related?**
Providers (1) → Food_Listings (M) via Provider_ID; Food_Listings (1) →
Claims (M) via Food_ID; Receivers (1) → Claims (M) via Receiver_ID.

**5. Why did you choose SQLite over MySQL/Postgres?**
SQLite is file-based and zero-config, which makes the project fully
portable and reproducible for grading/demo without a separate database
server. The schema is documented to translate to MySQL/Postgres with
minor type adjustments (e.g., AUTOINCREMENT syntax).

**6. Did your dataset have missing values?**
No — all eight audited columns (Providers.Contact, Providers.Address,
Receivers.Contact, Food_Listings.Expiry_Date, Food_Listings.Quantity,
Claims.Status, Claims.Timestamp) came back with 0 nulls when checked
programmatically. This is documented honestly in
`docs/null_value_analysis.md`, along with the handling plan that would
apply if nulls appeared in a future data load.

**7. How did you validate referential integrity?**
By running LEFT JOIN checks for orphaned foreign keys after database
build — confirmed 0 Food_Listings rows with a non-existent Provider_ID,
and 0 Claims rows with a non-existent Food_ID or Receiver_ID.

**8. What is the claim completion rate in your data, and why does it
matter?**
33.9% (339 of 1,000 claims). It's the platform's core efficiency
metric — it tells you what share of claimed food is actually
delivered versus lost to cancellation or left pending.

**9. What's the difference between a Pending, Completed, and
Cancelled claim?**
Pending = claim made, outcome not yet resolved. Completed = food
successfully transferred to the receiver. Cancelled = the claim did
not result in a transfer (receiver or provider backed out, food no
longer available, etc.).

**10. Why is the cancellation rate (33.6%) treated as a priority
metric in your recommendations, not just completion rate?**
Because a cancelled claim still consumed the pickup window — it
blocked other receivers from claiming that food during that time,
making it a more costly failure mode than a listing that simply went
unclaimed.

**11. What did your univariate analysis reveal about food type
distribution?**
A near-even three-way split: Vegetarian 336, Vegan 334,
Non-Vegetarian 330 — no dominant category.

**12. Why did you cap the "City vs Listings" chart at the top 15
cities instead of showing all of them?**
Because the data spans 624 unique cities with thin counts per city
(top city has only 6 listings); showing all 624 would be unreadable
and add no analytical value. This is a deliberate scope decision, not
an oversight.

**13. What does the Provider Type × Food Type treemap tell you that a
bar chart wouldn't?**
It shows the hierarchical breakdown of quantity within each provider
type by food type simultaneously, letting you see, e.g., whether
Restaurants skew toward Non-Vegetarian listings, in one view.

**14. Which provider contributes the most food, and by which
metric?**
Barry Group (Restaurant), by both total quantity listed (179 units)
and by quantity in completed claims (140 units) — making it both the
biggest and most reliably converting donor.

**15. Which meal type shows the most cancellations, and what's your
hypothesis for why?**
Breakfast (99 cancellations) — the hypothesis is a timing/shelf-life
mismatch, since breakfast items may be listed too close to spoilage
for receivers to act on in time. This is flagged as worth testing, not
asserted as proven.

**16. What's the business risk of the 749 providers with zero
completed claims?**
It suggests either a discoverability problem (receivers aren't seeing
these listings), a logistics problem (pickup is too hard), or a
listing-quality problem — and without that data point, the platform
might mistakenly assume supply is fine when the real issue is
conversion.

**17. How does your Streamlit app avoid hardcoded numbers going stale?**
Every page queries `food_wastage.db` directly at render time
(`run_query()` in `utils.py`) instead of using precomputed,
hand-typed values — so the dashboard updates automatically if the
underlying data changes.

**18. Why does the project rule say "don't merge datasets in
Python — use SQL joins"?**
To keep the database as the single source of truth and to demonstrate
SQL proficiency directly, rather than offloading relational logic into
pandas merges that bypass the database layer entirely.

**19. What was your approach to choosing a color palette for the
dashboard?**
A warm, food/harvest-grounded palette (terracotta, gold, deep
charcoal-green, cream) rather than a generic SaaS dashboard look —
chosen to feel specific to the subject rather than templated.

**20. What does the "Browse & Claim" page add beyond the analytics
pages?**
Operational utility — a searchable, filterable listing directory with
live provider contact info, addressing the original brief's
requirement that receivers be able to locate available food and reach
the provider.

**21. Why didn't you implement an actual "claim" button that writes
to the database?**
To keep the deliverable scoped to the analytics layer the project flow
requires; the page documents this explicitly as a noted simplification
rather than silently omitting it.

**22. What would you add if this became a production system?**
Real authentication for providers/receivers, an actual claim-writing
endpoint with concurrency handling (so two receivers can't claim the
same listing simultaneously), automated expiry alerts, and a feedback
loop capturing cancellation reasons.

**23. How did you decide the claim trend should be daily rather than
monthly?**
The data's claim timestamps span only March 1–21, 2025 (21 days). A
monthly grouping would collapse to one bar with zero analytical value,
so daily granularity was used instead — documented inline in the SQL
file so the reasoning isn't hidden.

**24. What indexes did you add to the database, and why?**
Indexes on `Food_Listings.Provider_ID`, `Claims.Food_ID`,
`Claims.Receiver_ID`, `Food_Listings.Location`, `Providers.City`, and
`Receivers.City` — these are exactly the columns the business queries
JOIN and GROUP BY on most heavily.

**25. What's the single most important recommendation from this
analysis, and why?**
Investigating the 749 zero-completed-claim providers, because it's
the largest structural inefficiency in the dataset (nearly 75% of
supply-side relationships aren't converting) and is directly
actionable via the existing SQL query.

**26. How would you extend this project to detect food safety risk?**
Cross-reference `Expiry_Date` against `Claims.Timestamp` to flag any
claim completed after the listed expiry date — not currently in the
query bank, but a natural extension using the same schema.

**27. What was the biggest data-quality surprise during this
project?**
That the dataset contained zero nulls despite the brief's detailed
null-analysis requirements — handled by documenting the actual
finding rather than fabricating nulls to match the brief.

**28. How do Provider_Type in Providers and Provider_Type in
Food_Listings relate?**
They're a denormalized duplicate — Food_Listings carries its own copy
of Provider_Type rather than requiring a join back to Providers for
every type-based query, which is how the source data was supplied and
was preserved as-is per the "don't merge in Python" rule.

**29. What's the purpose of the KPI cards on the Overview page?**
To give an at-a-glance health check (total providers, receivers,
listings, claims, total quantity, completion rate) before a viewer
drills into any specific analysis page.

**30. If you had more time, what's the next analysis you'd run?**
A receiver-side cancellation-reason analysis (would require adding a
reason field to Claims) to distinguish provider-side failures from
receiver-side failures in the 33.6% cancellation rate.

---

## Section B: SQL Viva Questions (30)

**1. What's the difference between INNER JOIN and LEFT JOIN, and
where did you use each?**
INNER JOIN returns only matching rows from both tables; LEFT JOIN
returns all rows from the left table plus matches from the right
(NULL where no match). Query #8 (Claims per Food Item) uses LEFT JOIN
specifically so food items with zero claims still appear in the
result.

**2. Why doesn't SQLite support FULL JOIN, and how did you work
around it?**
SQLite has no native FULL OUTER JOIN. Query #20 emulates it with two
LEFT JOINs (Providers→Receivers and Receivers→Providers) combined via
UNION, which produces the same result: every city that has a provider,
a receiver, or both.

**3. What is a CTE, and why use one instead of a subquery?**
A Common Table Expression (`WITH ... AS (...)`) names an intermediate
result so it can be referenced cleanly in the main query — improves
readability over deeply nested subqueries. Used in queries #14, #18,
#19.

**4. Explain the difference between RANK(), DENSE_RANK(), and
ROW_NUMBER().**
ROW_NUMBER() assigns a unique sequential number with no ties.
RANK() assigns the same rank to ties but skips the next rank number
(1,1,3). DENSE_RANK() assigns the same rank to ties without skipping
(1,1,2). Query #14 uses RANK(), #18 uses DENSE_RANK(), #19 uses
ROW_NUMBER() with PARTITION BY.

**5. What does PARTITION BY do in query #19?**
It resets the ROW_NUMBER() count for each City group separately, so
"rank 1" means the top provider within that specific city, not
globally across all cities.

**6. Why use HAVING instead of WHERE in query #13?**
HAVING filters on an aggregated value (`SUM(Quantity) > 0`), which
WHERE cannot do since WHERE filters rows before aggregation happens.

**7. Walk through query #10 (Claim Status Percentage).**
It groups Claims by Status, counts each group, then divides by a
scalar subquery `(SELECT COUNT(*) FROM Claims)` to compute each
status's share of the total, multiplied by 100 and rounded to 2
decimals.

**8. Why is the subquery in query #10 not correlated to the outer
query?**
It always counts the same denominator (total claims) regardless of
which Status row is being processed, so it doesn't need a correlation
condition back to the outer query.

**9. What is a correlated subquery, and does this project use one?**
A correlated subquery references a column from the outer query inside
its WHERE clause, re-evaluating per outer row. This project's
subqueries (in #10, #16, #17) are not correlated — they're scalar or
independent set-membership checks (`NOT IN`).

**10. Explain query #16's logic in plain English.**
It selects every provider whose Provider_ID does NOT appear in the
set of Provider_IDs that have at least one completed claim — i.e.,
providers with zero successful claims.

**11. Why use NOT IN instead of NOT EXISTS in query #16/#17?**
NOT IN is simpler to read for this case and performs comparably at
this data scale (1,000 rows); NOT EXISTS would be preferred at much
larger scale or if NULLs were possible in the subquery's column, since
NOT IN can behave unexpectedly with NULLs.

**12. What datatype is Expiry_Date stored as, and why does that
matter for query #17?**
It's stored as TEXT in ISO 8601 format (`YYYY-MM-DD`), normalized
during the build step specifically so that `ORDER BY Expiry_Date ASC`
sorts correctly as a date rather than as an arbitrary string.

**13. Why did build_database.py normalize dates before loading?**
The source CSVs had dates like `3/17/2025`, which sort incorrectly as
strings (e.g., "3/17/2025" < "3/2/2025" lexically). Converting to
ISO format makes both sorting and SQLite's `strftime()` functions
behave correctly.

**14. What does strftime('%Y-%m-%d', Timestamp) do in query #15?**
It extracts just the date portion (dropping the time-of-day) from each
Claims.Timestamp value so claims can be grouped by calendar day.

**15. Why did you choose daily grouping over monthly for the claim
trend?**
Because all timestamps fall within a single 21-day window
(2025-03-01 to 2025-03-21); a monthly GROUP BY would produce one row,
which carries no trend information.

**16. What's the primary key of each table, and is it auto-assigned
or supplied?**
Provider_ID, Receiver_ID, Food_ID, and Claim_ID are all supplied
directly from the source CSVs and declared as INTEGER PRIMARY KEY in
the schema — not auto-incremented, since the data already has unique
IDs.

**17. What foreign key constraints exist in this schema?**
Food_Listings.Provider_ID → Providers.Provider_ID;
Claims.Food_ID → Food_Listings.Food_ID;
Claims.Receiver_ID → Receivers.Receiver_ID.

**18. Did you verify the foreign keys actually hold in the real
data?**
Yes — `build_database.py` runs a post-load LEFT JOIN check for
orphaned rows on both relationships and prints the count (confirmed
0 in both cases).

**19. What indexes exist, and what's the tradeoff of adding them?**
Six indexes on the foreign-key and city/location columns. Tradeoff:
faster SELECT/JOIN/GROUP BY performance at the cost of slightly slower
INSERTs and additional storage — an easy tradeoff here since this is a
read-heavy analytics workload.

**20. Explain the CASE WHEN logic anywhere it's used in this
project.**
In the Streamlit app's KPI calculation:
`ROUND(100.0*SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END)/COUNT(*),1)`
— this converts each row into a 1 or 0 depending on whether its status
is "Completed," sums those, and divides by the total row count to get
a percentage.

**21. Why multiply by 100.0 and not 100 in percentage calculations?**
To force floating-point division instead of integer division — SQLite
(like many SQL engines) would otherwise truncate the result if both
operands were integers.

**22. What does GROUP BY p.Provider_ID, p.Name, p.Type accomplish in
query #3, and why include Name and Type if you're grouping by ID?**
SQLite allows including non-aggregated columns that are functionally
dependent on the GROUP BY key; including Name and Type explicitly
makes the query's intent clear and keeps it portable to stricter SQL
engines (like Postgres) that require every selected non-aggregate
column to appear in GROUP BY.

**23. What would happen if you ran query #14 without the WHERE
Status = 'Completed' filter?**
It would rank receivers by total quantity across all claims regardless
of outcome, inflating totals with Pending and Cancelled claims that
never actually delivered food — misrepresenting "impact."

**24. How is the database connection managed in the Streamlit app?**
Via a single cached connection (`st.cache_resource`) in `utils.py`,
shared across all pages in a session, with query results separately
cached for 5 minutes via `st.cache_data(ttl=300)`.

**25. Why cache query results for only 5 minutes instead of
indefinitely?**
To balance performance (avoid re-querying SQLite on every widget
interaction) against freshness (the underlying database file could be
rebuilt during a session).

**26. What SQL injection risk exists in the filter-driven queries on
the Data Analysis page, and how is it mitigated?**
The filter values come from a `SELECT DISTINCT` query against the
database itself (not free-text user input), and are passed as
parameterized placeholders (`?`) rather than string-concatenated into
the SQL — both reduce injection risk substantially.

**27. Why use parameterized queries (?) instead of f-string
interpolation for the actual filter values?**
Parameterized queries let SQLite's driver handle escaping safely,
preventing both injection and subtle bugs with special characters
(e.g., a city name containing an apostrophe).

**28. What's the difference between WHERE and ON in a JOIN?**
ON specifies the join condition (how rows from two tables are
matched); WHERE filters the resulting joined rows afterward. Using a
filter in ON vs WHERE produces different results specifically with
LEFT JOINs, since a WHERE filter on the right table can silently turn
a LEFT JOIN back into an INNER JOIN.

**29. How would you adapt schema.sql for MySQL instead of SQLite?**
Change `INTEGER PRIMARY KEY` to `INT PRIMARY KEY AUTO_INCREMENT` (if
auto-numbering were needed), `TEXT` to `VARCHAR(n)`, and
`DATETIME`/`DATE` types map over directly; foreign key syntax is
identical.

**30. What's one query you'd add if given more time, and why?**
A query joining Claims to Food_Listings with a date comparison
(`Claims.Timestamp > Food_Listings.Expiry_Date`) to detect any claim
that was completed after the food's listed expiry — a food-safety
flag not currently in the query bank.

---

## Section C: Streamlit Viva Questions (20)

**1. Why is this a multi-page Streamlit app instead of one long
script?**
Streamlit's `pages/` directory convention auto-generates sidebar
navigation and keeps each concern (Overview, Data Analysis, SQL
Insights, Claim Analysis, Browse & Claim, Recommendations) in its own
file for maintainability.

**2. How does the app connect to the database?**
`utils.py` defines `get_connection()`, a `@st.cache_resource`-decorated
function returning a single shared `sqlite3.connect()` to
`food_wastage.db`, reused across pages in a session.

**3. Why is `check_same_thread=False` passed to sqlite3.connect()?**
Streamlit can invoke callbacks from a different thread than the one
that created the connection; without this flag, SQLite raises a
thread-safety error.

**4. What does `@st.cache_data(ttl=300)` do on `run_query()`?**
Caches the DataFrame result of a given SQL query + params combination
for 5 minutes, so repeated calls with the same query don't re-hit
SQLite unnecessarily during a session.

**5. How do the sidebar filters on the Data Analysis page work
end-to-end?**
Filter options are populated from live `SELECT DISTINCT` queries
against the database; selections build a parameterized SQL WHERE
clause; the resulting filtered DataFrame drives every chart in that
page's tabs.

**6. Why use Plotly instead of matplotlib inside the Streamlit
pages?**
Plotly charts stay interactive (hover, zoom, pan) inside the
Streamlit UI via `st.plotly_chart()`; matplotlib figures are static
images once rendered, which is fine for the standalone EDA script but
less suited to an interactive dashboard.

**7. Where are the static matplotlib charts used in this project, if
not in the live app?**
They're generated by `eda/eda_report.py` and saved to
`outputs/charts/` as a standalone deliverable satisfying the "Python +
matplotlib/seaborn" EDA requirement, separate from the live Plotly
charts inside the Streamlit app itself.

**8. How does the custom color theme get applied?**
Two layers: `.streamlit/config.toml` sets Streamlit's native theme
variables (background, primary color, font), and `inject_css()` in
`utils.py` injects additional custom CSS for KPI cards, the sidebar,
and the insight callout boxes.

**9. What is `st.cache_resource` for, and how is it different from
`st.cache_data`?**
`st.cache_resource` is for objects that shouldn't be copied/serialized
between reruns (like a database connection); `st.cache_data` is for
data (like DataFrames) where Streamlit can safely hash inputs and
cache/copy the output.

**10. How does the KPI card component work?**
`kpi_card()` in `utils.py` takes a label and value, then renders a
small HTML/CSS block via `st.markdown(..., unsafe_allow_html=True)` —
reused identically across the Overview, Claim Analysis, and
Recommendations pages for visual consistency.

**11. How would a user download query results from the SQL Insights
page?**
Each expanded query block has a `st.download_button()` that serializes
the current result DataFrame to CSV bytes on click — no server-side
file write required.

**12. What happens if a filter combination on the Data Analysis page
returns zero rows?**
The page checks `if food_df.empty` and shows `st.warning()` with
`st.stop()`, halting further rendering cleanly instead of throwing
exceptions on empty-DataFrame chart calls.

**13. How is the SQL Insights page's query list structured in code?**
As a Python list of dictionaries, each with `title`, `objective`,
`sql`, and an optional `chart` lambda — looped over to render an
`st.expander()` per query, rather than 20 near-duplicate blocks of
manually repeated code.

**14. Why use `st.expander()` for the SQL Insights page instead of
showing all 20 queries at once?**
To keep the page scannable — a viewer can search/scroll the titles
and only expand the queries relevant to their question, rather than
loading 20 full result tables and charts simultaneously.

**15. What does the search box on the SQL Insights page filter on?**
It does a case-insensitive substring match against each query's
combined title + objective text, hiding non-matching expanders.

**16. How does the Browse & Claim page protect against SQL
injection in its filters?**
City/Food Type/Meal Type values come from dropdown `st.selectbox()`
options populated by `SELECT DISTINCT` against the database (not
free-text), and are passed into the query as parameterized `?`
placeholders.

**17. Why does the Recommendations page recompute its supporting
numbers from the database instead of hardcoding them in the text?**
So the recommendations can't silently drift out of sync if the
database is rebuilt with updated data — every number on that page is
a live query result formatted into the recommendation text at render
time.

**18. How would you deploy this app for others to access (not just
locally)?**
Push the repo to GitHub and deploy via Streamlit Community Cloud
pointing at `streamlit_app/app.py`, ensuring `food_wastage.db` is
either committed to the repo or rebuilt via a startup script that runs
`build_database.py` first.

**19. What's a limitation of using SQLite in a deployed (not local)
Streamlit app?**
SQLite is a single file with limited concurrent-write support; fine
for this read-heavy analytics use case, but would need to move to a
hosted database (Postgres/MySQL) if the app added real write
operations like an actual "Claim" button.

**20. How did you verify all six pages run without runtime errors
before calling the project done?**
Using Streamlit's official `AppTest` framework
(`streamlit.testing.v1.AppTest`) to execute each page's script
headlessly and assert `at.exception` is empty — confirmed clean for
all six pages, not just checked for Python syntax errors.
