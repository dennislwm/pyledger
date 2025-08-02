# Test-Driven Development Analysis: YAML Schema Design (Simplified)

## Overview

This analysis provides a practical TDD approach for implementing simplified field aliasing in the PyLedger application. The feature transforms user-friendly field names (`match`, `to`, `from`) to existing legacy fields (`transaction_type`, `debit_account`, `credit_account`) during YAML loading.

**Implementation Estimate: 2 hours total**

---

## Core Functions to Implement

### 1. Detection
```python
def has_simplified_syntax(rules: dict) -> bool:
    """Check if rules use simplified field names."""
    simplified_fields = ['match', 'to', 'from']
    rules_section = rules.get('rules', {})
    
    for category in ['income', 'expense']:
        for rule in rules_section.get(category, []):
            if any(field in rule for field in simplified_fields):
                return True
    return False
```

### 2. Pattern Conversion
```python
def convert_pattern(pattern: str) -> str:
    """Convert natural language pattern to fnmatch pattern."""
    if pattern.startswith('contains '):
        return f"*{pattern[9:]}*"
    elif pattern.startswith('starts with '):
        return f"{pattern[12:]}*"
    elif pattern.startswith('ends with '):
        return f"*{pattern[10:]}"
    elif pattern.startswith('exactly '):
        return pattern[8:]
    return pattern
```

### 3. Account Resolution
```python
def resolve_account(account_ref: str, shortcuts: dict) -> str:
    """Resolve account shortcut to full path."""
    return shortcuts.get(account_ref, account_ref)
```

### 4. Rules Transformation
```python
def transform_rules(rules: dict, shortcuts: dict) -> dict:
    """Transform simplified syntax to legacy format."""
    for category in ['income', 'expense']:
        for rule in rules.get('rules', {}).get(category, []):
            if 'match' in rule:
                rule['transaction_type'] = convert_pattern(rule.pop('match'))
            if 'to' in rule:
                rule['debit_account'] = resolve_account(rule.pop('to'), shortcuts)
            if 'from' in rule:
                rule['credit_account'] = resolve_account(rule.pop('from'), shortcuts)
    return rules
```

---

## Essential Test Suite

### Core Functionality Tests
```python
class TestFieldAliasing:
    def test_detects_simplified_syntax(self):
        # Test detection of simplified fields
        rules_with_match = {'rules': {'income': [{'match': 'salary'}], 'expense': []}}
        assert has_simplified_syntax(rules_with_match) is True
        
        rules_legacy = {'rules': {'income': [{'transaction_type': '*salary*'}], 'expense': []}}
        assert has_simplified_syntax(rules_legacy) is False
        
        rules_empty = {'rules': {'income': [], 'expense': []}}
        assert has_simplified_syntax(rules_empty) is False

    def test_converts_patterns(self):
        # Test pattern conversion
        assert convert_pattern("contains salary") == "*salary*"
        assert convert_pattern("starts with TRANSFER") == "TRANSFER*"
        assert convert_pattern("ends with PAYMENT") == "*PAYMENT"
        assert convert_pattern("exactly Rent") == "Rent"
        assert convert_pattern("unknown pattern") == "unknown pattern"

    def test_resolves_accounts(self):
        # Test account shortcuts
        shortcuts = {"checking": "Assets:Bank:Checking", "salary": "Income:Salary"}
        assert resolve_account("checking", shortcuts) == "Assets:Bank:Checking"
        assert resolve_account("unknown", shortcuts) == "unknown"
        assert resolve_account("Assets:Full:Path", shortcuts) == "Assets:Full:Path"

    def test_transforms_income_rule(self):
        # Test complete transformation
        rules = {
            'rules': {
                'income': [{
                    'match': 'contains salary',
                    'to': 'checking',
                    'from': 'salary'
                }],
                'expense': []
            }
        }
        shortcuts = {
            'checking': 'Assets:Bank:Checking',
            'salary': 'Income:Employment:Salary'
        }
        
        result = transform_rules(rules, shortcuts)
        income_rule = result['rules']['income'][0]
        
        assert income_rule['transaction_type'] == '*salary*'
        assert income_rule['debit_account'] == 'Assets:Bank:Checking'
        assert income_rule['credit_account'] == 'Income:Employment:Salary'
        assert 'match' not in income_rule
        assert 'to' not in income_rule
        assert 'from' not in income_rule

    def test_preserves_legacy_rules(self):
        # Test backward compatibility
        rules = {
            'rules': {
                'income': [{
                    'transaction_type': '*salary*',
                    'debit_account': 'Assets:Bank',
                    'credit_account': 'Income:Salary'
                }],
                'expense': []
            }
        }
        
        result = transform_rules(rules, {})
        income_rule = result['rules']['income'][0]
        
        assert income_rule['transaction_type'] == '*salary*'
        assert income_rule['debit_account'] == 'Assets:Bank'
        assert income_rule['credit_account'] == 'Income:Salary'
```

### Integration Test
```python
class TestBaseProcessorIntegration:
    def test_load_rules_with_transformation(self):
        # Test BaseProcessor integration
        # Create temporary YAML file with simplified syntax
        # Verify it loads and transforms correctly
        # Ensure it validates against existing schema
        pass
```

---

## Implementation Steps

### Step 1: Core Functions (30 minutes)
1. Write failing tests for each function
2. Implement minimal code to pass tests
3. Refactor for clarity

### Step 2: BaseProcessor Integration (30 minutes)
1. Modify `load_rules()` method to detect simplified syntax
2. Add transformation before validation
3. Ensure backward compatibility

### Step 3: Account Shortcuts (60 minutes)
1. Add support for `accounts:` section in YAML
2. Optional: Add basic bank preset loading
3. Test shortcut resolution

---

## BaseProcessor Integration

```python
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load and validate rules with simplified syntax support."""
    with open(file_path, "r") as file:
        rules = yaml.safe_load(file)
    
    # Transform simplified syntax if present
    if has_simplified_syntax(rules):
        shortcuts = rules.get('accounts', {})
        rules = transform_rules(rules, shortcuts)
    
    # Validate with existing schema
    self._validate_rules(rules, schema_path)
    return rules
```

---

## Example Transformation

### Input (Simplified)
```yaml
accounts:
  checking: "Assets:Personal:Bank:DBS:Checking"
  salary: "Income:Employment:Salary"

rules:
  income:
    - match: "contains salary"
      to: "checking"
      from: "salary"
```

### Output (Legacy)
```yaml
rules:
  income:
    - transaction_type: "*salary*"
      debit_account: "Assets:Personal:Bank:DBS:Checking"
      credit_account: "Income:Employment:Salary"
```

---

## Key Benefits

1. **User-friendly**: `match`, `to`, `from` instead of technical terms
2. **Natural language**: `contains salary` instead of `*salary*`
3. **Account shortcuts**: `checking` instead of full paths
4. **Backward compatible**: Existing files continue to work
5. **Simple implementation**: Minimal code changes required

This streamlined approach delivers the core user value with minimal complexity and development time.