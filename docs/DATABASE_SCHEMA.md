# Relational Database Schema & Normalization Analysis
## Agricultural Market Pricing & Sales Dashboard
**Database Name:** `agricultural_market_db`  
**RDBMS:** MySQL 8.x Enterprise / Community Server

---

## 1. Normalization Breakdown (From Flat CSV to 3NF)

### Unnormalized Form (0NF - Raw `avocado.csv`):
In the raw Kaggle dataset, every single row contains repeated strings for `region` ('California', 'NewYork'), repeated calendar properties (year, full date string), and repeated type literals ('conventional', 'organic'). This creates insertion, update, and deletion anomalies.

### First Normal Form (1NF):
- All attributes are atomic (no repeating groups or arrays).
- Every table has a primary key (`price_id`, `observation_id`, `date_id`, `region_id`, `type_id`).
- Unique row identification is guaranteed.

### Second Normal Form (2NF):
- Meets 1NF requirements.
- Eliminates partial dependencies: Every non-key attribute is fully functionally dependent on the primary key. In the fact table `avocado_observations`, all metrics (`average_price`, `total_volume`, `plu_4046`, `small_bags`) depend strictly on the observation instance.

### Third Normal Form (3NF):
- Meets 2NF requirements.
- Eliminates transitive dependencies:
  - Calendar properties (`day`, `month`, `quarter`, `year`, `week_number`) are separated from the observation and moved into `dim_date`.
  - Regional attributes (`market_tier`) depend solely on `region_id` in `dim_region`.
  - Variety descriptions depend solely on `type_id` in `dim_avocado_type`.

---

## 2. Table Specifications

### 2.1 `avocado_observations` (Fact Table)
Stores primary observational units recorded weekly.

| Column | Data Type | Nullable | Key | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `observation_id` | INT | NO | PRI | AUTO_INC | Surrogate primary key |
| `date_id` | INT | NO | MUL | - | FK to `dim_date.date_id` |
| `region_id` | INT | NO | MUL | - | FK to `dim_region.region_id` |
| `type_id` | INT | NO | MUL | - | FK to `dim_avocado_type.type_id` |
| `average_price` | DECIMAL(6,2) | NO | MUL | - | Average price per single avocado ($) |
| `total_volume` | DECIMAL(15,2) | NO | MUL | - | Total physical volume recorded (units) |
| `total_bags` | DECIMAL(15,2) | NO | - | 0.00 | Total packaged bag volume |
| `small_bags` | DECIMAL(15,2) | NO | - | 0.00 | Small bag volume |
| `large_bags` | DECIMAL(15,2) | NO | - | 0.00 | Large bag volume |
| `xlarge_bags` | DECIMAL(15,2) | NO | - | 0.00 | Extra large bag volume |
| `plu_4046` | DECIMAL(15,2) | NO | - | 0.00 | Small/Medium Hass avocado volume |
| `plu_4225` | DECIMAL(15,2) | NO | - | 0.00 | Large Hass avocado volume |
| `plu_4770` | DECIMAL(15,2) | NO | - | 0.00 | Extra Large Hass avocado volume |
| `created_at` | TIMESTAMP | YES | - | CURRENT_TIMESTAMP | Ingestion audit timestamp |

### 2.2 `dim_date` (Dimension Table)
Calendar dimension enabling slicing by ISO week, quarter, month, and year.

| Column | Data Type | Nullable | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| `date_id` | INT | NO | PRI | Surrogate primary key |
| `full_date` | DATE | NO | UNI | ISO Calendar Date (YYYY-MM-DD) |
| `day` | TINYINT | NO | - | Day of month (1-31) |
| `month` | TINYINT | NO | MUL | Month number (1-12) |
| `month_name` | VARCHAR(15) | NO | - | January to December |
| `quarter` | TINYINT | NO | MUL | Calendar quarter (1-4) |
| `year` | SMALLINT | NO | MUL | Year (2015-2018) |
| `week_number` | TINYINT | NO | MUL | ISO week number (1-53) |
| `is_weekend` | BOOLEAN | NO | - | Weekend indicator |

### 2.3 `dim_region` (Dimension Table)
54 tracked geographic market territories.

| Column | Data Type | Nullable | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| `region_id` | INT | NO | PRI | Surrogate primary key |
| `region_name` | VARCHAR(50) | NO | UNI | Unique market identifier |
| `market_tier` | VARCHAR(30) | NO | - | National Market, Multi-State, or Metro |
| `created_at` | TIMESTAMP | YES | - | Creation timestamp |

### 2.4 `dim_avocado_type` (Dimension Table)
Product classifications.

| Column | Data Type | Nullable | Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| `type_id` | INT | NO | PRI | Primary key |
| `type_name` | VARCHAR(20) | NO | UNI | 'conventional' or 'organic' |
| `description` | VARCHAR(100) | NO | - | Regulatory product specification |

---

## 3. Query Execution Plan Analysis & Indexing Strategy

To guarantee millisecond query performance across 18,249 rows, composite and selective B-Tree indexes were created:

```sql
-- Composite index for multi-dimensional slicing
CREATE INDEX idx_prices_composite ON avocado_prices (year, region, avocado_type);
CREATE INDEX idx_obs_composite ON avocado_observations (date_id, region_id, type_id);
```

### EXPLAIN Query Plan for Multi-Year Regional Aggregation:
```sql
EXPLAIN SELECT 
    r.region_name, d.year, AVG(o.average_price)
FROM avocado_observations o
JOIN dim_date d ON o.date_id = d.date_id
JOIN dim_region r ON o.region_id = r.region_id
WHERE d.year = 2017
GROUP BY r.region_name, d.year;
```

**Plan Output Highlights:**
- `d` (dim_date): Uses `idx_dim_date_year` (type: `ref`), narrowing 169 dates to 53 dates immediately.
- `o` (avocado_observations): Uses `idx_obs_date_id` (type: `ref`), performing indexed index-nested loop joins.
- `r` (dim_region): Uses `PRIMARY` (type: `eq_ref`), retrieving region metadata in $O(1)$ constant time.
- Avoids full table scans (`type: ALL`) completely.
