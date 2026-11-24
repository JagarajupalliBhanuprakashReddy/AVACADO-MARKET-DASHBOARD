# Entity-Relationship (ER) Architecture Documentation
## Agricultural Market Pricing & Sales Dashboard
**Database:** `agricultural_market_db` (MySQL 8.x)

---

## 1. Conceptual Dimensional Model

The database is structured around a **Dimensional Star Schema in Third Normal Form (3NF)** for Online Analytical Processing (OLAP) and high-speed analytical aggregations, backed by a canonical staging table for initial raw ingestion:

```mermaid
erDiagram
    DIM_DATE ||--o{ AVOCADO_OBSERVATIONS : "classifies by calendar"
    DIM_REGION ||--o{ AVOCADO_OBSERVATIONS : "locates geographic market"
    DIM_AVOCADO_TYPE ||--o{ AVOCADO_OBSERVATIONS : "categorizes product variety"
    DATASET_METADATA ||--o{ AVOCADO_PRICES : "tracks ingestion provenance"

    DIM_DATE {
        int date_id PK
        date full_date UK "Unique calendar date (2015-01-04 to 2018-03-25)"
        tinyint day "Day of the month (1-31)"
        tinyint month "Month number (1-12)"
        varchar month_name "Full English month name"
        tinyint quarter "Calendar quarter (1-4)"
        smallint year "Calendar year (2015-2018)"
        tinyint week_number "ISO calendar week (1-53)"
        boolean is_weekend "Flag for weekend dates"
    }

    DIM_REGION {
        int region_id PK
        varchar region_name UK "Distinct regional market (54 regions)"
        varchar market_tier "National, Multi-State, or Metro tier"
        timestamp created_at "System registration timestamp"
    }

    DIM_AVOCADO_TYPE {
        int type_id PK
        varchar type_name UK "conventional or organic"
        varchar description "Standardized product definition"
    }

    AVOCADO_OBSERVATIONS {
        int observation_id PK "Surrogate observation identifier"
        int date_id FK "Foreign key -> dim_date.date_id"
        int region_id FK "Foreign key -> dim_region.region_id"
        int type_id FK "Foreign key -> dim_avocado_type.type_id"
        decimal average_price "Recorded average unit price ($)"
        decimal total_volume "Total recorded volume (units)"
        decimal total_bags "Cumulative bagged volume"
        decimal small_bags "Small bag packaging volume"
        decimal large_bags "Large bag packaging volume"
        decimal xlarge_bags "Extra large bag packaging volume"
        decimal plu_4046 "Small/Medium Hass PLU volume"
        decimal plu_4225 "Large Hass PLU volume"
        decimal plu_4770 "Extra Large Hass PLU volume"
        timestamp created_at "Record creation timestamp"
    }

    AVOCADO_PRICES {
        int price_id PK "Canonical staging observation primary key"
        date price_date "Raw observation date"
        decimal average_price "Average retail price recorded ($)"
        decimal total_volume "Total recorded units"
        decimal plu_4046 "Volume under PLU 4046"
        decimal plu_4225 "Volume under PLU 4225"
        decimal plu_4770 "Volume under PLU 4770"
        decimal total_bags "Total packaged bags"
        decimal small_bags "Small bags volume"
        decimal large_bags "Large bags volume"
        decimal xlarge_bags "XLarge bags volume"
        varchar avocado_type "conventional or organic"
        smallint year "Calendar year"
        varchar region "Geographic market region"
    }

    DATASET_METADATA {
        int dataset_id PK "Metadata record identifier"
        varchar dataset_name "Avocado Prices 2015-2018"
        varchar source_url "Kaggle source reference"
        timestamp import_date "ETL execution timestamp"
        int record_count "Number of verified rows (18,249)"
        varchar source_file "avocado.csv"
        varchar data_version "HAB Release Version"
        varchar data_license "ODbL / Public Domain"
        varchar data_publisher "Justin Kiggins / Hass Avocado Board"
    }
```

---

## 2. Cardinality & Relationship Constraints

| Parent Table | Child Table | Relationship | Cardinality | Foreign Key | Cascade Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `dim_date` | `avocado_observations` | One-to-Many | 1 : N | `date_id` | `ON DELETE RESTRICT ON UPDATE CASCADE` |
| `dim_region` | `avocado_observations` | One-to-Many | 1 : N | `region_id` | `ON DELETE RESTRICT ON UPDATE CASCADE` |
| `dim_avocado_type` | `avocado_observations` | One-to-Many | 1 : N | `type_id` | `ON DELETE RESTRICT ON UPDATE CASCADE` |

### Constraint Validations:
- `chk_obs_price`: `average_price >= 0`
- `chk_obs_volume`: `total_volume >= 0`
- `dim_date.full_date`: `UNIQUE NOT NULL`
- `dim_region.region_name`: `UNIQUE NOT NULL`
- `dim_avocado_type.type_name`: `UNIQUE NOT NULL`
