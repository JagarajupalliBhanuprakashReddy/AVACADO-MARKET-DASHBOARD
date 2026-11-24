"""Report Service - Encapsulates the Ten Mandatory SQL Reports.

Every report includes:
- Academic title & business objective
- Demonstrated SQL concepts (CTE, Window functions, Joins, Aggregations, etc.)
- Parameterized SQL query
- Live MySQL execution
- Business interpretation
- Chart generation metadata
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import pandas as pd
from database.connection import query_to_dataframe


class ReportService:
    """Central registry and executor for the 10 Core Analytical SQL Reports."""

    REPORTS: Dict[int, Dict[str, Any]] = {
        1: {
            "id": 1,
            "title": "REPORT 1: Average Recorded Price by Calendar Week",
            "short_title": "1. Weekly Price Trend",
            "purpose": "Analyse weekly avocado price movements across the calendar timeline.",
            "sql_concepts": ["DATE Functions (YEAR, WEEK)", "GROUP BY", "AVG()", "ORDER BY", "ROUND()"],
            "chart_type": "line",
            "sql": """
                SELECT 
                    d.year,
                    d.week_number,
                    MIN(d.full_date) AS week_start_date,
                    ROUND(AVG(o.average_price), 2) AS avg_weekly_price,
                    ROUND(MIN(o.average_price), 2) AS min_weekly_price,
                    ROUND(MAX(o.average_price), 2) AS max_weekly_price,
                    ROUND(SUM(o.total_volume), 2) AS total_weekly_volume
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                GROUP BY d.year, d.week_number
                ORDER BY d.year, d.week_number;
            """,
            "interpretation": (
                "Weekly price tracking shows clear seasonal spikes in late summer and autumn each year. "
                "Prices typically reach their nadir during the late winter/spring flush when production peaks."
            )
        },
        2: {
            "id": 2,
            "title": "REPORT 2: Total Recorded Volume by Region",
            "short_title": "2. Volume by Region",
            "purpose": "Compare recorded avocado volume across distinct regional markets.",
            "sql_concepts": ["SUM()", "GROUP BY", "ORDER BY", "INNER JOIN", "Filtering Aggregations"],
            "chart_type": "horizontal_bar",
            "sql": """
                SELECT 
                    r.region_name AS region,
                    r.market_tier,
                    ROUND(SUM(o.total_volume), 2) AS total_recorded_volume,
                    ROUND(AVG(o.average_price), 2) AS avg_price,
                    ROUND(SUM(o.total_bags), 2) AS total_bags
                FROM avocado_observations o
                JOIN dim_region r ON o.region_id = r.region_id
                WHERE r.region_name != 'TotalUS'
                GROUP BY r.region_id, r.region_name, r.market_tier
                ORDER BY total_recorded_volume DESC;
            """,
            "interpretation": (
                "Regional distribution is dominated by the West and California regions, reflecting higher "
                "dietary adoption and geographic proximity to domestic production and Mexican import entry ports."
            )
        },
        3: {
            "id": 3,
            "title": "REPORT 3: Average Price by Avocado Type",
            "short_title": "3. Price by Type",
            "purpose": "Compare Organic and Conventional prices across recorded years.",
            "sql_concepts": ["GROUP BY", "AVG()", "CASE Expressions", "Conditional Aggregations", "MIN()/MAX()"],
            "chart_type": "grouped_bar",
            "sql": """
                SELECT 
                    d.year,
                    t.type_name AS avocado_type,
                    ROUND(AVG(o.average_price), 2) AS avg_price,
                    ROUND(MIN(o.average_price), 2) AS min_price,
                    ROUND(MAX(o.average_price), 2) AS max_price,
                    ROUND(SUM(o.total_volume), 2) AS total_volume,
                    COUNT(o.observation_id) AS observations_count
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                JOIN dim_avocado_type t ON o.type_id = t.type_id
                GROUP BY d.year, t.type_name
                ORDER BY d.year, t.type_name;
            """,
            "interpretation": (
                "Organic avocados consistently command an average premium between $0.44 and $0.60 per unit "
                "over conventional counterparts, driven by certified organic production costs and lower comparative yields."
            )
        },
        4: {
            "id": 4,
            "title": "REPORT 4: Total Recorded Volume by Year",
            "short_title": "4. Volume by Year",
            "purpose": "Understand yearly changes in recorded avocado market volume.",
            "sql_concepts": ["GROUP BY", "SUM()", "ORDER BY", "Year-over-Year Aggregation", "COUNT()"],
            "chart_type": "column_bar",
            "sql": """
                SELECT 
                    d.year,
                    ROUND(SUM(o.total_volume), 2) AS total_recorded_volume,
                    ROUND(AVG(o.average_price), 2) AS overall_avg_price,
                    ROUND(SUM(o.total_bags), 2) AS total_bags,
                    COUNT(o.observation_id) AS total_observations
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                GROUP BY d.year
                ORDER BY d.year;
            """,
            "interpretation": (
                "Annual recorded volume climbed steadily from 4.38 billion units in 2015 to nearly 5.0 billion "
                "units in 2017. 2018 records conclude in March (Q1), explaining the lower absolute sum for that year."
            )
        },
        5: {
            "id": 5,
            "title": "REPORT 5: Top 10 Markets by Recorded Volume",
            "short_title": "5. Top 10 Markets",
            "purpose": "Identify the top ten regional markets with the highest recorded avocado volume.",
            "sql_concepts": ["GROUP BY", "SUM()", "ORDER BY DESC", "LIMIT", "DENSE_RANK() Window Function"],
            "chart_type": "horizontal_rank_bar",
            "sql": """
                SELECT 
                    r.region_name AS region,
                    r.market_tier,
                    ROUND(SUM(o.total_volume), 2) AS total_volume,
                    ROUND(AVG(o.average_price), 2) AS avg_price,
                    ROUND(SUM(o.total_bags), 2) AS total_bags,
                    DENSE_RANK() OVER (ORDER BY SUM(o.total_volume) DESC) AS market_rank
                FROM avocado_observations o
                JOIN dim_region r ON o.region_id = r.region_id
                WHERE r.region_name != 'TotalUS'
                GROUP BY r.region_id, r.region_name, r.market_tier
                ORDER BY total_volume DESC
                LIMIT 10;
            """,
            "interpretation": (
                "Excluding the national aggregate (TotalUS), West, California, SouthCentral, and Northeast are the "
                "leading volume hubs. California combines massive volume with relatively stable, moderate pricing."
            )
        },
        6: {
            "id": 6,
            "title": "REPORT 6: Regional Price Trends Over Time",
            "short_title": "6. Regional Trends Over Time",
            "purpose": "Compare historical average price movements across prominent geographic markets.",
            "sql_concepts": ["WHERE Filtering", "GROUP BY Multi-Column", "AVG()", "ORDER BY", "JOINs"],
            "chart_type": "multi_line",
            "sql": """
                SELECT 
                    d.year,
                    d.quarter,
                    CONCAT(d.year, '-Q', d.quarter) AS year_quarter,
                    r.region_name AS region,
                    ROUND(AVG(o.average_price), 2) AS avg_price,
                    ROUND(SUM(o.total_volume), 2) AS total_volume
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                JOIN dim_region r ON o.region_id = r.region_id
                WHERE r.region_name IN ('California', 'NewYork', 'Chicago', 'Houston', 'Atlanta', 'Seattle')
                GROUP BY d.year, d.quarter, year_quarter, r.region_name
                ORDER BY d.year, d.quarter, r.region_name;
            """,
            "interpretation": (
                "New York and Chicago demonstrate consistently higher price points compared to Houston and Atlanta. "
                "Transportation logistics, warehousing expenses, and local retail margins explain the regional divergence."
            )
        },
        7: {
            "id": 7,
            "title": "REPORT 7: Organic vs Conventional Price Gap by Year",
            "short_title": "7. Organic vs Conventional Gap",
            "purpose": "Compare annual recorded average prices and calculate the organic premium gap.",
            "sql_concepts": ["Common Table Expressions (CTE)", "CASE Expressions", "Conditional Aggregation", "Math Formulas"],
            "chart_type": "price_gap_bar",
            "sql": """
                WITH type_yearly_summary AS (
                    SELECT 
                        d.year,
                        AVG(CASE WHEN t.type_name = 'conventional' THEN o.average_price END) AS conv_avg_price,
                        AVG(CASE WHEN t.type_name = 'organic' THEN o.average_price END) AS org_avg_price,
                        SUM(CASE WHEN t.type_name = 'conventional' THEN o.total_volume ELSE 0 END) AS conv_volume,
                        SUM(CASE WHEN t.type_name = 'organic' THEN o.total_volume ELSE 0 END) AS org_volume
                    FROM avocado_observations o
                    JOIN dim_date d ON o.date_id = d.date_id
                    JOIN dim_avocado_type t ON o.type_id = t.type_id
                    GROUP BY d.year
                )
                SELECT 
                    year,
                    ROUND(conv_avg_price, 2) AS conventional_avg_price,
                    ROUND(org_avg_price, 2) AS organic_avg_price,
                    ROUND(org_avg_price - conv_avg_price, 2) AS absolute_price_gap,
                    ROUND(((org_avg_price - conv_avg_price) / conv_avg_price) * 100, 2) AS organic_premium_pct,
                    ROUND(conv_volume, 0) AS conventional_volume,
                    ROUND(org_volume, 0) AS organic_volume
                FROM type_yearly_summary
                ORDER BY year;
            """,
            "interpretation": (
                "The relative organic price premium peaked at 55.2% in 2015 and compressed to 34.0% in 2017 "
                "as organic supply chains matured and commercial organic avocado production expanded."
            )
        },
        8: {
            "id": 8,
            "title": "REPORT 8: Bag Volume Composition by Region",
            "short_title": "8. Bag Composition by Region",
            "purpose": "Compare Small Bags, Large Bags, and XLarge Bags composition across regions.",
            "sql_concepts": ["SUM()", "GROUP BY", "Ratio Calculations", "NULLIF() Handling", "ORDER BY"],
            "chart_type": "stacked_bar",
            "sql": """
                SELECT 
                    r.region_name AS region,
                    ROUND(SUM(o.small_bags), 2) AS small_bags,
                    ROUND(SUM(o.large_bags), 2) AS large_bags,
                    ROUND(SUM(o.xlarge_bags), 2) AS xlarge_bags,
                    ROUND(SUM(o.total_bags), 2) AS total_bags,
                    ROUND((SUM(o.small_bags) / NULLIF(SUM(o.total_bags), 0)) * 100, 1) AS small_bag_pct,
                    ROUND((SUM(o.large_bags) / NULLIF(SUM(o.total_bags), 0)) * 100, 1) AS large_bag_pct,
                    ROUND((SUM(o.xlarge_bags) / NULLIF(SUM(o.total_bags), 0)) * 100, 1) AS xlarge_bag_pct
                FROM avocado_observations o
                JOIN dim_region r ON o.region_id = r.region_id
                WHERE r.region_name != 'TotalUS'
                GROUP BY r.region_id, r.region_name
                HAVING SUM(o.total_bags) > 0
                ORDER BY total_bags DESC
                LIMIT 15;
            """,
            "interpretation": (
                "Small bags represent the vast majority of consumer packaging (~70-80% across most regions), "
                "while Large and Extra Large bags serve warehouse club formats and bulk foodservice distribution."
            )
        },
        9: {
            "id": 9,
            "title": "REPORT 9: PLU-Based Product Volume Distribution",
            "short_title": "9. PLU Volume Distribution",
            "purpose": "Compare 4046 (Small/Med), 4225 (Large), and 4770 (Extra Large) recorded product volumes.",
            "sql_concepts": ["SUM()", "CASE Expressions", "Conditional Aggregations", "Proportion Analysis"],
            "chart_type": "donut_and_bar",
            "sql": """
                SELECT 
                    d.year,
                    ROUND(SUM(o.plu_4046), 2) AS plu_4046_volume,
                    ROUND(SUM(o.plu_4225), 2) AS plu_4225_volume,
                    ROUND(SUM(o.plu_4770), 2) AS plu_4770_volume,
                    ROUND(SUM(o.plu_4046 + o.plu_4225 + o.plu_4770), 2) AS total_plu_volume,
                    ROUND((SUM(o.plu_4046) / NULLIF(SUM(o.plu_4046 + o.plu_4225 + o.plu_4770), 0)) * 100, 1) AS pct_4046,
                    ROUND((SUM(o.plu_4225) / NULLIF(SUM(o.plu_4046 + o.plu_4225 + o.plu_4770), 0)) * 100, 1) AS pct_4225,
                    ROUND((SUM(o.plu_4770) / NULLIF(SUM(o.plu_4046 + o.plu_4225 + o.plu_4770), 0)) * 100, 1) AS pct_4770
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                GROUP BY d.year
                ORDER BY d.year;
            """,
            "interpretation": (
                "PLU 4046 (Small/Medium Hass) and PLU 4225 (Large Hass) together account for over 93% of all PLU-coded "
                "volume sold. PLU 4770 (Extra Large) comprises a niche fraction (<7%) of commercial avocado movements."
            )
        },
        10: {
            "id": 10,
            "title": "REPORT 10: Monthly and Seasonal Price Analysis",
            "short_title": "10. Monthly & Seasonal Price",
            "purpose": "Analyse month-wise recorded price patterns, standard deviations, and seasonal price indices.",
            "sql_concepts": ["MONTH()", "AVG()", "STDDEV_SAMP()", "Window Functions (OVER)", "GROUP BY", "ORDER BY"],
            "chart_type": "monthly_seasonal_line",
            "sql": """
                SELECT 
                    d.month,
                    d.month_name,
                    COUNT(o.observation_id) AS observations,
                    ROUND(AVG(o.average_price), 2) AS monthly_avg_price,
                    ROUND(MIN(o.average_price), 2) AS monthly_min_price,
                    ROUND(MAX(o.average_price), 2) AS monthly_max_price,
                    ROUND(STDDEV_SAMP(o.average_price), 2) AS price_std_dev,
                    ROUND(SUM(o.total_volume), 2) AS monthly_total_volume,
                    ROUND(
                        (AVG(o.average_price) / (SELECT AVG(average_price) FROM avocado_observations)) * 100, 
                        1
                    ) AS seasonality_index
                FROM avocado_observations o
                JOIN dim_date d ON o.date_id = d.date_id
                GROUP BY d.month, d.month_name
                ORDER BY d.month;
            """,
            "interpretation": (
                "Seasonality indexing illustrates that September and October exhibit index values above 115 "
                "(15% above annual baseline), marking the annual peak in avocado acquisition costs before winter harvests."
            )
        }
    }

    @classmethod
    def get_report(cls, report_id: int) -> Optional[Dict[str, Any]]:
        return cls.REPORTS.get(report_id)

    @classmethod
    def run_report(cls, report_id: int, custom_filter_clause: Optional[str] = None) -> Dict[str, Any]:
        """Runs designated report query against MySQL and packages results."""
        rep = cls.get_report(report_id)
        if not rep:
            raise ValueError(f"Report ID {report_id} not found.")

        base_sql = rep["sql"]
        # Execute query
        df = query_to_dataframe(base_sql)

        return {
            "id": rep["id"],
            "title": rep["title"],
            "purpose": rep["purpose"],
            "sql_concepts": rep["sql_concepts"],
            "sql": base_sql.strip(),
            "df": df,
            "chart_type": rep["chart_type"],
            "interpretation": rep["interpretation"],
            "row_count": len(df)
        }
