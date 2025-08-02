import pytest
from common.base_processor import BaseProcessor


class TestBaseProcessorSimplifiedSyntax:
    """Test cases for BaseProcessor simplified syntax detection"""

    def setup_class(self):
        """Initialize logging for test class"""
        pass

    def test_detects_simplified_syntax_common_case(self, base_processor, simplified_rules_data):
        """Test has_simplified_syntax() detects simplified syntax with match field"""
        # Arrange: Use simplified syntax rules fixture
        # (simplified_rules_data contains rules with match/to/from fields)
        
        # Act: Call has_simplified_syntax function
        result = base_processor.has_simplified_syntax(simplified_rules_data)
        
        # Assert: Should detect simplified syntax
        assert result is True, "Should detect simplified syntax when 'match' field is present"

    def test_detects_legacy_syntax_backward_compatibility(self, base_processor, legacy_rules_data):
        """Test has_simplified_syntax() returns False for legacy syntax (backward compatibility)"""
        # Arrange: Use legacy syntax rules fixture
        # (legacy_rules_data contains rules with transaction_type/debit_account/credit_account fields)
        
        # Act: Call has_simplified_syntax function
        result = base_processor.has_simplified_syntax(legacy_rules_data)
        
        # Assert: Should return False for legacy syntax to ensure backward compatibility
        assert result is False, "Should return False for legacy syntax (transaction_type, debit_account, credit_account)"

    def test_converts_contains_pattern(self, base_processor, pattern_conversion_test_data):
        """Test convert_pattern() converts 'contains salary' to '*salary*'"""
        # Arrange: Use pattern conversion test data fixture
        input_pattern = pattern_conversion_test_data["input_pattern"]
        expected_output = pattern_conversion_test_data["expected_output"]
        
        # Act: Call convert_pattern function
        result = base_processor.convert_pattern(input_pattern)
        
        # Assert: Should convert contains pattern to wildcard pattern
        assert result == expected_output, f"Expected '{expected_output}', but got '{result}'"

    def test_transform_rules_complete_integration(self, base_processor, comprehensive_simplified_rules, expected_legacy_transformation, shortcuts_data):
        """Test transform_rules() orchestrates complete transformation from simplified to legacy format"""
        # Arrange: Use comprehensive simplified rules fixture and expected legacy transformation fixture
        # (comprehensive_simplified_rules contains realistic user scenarios with simplified syntax)
        # (expected_legacy_transformation contains the expected result after complete transformation)
        
        # Act: Call transform_rules function (this should fail since function doesn't exist yet)
        result = base_processor.transform_rules(comprehensive_simplified_rules, shortcuts_data)
        
        # Assert: Should transform simplified syntax to complete legacy format
        assert result == expected_legacy_transformation, f"Expected transformed rules to match legacy format, but got: {result}"
        
        # Assert: Verify specific transformations
        # Pattern conversion: "contains salary" → "*salary*"
        assert result["rules"]["income"][0]["transaction_type"] == "*salary*"
        
        # Account resolution: "checking" → "Assets:Bank:Checking"
        assert result["rules"]["income"][0]["debit_account"] == "Assets:Bank:Checking"
        
        # Account resolution: "salary" → "Income:Salary"
        assert result["rules"]["income"][0]["credit_account"] == "Income:Salary"
        
        # Field name transformation: match → transaction_type, to → debit_account, from → credit_account
        assert "match" not in result["rules"]["income"][0], "Simplified field 'match' should be removed"
        assert "to" not in result["rules"]["income"][0], "Simplified field 'to' should be removed"
        assert "from" not in result["rules"]["income"][0], "Simplified field 'from' should be removed"
        assert "transaction_type" in result["rules"]["income"][0], "Legacy field 'transaction_type' should be present"
        assert "debit_account" in result["rules"]["income"][0], "Legacy field 'debit_account' should be present"
        assert "credit_account" in result["rules"]["income"][0], "Legacy field 'credit_account' should be present"