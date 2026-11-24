-- ==============================================================================
-- AGRICULTURAL MARKET PRICING & SALES DASHBOARD - DATABASE INDEXES
-- ==============================================================================

USE agricultural_market_db;

-- Indexes on avocado_prices (base/staging table)
CREATE INDEX idx_prices_date ON avocado_prices (price_date);
CREATE INDEX idx_prices_region ON avocado_prices (region);
CREATE INDEX idx_prices_type ON avocado_prices (avocado_type);
CREATE INDEX idx_prices_year ON avocado_prices (year);
CREATE INDEX idx_prices_composite ON avocado_prices (year, region, avocado_type);
CREATE INDEX idx_prices_avg_price ON avocado_prices (average_price);
CREATE INDEX idx_prices_volume ON avocado_prices (total_volume);

-- Indexes on dim_date
CREATE INDEX idx_dim_date_year ON dim_date (year);
CREATE INDEX idx_dim_date_month ON dim_date (month);
CREATE INDEX idx_dim_date_quarter ON dim_date (quarter);
CREATE INDEX idx_dim_date_week ON dim_date (week_number);

-- Indexes on dim_region
CREATE INDEX idx_dim_region_name ON dim_region (region_name);

-- Indexes on dim_avocado_type
CREATE INDEX idx_dim_type_name ON dim_avocado_type (type_name);

-- Indexes on avocado_observations (fact table)
CREATE INDEX idx_obs_date_id ON avocado_observations (date_id);
CREATE INDEX idx_obs_region_id ON avocado_observations (region_id);
CREATE INDEX idx_obs_type_id ON avocado_observations (type_id);
CREATE INDEX idx_obs_composite ON avocado_observations (date_id, region_id, type_id);
CREATE INDEX idx_obs_price ON avocado_observations (average_price);
CREATE INDEX idx_obs_volume ON avocado_observations (total_volume);
