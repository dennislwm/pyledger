import pytest
from common.base_processor import BaseProcessor


class TestBaseProcessorAccountShortcuts:
    """Test cases for BaseProcessor account shortcut resolution"""

    def setup_class(self):
        """Initialize logging for test class"""
        pass

    def test_resolve_account_with_valid_shortcut(self, base_processor, shortcuts_data):
        """Test resolve_account() resolves valid account shortcuts to full paths"""
        # Arrange: Use shortcuts data fixture with "checking" shortcut
        shortcut = "checking"
        expected_account = "Assets:Bank:Checking"
        
        # Act: Call resolve_account function
        result = base_processor.resolve_account(shortcut, shortcuts_data)
        
        # Assert: Should resolve shortcut to full account path
        assert result == expected_account, f"Expected '{expected_account}', but got '{result}'"

    def test_resolve_account_with_invalid_shortcut(self, base_processor, shortcuts_data):
        """Test resolve_account() returns original input for invalid shortcuts"""
        # Arrange: Use non-existent shortcut
        invalid_shortcut = "nonexistent"
        
        # Act: Call resolve_account function  
        result = base_processor.resolve_account(invalid_shortcut, shortcuts_data)
        
        # Assert: Should return original input when shortcut not found
        assert result == invalid_shortcut, f"Expected '{invalid_shortcut}', but got '{result}'"

    def test_resolve_account_with_empty_shortcuts(self, base_processor):
        """Test resolve_account() handles empty shortcuts dictionary"""
        # Arrange: Empty shortcuts dictionary
        empty_shortcuts = {}
        account = "checking"
        
        # Act: Call resolve_account function
        result = base_processor.resolve_account(account, empty_shortcuts)
        
        # Assert: Should return original input when shortcuts dict is empty
        assert result == account, f"Expected '{account}', but got '{result}'"
