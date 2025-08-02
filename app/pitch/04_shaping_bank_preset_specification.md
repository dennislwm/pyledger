# Bank Preset Specification: Simple Account Collections

## Overview

Bank presets are simple YAML files containing account shortcuts for specific banks.

## File Format

```yaml
# presets/dbs.yaml
bank: "dbs"
accounts:
  checking: "Assets:Personal:Bank:DBS:Checking"
  savings: "Assets:Personal:Bank:DBS:Savings"
  credit_card: "Liabilities:Personal:CreditCard:DBS"
  salary: "Income:Employment:Salary"
  groceries: "Expenses:Living:Food:Groceries"
  utilities: "Expenses:Living:Utilities"
  transport: "Expenses:Living:Transport"
```

## Directory Structure
```
app/
├── presets/
│   ├── dbs.yaml           # DBS Bank preset
│   ├── uob.yaml           # UOB Bank preset
│   ├── ocbc.yaml          # OCBC Bank preset
│   └── hsbc.yaml          # HSBC Bank preset
```

## Usage in Rules Files

```yaml
bank: "dbs"  # Loads preset account shortcuts

# Optional: override or add accounts
accounts:
  emergency: "Assets:Personal:Emergency:Fund"

rules:
  income:
    - match: "contains salary"
      to: "checking"      # Uses DBS preset shortcut
      from: "salary"      # Uses DBS preset shortcut
  expense:
    - match: "contains grocery"
      to: "groceries"     # Uses DBS preset shortcut
      from: "checking"    # Uses DBS preset shortcut
```

## Loading Implementation

```python
def load_bank_preset(bank_name: str) -> dict:
    """Load account shortcuts from bank preset file."""
    try:
        with open(f"presets/{bank_name}.yaml", 'r') as file:
            preset = yaml.safe_load(file)
            return preset.get('accounts', {})
    except FileNotFoundError:
        return {}  # No preset found, return empty shortcuts
```

## Account Resolution

```python
def resolve_accounts(rules: dict) -> dict:
    """Resolve account shortcuts in rules."""
    shortcuts = {}
    
    # Load bank preset shortcuts
    if 'bank' in rules:
        shortcuts.update(load_bank_preset(rules['bank']))
    
    # Add user shortcuts (override preset)
    shortcuts.update(rules.get('accounts', {}))
    
    return shortcuts
```

## Benefits

1. **Reduced typing**: `checking` instead of full account path
2. **Consistency**: Standardized shortcuts across users
3. **Bank-specific**: Each bank has appropriate account structure
4. **Simple**: Just account name mappings
5. **User override**: User accounts take precedence over presets

This approach provides bank-specific account shortcuts with minimal complexity.