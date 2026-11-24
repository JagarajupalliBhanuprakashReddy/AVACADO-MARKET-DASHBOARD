# Comprehensive Data Dictionary
## Agricultural Market Pricing & Sales Dashboard
**Database:** `agricultural_market_db`

---

## 1. Domain Entities & Metrics Definitions

| Field / Attribute | Entity | Data Type | Units / Format | Business Definition & Calculation Rules |
| :--- | :--- | :--- | :--- | :--- |
| `observation_id` | `avocado_observations` | INT | Integer | Surrogate numeric primary key uniquely identifying a weekly observation. |
| `price_date` | `dim_date` / `avocado_prices` | DATE | YYYY-MM-DD | The ending Sunday date of the observation week reported by the Hass Avocado Board. |
| `average_price` | `avocado_observations` | DECIMAL(6,2) | USD ($) | Average recorded price for a single avocado unit in the given market during that week. |
| `total_volume` | `avocado_observations` | DECIMAL(15,2) | Units | Total number of physical avocados recorded/shipped in that market. Not monetary revenue. |
| `plu_4046` | `avocado_observations` | DECIMAL(15,2) | Units | Recorded volume of Small/Medium Hass avocados (Price Look-Up code 4046). |
| `plu_4225` | `avocado_observations` | DECIMAL(15,2) | Units | Recorded volume of Large Hass avocados (Price Look-Up code 4225). |
| `plu_4770` | `avocado_observations` | DECIMAL(15,2) | Units | Recorded volume of Extra Large Hass avocados (Price Look-Up code 4770). |
| `total_bags` | `avocado_observations` | DECIMAL(15,2) | Units | Aggregate volume of avocados sold in packaged bags (`small_bags + large_bags + xlarge_bags`). |
| `small_bags` | `avocado_observations` | DECIMAL(15,2) | Units | Packaged volume in standard consumer retail small bags. |
| `large_bags` | `avocado_observations` | DECIMAL(15,2) | Units | Packaged volume in larger club-pack or family-sized bags. |
| `xlarge_bags` | `avocado_observations` | DECIMAL(15,2) | Units | Packaged volume in bulk extra-large bags. |
| `avocado_type` | `dim_avocado_type` | VARCHAR(20) | Categorical | Variety of avocado: `'conventional'` (standard commercial) or `'organic'` (USDA certified). |
| `region` | `dim_region` | VARCHAR(50) | Categorical | Geographic market name (e.g. `'California'`, `'NewYork'`, `'TotalUS'`, `'Chicago'`). |
| `market_tier` | `dim_region` | VARCHAR(30) | Categorical | Market level classification: `'National Market'`, `'Multi-State Region'`, or `'Metro / Sub-Regional Market'`. |
| `year` | `dim_date` | SMALLINT | Year (YYYY) | Calendar year of observation (2015, 2016, 2017, or 2018). |
| `quarter` | `dim_date` | TINYINT | Quarter (1-4) | Calendar quarter based on month: Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec). |
| `week_number` | `dim_date` | TINYINT | Week (1-53) | ISO calendar week number of the observation. |
| `pct_price_change` | Analytical Metric | DECIMAL(5,2) | Percentage (%) | Percentage change between baseline Year A and comparison Year B: `((New Avg - Old Avg) / Old Avg) * 100`. |
| `organic_premium_pct` | Analytical Metric | DECIMAL(5,2) | Percentage (%) | Relative premium of organic over conventional: `((Organic Avg - Conv Avg) / Conv Avg) * 100`. |
