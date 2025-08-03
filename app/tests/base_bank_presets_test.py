import pytest
from unittest.mock import patch, mock_open


class TestBaseProcessorBankPresets:
    """Test cases for BaseProcessor bank preset functionality"""

    def setup_class(self):
        """Initialize test class"""
        pass

    def test_bank_preset_user_override_priority(self, base_processor, bank_preset_test_data):
        """Test user shortcuts override bank presets
        
        Business Behavior: When user specifies 'bank: dbs' and defines custom accounts,
        user shortcuts take priority over bank presets while bank shortcuts provide fallback.
        """
        # Arrange: Get test data from fixture
        data = bank_preset_test_data
        preset_yaml = 'accounts:\n  checking: Assets:Bank:DBS:Checking\n  savings: Assets:Bank:DBS:Savings'
        
        # Act: Test complete workflow with simple mock
        with patch('builtins.open', mock_open(read_data=preset_yaml)):
            # Load bank preset
            bank_shortcuts = base_processor._load_bank_preset('dbs')
            
            # Merge with user shortcuts (user takes priority)
            combined_shortcuts = {**bank_shortcuts, **data['user_rules']['accounts']}
            
            # Transform rules using combined shortcuts
            result = base_processor.transform_rules(data['user_rules'], combined_shortcuts)
        
        # Assert: User override takes precedence
        income_rule = result['rules']['income'][0]
        assert income_rule['debit_account'] == 'Assets:Personal:Custom:Checking', \
            "User override should take precedence over bank preset"
        
        # Assert: Bank shortcuts provide fallback
        assert combined_shortcuts['savings'] == 'Assets:Bank:DBS:Savings', \
            "Bank preset should provide fallback for non-overridden shortcuts"

    def test_missing_preset_graceful_degradation(self, base_processor):
        """Test system handles missing preset file gracefully
        
        Business Behavior: When bank preset file doesn't exist,
        system continues operation using only user-defined shortcuts.
        """
        # Act: Load preset for nonexistent bank
        result = base_processor._load_bank_preset('nonexistent_bank')
        
        # Assert: Returns empty dictionary (graceful degradation)
        assert result == {}, "Missing preset should return empty dictionary"