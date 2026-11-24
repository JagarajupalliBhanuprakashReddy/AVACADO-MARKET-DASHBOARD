# User Manual & Operator Guide
## Agricultural Market Pricing & Sales Dashboard
**Enterprise Market Intelligence & Pricing Analytics Platform**

---

## 1. Quick Start & Execution

### 1.1 Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- MySQL Server 8.x running on port `3306` with database `agricultural_market_db`
- Recommended virtual environment: `C:\venvs\agricultural_market_env`

### 1.2 Environment Setup
Ensure your `.env` file in the project root contains your valid MySQL credentials:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=agricultural_market_db
DB_USER=root
DB_PASSWORD=admin
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 1.3 Launching the Application
Execute the following command in PowerShell:
```powershell
C:\venvs\agricultural_market_env\Scripts\python.exe -m streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

---

## 2. Navigation & Feature Walkthrough

### 2.1 Overview Dashboard
- Access dynamic global KPI cards: Total Records (18,249), Average Price ($1.41), Total Volume (15.5B units), Region Count (54), and Earliest/Latest observation dates.
- Use the **Dashboard Scope & Filters** expander to adjust calendar year, market territory, or product type.

### 2.2 Historical Price Search Engine
- **Main Search Bar:** Ask natural language questions such as *"Compare avocado prices in 2016 and 2017"* or *"Which region had the highest price in 2018?"*.
- **Quick Example Pills:** Click any of the 10 pre-loaded query buttons to instantly generate results, charts, and explanations.
- **Dedicated Year Comparison Engine:** Compare any two years (e.g. Year A: 2016 vs Year B: 2017) to calculate percentage price changes using the exact formula:
  $$\text{Price Delta (\%)} = \left(\frac{\text{Price}_{B} - \text{Price}_{A}}{\text{Price}_{A}}\right) \times 100$$
- **Temporal Boundary Notice:** Queries targeting years outside 2015-2018 (e.g. 2020) will display a helpful temporal boundary notice rather than fabricating data.

### 2.3 Market Price Analytics
- View price distribution histograms, weekly price trajectories with rolling 4-week moving averages, and month-by-month seasonality charts.

### 2.4 Regional Market Analysis
- Identify the Top 10 Highest-Priced and Lowest-Priced markets using MySQL `DENSE_RANK()`.
- Compare multiple selected regions across prices and volumes simultaneously.

### 2.5 Product Type Analysis
- Examine the Organic vs Conventional price gap and percentage premium over time.
- Review volume share and monthly seasonal spreads by variety.

### 2.6 Volume & Demand Analysis
- Analyze physical shipment volumes by Hass PLU size code (4046, 4225, 4770) and packaged bag sizes (Small, Large, XLarge).

### 2.7 Ten Mandatory SQL Reports
- Navigate through all 10 academic SQL reports.
- Each report displays:
  - Demonstrated SQL concepts (CTEs, Window Functions, Date Functions, Aggregations)
  - Full MySQL 8.x SQL query
  - Interactive Plotly visualization
  - Raw data table
  - Academic & business insights
  - Direct CSV and formal ReportLab PDF download buttons

### 2.8 Interactive Data Explorer
- Search and filter records with server-side SQL pagination (`LIMIT` and `OFFSET`), avoiding client-side memory overload.
- Sort by date, price, or volume in ascending or descending order.

### 2.9 Database Management & CRUD
- Inspect live database tables, row counts, column types, and indexes.
- Perform validated `INSERT`, `READ`, `UPDATE`, and `DELETE` operations on `avocado_prices` with strict safety confirmation checkboxes.

### 2.10 Dataset Import & Export Center
- Upload new or updated CSV datasets, validate schema constraints, check for nulls and duplicates.
- Execute full ETL into dimensional tables (`dim_date`, `dim_region`, `dim_avocado_type`, `avocado_observations`).
- Export records to CSV or formal academic PDF briefs rendered with ReportLab.

### 2.11 AI-Powered Natural Language SQL Assistant
- Enter plain-English questions to synthesize, validate, and execute read-only MySQL queries.
- Connected to local Ollama (`llama3.2`) with autonomous rule-based fallback when Ollama is offline.
- Enforces strict read-only security (blocks all `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`).
