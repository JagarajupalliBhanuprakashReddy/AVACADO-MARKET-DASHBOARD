# AVACADO-MARKET-DASHBOARD
## Agricultural Market Pricing & Sales Dashboard
### Enterprise Database-Driven Market Intelligence & Pricing Analytics Platform

---

## 🌟 Overview

The **Agricultural Market Pricing & Sales Dashboard** is an enterprise-grade, database-driven web application designed to analyze historical agricultural commodity prices, volume trends, regional divergences, and variety premiums.

Built using the official **Avocado Prices** dataset from the Hass Avocado Board (HAB), the system integrates a normalized **MySQL 8.x dimensional star schema (3NF)** with an interactive **Streamlit** user interface, **Plotly** visualizations, and a local **Ollama** natural-language AI SQL assistant.

---

## 🚀 Key Features

1. **Overview Executive Dashboard:** Dynamic KPI cards and multi-dimensional charts powered by live MySQL aggregation.
2. **Historical Price Search Engine:** Search previous years' prices in ordinary English or via advanced time, market, product, and price filters.
3. **Historical Year Comparison Engine:** Compare two or more calendar baselines with exact percentage change math:
   $$\Delta P\% = \left(\frac{P_{\text{new}} - P_{\text{old}}}{P_{\text{old}}}\right) \times 100$$
4. **Market Price Analytics:** Price distributions, rolling moving averages, and volatility tracking.
5. **Regional Market Analysis:** Rank and compare 54 metropolitan and regional markets using `DENSE_RANK()`.
6. **Product Type Analysis:** Evaluate Organic vs Conventional price premiums and market shares.
7. **Volume & Supply Analysis:** Slicing recorded physical shipments across PLU size codes (4046, 4225, 4770) and bag formats.
8. **Ten Mandatory SQL Reports:** Demonstrating Window Functions, CTEs, Date Manipulations, and Joins with Plotly charts, data tables, and CSV/PDF exports.
9. **Interactive Data Explorer:** Server-side paginated inspector using SQL `LIMIT` and `OFFSET`.
10. **Database Management & CRUD:** Inspect tables, column schemas, and indexes; perform validated `INSERT`, `READ`, `UPDATE`, and `DELETE` operations.
11. **Dataset Import & Export Center:** Clean and validate raw CSVs, trigger reproducible dimensional ETL, and generate ReportLab PDF reports.
12. **AI-Powered Natural Language SQL Assistant:** Local Ollama integration with schema-aware SQL generation and autonomous fallback.

---

## 🛠️ Technology Stack

- **Frontend & App Framework:** Python, Streamlit, Custom CSS
- **Data & Computation:** Pandas, NumPy
- **Database Engine:** MySQL 8.x, Connection Pooling, `mysql-connector-python`, SQLAlchemy
- **Data Visualization:** Plotly Express & Plotly Graph Objects
- **AI / LLM Service:** Ollama (`llama3.2` on `http://localhost:11434`)
- **Document Generation:** ReportLab 5.x (PDFs), Openpyxl (Excel)
- **Testing Framework:** Pytest (19/19 passing tests)

---

## 📋 Quick Setup & Startup

1. **Verify Database Configuration:**
   Copy `.env.example` to `.env` and configure your MySQL credentials:
   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=agricultural_market_db
   DB_USER=root
   DB_PASSWORD=admin
   ```

2. **Run Application:**
   ```powershell
   C:\venvs\agricultural_market_env\Scripts\python.exe -m streamlit run app.py
   ```

3. **Run Test Suite:**
   ```powershell
   C:\venvs\agricultural_market_env\Scripts\python.exe -m pytest tests/ -v
   ```

---

## 📁 Project Architecture

```
DBMS/
├── app.py                      # Main application entry point & page router
├── requirements.txt            # Python dependencies
├── .env                        # Local environment credentials
├── .env.example                # Environment configuration template
├── README.md                   # Project overview & startup instructions
├── config/
│   └── database_config.py      # Environment & database configuration
├── database/
│   ├── connection.py           # Connection pool & query execution engine
│   ├── schema.sql              # Normalized 3NF star schema DDL
│   ├── views.sql               # Analytical database views
│   └── indexes.sql             # Performance indexes DDL
├── data/
│   ├── raw/avocado.csv         # Official Hass Avocado Board dataset
│   └── processed/
├── services/
│   ├── data_cleaning.py        # Data hygiene & constraint validation
│   ├── dataset_import.py       # Reproducible ETL to star schema
│   ├── analytics_service.py    # Analytical queries & KPI calculations
│   ├── historical_search_service.py # Natural language & comparison engine
│   ├── report_service.py       # Ten Core Analytical SQL Reports executor
│   ├── export_service.py       # CSV & ReportLab PDF generator
│   └── ai_sql_service.py       # Ollama AI & read-only SQL validator
├── components/
│   ├── header.py               # Enterprise header with status pills
│   ├── sidebar.py              # Navigation menu controller
│   ├── kpi_cards.py            # Responsive metric cards
│   ├── charts.py               # Plotly chart generation factory
│   ├── filters.py              # Global multi-dimensional filters
│   └── search_bar.py           # Historical price search bar
├── pages/                      # 12 integrated application pages
├── tests/                      # Pytest automated test suite
└── docs/                       # Complete system documentation
```
