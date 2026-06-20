-- ============================================================
-- Local Food Wastage Management System
-- Database Schema
-- Engine: SQLite (portable; same DDL works on MySQL/Postgres
--          with minor type adjustments noted in comments)
-- ============================================================

DROP TABLE IF EXISTS Claims;
DROP TABLE IF EXISTS Food_Listings;
DROP TABLE IF EXISTS Receivers;
DROP TABLE IF EXISTS Providers;

-- ------------------------------------------------------------
-- Table: Providers
-- One row per organization that donates/lists surplus food.
-- ------------------------------------------------------------
CREATE TABLE Providers (
    Provider_ID   INTEGER PRIMARY KEY,
    Name          TEXT NOT NULL,
    Type          TEXT NOT NULL,   -- Supermarket / Grocery Store / Restaurant / Catering Service
    Address       TEXT,
    City          TEXT NOT NULL,
    Contact       TEXT
);

-- ------------------------------------------------------------
-- Table: Receivers
-- One row per organization/individual that claims food.
-- ------------------------------------------------------------
CREATE TABLE Receivers (
    Receiver_ID   INTEGER PRIMARY KEY,
    Name          TEXT NOT NULL,
    Type          TEXT NOT NULL,   -- NGO / Charity / Shelter / Individual
    City          TEXT NOT NULL,
    Contact       TEXT
);

-- ------------------------------------------------------------
-- Table: Food_Listings
-- One row per food item listed by a provider.
-- Provider_Type and Location are denormalized copies that
-- exist in the source data (kept as-is, not deduplicated,
-- since the project rules forbid merging in Python and we
-- preserve the data as supplied).
-- ------------------------------------------------------------
CREATE TABLE Food_Listings (
    Food_ID        INTEGER PRIMARY KEY,
    Food_Name      TEXT NOT NULL,
    Quantity       INTEGER NOT NULL CHECK (Quantity >= 0),
    Expiry_Date    DATE NOT NULL,
    Provider_ID    INTEGER NOT NULL,
    Provider_Type  TEXT,
    Location       TEXT,
    Food_Type      TEXT,   -- Vegetarian / Non-Vegetarian / Vegan
    Meal_Type      TEXT,   -- Breakfast / Lunch / Dinner / Snacks
    FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID)
);

-- ------------------------------------------------------------
-- Table: Claims
-- One row per claim a receiver makes on a food listing.
-- ------------------------------------------------------------
CREATE TABLE Claims (
    Claim_ID      INTEGER PRIMARY KEY,
    Food_ID       INTEGER NOT NULL,
    Receiver_ID   INTEGER NOT NULL,
    Status        TEXT NOT NULL,  -- Pending / Completed / Cancelled
    Timestamp     DATETIME NOT NULL,
    FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID),
    FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID)
);

-- ------------------------------------------------------------
-- Indexes to speed up the JOIN-heavy analytical queries
-- ------------------------------------------------------------
CREATE INDEX idx_food_provider   ON Food_Listings(Provider_ID);
CREATE INDEX idx_claims_food     ON Claims(Food_ID);
CREATE INDEX idx_claims_receiver ON Claims(Receiver_ID);
CREATE INDEX idx_food_city       ON Food_Listings(Location);
CREATE INDEX idx_provider_city   ON Providers(City);
CREATE INDEX idx_receiver_city   ON Receivers(City);

-- ============================================================
-- ER RELATIONSHIPS (description)
-- ============================================================
-- Providers (1) ----< Food_Listings (M)    via Provider_ID
-- Food_Listings (1) ----< Claims (M)       via Food_ID
-- Receivers (1) ----< Claims (M)           via Receiver_ID
--
-- A Provider can list many Food items.
-- A Food item can receive many Claims (e.g. re-claimed after
--   a cancellation), but typically tracks one active claim.
-- A Receiver can make many Claims.
-- ============================================================
