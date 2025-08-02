# Bank Preset Specification for Ledger Application

## Overview

This document defines the comprehensive specification for bank preset files that provide default configurations, account structures, and validation rules for different banks in the Ledger application.

**Version**: 1.0.0  
**Purpose**: Enable simplified YAML syntax through bank presets, account shortcuts, and enhanced validation  
**Integration**: Works with existing rules system and processors  

## File Structure

### Recommended Directory Layout
```
app/
├── presets/
│   ├── banks/
│   │   ├── dbs.yaml           # DBS Bank preset
│   │   ├── uob.yaml           # UOB Bank preset
│   │   ├── ocbc.yaml          # OCBC Bank preset
│   │   ├── hsbc.yaml          # HSBC Bank preset
│   │   └── maybank.yaml       # Maybank preset
│   └── schema/
│       └── bank_preset_schema.json  # JSON Schema validation
```

## Bank Preset Schema

### Required Fields

- **bank**: Unique bank identifier (lowercase, alphanumeric, underscores)
- **version**: Semantic version of the preset file
- **presets**: Main configuration object containing:
  - **accounts**: Predefined account shortcuts
  - **input**: Default input configuration for bank statements

### Optional Fields

- **metadata**: Bank information (display_name, country, description, author, last_updated)
- **output**: Default output configuration
- **patterns**: Common transaction patterns for the bank
- **validation**: Bank-specific validation rules and constraints

## Account Shortcuts System

### Format
Account shortcuts map simple names to full Ledger account paths:

```yaml
accounts:
  checking: "Assets:Personal:Bank:DBS:Checking"
  savings: "Assets:Personal:Bank:DBS:Savings"
  credit_card: "Liabilities:Personal:CreditCard:DBS"
  salary: "Income:Employment:Salary"
  groceries: "Expenses:Living:Food:Groceries"
```

### Naming Conventions
- Use lowercase with underscores for shortcut names
- Follow pattern: `^[a-z][a-z0-9_]*$`
- Maximum 200 characters for account paths
- Account paths must start with uppercase letter

### Common Account Categories
- **Assets**: `checking`, `savings`, `investment`
- **Liabilities**: `credit_card`, `loan`, `mortgage`
- **Income**: `salary`, `bonus`, `interest`, `dividends`
- **Expenses**: `groceries`, `utilities`, `transport`, `dining`, `entertainment`, `medical`

## Input Configuration

### CSV Format
```yaml
input:
  csv:
    header:
      date: "Transaction Date"
      description: "Client Reference"
      amount: "Amount"
      deposit: "Credit Amount"
      withdraw: "Debit Amount"
```

### Excel Format
```yaml
input:
  xls:
    header:
      date: "Transaction Date"
      description: "Description"
      amount: "Amount"
    sheet:
      first_row: 2
```

## Transaction Patterns

### Income Patterns
```yaml
patterns:
  income:
    - name: "salary"
      pattern: "contains salary"
      description: "Monthly salary payments"
      suggested_accounts:
        to: "checking"
        from: "salary"
```

### Expense Patterns
```yaml
patterns:
  expense:
    - name: "grocery"
      pattern: "contains grocery"
      description: "Grocery store purchases"
      suggested_accounts:
        to: "groceries"
        from: "checking"
```

## Usage in Rules Files

### Basic Usage
```yaml
# User's rules file leveraging DBS preset
bank: "dbs"  # Loads DBS preset automatically

rules:
  income:
    - match: "contains salary"
      to: "checking"      # Uses preset account
      from: "salary"      # Uses preset account
      
  expense:
    - match: "contains grocery"
      to: "groceries"     # Uses preset account
      from: "checking"    # Uses preset account
```

### Override Preset Accounts
```yaml
bank: "dbs"

# Override or add to preset accounts
accounts:
  # Inherits all DBS preset accounts (checking, savings, etc.)
  emergency_fund: "Assets:Personal:Emergency:Fund"  # Additional account
  checking: "Assets:Personal:Bank:DBS:Main"          # Override preset

rules:
  expense:
    - match: "contains emergency"
      to: "emergency_fund"  # Uses custom account
      from: "checking"      # Uses overridden account
```

## Validation Rules

### Account Pattern Validation
```yaml
validation:
  account_patterns:
    assets: "^Assets:Personal:Bank:DBS:.*"
    liabilities: "^Liabilities:Personal:.*:DBS.*"
    income: "^Income:.*"
    expenses: "^Expenses:.*"
  required_accounts: ["checking"]
  reserved_shortcuts: ["dbs_checking", "dbs_savings"]
```

