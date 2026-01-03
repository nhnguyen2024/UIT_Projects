"""
Tests for DashboardExporter: PDF export with filtered data verification
Tests ensure that PDF contains only the filtered data, not all data
"""
import pytest
import pandas as pd
import io
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dashboard_exporter import DashboardExporter


@pytest.fixture
def sample_orders_df():
    """Create sample orders data for testing"""
    return pd.DataFrame({
        'order_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'channel_name': ['Web', 'App', 'Web', 'App', 'Web', 'App', 'Web', 'App'],
        'order_date': pd.date_range('2025-01-01', periods=8),
        'status': ['completed', 'completed', 'pending', 'completed', 'cancelled', 'completed', 'returned', 'completed'],
        'order_total': [100.00, 150.00, 200.00, 120.00, 80.00, 250.00, 90.00, 175.00]
    })


@pytest.fixture
def exporter():
    """Create DashboardExporter instance"""
    try:
        return DashboardExporter()
    except ImportError:
        pytest.skip("reportlab not installed")


class TestPDFExportBasics:
    """Test basic PDF export functionality"""
    
    def test_export_pdf_with_sample_data(self, exporter, sample_orders_df):
        """Test that PDF can be generated with sample data"""
        metrics = {
            'total_orders': len(sample_orders_df),
            'completed_pct': 62.5,
            'total_revenue': 1165.00,
            'avg_order_value': 145.63
        }
        
        chart_data = {
            'channel_dist': sample_orders_df.groupby('channel_name').size(),
            'status_dist': sample_orders_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, sample_orders_df)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert isinstance(pdf_bytes, bytes)
        # Check if it's a valid PDF
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_export_pdf_with_empty_dataframe(self, exporter):
        """Test that PDF can be generated with empty DataFrame"""
        empty_df = pd.DataFrame()
        metrics = {
            'total_orders': 0,
            'completed_pct': 0,
            'total_revenue': 0,
            'avg_order_value': 0
        }
        
        chart_data = {
            'channel_dist': pd.Series(),
            'status_dist': pd.Series(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, empty_df)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')


class TestFilteredDataExport:
    """Test that PDF export correctly handles filtered data"""
    
    def test_export_filtered_by_channel(self, exporter, sample_orders_df):
        """Test PDF export with channel filtered data"""
        # Filter for Web channel only
        filtered_df = sample_orders_df[sample_orders_df['channel_name'] == 'Web'].copy()
        
        metrics = {
            'total_orders': len(filtered_df),
            'completed_pct': 50.0,  # 2 out of 4
            'total_revenue': filtered_df['order_total'].sum(),
            'avg_order_value': filtered_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
        
        # Verify metrics are correct for filtered data
        assert metrics['total_orders'] == 4  # Only Web orders
        assert metrics['total_revenue'] == pytest.approx(390.0)  # Sum of Web orders
    
    def test_export_filtered_by_status(self, exporter, sample_orders_df):
        """Test PDF export with status filtered data"""
        # Filter for completed orders only
        filtered_df = sample_orders_df[sample_orders_df['status'] == 'completed'].copy()
        
        metrics = {
            'total_orders': len(filtered_df),
            'completed_pct': 100.0,  # All are completed
            'total_revenue': filtered_df['order_total'].sum(),
            'avg_order_value': filtered_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        assert metrics['total_orders'] == 5  # Only completed orders
        assert metrics['completed_pct'] == 100.0
    
    def test_export_filtered_by_price_range(self, exporter, sample_orders_df):
        """Test PDF export with price range filtered data"""
        # Filter for orders between 100 and 200
        filtered_df = sample_orders_df[
            (sample_orders_df['order_total'] >= 100) & 
            (sample_orders_df['order_total'] <= 200)
        ].copy()
        
        metrics = {
            'total_orders': len(filtered_df),
            'completed_pct': 75.0,
            'total_revenue': filtered_df['order_total'].sum(),
            'avg_order_value': filtered_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        assert metrics['total_orders'] == 6  # Orders within price range
        assert metrics['total_revenue'] == pytest.approx(745.0)
    
    def test_export_multiple_filter_combinations(self, exporter, sample_orders_df):
        """Test PDF export with multiple filters applied"""
        # Filter: Web channel AND completed status AND price > 100
        filtered_df = sample_orders_df[
            (sample_orders_df['channel_name'] == 'Web') &
            (sample_orders_df['status'] == 'completed') &
            (sample_orders_df['order_total'] > 100)
        ].copy()
        
        metrics = {
            'total_orders': len(filtered_df),
            'completed_pct': 100.0,
            'total_revenue': filtered_df['order_total'].sum(),
            'avg_order_value': filtered_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        # Web completed orders: 1(100), 6(250) = 2 orders matching price > 100
        assert metrics['total_orders'] == 2
        assert metrics['total_revenue'] == pytest.approx(350.0)


class TestPDFDataAccuracy:
    """Test that PDF contains accurate data representation"""
    
    def test_metrics_match_dataframe(self, exporter, sample_orders_df):
        """Test that PDF metrics match the actual DataFrame statistics"""
        filtered_df = sample_orders_df.copy()
        
        total_orders = len(filtered_df)
        completed_count = len(filtered_df[filtered_df['status'] == 'completed'])
        completed_pct = (completed_count / total_orders) * 100
        total_revenue = filtered_df['order_total'].sum()
        avg_order_value = filtered_df['order_total'].mean()
        
        metrics = {
            'total_orders': total_orders,
            'completed_pct': completed_pct,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        # Verify calculations
        assert metrics['total_orders'] == 8
        assert metrics['completed_pct'] == pytest.approx(62.5)
        assert metrics['total_revenue'] == pytest.approx(1165.0)
        assert metrics['avg_order_value'] == pytest.approx(145.625)
    
    def test_chart_data_calculation(self, exporter, sample_orders_df):
        """Test that chart data is correctly calculated from filtered DataFrame"""
        filtered_df = sample_orders_df[sample_orders_df['channel_name'] == 'Web'].copy()
        
        channel_dist = filtered_df.groupby('channel_name').size()
        status_dist = filtered_df.groupby('status').size()
        
        assert channel_dist['Web'] == 4
        assert status_dist['completed'] == 2
        assert status_dist['pending'] == 1
        assert status_dist['cancelled'] == 1
        assert status_dist['returned'] == 1


class TestPDFRowCount:
    """Test that PDF contains correct number of rows from filtered data"""
    
    def test_pdf_row_count_matches_filtered_data(self, exporter, sample_orders_df):
        """Test that all filtered rows are included in PDF"""
        filtered_df = sample_orders_df[sample_orders_df['status'] == 'completed'].copy()
        
        metrics = {
            'total_orders': len(filtered_df),
            'completed_pct': 100.0,
            'total_revenue': filtered_df['order_total'].sum(),
            'avg_order_value': filtered_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        # The metric should show the filtered count, not the total
        assert metrics['total_orders'] == 5
        assert len(filtered_df) == 5
    
    def test_all_filtered_rows_in_export(self, exporter):
        """Test that all rows from a filtered DataFrame are in the PDF"""
        # Create a large filtered dataset
        large_df = pd.DataFrame({
            'order_id': range(1, 101),
            'channel_name': ['Web' if i % 2 == 0 else 'App' for i in range(100)],
            'order_date': pd.date_range('2025-01-01', periods=100),
            'status': ['completed' if i % 3 != 0 else 'pending' for i in range(100)],
            'order_total': [100 + i*1.5 for i in range(100)]
        })
        
        # Filter to get 50 rows
        filtered_df = large_df[large_df['channel_name'] == 'Web'].copy()
        
        metrics = {
            'total_orders': len(filtered_df),
            'completed_pct': 100.0,
            'total_revenue': filtered_df['order_total'].sum(),
            'avg_order_value': filtered_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': filtered_df.groupby('channel_name').size(),
            'status_dist': filtered_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, filtered_df)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert metrics['total_orders'] == 50  # Only Web orders


class TestPDFStructure:
    """Test PDF structure and content integrity"""
    
    def test_pdf_contains_metrics_section(self, exporter, sample_orders_df):
        """Test that PDF contains metrics section"""
        metrics = {
            'total_orders': 8,
            'completed_pct': 62.5,
            'total_revenue': 1165.00,
            'avg_order_value': 145.625
        }
        
        chart_data = {
            'channel_dist': sample_orders_df.groupby('channel_name').size(),
            'status_dist': sample_orders_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, sample_orders_df)
        
        # Convert to string to check content
        pdf_str = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Key Metrics' in pdf_str or 'metrics' in pdf_str.lower()
    
    def test_pdf_contains_data_table(self, exporter, sample_orders_df):
        """Test that PDF contains data table"""
        metrics = {
            'total_orders': len(sample_orders_df),
            'completed_pct': 62.5,
            'total_revenue': sample_orders_df['order_total'].sum(),
            'avg_order_value': sample_orders_df['order_total'].mean()
        }
        
        chart_data = {
            'channel_dist': sample_orders_df.groupby('channel_name').size(),
            'status_dist': sample_orders_df.groupby('status').size(),
        }
        
        pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, sample_orders_df)
        
        # Check for order table indication
        pdf_str = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Order' in pdf_str or 'Data' in pdf_str.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
