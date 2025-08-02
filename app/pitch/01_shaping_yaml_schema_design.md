# YAML Schema Design: Simple Field Aliasing

## Overview

This specification defines a simple field aliasing system that transforms user-friendly field names to existing schema fields during YAML loading.

**Design Principle**: Simple transformation without changing core schema or architecture.

## Field Mapping

| Simplified Field | Legacy Field | Purpose |
|-----------------|--------------|---------|
| `match` | `transaction_type` | Transaction pattern |
| `to` | `debit_account` | Destination account |
| `from` | `credit_account` | Source account |

## Implementation

### Detection
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

### Transformation
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

### Pattern Conversion
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
    return pattern  # Return as-is if no prefix matches
```

### Account Resolution
```python
def resolve_account(account_ref: str, shortcuts: dict) -> str:
    """Resolve account shortcut to full path."""
    return shortcuts.get(account_ref, account_ref)
```

## Integration with BaseProcessor

```python
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load and validate rules with simplified syntax support."""
    # Load YAML
    with open(file_path, "r") as file:
        rules = yaml.safe_load(file)
    
    # Transform simplified syntax if present
    if has_simplified_syntax(rules):
        shortcuts = rules.get('accounts', {})
        
        # Load bank preset if specified  
        if 'bank' in rules:
            preset_shortcuts = load_bank_preset(rules['bank'])
            shortcuts = {**preset_shortcuts, **shortcuts}
        
        rules = transform_rules(rules, shortcuts)
    
    # Validate with existing schema
    self._validate_rules(rules, schema_path)
    return rules
```

## Example

### Input (Simplified)
```yaml
bank: "dbs"
accounts:
  checking: "Assets:Personal:Bank:DBS:Checking"

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

This simple approach provides user-friendly syntax while maintaining backward compatibility with minimal implementation complexity.