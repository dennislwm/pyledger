# Account Shortcuts System: Simple Dictionary Lookup

## Overview

This specification defines a simple account shortcuts system that maps friendly names to full Ledger account paths using basic dictionary lookup.

## Implementation

### Account Resolution
```python
def resolve_account(account_ref: str, shortcuts: dict) -> str:
    """Resolve account shortcut to full path."""
    return shortcuts.get(account_ref, account_ref)
```

### Bank Preset Loading
```python
def load_bank_preset(bank_name: str) -> dict:
    """Load account shortcuts from bank preset file."""
    try:
        with open(f"presets/{bank_name}.yaml", 'r') as file:
            preset = yaml.safe_load(file)
            return preset.get('accounts', {})
    except FileNotFoundError:
        return {}  # No preset found, return empty
```

## Usage

### Define Shortcuts
```yaml
bank: "dbs"  # Optional: loads preset shortcuts

accounts:
  # User-defined shortcuts (override preset)
  checking: "Assets:Personal:Bank:DBS:Checking"
  savings: "Assets:Personal:Bank:DBS:Savings"
  salary: "Income:Employment:Salary"
  groceries: "Expenses:Living:Food:Groceries"

rules:
  income:
    - match: "contains salary"
      to: "checking"     # Uses shortcut
      from: "salary"     # Uses shortcut
```

### Resolution Order
1. **User shortcuts** (in `accounts:` section) take priority
2. **Bank preset shortcuts** (from `bank:` preset file) used as fallback
3. **Literal values** returned if no shortcut found

## Bank Preset Format
```yaml
# presets/dbs.yaml
bank: "dbs"
accounts:
  checking: "Assets:Personal:Bank:DBS:Checking"
  savings: "Assets:Personal:Bank:DBS:Savings"
  credit_card: "Liabilities:Personal:CreditCard:DBS"
  salary: "Income:Employment:Salary"
  groceries: "Expenses:Living:Food:Groceries"
```

## Benefits

1. **Simple**: Dictionary lookup with fallback
2. **User control**: User shortcuts override presets
3. **Bank presets**: Common shortcuts predefined
4. **No complexity**: No validation, caching, or error handling needed
5. **Backward compatible**: Full account paths still work

This approach provides account shortcuts with minimal implementation complexity using standard dictionary operations.