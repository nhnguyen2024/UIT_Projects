"""
MySQL DataLoader: Load CSV data into MySQL database
"""
import pandas as pd
import os
from datetime import datetime
import streamlit as st
from mysql_connector import MySQLConnector


class MySQLDataLoader:
    """Handle CSV file loading and MySQL database operations"""
    
    def __init__(self, 
                 host: str = "localhost",
                 user: str = "root",
                 password: str = "root",
                 database: str = "orders_dashboard"):
        self.connector = MySQLConnector(host, user, password, database)
        self.import_log = []
    
    def connect(self) -> bool:
        """Connect to MySQL"""
        return self.connector.connect()
    
    def disconnect(self):
        """Disconnect from MySQL"""
        self.connector.disconnect()
    
    def load_csv_to_dataframe(self, file_path: str) -> pd.DataFrame:
        """Load CSV file to DataFrame"""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    def load_channels(self, df: pd.DataFrame, file_name: str = "channels.csv") -> tuple:
        """Load channels data into MySQL"""
        try:
            # Clear existing channels
            self.connector.execute_query("DELETE FROM channels")
            
            # Prepare data
            data = [(int(row['channel_id']), row['channel_name']) 
                   for _, row in df.iterrows()]
            
            # Insert
            query = "INSERT INTO channels (channel_id, channel_name) VALUES (%s, %s)"
            success = self.connector.execute_many(query, data)
            
            if success:
                log_entry = {
                    "file_name": file_name,
                    "file_type": "channels",
                    "rows_imported": len(df),
                    "status": "success"
                }
                self._log_import(log_entry)
                return True, f"Loaded {len(df)} channels"
            else:
                return False, "Failed to insert channels"
        except Exception as e:
            return False, f"Error loading channels: {e}"
    
    def load_orders(self, df: pd.DataFrame, file_name: str = "orders.csv") -> tuple:
        """Load orders data into MySQL"""
        try:
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
                log_entry = {
                    "file_name": file_name,
                    "file_type": "orders",
                    "rows_imported": len(df),
                    "status": "success"
                }
                self._log_import(log_entry)
                return True, f"Loaded {len(df)} orders"
            else:
                return False, "Failed to insert orders"
        except Exception as e:
            return False, f"Error loading orders: {e}"
    
    def load_items(self, df: pd.DataFrame, file_name: str = "items.csv") -> tuple:
        """Load items data into MySQL"""
        try:
            # Remove duplicates and invalid rows
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
                log_entry = {
                    "file_name": file_name,
                    "file_type": "items",
                    "rows_imported": len(df),
                    "status": "success"
                }
                self._log_import(log_entry)
                return True, f"Loaded {len(df)} items"
            else:
                return False, "Failed to insert items"
        except Exception as e:
            return False, f"Error loading items: {e}"
    
    def load_uploaded_file(self, uploaded_file, file_type: str) -> tuple:
        """Load an uploaded file based on file type"""
        try:
            df = pd.read_csv(uploaded_file)
            
            if file_type.lower() == "channels":
                return self.load_channels(df, uploaded_file.name)
            elif file_type.lower() == "orders":
                return self.load_orders(df, uploaded_file.name)
            elif file_type.lower() == "items":
                return self.load_items(df, uploaded_file.name)
            else:
                return False, f"Unknown file type: {file_type}"
        except Exception as e:
            return False, f"Error processing file: {e}"
    
    def _log_import(self, log_entry: dict):
        """Log import operation to database"""
        try:
            query = """
            INSERT INTO data_import_log (file_name, file_type, rows_imported, import_status)
            VALUES (%s, %s, %s, %s)
            """
            data = (
                log_entry.get("file_name"),
                log_entry.get("file_type"),
                log_entry.get("rows_imported"),
                log_entry.get("status")
            )
            self.connector.execute_query(query, data)
        except Exception as e:
            print(f"Error logging import: {e}")
    
    def get_import_history(self) -> pd.DataFrame:
        """Get import history from database"""
        query = "SELECT * FROM data_import_log ORDER BY import_date DESC LIMIT 50"
        return self.connector.fetch_df(query)
    
    def get_table_stats(self) -> dict:
        """Get row counts for all tables"""
        stats = {}
        for table in ['channels', 'orders', 'items']:
            count = self.connector.get_table_count(table)
            stats[table] = count
        return stats
