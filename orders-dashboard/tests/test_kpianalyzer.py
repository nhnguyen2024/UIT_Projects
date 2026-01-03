"""
Essential KPIAnalyzer Tests - Key Performance Indicators
"""
import pytest
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import KPIAnalyzer


class TestKPIAnalyzerCore:
    """Essential KPIAnalyzer tests"""
    
    def test_revenue_calculation(self, merged_data):
        """Test total revenue from completed orders"""
        analyzer = KPIAnalyzer(merged_data)
        rev, _, _, _, _ = analyzer.get_metrics()
        
        completed = merged_data[merged_data['status'] == 'completed']
        expected_rev = completed['line_total'].sum()
        
        assert rev == expected_rev
        assert rev > 0
    
    def test_return_rate_calculation(self, merged_data):
        """Test return rate (returned quantity / total quantity)"""
        analyzer = KPIAnalyzer(merged_data)
        _, ret_rate, _, _, _ = analyzer.get_metrics()
        
        total_qty = merged_data['quantity'].sum()
        returned_qty = merged_data[merged_data['status'] == 'returned']['quantity'].sum()
        expected_rate = (returned_qty / total_qty * 100) if total_qty > 0 else 0
        
        assert ret_rate == expected_rate
    
    def test_aov_calculation(self, merged_data):
        """Test Average Order Value (AOV)"""
        analyzer = KPIAnalyzer(merged_data)
        _, _, aov, _, _ = analyzer.get_metrics()
        
        completed = merged_data[merged_data['status'] == 'completed']
        if not completed.empty:
            expected_aov = completed.groupby('order_id')['line_total'].sum().mean()
            assert aov == expected_aov
        assert aov >= 0
    
    def test_filter_by_channel(self, merged_data):
        """Test filtering by channel"""
        analyzer = KPIAnalyzer(merged_data)
        
        channels = merged_data['channel_name'].dropna().unique()
        if len(channels) > 0:
            filtered = analyzer.filter(channels[0], [])
            assert len(filtered.df) <= len(merged_data)
