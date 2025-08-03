import pytest
from common.base_processor import BaseProcessor


class TestBaseProcessorAccountShortcuts:
    """Test BaseProcessor account shortcut resolution"""

    def test_resolve_account(self, base_processor):
        """Test account shortcut resolution functionality"""
        shortcuts = {"checking": "Assets:Bank:Checking", "savings": "Assets:Bank:Savings"}
        
        # Test valid shortcut resolution
        assert base_processor.resolve_account("checking", shortcuts) == "Assets:Bank:Checking"
        
        # Test invalid shortcut fallback
        assert base_processor.resolve_account("nonexistent", shortcuts) == "nonexistent"
        
        # Test empty shortcuts dictionary
        assert base_processor.resolve_account("checking", {}) == "checking"
