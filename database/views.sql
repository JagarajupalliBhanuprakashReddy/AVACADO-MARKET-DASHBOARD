-- ==============================================================================
-- AGRICULTURAL MARKET PRICING & SALES DASHBOARD - DATABASE ANALYTICAL VIEWS
-- ==============================================================================

USE agricultural_market_db;

-- ------------------------------------------------------------------------------
-- 1. Complete Denormalized View (Fact + All Dimensions)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_avocado_complete AS
SELECT 
    o.observation_id,
    d.full_date AS price_date,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.week_number,
    r.region_name AS region,
    r.market_tier,
    t.type_name AS avocado_type,
    o.average_price,
    o.total_volume,
    o.total_bags,
    o.small_bags,
    o.large_bags,
    o.xlarge_bags,
    o.plu_4046,
    o.plu_4225,
    o.plu_4770
FROM avocado_observations o
JOIN dim_date d ON o.date_id = d.date_id
JOIN dim_region r ON o.region_id = r.region_id
JOIN dim_avocado_type t ON o.type_id = t.type_id;

-- ------------------------------------------------------------------------------
-- 2. Weekly Price Trends View (with Window Functions & Moving Averages)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_weekly_price_trends AS
SELECT 
    d.year,
    d.week_number,
    MIN(d.full_date) AS week_start_date,
    COUNT(*) AS observation_count,
    ROUND(AVG(o.average_price), 2) AS avg_weekly_price,
    ROUND(MIN(o.average_price), 2) AS min_weekly_price,
    ROUND(MAX(o.average_price), 2) AS max_weekly_price,
    ROUND(SUM(o.total_volume), 2) AS total_weekly_volume,
    ROUND(AVG(AVG(o.average_price)) OVER (
        PARTITION BY d.year 
        ORDER BY d.week_number 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_4wk_avg_price
FROM avocado_observations o
JOIN dim_date d ON o.date_id = d.date_id
GROUP BY d.year, d.week_number;

-- ------------------------------------------------------------------------------
-- 3. Regional Performance Ranking View (with RANK() Window Function)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_regional_performance AS
SELECT 
    r.region_name,
    COUNT(o.observation_id) AS total_records,
    ROUND(AVG(o.average_price), 2) AS overall_avg_price,
    ROUND(MIN(o.average_price), 2) AS lowest_price,
    ROUND(MAX(o.average_price), 2) AS highest_price,
    ROUND(SUM(o.total_volume), 2) AS cumulative_volume,
    ROUND(SUM(o.total_bags), 2) AS cumulative_bags,
    DENSE_RANK() OVER (ORDER BY SUM(o.total_volume) DESC) AS volume_rank
FROM avocado_observations o
JOIN dim_region r ON o.region_id = r.region_id
GROUP BY r.region_id, r.region_name;

-- ------------------------------------------------------------------------------
-- 4. Yearly Price Gap View (Conventional vs Organic Price Premium)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_yearly_price_gap AS
SELECT 
    d.year,
    ROUND(AVG(CASE WHEN t.type_name = 'conventional' THEN o.average_price END), 2) AS conventional_avg_price,
    ROUND(AVG(CASE WHEN t.type_name = 'organic' THEN o.average_price END), 2) AS organic_avg_price,
    ROUND(
        AVG(CASE WHEN t.type_name = 'organic' THEN o.average_price END) - 
        AVG(CASE WHEN t.type_name = 'conventional' THEN o.average_price END), 
        2
    ) AS absolute_gap,
    ROUND(
        (
            (AVG(CASE WHEN t.type_name = 'organic' THEN o.average_price END) - 
             AVG(CASE WHEN t.type_name = 'conventional' THEN o.average_price END)) /
            AVG(CASE WHEN t.type_name = 'conventional' THEN o.average_price END)
        ) * 100, 
        2
    ) AS organic_premium_pct,
    ROUND(SUM(CASE WHEN t.type_name = 'conventional' THEN o.total_volume ELSE 0 END), 2) AS conventional_volume,
    ROUND(SUM(CASE WHEN t.type_name = 'organic' THEN o.total_volume ELSE 0 END), 2) AS organic_volume
FROM avocado_observations o
JOIN dim_date d ON o.date_id = d.date_id
JOIN dim_avocado_type t ON o.type_id = t.type_id
GROUP BY d.year;

-- ------------------------------------------------------------------------------
-- 5. Monthly Seasonality View
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_monthly_seasonality AS
SELECT 
    d.month,
    d.month_name,
    COUNT(o.observation_id) AS total_observations,
    ROUND(AVG(o.average_price), 2) AS monthly_avg_price,
    ROUND(MIN(o.average_price), 2) AS monthly_min_price,
    ROUND(MAX(o.average_price), 2) AS monthly_max_price,
    ROUND(SUM(o.total_volume), 2) AS monthly_total_volume
FROM avocado_observations o
JOIN dim_date d ON o.date_id = d.date_id
GROUP BY d.month, d.month_name
ORDER BY d.month;

-- ------------------------------------------------------------------------------
-- 6. Bag Distribution View
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_bag_distribution AS
SELECT 
    r.region_name,
    ROUND(SUM(o.small_bags), 2) AS total_small_bags,
    ROUND(SUM(o.large_bags), 2) AS total_large_bags,
    ROUND(SUM(o.xlarge_bags), 2) AS total_xlarge_bags,
    ROUND(SUM(o.total_bags), 2) AS total_bags,
    ROUND((SUM(o.small_bags) / NULLIF(SUM(o.total_bags), 0)) * 100, 2) AS small_bag_pct,
    ROUND((SUM(o.large_bags) / NULLIF(SUM(o.total_bags), 0)) * 100, 2) AS large_bag_pct,
    ROUND((SUM(o.xlarge_bags) / NULLIF(SUM(o.total_bags), 0)) * 100, 2) AS xlarge_bag_pct
FROM avocado_observations o
JOIN dim_region r ON o.region_id = r.region_id
GROUP BY r.region_id, r.region_name;
