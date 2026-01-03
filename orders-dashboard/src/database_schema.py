"""
Database Schema: Create and initialize MySQL schema
"""
from mysql_connector import MySQLConnector


class DatabaseSchema:
    """Create and manage database schema"""
    
    @staticmethod
    def create_database(connector: MySQLConnector, database_name: str = "orders_dashboard") -> bool:
        """Create the orders_dashboard database"""
        try:
            cursor = connector.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            cursor.close()
            connector.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    
    @staticmethod
    def create_schema(connector: MySQLConnector) -> bool:
        """Create all tables in the schema"""
        
        # 1. Channels table
        channels_table = """
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INT,
            channel_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        # 2. Orders table (combines orders_app and orders_web)
        orders_table = """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT,
            channel_id INT,
            order_date DATE,
            status VARCHAR(50),
            updated_at DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        # 3. Items table
        items_table = """
        CREATE TABLE IF NOT EXISTS items (
            item_id INT,
            order_id INT,
            sku VARCHAR(50),
            quantity INT,
            unit_price DECIMAL(10, 2),
            total_price DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        # 4. Data Import Log (for tracking file uploads)
        import_log_table = """
        CREATE TABLE IF NOT EXISTS data_import_log (
            import_id INT,
            file_name VARCHAR(255),
            file_type VARCHAR(50),
            rows_imported INT,
            rows_failed INT DEFAULT 0,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            import_status VARCHAR(50),
            error_message LONGTEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        # Execute all table creations
        tables = [
            ("channels", channels_table),
            ("orders", orders_table),
            ("items", items_table),
            ("data_import_log", import_log_table)
        ]
        
        for table_name, table_sql in tables:
            try:
                connector.execute_query(table_sql)
                print(f"✓ Table '{table_name}' created successfully")
            except Exception as e:
                print(f"✗ Error creating table '{table_name}': {e}")
                return False
        
        return True
    
    @staticmethod
    def create_views(connector: MySQLConnector) -> bool:
        """Create useful views for analysis"""
        
        # Orders summary view
        orders_summary_view = """
        CREATE OR REPLACE VIEW v_orders_summary AS
        SELECT 
            o.order_id,
            o.channel_id,
            c.channel_name,
            o.order_date,
            o.status,
            COUNT(i.item_id) as item_count,
            SUM(i.total_price) as order_total
        FROM orders o
        LEFT JOIN channels c ON o.channel_id = c.channel_id
        LEFT JOIN items i ON o.order_id = i.order_id
        GROUP BY o.order_id, o.channel_id, c.channel_name, o.order_date, o.status
        """
        
        try:
            connector.execute_query(orders_summary_view)
            print("✓ View 'v_orders_summary' created")
            return True
        except Exception as e:
            print(f"✗ Error creating view: {e}")
            return False
