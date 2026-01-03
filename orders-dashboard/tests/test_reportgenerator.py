"""
Essential ReportGenerator Tests - PDF export
"""
import pytest
import os
import pandas as pd
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import ReportGenerator, KPIAnalyzer


class TestReportGeneratorCore:
    """Essential ReportGenerator tests"""
    
    def test_pdf_export_basic_data(self):
        """Test PDF export with basic valid data"""
        data = pd.DataFrame({
            'order_id': [1],
            'status': ['completed'],
            'quantity': [1],
            'unit_price': [100.0],
            'order_date': pd.to_datetime(['2025-01-01']),
            'line_total': [100.0],
            'channel_name': ['Website'],
            'sku': ['SKU001']
        })
        
        analyzer = KPIAnalyzer(data)
        rev, rate, aov, cancel, best = analyzer.get_metrics()
        assert rev > 0
        assert aov > 0
    
    def test_metrics_calculation_from_data(self):
        """Test metrics calculation from analyzer"""
        data = pd.DataFrame({
            'order_id': [1, 2, 3],
            'status': ['completed', 'completed', 'returned'],
            'quantity': [2, 1, 3],
            'unit_price': [100.0, 50.0, 100.0],
            'order_date': pd.date_range('2025-01-01', periods=3),
            'line_total': [200.0, 50.0, 300.0],
            'channel_name': ['Website', 'App', 'Website'],
            'sku': ['SKU001', 'SKU002', 'SKU001']
        })
        
        analyzer = KPIAnalyzer(data)
        rev, ret_rate, aov, cancel_rate, best_sku = analyzer.get_metrics()
        
        assert rev == 250.0
        assert ret_rate > 0
        assert aov > 0
        assert best_sku != "N/A"

