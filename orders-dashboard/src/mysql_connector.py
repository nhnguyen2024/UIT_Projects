"""
MySQL Connector: Manage database connections and operations
"""
import mysql.connector
from mysql.connector import Error
import streamlit as st
from typing import Optional, List
import pandas as pd


class MySQLConnector:
    """Handle MySQL database connections and operations"""
    
    def __init__(self, 
                 host: str = "localhost",
                 user: str = "root",
                 password: str = "root",
                 database: str = "orders_dashboard"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self) -> bool:
        """Establish MySQL connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute a single query (CREATE, INSERT, UPDATE, DELETE)"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return False
    
    def execute_many(self, query: str, data: List[tuple]) -> bool:
        """Execute multiple inserts/updates"""
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, data)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error executing batch query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str) -> Optional[List]:
        """Fetch all results from a SELECT query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    def fetch_df(self, query: str) -> Optional[pd.DataFrame]:
        """Fetch results as pandas DataFrame"""
        try:
            return pd.read_sql(query, self.connection)
        except Error as e:
            print(f"Error fetching DataFrame: {e}")
            return None
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        query = f"""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = '{self.database}' 
        AND table_name = '{table_name}'
        """
        result = self.fetch_all(query)
        return result[0][0] > 0 if result else False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count from a table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.fetch_all(query)
        return result[0][0] if result else 0
