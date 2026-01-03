"""
DataWarehouse: ETL pipeline for merging, deduplication, and transformation
"""
import pandas as pd


class DataWarehouse:
    """
    ETL Layer: Merge multi-source data, deduplicate, and prepare for analysis
    """
    
    def __init__(self):
        """Initialize the data warehouse"""
        self.merged_data = pd.DataFrame()

    def transform_and_load(self, web_df, app_df, items_df, channels_df):
        """
        Transform and load data from multiple sources
        
        Process:
        1. Merge web and app orders
        2. Deduplicate by order_id (keep latest)
        3. Join items and channels tables
        4. Calculate derived fields
        
        Args:
            web_df: Web orders DataFrame
            app_df: App orders DataFrame
            items_df: Items/SKU details DataFrame
            channels_df: Sales channels DataFrame
        """
        valid_sources = [df for df in [web_df, app_df] if not df.empty]
        if not valid_sources: 
            return

        # 1. Merge web + app orders
        raw_orders = pd.concat(valid_sources, ignore_index=True)

        # 2. Deduplicate (Lấy updated_at mới nhất)
        if 'updated_at' in raw_orders.columns:
            raw_orders['updated_at'] = pd.to_datetime(raw_orders['updated_at'])
            raw_orders = raw_orders.sort_values('updated_at', ascending=False)
        
        orders = raw_orders.drop_duplicates(subset=['order_id'], keep='first')
        
        # Convert date column
        if 'order_date' in orders.columns:
            orders['order_date'] = pd.to_datetime(orders['order_date'])

        # 3. Join Items table
        if not items_df.empty:
            full_data = orders.merge(items_df, on='order_id', how='left')
        else:
            full_data = orders
            full_data[['quantity', 'unit_price']] = 0

        # 4. Join Channels table
        if not channels_df.empty:
            full_data = full_data.merge(channels_df, on='channel_id', how='left')
        
        # 5. Calculate derived fields
        full_data['line_total'] = full_data['quantity'] * full_data['unit_price']
        self.merged_data = full_data
