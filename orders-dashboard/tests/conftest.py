"""
Pytest fixtures for testing Orders Dashboard (Minimal Essential Tests)
"""
import pytest
import pandas as pd
import os
import tempfile
import sys

# Add parent directory to path to import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import DataLoader, DataWarehouse, KPIAnalyzer


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_web_orders():
    """Sample web orders data"""
    return pd.DataFrame({
        'order_id': [1, 2, 3, 4],
        'order_date': pd.date_range('2025-01-01', periods=4),
        'updated_at': pd.date_range('2025-01-01', periods=4),
        'status': ['completed', 'completed', 'returned', 'cancelled'],
        'channel_id': [1, 1, 2, 1]
    })


@pytest.fixture
def sample_app_orders():
    """Sample app orders data"""
    return pd.DataFrame({
        'order_id': [5, 6, 7],
        'order_date': pd.date_range('2025-01-05', periods=3),
        'updated_at': pd.date_range('2025-01-05', periods=3),
        'status': ['completed', 'completed', 'returned'],
        'channel_id': [2, 1, 2]
    })


@pytest.fixture
def sample_items():
    """Sample order items data"""
    return pd.DataFrame({
        'order_id': [1, 2, 2, 3, 4, 5, 6, 7],
        'sku': ['SKU001', 'SKU002', 'SKU001', 'SKU003', 'SKU001', 'SKU002', 'SKU001', 'SKU003'],
        'quantity': [2, 1, 3, 1, 2, 2, 4, 1],
        'unit_price': [100.0, 50.0, 100.0, 75.0, 100.0, 50.0, 100.0, 75.0]
    })


@pytest.fixture
def sample_channels():
    """Sample channels data"""
    return pd.DataFrame({
        'channel_id': [1, 2],
        'channel_name': ['Website', 'Mobile App']
    })


@pytest.fixture
def sample_csv_files(temp_dir, sample_web_orders, sample_app_orders, sample_items, sample_channels):
    """Create sample CSV files in temp directory"""
    web_path = os.path.join(temp_dir, 'orders_web.csv')
    app_path = os.path.join(temp_dir, 'orders_app.csv')
    items_path = os.path.join(temp_dir, 'items.csv')
    channels_path = os.path.join(temp_dir, 'channels.csv')
    
    sample_web_orders.to_csv(web_path, index=False)
    sample_app_orders.to_csv(app_path, index=False)
    sample_items.to_csv(items_path, index=False)
    sample_channels.to_csv(channels_path, index=False)
    
    return {
        'web': web_path,
        'app': app_path,
        'items': items_path,
        'channels': channels_path,
        'temp_dir': temp_dir
    }


@pytest.fixture
def merged_data(sample_web_orders, sample_app_orders, sample_items, sample_channels):
    """Expected merged and processed data"""
    # Combine web and app orders
    orders = pd.concat([sample_web_orders, sample_app_orders], ignore_index=True)
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders['updated_at'] = pd.to_datetime(orders['updated_at'])
    
    # Merge with items
    merged = orders.merge(sample_items, on='order_id', how='left')
    
    # Merge with channels
    merged = merged.merge(sample_channels, on='channel_id', how='left')
    
    # Calculate line_total
    merged['line_total'] = merged['quantity'] * merged['unit_price']
    
    return merged
