# 📊 Orders Analytics Dashboard

A **Streamlit-based analytics dashboard** with **MySQL database** for real-time monitoring and visualization of orders across multiple channels.

---

## 🎯 Quick Start

```bash
# Start everything with one command
bash start.sh

# Access dashboard at: http://localhost:8501
```

---

## 📁 Project Structure

```
orders-dashboard/
├── src/                         # Source code
│   ├── dashboard_mysql.py       # Main Streamlit dashboard
│   ├── csv_insert.py            # CSV data insertion utility
│   ├── mysql_connector.py       # MySQL connection
│   ├── init_database.py         # Database initialization
│   └── ...
├── data/                        # Sample CSV files
│   ├── channels.csv
│   ├── orders.csv
│   └── items.csv
├── tests/                       # Unit tests
├── requirement.txt              # Python dependencies
├── start.sh                     # Quick start script
└── README.md                    # This file
```

---

## 🛠️ Common Commands

### **Start Dashboard**
```bash
# Quick start (recommended)
bash start.sh

# Manual start (if start.sh fails)
cd src
python3 -m streamlit run dashboard_mysql.py
```

### **Database Management**

```bash
# Initialize database (first time only)
cd src
python3 init_database.py

# Insert CSV data (without clearing existing data)
cd src
python3 csv_insert.py ../data/orders.csv orders --password ""
python3 csv_insert.py ../data/channels.csv channels --password ""
python3 csv_insert.py ../data/items.csv items --password ""

# With custom credentials
python3 csv_insert.py <csv_file> <table> \
  --host localhost \
  --user root \
  --password "" \
  --database orders_dashboard
```

### **Testing**

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/test_dataloader.py -v
```

### **Dependencies**

```bash
# Install dependencies
pip install -r requirement.txt

# Update all packages
pip install --upgrade -r requirement.txt
```

---

## 📊 Dashboard Features

### Filters
- **Channels**: Web, App, etc.
- **Status**: Completed, Pending, etc.
- **Price Range**: Min to Max values

### KPI Metrics
- **Orders**: Total order count (with thousand separator)
- **Completed**: Percentage of completed orders
- **Revenue**: Total monetary value (formatted with decimals)
- **Avg Value**: Average order value (formatted with decimals)

### Visualizations
- **Bar Chart**: Orders by Channel
- **Pie Chart**: Orders by Status
- **Data Table**: All orders with scroll

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| `channels` | Sales channels (Web, App) |
| `orders` | Main orders with totals |
| `items` | Order line items |
| `data_import_log` | Import audit trail |

---

## 💾 CSV Data Format

**channels.csv:**
```
channel_id,channel_name
1,Web
2,App
```

**orders.csv:**
```
order_id,channel_id,order_date,status,updated_at
ORD001,1,2024-01-01,completed,2024-01-01 12:00:00
ORD002,2,2024-01-02,pending,2024-01-02 14:30:00
```

**items.csv:**
```
order_id,sku,quantity,unit_price
ORD001,SKU001,2,75.50
ORD001,SKU002,1,50.00
```

---

## 🔧 Core Modules

| Module | Purpose |
|--------|---------|
| `dashboard_mysql.py` | Main Streamlit application (~293 lines) |
| `csv_insert.py` | CLI utility for CSV data insertion (~240 lines) |
| `mysql_connector.py` | MySQL connection and query handler |
| `init_database.py` | One-time database setup |
| `mysql_data_loader.py` | Data loading from CSV files |
| `kpi_analyzer.py` | KPI calculations |
| `database_schema.py` | Schema creation |

---

## 🧪 Testing

All tests pass: **12/12 ✅**

```bash
# Run tests (set PYTHONPATH if needed)
PYTHONPATH=src python3 -m pytest tests/ -v
```

Test coverage:
- DataLoader: 3 tests
- DataWarehouse: 3 tests
- KPI Analyzer: 4 tests
- Report Generator: 2 tests

---

## 📦 Dependencies

**Core:**
- `streamlit>=1.20.0` - Dashboard framework
- `pandas>=1.3.0` - Data manipulation
- `altair>=5.0.0` - Charts and visualization
- `mysql-connector-python` - MySQL client

**Testing:**
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reports

See `requirement.txt` for full list.

---

## ⚙️ Configuration

**Default MySQL Credentials:**
- Host: `localhost`
- User: `root`
- Password: (empty)
- Database: `orders_dashboard`

To change credentials, pass arguments to commands:
```bash
python3 csv_insert.py file.csv table --host myhost --user myuser --password mypass
```

---

## 📝 Key Features

- ✅ **Loads all data from database** (~22,000+ orders)
- ✅ **No data loss**: CSV insertion skips duplicates, updates existing records
- ✅ **Single-screen dashboard**: No scrolling needed
- ✅ **Real-time filtering**: Charts, KPIs, and table update immediately
- ✅ **Refresh button**: Click "�� Refresh Data" to reload from database
- ✅ **Formatted numbers**: Thousand separators and currency formatting

---

## 🚀 Deployment

**Local Development:**
```bash
bash start.sh
```

**Production (Streamlit Cloud):**
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy via cloud console

---

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| MySQL connection error | Check MySQL is running: `brew services list` |
| Import errors | Run: `pip install -r requirement.txt` |
| Dashboard won't start | Ensure port 8501 is available, or run: `streamlit run src/dashboard_mysql.py --server.port 8502` |
| Tests fail | Run with PYTHONPATH: `PYTHONPATH=src pytest -v` |
| No data showing | Click "🔄 Refresh Data" button or ensure MySQL has data |
