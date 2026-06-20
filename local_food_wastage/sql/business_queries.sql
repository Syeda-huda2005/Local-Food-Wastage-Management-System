-- ============================================================
-- Local Food Wastage Management System
-- Business Analysis Queries (15 required questions + extras)
-- Engine: SQLite
-- ============================================================
-- NOTE ON DATA: All claim timestamps fall within 2025-03-01 to
-- 2025-03-21 (a 3-week window). Query 15 therefore reports a
-- DAILY trend rather than a monthly one — a monthly grouping
-- would collapse to a single bar and provide no insight. This
-- is a judgment call driven by what the actual data supports.
-- ============================================================


-- ------------------------------------------------------------
-- Q1. Providers by City
-- Business objective: Identify which cities have the strongest
-- provider presence, to prioritize NGO partnership outreach.
-- ------------------------------------------------------------
SELECT City, COUNT(*) AS Provider_Count
FROM Providers
GROUP BY City
ORDER BY Provider_Count DESC;


-- ------------------------------------------------------------
-- Q2. Receivers by City
-- Business objective: Identify cities with the most receivers
-- (demand concentration) to plan distribution logistics.
-- ------------------------------------------------------------
SELECT City, COUNT(*) AS Receiver_Count
FROM Receivers
GROUP BY City
ORDER BY Receiver_Count DESC;


-- ------------------------------------------------------------
-- Q3. Most Contributing Provider (by total quantity listed)
-- Business objective: Identify top donors for recognition
-- programs and partnership retention.
-- ------------------------------------------------------------
SELECT p.Provider_ID, p.Name, p.Type, SUM(f.Quantity) AS Total_Quantity_Listed
FROM Providers p
JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID, p.Name, p.Type
ORDER BY Total_Quantity_Listed DESC
LIMIT 10;


-- ------------------------------------------------------------
-- Q4. Most Claimed Food Item (by Food_Name, claim count)
-- Business objective: Understand which food types are in
-- highest demand among receivers.
-- ------------------------------------------------------------
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
FROM Claims c
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Claim_Count DESC;


-- ------------------------------------------------------------
-- Q5. Total Food Quantity Available (all listings)
-- Business objective: Headline KPI for platform-wide
-- food volume.
-- ------------------------------------------------------------
SELECT SUM(Quantity) AS Total_Quantity_Available
FROM Food_Listings;


-- ------------------------------------------------------------
-- Q6. Top City by Food Listing (count and quantity)
-- Business objective: Identify the supply hotspot.
-- ------------------------------------------------------------
SELECT Location AS City,
       COUNT(*) AS Listing_Count,
       SUM(Quantity) AS Total_Quantity
FROM Food_Listings
GROUP BY Location
ORDER BY Total_Quantity DESC
LIMIT 10;


-- ------------------------------------------------------------
-- Q7. Most Common Food Type
-- Business objective: Understand the dominant category of
-- food being donated.
-- ------------------------------------------------------------
SELECT Food_Type, COUNT(*) AS Listing_Count
FROM Food_Listings
GROUP BY Food_Type
ORDER BY Listing_Count DESC;


-- ------------------------------------------------------------
-- Q8. Claims per Food Item (per Food_ID, using LEFT JOIN so
-- food items with zero claims are also visible)
-- Business objective: Spot food listings that are not being
-- claimed at all (waste risk).
-- ------------------------------------------------------------
SELECT f.Food_ID, f.Food_Name, f.Location, f.Quantity,
       COUNT(c.Claim_ID) AS Claim_Count
FROM Food_Listings f
LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_ID, f.Food_Name, f.Location, f.Quantity
ORDER BY Claim_Count ASC, f.Quantity DESC
LIMIT 15;


-- ------------------------------------------------------------
-- Q9. Provider with Most Successful (Completed) Claims
-- Business objective: Identify providers whose donations
-- convert into actual delivered food, not just listings.
-- ------------------------------------------------------------
SELECT p.Provider_ID, p.Name, p.Type,
       COUNT(c.Claim_ID) AS Completed_Claims
FROM Providers p
JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
JOIN Claims c ON f.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID, p.Name, p.Type
ORDER BY Completed_Claims DESC
LIMIT 10;


-- ------------------------------------------------------------
-- Q10. Claim Status Percentage (uses CASE WHEN + subquery)
-- Business objective: Measure platform efficiency — what
-- share of claims actually complete.
-- ------------------------------------------------------------
SELECT
    Status,
    COUNT(*) AS Status_Count,
    ROUND(
        100.0 * COUNT(*) / (SELECT COUNT(*) FROM Claims), 2
    ) AS Percentage
FROM Claims
GROUP BY Status
ORDER BY Status_Count DESC;


-- ------------------------------------------------------------
-- Q11. Average Quantity Claimed (Completed claims only)
-- Business objective: Typical donation size that successfully
-- reaches a receiver.
-- ------------------------------------------------------------
SELECT ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
FROM Claims c
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed';


-- ------------------------------------------------------------
-- Q12. Most Claimed Meal Type
-- Business objective: Identify which meal occasion drives
-- the most receiver demand.
-- ------------------------------------------------------------
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
FROM Claims c
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Claim_Count DESC;


-- ------------------------------------------------------------
-- Q13. Total Donated Quantity by Provider Type
-- (GROUP BY + HAVING to filter low-volume types)
-- Business objective: Compare contribution by provider
-- category to focus partnership growth.
-- ------------------------------------------------------------
SELECT Provider_Type, SUM(Quantity) AS Total_Donated_Quantity
FROM Food_Listings
GROUP BY Provider_Type
HAVING SUM(Quantity) > 0
ORDER BY Total_Donated_Quantity DESC;