### Validation Process
1. **Schema validation**: All preset files validated against JSON schema (YAML files validated using JSON schema)
2. **Account pattern matching**: Account paths must match defined patterns
3. **Required accounts**: Specified shortcuts must be defined
4. **Reserved shortcuts**: Prevent conflicts with bank-specific names

## Example: DBS Bank Preset

```yaml
bank: "dbs"
version: "1.0.0"
metadata:
  display_name: "DBS Bank"
  country: "SG"
  description: "DBS Bank Singapore preset with common account structures"
  author: "Ledger Community"
  last_updated: "2024-01-15"
presets:
  accounts:
    checking: "Assets:Personal:Bank:DBS:Checking"
    savings: "Assets:Personal:Bank:DBS:Savings"
    investment: "Assets:Personal:Investment:DBS:Portfolio"
    credit_card: "Liabilities:Personal:CreditCard:DBS"
    salary: "Income:Employment:Salary"
    bonus: "Income:Employment:Bonus"
    interest: "Income:Investment:Interest"
    groceries: "Expenses:Living:Food:Groceries"
    utilities: "Expenses:Living:Utilities:Electric"
    transport: "Expenses:Living:Transport:Public"
    dining: "Expenses:Living:Food:Dining"
    entertainment: "Expenses:Personal:Entertainment"
    medical: "Expenses:Personal:Healthcare"
  input:
    csv:
      header:
        date: "Transaction Date"
        description: "Client Reference"
        amount: "Amount"
        deposit: "Credit Amount"
        withdraw: "Debit Amount"
  output:
    amount:
      prefix: "$"
  patterns:
    income:
      - name: "salary"
        pattern: "contains salary"
        description: "Monthly salary payments"
        suggested_accounts:
          to: "checking"
          from: "salary"
      - name: "bonus"
        pattern: "contains bonus"
        description: "Bonus payments"
        suggested_accounts:
          to: "checking"
          from: "bonus"
    expense:
      - name: "grocery"
        pattern: "contains grocery"
        description: "Grocery store purchases"
        suggested_accounts:
          to: "groceries"
          from: "checking"
      - name: "utilities"
        pattern: "contains utilities"
        description: "Utility bill payments"
        suggested_accounts:
          to: "utilities"
          from: "checking"
validation:
  account_patterns:
    assets: "^Assets:Personal:Bank:DBS:.*"
    liabilities: "^Liabilities:Personal:.*:DBS.*"
  required_accounts: ["checking"]
  reserved_shortcuts: ["dbs_checking", "dbs_savings"]
```

## Integration Points

### BaseProcessor Integration
- Modify `BaseProcessor.load_rules()` to support bank preset loading via the `bank` field
- Bank presets provide default account shortcuts that can be overridden by user-defined accounts
- Validation occurs during rules file loading

### Account Resolution
- Bank preset accounts are loaded first
- User-defined accounts override preset accounts with same shortcut name
- Account resolution has O(1) lookup time through hash maps

### Pattern Suggestions
- Bank-specific patterns can be used for autocomplete or validation suggestions
- Patterns include natural language matching and suggested account mappings

## Performance Considerations

- **Caching**: Bank presets should be cached after first load
- **Validation**: Schema validation happens during preset file creation, not at runtime (YAML files validated using JSON schema)
- **Lookup**: Account resolution uses hash maps for O(1) access time
- **Memory**: Presets loaded on-demand and shared across processor instances

## Migration Path

### Phase 1: Core Infrastructure
1. Create bank preset schema and validation
2. Implement preset loading in BaseProcessor
3. Add account shortcut resolution

### Phase 2: Bank Presets
1. Create common bank presets (DBS, UOB, OCBC)
2. Add pattern matching and suggestions
3. Implement validation rules

### Phase 3: Enhanced Features
1. Add natural language pattern grammar
2. Implement advanced validation
3. Create preset management tools

## Benefits

1. **Simplified Configuration**: Users only need to specify `bank: "dbs"` instead of full account structures
2. **Consistency**: Standardized account naming across users of the same bank
3. **Reduced Errors**: Validation prevents common account naming mistakes
4. **Pattern Recognition**: Bank-specific transaction patterns improve automation
5. **Maintainability**: Centralized bank configurations reduce duplication
6. **Extensibility**: Easy to add new banks and enhance existing presets