# Glovo Poland (Synthetic) Dataset — Data Dictionary

A synthetic, Olist-style dataset simulating Glovo food-delivery operations across
36 Polish cities. Built for practicing a Data Engineering pipeline (e.g. Azure
Databricks bronze → silver → gold). **Data quality issues are intentional** —
see the "Known issues" column per table. Nothing here is real customer, courier,
or restaurant data.

**Time span:** 2023-01-01 to 2024-12-31
**Currency:** PLN

---

## 1. `glovo_cities_dataset.csv` — 36 rows — Quality: Clean
Reference/dimension table.

| Column | Type | Description |
|---|---|---|
| city_id | string | Surrogate key, e.g. `CTY001` |
| city_name | string | Polish city name |
| voivodeship | string | Region (województwo) |
| population | int | Approximate population |
| latitude / longitude | float | Coordinates |
| city_tier | string | `tier_1` (>500k), `tier_2` (200k–500k), `tier_3` (<200k) |

---

## 2. `glovo_cuisine_category_translation.csv` — 20 rows — Quality: Clean
Lookup table, mirrors Olist's category translation table.

| Column | Description |
|---|---|
| cuisine_category_pl | Polish category slug (e.g. `kuchnia_polska`) |
| cuisine_category_en | English translation (e.g. `polish_cuisine`) |

---

## 3. `glovo_couriers_dataset.csv` — ~1,500 rows — Quality: Light mess
| Column | Description |
|---|---|
| courier_id | Surrogate key `CURxxxxx` |
| courier_name | Faker-generated Polish name |
| city | City the courier operates in |
| vehicle_type | bike / scooter / car / e-bike |
| signup_date | Date joined |

**Known issues:** ~5% inconsistent city casing/whitespace; ~2% missing city.

---

## 4. `glovo_restaurants_dataset.csv` — ~1,236 rows — Quality: Moderate mess
| Column | Description |
|---|---|
| restaurant_id | Surrogate key `RESTxxxxx` |
| restaurant_name | Chain or generated local name |
| city | City name — join key to `cities` (not always clean, see below) |
| cuisine_category_pl | FK to cuisine translation table |
| avg_rating | 1.0–5.0 |
| is_active | Boolean |

**Known issues:** ~8% inconsistent city casing/whitespace; ~7% missing
`avg_rating`; ~3% duplicate rows (same restaurant_id repeated).

---

## 5. `glovo_customers_dataset.csv` — ~20,600 rows — Quality: Moderate mess
| Column | Description |
|---|---|
| customer_id | Unique per "session"/order account (hex) |
| customer_unique_id | Stable identity across accounts (hex) |
| customer_city | City name |
| customer_zip_code | Polish-style postcode |
| signup_date | Date |

**Known issues:** ~7% inconsistent city casing/whitespace; ~5% Polish
diacritics stripped/broken (e.g. `Łódź` → `Lodz`, simulating an encoding bug
upstream); ~4% missing `customer_unique_id`; ~3% duplicate rows.

---

## 6. `glovo_menu_items_dataset.csv` — ~5,389 rows — Quality: Moderate mess
| Column | Description |
|---|---|
| item_id | Surrogate key `ITEMxxxxxx` |
| restaurant_id | FK to restaurants |
| item_name | Dish name |
| item_category_pl | Cuisine category (may be null) |
| price_pln | Price — **stored as text**, format varies (see issues) |

**Known issues:** ~10% of prices use comma decimal (`24,99`) or a `zł` text
suffix (`24.99 zl`) instead of clean floats — expect to cast/clean this
column; ~5% missing `item_category_pl`; ~1% negative prices (data bug).

---

## 7. `glovo_orders_dataset.csv` — ~51,500 rows — Quality: **Heavy mess**
The core fact table.

| Column | Description |
|---|---|
| order_id | Hex order identifier (not always unique — see issues) |
| customer_id | FK to customers (not always valid — see issues) |
| restaurant_id | FK to restaurants (not always valid — see issues) |
| courier_id | FK to couriers, null for pending/cancelled orders |
| order_status | delivered / cancelled / in_transit / pending / returned |
| order_placed_at | Timestamp — **mixed formats**, see issues |
| order_picked_up_at | Timestamp, null if never picked up |
| order_delivered_at | Timestamp, null unless status is delivered/returned |
| delivery_distance_km | Float, includes outliers |

**Known issues:**
- ~10% of `order_placed_at` values use alternate formats (`DD/MM/YYYY HH:MM:SS`,
  `Mon DD YYYY hh:mm AM/PM`, ISO `T`-separated) instead of the default
  `YYYY-MM-DD HH:MM:SS` — a classic multi-format datetime parsing exercise.
