import pytest
from unittest.mock import patch, mock_open


class TestBaseProcessorBankPresetSystem:
    """Test cases for BaseProcessor bank preset functionality"""

    def setup_class(self):
        """Initialize test class"""
        pass

    def test_bank_preset_loading_and_merging_behavior(self, base_processor):
        """Test _load_bank_preset() loads presets and merges with user shortcuts correctly"""
        preset_yaml = "accounts:\n  checking: Assets:Bank:DBS:Checking\n  savings: Assets:Bank:DBS:Savings"
        
        # Test successful load and merge with user priority
        with patch("builtins.open", mock_open(read_data=preset_yaml)):
            bank_shortcuts = base_processor._load_bank_preset("dbs")
            user_shortcuts = {"checking": "Assets:Personal:Custom:Checking"}
            result = {**bank_shortcuts, **user_shortcuts}
            
            assert result["checking"] == "Assets:Personal:Custom:Checking"  # User priority
            assert result["savings"] == "Assets:Bank:DBS:Savings"           # Bank fallback
        
        # Test missing file graceful degradation
        with patch("builtins.open", side_effect=FileNotFoundError()):
            assert base_processor._load_bank_preset("missing") == {}
        
        # Test account resolution in rule transformation
        simplified_rules = {
            "rules": {
                "income": [{
                    "match": "contains salary",
                    "to": "checking",
                    "from": "Income:Salary"
                }]
            }
        }
        
        transformed = base_processor.transform_rules(simplified_rules, result)
        income_rule = transformed["rules"]["income"][0]
        
        assert income_rule["transaction_type"] == "*salary*"
        assert income_rule["debit_account"] == "Assets:Personal:Custom:Checking"
        assert income_rule["credit_account"] == "Income:Salary"
        assert "match" not in income_rule  # Simplified fields removed