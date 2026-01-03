"""
Essential DataLoader Tests - CSV loading
"""
import pytest
import pandas as pd
import os
import sys
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import DataLoader


class TestDataLoaderCore:
    """Essential DataLoader tests"""
    
    def test_load_existing_file(self, temp_dir):
        """Test loading existing CSV file"""
        # Create test file
        test_file = os.path.join(temp_dir, 'test.csv')
        pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}).to_csv(test_file, index=False)
        
        result = DataLoader.load(None, test_file, 'Test')
        assert not result.empty
        assert len(result) == 2
    
    def test_load_missing_file(self):
        """Test loading non-existent file returns empty DataFrame"""
        result = DataLoader.load(None, '/nonexistent/path.csv', 'Test')
        assert result.empty
    
    def test_load_semicolon_separator(self, temp_dir):
        """Test loading CSV with different separators"""
        test_file = os.path.join(temp_dir, 'test_comma.csv')
        # Create regular comma-separated CSV
        pd.DataFrame({'col1': [1, 3], 'col2': [2, 4]}).to_csv(test_file, index=False)
        
        result = DataLoader.load(None, test_file, 'Test')
        assert not result.empty
        assert 'col1' in result.columns
        assert len(result) == 2
