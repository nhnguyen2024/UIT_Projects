#!/usr/bin/env python3
"""
Initialize MySQL Database: Run this script to set up the database schema
Usage: python -m src.init_database
       OR from src/: python init_database.py
"""

from mysql_connector import MySQLConnector
from database_schema import DatabaseSchema
from mysql_data_loader import MySQLDataLoader
import os


def init_database(host="localhost", user="root", password="root", database="orders_dashboard"):
    """Initialize the MySQL database"""
    print("=" * 60)
    print("Initializing Orders Dashboard MySQL Database")
    print("=" * 60)
    
    # Step 1: Create connector (without specifying database first)
    print("\n[1] Connecting to MySQL...")
    connector = MySQLConnector(host, user, password, "mysql")  # Connect to 'mysql' DB first
    
    if connector.connect():
        print("✓ Connected to MySQL")
    else:
        print("✗ Failed to connect to MySQL")
        print("Please check your credentials:")
        print(f"  Host: {host}")
        print(f"  User: {user}")
        return False
    
    # Step 1.5: Drop existing database to start fresh
    print("\n[1.5] Dropping existing database (if any)...")
    try:
        connector.execute_query(f"DROP DATABASE IF EXISTS {database}")
        print(f"✓ Dropped existing database (if it existed)")
    except Exception as e:
        print(f"⚠ Could not drop database: {e}")
    
    # Step 2: Create database
    print("\n[2] Creating database...")
    if DatabaseSchema.create_database(connector):
        print(f"✓ Database '{database}' created")
    
    # Step 3: Create schema
    print("\n[3] Creating tables...")
    # Switch to the new database by executing USE statement
    connector.execute_query(f"USE {database}")
    if DatabaseSchema.create_schema(connector):
        print("✓ All tables created successfully")
    else:
        print("✗ Failed to create tables")
        connector.disconnect()
        return False
    
    # Step 4: Create views
    print("\n[4] Creating views...")
    if DatabaseSchema.create_views(connector):
        print("✓ Views created successfully")
    
    # Step 5: Load initial data from CSV
    print("\n[5] Loading initial data from CSV...")
    loader = MySQLDataLoader(host, user, password, database)
    loader.connector = connector  # Reuse connection
    
    csv_files = {
        'data/channels.csv': 'channels',
        'data/items.csv': 'items',
        'data/orders_app.csv': 'orders',
        'data/orders_web.csv': 'orders'
    }
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to project root
    
    for csv_file, file_type in csv_files.items():
        csv_path = os.path.join(base_dir, csv_file)
        if os.path.exists(csv_path):
            print(f"\n  Loading {csv_file}...")
            try:
                df = loader.load_csv_to_dataframe(csv_path)
                if not df.empty:
                    if file_type == 'channels':
                        success, message = loader.load_channels(df, csv_file)
                    elif file_type == 'orders':
                        success, message = loader.load_orders(df, csv_file)
                    elif file_type == 'items':
                        success, message = loader.load_items(df, csv_file)
                    
                    if success:
                        print(f"    ✓ {message}")
                    else:
                        print(f"    ✗ {message}")
            except Exception as e:
                print(f"    ✗ Error: {e}")
        else:
            print(f"  ⚠ File not found: {csv_file}")
    
    # Step 6: Display statistics
    print("\n[6] Database Statistics:")
    stats = loader.get_table_stats()
    for table, count in stats.items():
        print(f"  {table}: {count} rows")
    
    connector.disconnect()
    
    print("\n" + "=" * 60)
    print("✓ Database initialization complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    init_database(host="localhost", user="root", password="", database="orders_dashboard")