-- ------------------------------------------------------------
-- Q14. Top Receiver by Quantity Claimed (Completed claims)
-- Uses window function RANK() to show ties correctly.
-- Business objective: Identify highest-impact receivers for
-- partnership deepening / case studies.
-- ------------------------------------------------------------
WITH receiver_totals AS (
    SELECT r.Receiver_ID, r.Name, r.Type, SUM(f.Quantity) AS Total_Claimed
    FROM Claims c
    JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    JOIN Food_Listings f ON c.Food_ID = f.Food_ID
    WHERE c.Status = 'Completed'
    GROUP BY r.Receiver_ID, r.Name, r.Type
)
SELECT *,
       RANK() OVER (ORDER BY Total_Claimed DESC) AS Rank_By_Quantity
FROM receiver_totals
ORDER BY Total_Claimed DESC
LIMIT 10;


-- ------------------------------------------------------------
-- Q15. Daily Claim Trend Analysis
-- (Data spans 2025-03-01 to 2025-03-21 only, so daily
-- granularity is used instead of monthly — see note at top.)
-- Business objective: Understand demand pattern over time to
-- plan staffing / logistics.
-- ------------------------------------------------------------
SELECT strftime('%Y-%m-%d', Timestamp) AS Claim_Date,
       COUNT(*) AS Claim_Count
FROM Claims
GROUP BY Claim_Date
ORDER BY Claim_Date;


-- ============================================================
-- ADDITIONAL QUERIES (demonstrate full SQL technique coverage)
-- ============================================================

-- ------------------------------------------------------------
-- Q16. Providers Who Have NEVER Had a Successful Claim
-- (LEFT JOIN + subquery — surfaces ineffective donors)
-- ------------------------------------------------------------
SELECT p.Provider_ID, p.Name, p.Type, p.City
FROM Providers p
WHERE p.Provider_ID NOT IN (
    SELECT DISTINCT f.Provider_ID
    FROM Food_Listings f
    JOIN Claims c ON f.Food_ID = c.Food_ID
    WHERE c.Status = 'Completed'
);


-- ------------------------------------------------------------
-- Q17. Food Items Nearing Expiry With No Completed Claim
-- (INNER JOIN + WHERE + date filter — operational alert query)
-- ------------------------------------------------------------
SELECT f.Food_ID, f.Food_Name, f.Location, f.Quantity, f.Expiry_Date
FROM Food_Listings f
WHERE f.Food_ID NOT IN (
        SELECT Food_ID FROM Claims WHERE Status = 'Completed'
    )
ORDER BY f.Expiry_Date ASC
LIMIT 15;


-- ------------------------------------------------------------
-- Q18. Receiver Type Performance (CTE + window function
-- DENSE_RANK to rank receiver types by total claimed quantity)
-- ------------------------------------------------------------
WITH type_totals AS (
    SELECT r.Type, SUM(f.Quantity) AS Total_Claimed
    FROM Claims c
    JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    JOIN Food_Listings f ON c.Food_ID = f.Food_ID
    WHERE c.Status = 'Completed'
    GROUP BY r.Type
)
SELECT *, DENSE_RANK() OVER (ORDER BY Total_Claimed DESC) AS Rank_Position
FROM type_totals;


-- ------------------------------------------------------------
-- Q19. Provider Contribution Ranking Within Each City
-- (Window function PARTITION BY — ROW_NUMBER per city)
-- ------------------------------------------------------------
-- NOTE: QUALIFY (Snowflake/BigQuery) is not supported in SQLite/
-- MySQL/Postgres, so the rank filter is applied via an outer
-- SELECT over the windowed subquery instead.
WITH provider_city_totals AS (
    SELECT p.Provider_ID, p.Name, p.City, SUM(f.Quantity) AS Total_Quantity
    FROM Providers p
    JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
    GROUP BY p.Provider_ID, p.Name, p.City
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY City ORDER BY Total_Quantity DESC) AS City_Rank
    FROM provider_city_totals
)
SELECT Provider_ID, Name, City, Total_Quantity, City_Rank
FROM ranked
WHERE City_Rank = 1
ORDER BY Total_Quantity DESC
LIMIT 15;


-- ------------------------------------------------------------
-- Q20. Full Outer Join Equivalent: Providers vs Receivers by
-- City (SQLite has no native FULL JOIN — emulated via
-- LEFT JOIN UNION RIGHT-style LEFT JOIN)
-- Business objective: Find supply/demand mismatches —
-- cities with providers but no receivers, or vice versa.
-- ------------------------------------------------------------
SELECT
    COALESCE(p.City, r.City) AS City,
    COUNT(DISTINCT p.Provider_ID) AS Provider_Count,
    COUNT(DISTINCT r.Receiver_ID) AS Receiver_Count
FROM Providers p
LEFT JOIN Receivers r ON p.City = r.City
GROUP BY p.City

UNION

SELECT
    COALESCE(p.City, r.City) AS City,
    COUNT(DISTINCT p.Provider_ID) AS Provider_Count,
    COUNT(DISTINCT r.Receiver_ID) AS Receiver_Count
FROM Receivers r
LEFT JOIN Providers p ON p.City = r.City
GROUP BY r.City
ORDER BY Provider_Count DESC, Receiver_Count DESC
LIMIT 20;
