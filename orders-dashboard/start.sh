#!/bin/bash
# Quick Start Script for Orders Dashboard with MySQL

echo "================================"
echo "Orders Dashboard - Quick Start"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check MySQL
echo "📋 Checking MySQL installation..."
if command -v mysql &> /dev/null; then
    MYSQL_VERSION=$(mysql --version)
    echo -e "${GREEN}✓ MySQL installed: $MYSQL_VERSION${NC}"
else
    echo -e "${RED}✗ MySQL not found. Please install MySQL first.${NC}"
    echo "  macOS: brew install mysql-community-server"
    exit 1
fi

# Check MySQL is running
echo ""
echo "🔌 Checking if MySQL is running..."
if mysql -u root -e "SELECT 1" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ MySQL is running${NC}"
else
    echo -e "${YELLOW}⚠ MySQL might not be running${NC}"
    echo "  Start MySQL: brew services start mysql-community-server"
    echo "  or: mysql.server start"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirement.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Initialize database
echo ""
echo "🗄️  Initializing database..."
if python3 src/init_database.py; then
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${RED}✗ Database initialization failed${NC}"
    exit 1
fi

# Launch dashboard
echo ""
echo "================================"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "================================"
echo ""
echo "📊 Launching dashboard..."
echo "    Open browser: http://localhost:8501"
echo "    Press Ctrl+C to stop"
echo ""
echo "💡 Tip: To insert CSV data into existing tables without clearing:"
echo "    python3 src/csv_insert.py data/<file>.csv <table_name> --password \"\""
echo ""

python3 -m streamlit run src/dashboard_mysql.py