# Null Value Analysis

## Method

Each of the four tables was audited for the columns the project brief
flagged as missing-value risks. For every column we report the null count,
null percentage, the most likely real-world reason a null would occur, how
it should be handled if found, and the business impact of leaving it
unhandled.

## Finding

**Across all eight audited columns, in this dataset, the null count is 0.**
This was verified programmatically (`df[col].isnull().sum()` for every
column in every table) rather than assumed — see `eda/eda_report.py`,
function `null_analysis()`, and the generated
`outputs/null_analysis_summary.csv`.

| Table | Column | Null Count | Null % | Total Rows |
|---|---|---|---|---|
| Providers | Contact | 0 | 0.0% | 1,000 |
| Providers | Address | 0 | 0.0% | 1,000 |
| Receivers | Contact | 0 | 0.0% | 1,000 |
| Food_Listings | Expiry_Date | 0 | 0.0% | 1,000 |
| Food_Listings | Quantity | 0 | 0.0% | 1,000 |
| Claims | Status | 0 | 0.0% | 1,000 |
| Claims | Timestamp | 0 | 0.0% | 1,000 |

This is reported honestly rather than fabricated, since inventing missing
data to match the brief's assumption would misrepresent the actual
dataset. That said, the brief's concern is still a real production risk —
below is the handling methodology that would apply the moment nulls do
appear in a future data load (e.g., as the platform scales and onboards
real providers who skip optional fields).

## Column-by-Column Handling Plan (for future data loads)

### Providers.Contact
- **Possible reason:** Provider declined to share a phone number, or the
  field was left blank during registration.
- **Handling method:** Do not drop the row — a provider with no contact
  can still have valid food listings. Impute with `"Not Provided"` and
  flag the provider for a follow-up data-completion request.
- **Business impact if unhandled:** Receivers cannot coordinate pickup
  directly with the provider, which can stall or cancel an otherwise
  valid claim.

### Providers.Address
- **Possible reason:** Same as above — optional field skipped at
  registration, or a provider operating from a non-fixed location
  (e.g., a mobile catering service).
- **Handling method:** Impute with `"Not Provided"` and fall back to the
  `City` field for routing; do not block the provider's listings from
  appearing.
- **Business impact if unhandled:** Pickup logistics for receivers
  becomes guesswork, increasing the chance of a cancelled claim.

### Receivers.Contact
- **Possible reason:** Privacy concern from an individual receiver, or
  an NGO submitting through a shared intake form that doesn't enforce
  the field.
- **Handling method:** Impute with `"Not Provided"`; route communication
  through the platform's internal messaging if available rather than
  blocking registration.
- **Business impact if unhandled:** Providers cannot confirm a claim
  before releasing food, which risks both wasted food (if the provider
  is cautious and withholds it) and unsafe handoffs (if they aren't).

### Food_Listings.Expiry_Date
- **Possible reason:** Provider uncertain of exact expiry (e.g., bulk
  prepared food without printed labeling) or rushed data entry.
- **Handling method:** Do not silently drop — these are exactly the
  listings most at risk of being wasted. Flag as `"Unknown — verify
  before claiming"` and surface a warning badge in the UI rather than
  guessing a date.
- **Business impact if unhandled:** A missing expiry date could cause a
  receiver to claim and distribute food that has already spoiled
  (safety risk), or cause the platform to silently exclude valid food
  from listings (lost donation).

### Food_Listings.Quantity
- **Possible reason:** Provider entry error, or a listing created as a
  placeholder before quantity was finalized.
- **Handling method:** Do not impute a fabricated number — exclude the
  row from quantity-based aggregations and flag it for the provider to
  complete before the listing goes live to receivers.
- **Business impact if unhandled:** Any SUM/AVG-based KPI (total food
  available, average claim size) would silently understate true
  values, distorting every downstream business query.

### Claims.Status
- **Possible reason:** Claim created but the receiver or system
  workflow never finalized a status (e.g., an interrupted session).
- **Handling method:** Default to `"Pending"` rather than assuming
  completion or cancellation, since `"Pending"` is the only status that
  doesn't make an unverified claim about what happened.
- **Business impact if unhandled:** A null treated as "Completed" would
  inflate the claim-success KPI; treated as "Cancelled" would
  understate platform effectiveness. Both distort the Claim Status
  Percentage analysis (SQL Insight #10).

### Claims.Timestamp
- **Possible reason:** Logging failure at claim-creation time, or a
  claim imported from a legacy system without a timestamp.
- **Handling method:** Do not impute a fabricated timestamp — exclude
  the row from any time-series analysis (e.g., the daily claim trend in
  SQL Insight #15) while keeping it in status-based counts.
- **Business impact if unhandled:** Trend analysis would show
  artificial gaps or spikes depending on how nulls sort, misleading
  staffing and logistics planning.

## Summary

The dataset audited for this submission is clean. The methodology above
is the team's documented standard so that if/when real-world data
collection introduces nulls (which is the norm for crowdsourced or
multi-organization data entry), the platform has a pre-agreed, defensible
handling policy rather than ad hoc decisions made under deadline pressure.