- ~7% inconsistent `order_status` casing/spelling (`DELIVERED`, `Cancelled`,
  `in transit`).
- ~3% have `order_delivered_at` earlier than `order_placed_at` (logically
  impossible — a data bug to catch in validation).
- ~2% have `delivery_distance_km` = 9999 (sensor/outlier bug).
- ~2% reference a `restaurant_id` that doesn't exist in the restaurants table.
- ~2% reference a `customer_id` that doesn't exist in the customers table.
- ~2% missing `courier_id` despite being delivered.
- ~3% duplicate order rows (same order_id repeated).

---

## 8. `glovo_order_items_dataset.csv` — ~127,566 rows — Quality: Moderate-heavy mess
| Column | Description |
|---|---|
| order_id | FK to orders |
| order_item_id | Surrogate key |
| item_id | FK to menu_items (not always valid — see issues) |
| quantity | Int, occasionally negative |
| unit_price_pln | Float, occasionally negative |

**Known issues:** ~5% reference an `item_id` that doesn't exist in
menu_items; ~2% negative quantity; ~2% negative unit_price; ~4% duplicate
rows.

---

## 9. `glovo_payments_dataset.csv` — ~55,166 rows — Quality: **Heavy mess**
| Column | Description |
|---|---|
| order_id | FK to orders (not always valid — see issues) |
| payment_type | card / blik / cash / glovo_credit — **inconsistent spelling** |
| payment_value_pln | Amount — **stored as text**, mixed decimal format |

**Known issues:**
- ~12% of `payment_type` values are inconsistent variants of the four
  canonical types (`CARD`, `Card`, `karta`, `payment_card`, `BLIK`,
  `blik_payment`, `gotowka`, `cash_on_delivery`, `GLOVO_CREDIT`, `credit`,
  etc.) — needs a mapping/standardization step.
- ~10% of `payment_value_pln` use comma decimals (`45,90`) instead of dots.
- ~2% negative values (refund glitches, not flagged as such).
- ~3% of rows are orphans — `order_id` doesn't exist in the orders table
  (simulates payment-gateway records that never matched back to an order).
- ~4% duplicate payment rows.

---

## 10. `glovo_reviews_dataset.csv` — ~41,200 rows — Quality: Moderate mess
Covers ~80% of unique orders (not every order gets reviewed — that 20% gap
is expected/realistic, not a bug).

| Column | Description |
|---|---|
| review_id | Surrogate key `REVxxxxxxx` |
| order_id | FK to orders (not always valid — see issues) |
| review_score | Intended range 1–5 |
| review_comment | Free text, frequently null |
| review_date | Date |

**Known issues:** ~3% `review_score` outside the valid 1–5 range (0, -1, 6,
10); ~3% orphan `order_id` (doesn't exist in orders); ~3% duplicate review
rows.

---

## Suggested pipeline exercises
- **Bronze layer:** ingest as-is, preserve raw text columns (prices, dates)
  untyped.
- **Silver layer:** parse multi-format dates, cast comma-decimal prices,
  standardize `payment_type` and `order_status` categorical values, strip
  whitespace/casing on city names, deduplicate on natural keys, quarantine
  orphaned FK rows into a "rejected records" table.
- **Gold layer:** build a star schema — `fact_orders` + `dim_customer`,
  `dim_restaurant`, `dim_city`, `dim_date`, `dim_courier` — with revenue,
  delivery-time, and rating aggregations, likely with referential-integrity
  checks (e.g. Delta Live Tables expectations) rejecting the orphan rows
  identified above.

---

## Profiling findings (added by this project)

- **`glovo_orders_dataset.csv` was re-saved in Excel** (only file with CRLF line endings).
  Excel rewrote most timestamps to US `M/D/YYYY H:MM` and dropped seconds in all three
  timestamp columns. All remaining `DD/MM/YYYY HH:MM:SS` values have a day > 12, which
  means values with day ≤ 12 were most likely re-read as `M/D` and silently had day and
  month swapped. Parsing rule for Silver: slash format **with** seconds = `DD/MM/YYYY`,
  **without** seconds = `M/D/YYYY`. See [ADR-0001](adr/0001-parquet-landing-format.md).
- 17,455 of 20,600 `customers.signup_date` values (85%) fall after 2024-12-31 (latest
  2026-09-12), outside the stated 2023–2024 span. Many customers therefore "sign up"
  after their own orders. Treat `signup_date` as unreliable; derive first-order date in Silver.
