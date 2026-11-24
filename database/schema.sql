-- ==============================================================================
-- AGRICULTURAL MARKET PRICING & SALES DASHBOARD - DATABASE SCHEMA
-- Database: agricultural_market_db
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS agricultural_market_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE agricultural_market_db;

-- ------------------------------------------------------------------------------
-- 1. BASE / STAGING TABLE: avocado_prices
-- Preserves flat historical records as originally imported from avocado.csv
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS avocado_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    price_date DATE NOT NULL,
    average_price DECIMAL(6,2) NOT NULL,
    total_volume DECIMAL(15,2) NOT NULL,
    plu_4046 DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    plu_4225 DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    plu_4770 DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_bags DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    small_bags DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    large_bags DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    xlarge_bags DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    avocado_type VARCHAR(20) NOT NULL,
    year SMALLINT NOT NULL,
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_average_price CHECK (average_price >= 0),
    CONSTRAINT chk_total_volume CHECK (total_volume >= 0),
    CONSTRAINT chk_avocado_type CHECK (avocado_type IN ('conventional', 'organic'))
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 2. DIMENSION TABLE: dim_date
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day TINYINT NOT NULL,
    month TINYINT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    quarter TINYINT NOT NULL,
    year SMALLINT NOT NULL,
    week_number TINYINT NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 3. DIMENSION TABLE: dim_region
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_region (
    region_id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE,
    market_tier VARCHAR(30) NOT NULL DEFAULT 'Major Metro / Regional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 4. DIMENSION TABLE: dim_avocado_type
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_avocado_type (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 5. FACT TABLE: avocado_observations
-- Normalized 3NF star schema referencing dimension tables with strict referential integrity
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS avocado_observations (
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    date_id INT NOT NULL,
    region_id INT NOT NULL,
    type_id INT NOT NULL,
    average_price DECIMAL(6,2) NOT NULL,
    total_volume DECIMAL(15,2) NOT NULL,
    total_bags DECIMAL(15,2) NOT NULL,
    small_bags DECIMAL(15,2) NOT NULL,
    large_bags DECIMAL(15,2) NOT NULL,
    xlarge_bags DECIMAL(15,2) NOT NULL,
    plu_4046 DECIMAL(15,2) NOT NULL,
    plu_4225 DECIMAL(15,2) NOT NULL,
    plu_4770 DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_obs_date FOREIGN KEY (date_id) REFERENCES dim_date(date_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_obs_region FOREIGN KEY (region_id) REFERENCES dim_region(region_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_obs_type FOREIGN KEY (type_id) REFERENCES dim_avocado_type(type_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_obs_price CHECK (average_price >= 0),
    CONSTRAINT chk_obs_volume CHECK (total_volume >= 0)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------------------
-- 6. AUDIT / METADATA TABLE: dataset_metadata
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dataset_metadata (
    dataset_id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL,
    source_url VARCHAR(255) NOT NULL,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_count INT NOT NULL,
    source_file VARCHAR(100) NOT NULL,
    data_version VARCHAR(100) NOT NULL,
    data_license VARCHAR(100) NOT NULL,
    data_publisher VARCHAR(100) NOT NULL
) ENGINE=InnoDB;
