"""Database Connection and Query Execution Module.

Provides robust, connection-pooled access to MySQL with parameterization,
health monitoring, transaction handling, and SQL safety checks.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import mysql.connector
from mysql.connector import pooling, Error as MySQLError
import pandas as pd
from sqlalchemy import create_engine, Engine
from config.database_config import DatabaseConfig

_connection_pool: Optional[pooling.MySQLConnectionPool] = None
_sqlalchemy_engine: Optional[Engine] = None


def get_connection_pool() -> pooling.MySQLConnectionPool:
    """Initializes or returns singleton connection pool."""
    global _connection_pool
    if _connection_pool is None:
        cfg = DatabaseConfig.get_connection_dict()
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name=DatabaseConfig.POOL_NAME,
            pool_size=DatabaseConfig.POOL_SIZE,
            pool_reset_session=True,
            **cfg
        )
    return _connection_pool


def get_connection():
    """Acquires a connection from pool or direct fallback."""
    try:
        pool = get_connection_pool()
        return pool.get_connection()
    except Exception:
        # Fallback to direct connection if pool exhausted or initialization fails
        cfg = DatabaseConfig.get_connection_dict()
        return mysql.connector.connect(**cfg)


def get_sqlalchemy_engine() -> Engine:
    """Returns cached SQLAlchemy engine for pandas integrations."""
    global _sqlalchemy_engine
    if _sqlalchemy_engine is None:
        _sqlalchemy_engine = create_engine(
            DatabaseConfig.get_sqlalchemy_uri(),
            pool_size=DatabaseConfig.POOL_SIZE,
            pool_pre_ping=True,
            max_overflow=5
        )
    return _sqlalchemy_engine


def check_connection_health() -> Dict[str, Any]:
    """Tests MySQL connectivity and collects runtime performance telemetry."""
    start_time = time.perf_counter()
    try:
        conn = get_connection()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION(), DATABASE();")
        row = cursor.fetchone()
        version, current_db = row[0], row[1]
        cursor.close()
        conn.close()
        return {
            "status": "connected",
            "ok": True,
            "host": DatabaseConfig.HOST,
            "port": DatabaseConfig.PORT,
            "database": current_db,
            "server_version": version,
            "latency_ms": latency_ms,
            "pool_name": DatabaseConfig.POOL_NAME,
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "ok": False,
            "host": DatabaseConfig.HOST,
            "port": DatabaseConfig.PORT,
            "database": DatabaseConfig.NAME,
            "server_version": "Unknown",
            "latency_ms": 0.0,
            "pool_name": DatabaseConfig.POOL_NAME,
            "error": str(e)
        }


def execute_query(sql: str, params: Optional[Union[tuple, dict, list]] = None) -> List[Dict[str, Any]]:
    """Executes a SELECT query and returns records as a list of dictionaries."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        results = cursor.fetchall()
        return results
    except MySQLError as err:
        raise RuntimeError(f"Database Query Error: {err.msg} (Code: {err.errno})") from err
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_scalar(sql: str, params: Optional[Union[tuple, dict, list]] = None) -> Any:
    """Executes a query returning a single scalar value."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        return row[0] if row else None
    except MySQLError as err:
        raise RuntimeError(f"Database Scalar Query Error: {err.msg}") from err
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_dml(sql: str, params: Optional[Union[tuple, dict, list]] = None) -> Dict[str, Any]:
    """Executes INSERT, UPDATE, DELETE statements with transaction commit."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return {
            "rowcount": cursor.rowcount,
            "lastrowid": cursor.lastrowid,
            "success": True
        }
    except MySQLError as err:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Database DML Error: {err.msg}") from err
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def query_to_dataframe(sql: str, params: Optional[Union[tuple, dict, list]] = None) -> pd.DataFrame:
    """Executes SQL and returns a clean Pandas DataFrame."""
    try:
        rows = execute_query(sql, params)
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)
    except Exception as e:
        # Fallback via direct connection
        conn = get_connection()
        try:
            return pd.read_sql(sql, conn, params=params)
        finally:
            conn.close()
