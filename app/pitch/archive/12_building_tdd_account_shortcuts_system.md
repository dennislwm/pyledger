# TDD Design: Bank Preset Shortcuts

## Implementation Requirements

**Goal**: Add bank preset loading to existing account shortcuts system in BaseProcessor.

**Core Feature**: Load bank-specific account shortcuts from `presets/{bank_name}.yaml` files and merge with user shortcuts (user shortcuts take priority).

**Integration Point**: Enhance `load_rules()` method in BaseProcessor:

```python
# Current code (lines 69-71):
if self.has_simplified_syntax(rules):
    shortcuts = rules.get('accounts', {})
    rules = self.transform_rules(rules, shortcuts)

# Enhanced implementation:
if self.has_simplified_syntax(rules):
    bank_shortcuts = self._load_bank_preset(rules.get('bank', ''))
    user_shortcuts = rules.get('accounts', {})
    shortcuts = {**bank_shortcuts, **user_shortcuts}  # User overrides
    rules = self.transform_rules(rules, shortcuts)
```

**Implementation**:

```python
def _load_bank_preset(self, bank_name: str) -> dict:
    if not bank_name:
        return {}
    preset_path = f"presets/{bank_name}.yaml"
    try:
        with open(preset_path, 'r') as f:
            preset = yaml.safe_load(f)
            return preset.get('accounts', {}) if preset else {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}  # Graceful degradation
```

## TDD Test Strategy

**Essential Tests Only (2 tests maximum)**:

### Test 1: End-to-End Bank Preset Integration

```python
def test_bank_preset_integration_with_user_override(self, tmp_path):
    """Test complete bank preset loading and user override workflow"""
    # Setup: Create preset file
    preset_dir = tmp_path / "presets"
    preset_dir.mkdir()
    preset_file = preset_dir / "dbs.yaml"
    preset_file.write_text("accounts:\n  checking: 'Assets:Bank:DBS:Checking'\n  savings: 'Assets:Bank:DBS:Savings'")
    
    # Setup: Rules with bank preset and user override
    rules = {
        'bank': 'dbs',
        'accounts': {
            'checking': 'Assets:Personal:Custom:Checking',  # User override
            'investment': 'Assets:Personal:Investment'       # User-only
        },
        'income': [{
            'transaction_type': 'salary',
            'debit_account': 'checking',
            'credit_account': 'Income:Salary'
        }]
    }
    
    # Execute: Transform rules
    processor = BaseProcessor()
    with patch('builtins.open', mock_open(read_data=preset_file.read_text())):
        transformed = processor.transform_rules(rules, 
            {**{'checking': 'Assets:Bank:DBS:Checking', 'savings': 'Assets:Bank:DBS:Savings'}, 
             **rules['accounts']})
    
    # Verify: User override takes precedence, preset provides fallback
    assert transformed['income'][0]['debit_account'] == 'Assets:Personal:Custom:Checking'
```

### Test 2: Missing Preset Graceful Handling

```python
def test_missing_preset_graceful_handling():
    """Test system continues when preset file missing"""
    rules = {
        'bank': 'nonexistent',
        'accounts': {'checking': 'Assets:Personal:Checking'},
        'income': [{
            'transaction_type': 'salary',
            'debit_account': 'checking',
            'credit_account': 'Income:Salary'
        }]
    }
    
    processor = BaseProcessor()
    # Should not raise exception, should use only user shortcuts
    transformed = processor.transform_rules(rules, rules['accounts'])
    assert transformed['income'][0]['debit_account'] == 'Assets:Personal:Checking'
```

## Integration Points

**BaseProcessor Changes**:

1. Add `_load_bank_preset()` private method
2. Modify `load_rules()` to integrate bank presets
3. Maintain existing `resolve_account()` and `transform_rules()` unchanged

**File Structure**:

- Preset files: `presets/{bank_name}.yaml`
- Format: `accounts: {shortcut: full_account_path}`
- No validation required (per specification)

**Priority Order**:

1. User shortcuts (from rules.accounts)
2. Bank presets (from presets/{bank}.yaml)
3. Literal account names (existing fallback)

## Success Criteria

**Functional Requirements**:

- [ ] Users can specify `bank: dbs` in YAML rules
- [ ] System loads shortcuts from `presets/dbs.yaml`
- [ ] User shortcuts override bank presets
- [ ] Missing preset files don't break system
- [ ] No breaking changes to existing functionality

**Implementation Constraints**:

- [ ] Add maximum 15 lines of code
- [ ] Zero changes to existing public methods
- [ ] All existing tests pass
- [ ] No performance degradation

**Quality Gates**:

- [ ] Both TDD tests pass
- [ ] No regression in existing test suite
- [ ] Implementation follows project patterns
