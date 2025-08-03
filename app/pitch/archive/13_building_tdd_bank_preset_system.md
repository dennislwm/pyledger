# Test-Driven Development Design: Bank Preset System

## Overview

Bank preset system allows users to specify `bank: "dbs"` in YAML rules to load bank-specific account shortcuts, reducing typing while maintaining accuracy.

**Business Value**: Write `checking` instead of `Assets:Personal:Bank:DBS:Checking`
**Implementation**: 1.5 hours (1 hour testing, 30 minutes preset files)

## Core Behaviors

- **Bank preset loading**: Load bank shortcuts from preset files
- **User override priority**: User shortcuts override bank presets
- **Graceful degradation**: Work without preset files

## Focused Test Suite

```python
class TestBankPresetSystem:
    """Focused tests for bank preset functionality."""
    
    @pytest.fixture
    def sample_preset(self):
        """Simple bank preset data for testing."""
        return {
            "checking": "Assets:Bank:DBS:Checking",
            "savings": "Assets:Bank:DBS:Savings",
            "salary": "Income:Salary"
        }
    
    def test_bank_preset_loading_and_merging(self, sample_preset):
        """Test complete preset loading with user override priority."""
        # Arrange: User rules with override
        user_shortcuts = {"checking": "Assets:Personal:Custom:Checking"}
        
        # Act: Merge bank preset with user shortcuts (user takes priority)
        combined = {**sample_preset, **user_shortcuts}
        
        # Assert: User override works, bank shortcuts provide fallback
        assert combined["checking"] == "Assets:Personal:Custom:Checking"  # User override
        assert combined["savings"] == "Assets:Bank:DBS:Savings"           # Bank fallback
        assert combined["salary"] == "Income:Salary"                      # Bank fallback
        
    def test_missing_preset_graceful_degradation(self):
        """Test system works without preset files."""
        # Arrange & Act: Load non-existent preset
        processor = BaseProcessor()
        shortcuts = processor._load_bank_preset('nonexistent_bank')
        
        # Assert: Returns empty dict without errors
        assert shortcuts == {}
        
    def test_account_resolution_in_rules(self, sample_preset):
        """Test shortcuts resolve correctly in rule transformation."""
        # Arrange: Simplified rules using shortcuts
        rules = {
            'rules': {
                'income': [{
                    'match': 'contains salary',
                    'to': 'checking',
                    'from': 'salary'
                }]
            }
        }
        
        # Act: Transform rules using preset shortcuts
        processor = BaseProcessor()
        transformed = processor.transform_rules(rules, sample_preset)
        
        # Assert: Shortcuts resolved to full account paths
        income_rule = transformed['rules']['income'][0]
        assert income_rule['debit_account'] == 'Assets:Bank:DBS:Checking'
        assert income_rule['credit_account'] == 'Income:Salary'
```

## Implementation Plan

1. **Validate existing `_load_bank_preset()` method** (30 minutes)
2. **Implement focused test suite** (60 minutes) 
3. **Create essential preset files: dbs.yaml, uob.yaml** (30 minutes)

## Success Criteria

- [ ] Bank preset loading with user override priority
- [ ] Graceful degradation without preset files
- [ ] Account shortcuts resolve in rule transformation
- [ ] Zero breaking changes to existing functionality
EOF < /dev/null