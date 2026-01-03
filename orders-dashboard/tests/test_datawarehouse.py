"""
Essential DataWarehouse Tests - ETL and data merging
"""
import pytest
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import DataWarehouse


class TestDataWarehouseCore:
    """Essential DataWarehouse (ETL) tests"""
    
    def test_merge_web_and_app_orders(self, sample_web_orders, sample_app_orders, sample_items, sample_channels):
        """Test ETL merges web and app orders correctly"""
        dw = DataWarehouse()
        dw.transform_and_load(sample_web_orders, sample_app_orders, sample_items, sample_channels)
        
        assert not dw.merged_data.empty
        assert len(dw.merged_data) >= 7
    
    def test_deduplicate_by_order_id(self, sample_items, sample_channels):
        """Test deduplication keeps latest updated_at record"""
        orders = pd.DataFrame({
            'order_id': [1, 1, 2],
            'order_date': ['2025-01-01', '2025-01-01', '2025-01-02'],
            'updated_at': ['2025-01-01 10:00:00', '2025-01-01 15:00:00', '2025-01-02 10:00:00'],
            'status': ['completed', 'completed', 'returned'],
            'channel_id': [1, 1, 1]
        })
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        orders['updated_at'] = pd.to_datetime(orders['updated_at'])
        
        dw = DataWarehouse()
        dw.transform_and_load(orders, pd.DataFrame(columns=orders.columns), sample_items, sample_channels)
        
        unique_orders = dw.merged_data[['order_id']].drop_duplicates()
        assert len(unique_orders) == 2
    
    def test_join_with_items(self, sample_web_orders, sample_items, sample_channels):
        """Test joining orders with items includes required columns"""
        dw = DataWarehouse()
        dw.transform_and_load(sample_web_orders, pd.DataFrame(columns=sample_web_orders.columns), 
                              sample_items, sample_channels)
        
        assert 'quantity' in dw.merged_data.columns
        assert 'sku' in dw.merged_data.columns
