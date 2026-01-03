"""
CSV Data Insertion Script
Insert or append CSV data to existing MySQL tables without clearing data
Usage: python csv_insert.py <csv_file_path> <table_name> [--host] [--user] [--password] [--database]
"""
import sys
import argparse
import pandas as pd
from mysql_connector import MySQLConnector


class CSVInserter:
    """Insert CSV data into MySQL database tables"""
    
    def __init__(self, host="localhost", user="root", password="root", database="orders_dashboard"):
        self.connector = MySQLConnector(host, user, password, database)
        self.connected = False
    
    def connect(self):
        """Connect to MySQL database"""
        if self.connector.connect():
            self.connected = True
            print("✅ Connected to MySQL database")
            return True
        else:
            print("❌ Failed to connect to MySQL database")
            return False
    
    def disconnect(self):
        """Disconnect from MySQL"""
        if self.connected:
            self.connector.disconnect()
            print("Disconnected from database")
    
    def insert_channels(self, df: pd.DataFrame, file_name: str = "channels.csv") -> tuple:
        """Append channels data (INSERT IGNORE to skip duplicates)"""
        try:
            print(f"\n📤 Inserting channels from {file_name}...")
            
            # Validate required columns
            required_cols = ['channel_id', 'channel_name']
            if not all(col in df.columns for col in required_cols):
                return False, f"Missing required columns: {required_cols}"
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['channel_id'], keep='last')
            
            # Prepare data
            data = [(int(row['channel_id']), row['channel_name']) 
                   for _, row in df.iterrows()]
            
            # Insert with ignore duplicates
            query = """
            INSERT IGNORE INTO channels (channel_id, channel_name) 
            VALUES (%s, %s)
            """
            success = self.connector.execute_many(query, data)
            
            if success:
                print(f"✅ Inserted {len(data)} channels")
                return True, f"Inserted {len(data)} channels"
            else:
                return False, "Failed to insert channels"
        except Exception as e:
            error_msg = f"Error inserting channels: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def insert_orders(self, df: pd.DataFrame, file_name: str = "orders.csv") -> tuple:
        """Append orders data (INSERT or UPDATE on duplicate)"""
        try:
            print(f"\n📤 Inserting orders from {file_name}...")
            
            # Validate required columns
            required_cols = ['order_id', 'channel_id', 'order_date', 'status']
            if not all(col in df.columns for col in required_cols):
                return False, f"Missing required columns: {required_cols}"
            
            # Remove duplicates based on order_id
            df = df.drop_duplicates(subset=['order_id'], keep='last')
            
            # Prepare data
            data = []
            for _, row in df.iterrows():
                data.append((
                    int(row['order_id']),
                    int(row['channel_id']),
                    row['order_date'],
                    row['status'],
                    row['updated_at'] if 'updated_at' in row else None
                ))
            
            # Insert or update
            query = """
            INSERT INTO orders (order_id, channel_id, order_date, status, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                channel_id = VALUES(channel_id),
                order_date = VALUES(order_date),
                status = VALUES(status),
                updated_at = VALUES(updated_at)
            """
            success = self.connector.execute_many(query, data)
            
            if success:
                print(f"✅ Inserted/Updated {len(data)} orders")
                return True, f"Inserted/Updated {len(data)} orders"
            else:
                return False, "Failed to insert orders"
        except Exception as e:
            error_msg = f"Error inserting orders: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def insert_items(self, df: pd.DataFrame, file_name: str = "items.csv") -> tuple:
        """Append items data"""
        try:
            print(f"\n📤 Inserting items from {file_name}...")
            
            # Validate required columns
            required_cols = ['order_id', 'sku', 'quantity', 'unit_price']
            if not all(col in df.columns for col in required_cols):
                return False, f"Missing required columns: {required_cols}"
            
            # Remove invalid rows
            df = df.dropna(subset=['order_id', 'quantity', 'unit_price'])
            
            # Prepare data
            data = []
            for _, row in df.iterrows():
                data.append((
                    int(row['order_id']),
                    row['sku'],
                    int(row['quantity']),
                    float(row['unit_price'])
                ))
            
            # Insert
            query = """
            INSERT INTO items (order_id, sku, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            """
            success = self.connector.execute_many(query, data)
            
            if success:
                print(f"✅ Inserted {len(data)} items")
                return True, f"Inserted {len(data)} items"
            else:
                return False, "Failed to insert items"
        except Exception as e:
            error_msg = f"Error inserting items: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def insert_data(self, csv_file: str, table_name: str) -> tuple:
        """Generic insert function - accepts any table name"""
        try:
            # Load CSV
            print(f"\n📂 Loading {csv_file}...")
            df = pd.read_csv(csv_file)
            print(f"✅ Loaded {len(df)} rows")
            
            # Normalize table name
            table_name = table_name.lower().strip()
            
            # Route to appropriate function
            if table_name == "channels":
                return self.insert_channels(df, csv_file)
            elif table_name == "orders":
                return self.insert_orders(df, csv_file)
            elif table_name == "items":
                return self.insert_items(df, csv_file)
            else:
                return False, f"Unsupported table: {table_name}. Supported: channels, orders, items"
        
        except FileNotFoundError:
            error_msg = f"File not found: {csv_file}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Insert CSV data into MySQL database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_insert.py data/orders.csv orders
  python csv_insert.py data/channels.csv channels --host localhost --user root
  python csv_insert.py data/items.csv items --database orders_dashboard
        """
    )
    
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("table", help="Table name (channels, orders, items)")
    parser.add_argument("--host", default="localhost", help="MySQL host (default: localhost)")
    parser.add_argument("--user", default="root", help="MySQL user (default: root)")
    parser.add_argument("--password", default="root", help="MySQL password (default: root)")
    parser.add_argument("--database", default="orders_dashboard", help="Database name (default: orders_dashboard)")
    
    args = parser.parse_args()
    
    # Create inserter
    inserter = CSVInserter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    # Connect
    if not inserter.connect():
        sys.exit(1)
    
    try:
        # Insert data
        success, message = inserter.insert_data(args.csv_file, args.table)
        
        if success:
            print(f"\n✅ SUCCESS: {message}")
            sys.exit(0)
        else:
            print(f"\n❌ FAILED: {message}")
            sys.exit(1)
    
    finally:
        inserter.disconnect()


if __name__ == "__main__":
    main()
