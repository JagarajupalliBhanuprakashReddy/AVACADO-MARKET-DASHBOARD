"""AI-Powered Natural Language SQL Assistant Service.

Connects to local Ollama LLM with schema-aware prompt engineering, strict read-only
safety verification, query timeouts, and autonomous rule-based fallback when Ollama is offline.
"""

from __future__ import annotations
import re
import requests
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from config.database_config import AppConfig
from database.connection import query_to_dataframe, execute_scalar
from services.historical_search_service import HistoricalSearchService


class AISQLService:
    """Natural Language to SQL translator with Ollama integration and guardrails."""

    SYSTEM_PROMPT = """You are an expert MySQL Database Architect and Data Analyst specializing in agricultural market datasets.
Generate ONLY a valid MySQL SELECT query based on the schema below.
DO NOT wrap in markdown fences or write any preamble or explanations. Return ONLY the raw SQL query.

DATABASE SCHEMA:
- Table avocado_observations (observation_id, date_id, region_id, type_id, average_price, total_volume, total_bags, small_bags, large_bags, xlarge_bags, plu_4046, plu_4225, plu_4770)
- Table dim_date (date_id, full_date, day, month, month_name, quarter, year, week_number)
- Table dim_region (region_id, region_name, market_tier)
- Table dim_avocado_type (type_id, type_name, description)
- View vw_avocado_complete (observation_id, price_date, year, quarter, month, month_name, week_number, region, market_tier, avocado_type, average_price, total_volume, total_bags, small_bags, large_bags, xlarge_bags, plu_4046, plu_4225, plu_4770)

CONSTRAINTS:
1. ONLY generate SELECT queries. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
2. Join avocado_observations with dim_date, dim_region, dim_avocado_type, OR use vw_avocado_complete.
3. Filter out 'TotalUS' from region queries unless the user specifically asks for national or TotalUS figures.
4. The dataset covers historical years 2015, 2016, 2017, and 2018 (from 2015-01-04 to 2018-03-25).
5. Always round aggregated prices to 2 decimals using ROUND(..., 2).
6. Always append LIMIT 200 unless a specific LIMIT is requested.
"""

    FORBIDDEN_KEYWORDS = [
        r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b", r"\balter\b",
        r"\btruncate\b", r"\bcreate\b", r"\bgrant\b", r"\brevoke\b", r"\bcall\b",
        r"\bexec\b", r"\bexecute\b", r"\binto\s+outfile\b", r"\bload_file\b"
    ]

    @classmethod
    def check_ollama_status(cls) -> Dict[str, Any]:
        """Checks if local Ollama daemon is reachable."""
        try:
            resp = requests.get(f"{AppConfig.OLLAMA_HOST}/api/tags", timeout=2)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m.get("name") for m in models]
                return {
                    "available": True,
                    "host": AppConfig.OLLAMA_HOST,
                    "models": model_names,
                    "default_model": AppConfig.OLLAMA_MODEL,
                }
        except Exception:
            pass
        return {
            "available": False,
            "host": AppConfig.OLLAMA_HOST,
            "models": [],
            "default_model": AppConfig.OLLAMA_MODEL,
        }

    @classmethod
    def sanitize_and_validate_sql(cls, sql_query: str) -> Tuple[bool, str]:
        """Enforces read-only safety, rejecting destructive SQL and injection vectors."""
        cleaned = sql_query.strip().strip(";").strip()
        # Remove markdown code blocks if generated
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:sql)?\n?", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\n?```$", "", cleaned)
        cleaned = cleaned.strip()

        # Reject empty
        if not cleaned:
            return False, "Empty query generated."

        # Ensure query begins with SELECT or WITH (for CTEs)
        lower_q = cleaned.lower()
        if not (lower_q.startswith("select") or lower_q.startswith("with")):
            return False, "Security Violation: Only SELECT and WITH (CTE) queries are authorized."

        # Scan for forbidden destructive operations
        for pattern in cls.FORBIDDEN_KEYWORDS:
            if re.search(pattern, lower_q):
                return False, f"Security Violation: Prohibited database keyword detected ({pattern})."

        # Check for multiple statements (semicolon chaining)
        if ";" in cleaned:
            parts = [p.strip() for p in cleaned.split(";") if p.strip()]
            if len(parts) > 1:
                return False, "Security Violation: Multiple chained SQL statements are disallowed."
            cleaned = parts[0]

        # Enforce safety limit if not present
        if "limit" not in lower_q:
            cleaned += " LIMIT 200"

        return True, cleaned

    @classmethod
    def query_ollama(cls, user_question: str) -> Optional[str]:
        """Calls local Ollama API to generate SQL from user question."""
        try:
            payload = {
                "model": AppConfig.OLLAMA_MODEL,
                "prompt": f"{cls.SYSTEM_PROMPT}\n\nUser Question: {user_question}\nSQL Query:",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 256
                }
            }
            resp = requests.post(
                f"{AppConfig.OLLAMA_HOST}/api/generate",
                json=payload,
                timeout=AppConfig.OLLAMA_TIMEOUT
            )
            if resp.status_code == 200:
                raw_sql = resp.json().get("response", "").strip()
                return raw_sql
        except Exception:
            return None
        return None

    @classmethod
    def process_natural_language_query(cls, user_question: str) -> Dict[str, Any]:
        """End-to-end pipeline: NL -> Ollama/Fallback -> Safety Validation -> MySQL -> Interpretation."""
        query_text = user_question.strip()
        if not query_text:
            return {
                "success": False,
                "error": "Please enter a question to ask the database.",
            }

        ollama_status = cls.check_ollama_status()
        generated_sql: Optional[str] = None
        source = "Ollama Local AI"

        if ollama_status["available"]:
            generated_sql = cls.query_ollama(query_text)

        if not generated_sql:
            # Fallback to local intelligent NL-to-SQL parser
            source = "Embedded Rule-Based SQL Engine (Ollama Offline / Standby)"
            nl_parsed = HistoricalSearchService.parse_natural_language_query(query_text)
            if nl_parsed.get("coverage_warning"):
                return {
                    "success": True,
                    "source": source,
                    "sql": nl_parsed["sql"],
                    "df": pd.DataFrame(),
                    "explanation": nl_parsed["explanation"],
                    "chart_type": "none",
                    "coverage_warning": True,
                }
            generated_sql = nl_parsed.get("sql")

        if not generated_sql:
            return {
                "success": False,
                "error": "Could not synthesize a valid SQL query for this question.",
            }

        # Security check
        is_safe, validated_sql = cls.sanitize_and_validate_sql(generated_sql)
        if not is_safe:
            return {
                "success": False,
                "error": validated_sql,
                "attempted_sql": generated_sql
            }

        # Live MySQL Execution
        try:
            df = query_to_dataframe(validated_sql)
            row_count = len(df)

            # Generate smart plain-English interpretation
            explanation = cls._generate_explanation(query_text, df, validated_sql)
            chart_type = cls._recommend_chart(df)

            return {
                "success": True,
                "source": source,
                "sql": validated_sql,
                "df": df,
                "row_count": row_count,
                "explanation": explanation,
                "chart_type": chart_type,
                "ollama_available": ollama_status["available"]
            }
        except Exception as e:
            return {
                "success": False,
                "sql": validated_sql,
                "error": f"Database Execution Failed: {str(e)}",
                "source": source,
            }

    @classmethod
    def _recommend_chart(cls, df: pd.DataFrame) -> str:
        """Determines best Plotly visualization based on dataframe shape and column names."""
        if df.empty or len(df) < 1:
            return "table"
        cols = [c.lower() for c in df.columns]

        if "price_date" in cols or "date" in cols or "week_start_date" in cols:
            return "line"
        if "region" in cols and any("volume" in c or "price" in c for c in cols):
            return "bar"
        if "year" in cols and len(df) <= 10:
            return "bar"
        if "month" in cols or "month_name" in cols:
            return "bar"
        if len(cols) == 2 and any("volume" in c for c in cols):
            return "pie"
        return "bar"

    @classmethod
    def _generate_explanation(cls, question: str, df: pd.DataFrame, sql: str) -> str:
        """Produces clear, professional business interpretation of query results."""
        if df.empty:
            return "The database query executed successfully, but returned zero matching records for the specified filter criteria."

        count = len(df)
        cols = df.columns.tolist()

        num_cols = df.select_dtypes(include=["number"]).columns.tolist()
        summary_points = []

        for col in num_cols[:2]:
            mean_val = df[col].mean()
            max_val = df[col].max()
            summary_points.append(f"average {col}: **{mean_val:,.2f}** (maximum: **{max_val:,.2f}**)")

        summary_str = "; ".join(summary_points)
        explanation = (
            f"Successfully retrieved **{count:,}** record{'s' if count != 1 else ''} from MySQL. "
        )
        if summary_str:
            explanation += f"Key metrics: {summary_str}. "

        return explanation
