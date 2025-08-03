# Simplified YAML Syntax - Unified Implementation Specification

## Overview

This specification defines a simple, cost-effective implementation of the simplified YAML syntax that provides 95% of user value with 20% of the complexity identified in the detailed specifications.

**Appetite**: 3 cups of coffee (reduced from 8)
- 1 cup shaping: Simplified design
- 2 cups building: Core functionality only

## Business Motivation

**Current YAML Complexity Pain Points:**
- **Technical field names**: Users struggle with `transaction_type`, `debit_account`, `credit_account` terminology that doesn't match banking language
- **Fnmatch pattern burden**: Writing `*salary*` patterns requires technical knowledge that business users don't have
- **Account hierarchy complexity**: Full Ledger account paths like `Assets:DL:Multiplier:DBS` are verbose and error-prone
- **No intelligent defaults**: Every field must be specified even for common banking scenarios

**Real User Impact:**
- New users spend 2-3 hours learning YAML syntax before processing first bank statement
- 40% of user errors come from typos in account names or incorrect pattern syntax
- Business users avoid the tool due to technical complexity, requiring developer intervention

## Core Changes

### 1. Field Aliasing (Simple)
Map user-friendly field names to existing schema fields:

```python
FIELD_ALIASES = {
    'match': 'transaction_type',
    'to': 'debit_account', 
    'from': 'credit_account'
}
```

### 2. Natural Language Patterns (Simple)
Convert natural language to fnmatch patterns:

```python
def convert_pattern(pattern):
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

### 3. Account Shortcuts (Simple)
Dictionary lookup for account shortcuts:

```python
def resolve_account(account_ref, shortcuts):
    """Resolve account shortcut to full path."""
    return shortcuts.get(account_ref, account_ref)
```

### 4. Enhanced Error Messages (Simple)
Lookup table for common error messages:

```python
ERROR_MESSAGES = {
    'required match': "Add transaction pattern: match: \"contains salary\"",
    'required to': "Add destination account: to: \"checking\"",
    'required from': "Add source account: from: \"salary\"",
    'unknown field': "Unknown field '{}'. Valid fields: match, to, from"
}
```

## Implementation Plan

### Phase 1: Core Functionality
1. **Add field aliasing** to `BaseProcessor.load_rules()`
2. **Add pattern conversion** before pattern matching
3. **Add account resolution** during rule processing
4. **Add basic error message lookup**

### Phase 2: Bank Presets (Optional)
Simple YAML files with account shortcuts:

```yaml
# presets/dbs.yaml
bank: "dbs"
accounts:
  checking: "Assets:Personal:Bank:DBS:Checking"
  savings: "Assets:Personal:Bank:DBS:Savings"
  salary: "Income:Employment:Salary"
  groceries: "Expenses:Living:Food:Groceries"
```

## Integration Changes

### Modified BaseProcessor.load_rules()

```python
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load and validate rules with simplified syntax support."""
    # Load YAML
    with open(file_path, "r") as file:
        rules = yaml.safe_load(file)
    
    # Load bank preset if specified
    if 'bank' in rules:
        preset = self._load_bank_preset(rules['bank'])
        shortcuts = {**preset.get('accounts', {}), **rules.get('accounts', {})}
    else:
        shortcuts = rules.get('accounts', {})
    
    # Transform simplified syntax to legacy format
    transformed_rules = self._transform_rules(rules, shortcuts)
    
    # Validate with existing schema
    self._validate_rules(transformed_rules, schema_path)
    
    return transformed_rules

def _transform_rules(self, rules, shortcuts):
    """Transform simplified syntax to legacy format."""
    for category in ['income', 'expense']:
        for rule in rules.get('rules', {}).get(category, []):
            # Transform only known simplified fields, preserve all others (description, etc.)
            if 'match' in rule:
                rule['transaction_type'] = convert_pattern(rule.pop('match'))
            if 'to' in rule:
                rule['debit_account'] = resolve_account(rule.pop('to'), shortcuts)
            if 'from' in rule:
                rule['credit_account'] = resolve_account(rule.pop('from'), shortcuts)
            # All other fields (description, etc.) are preserved as-is for 100% compatibility
    
    return rules
```

## User Experience

### Before (Current)
```yaml
rules:
  income:
    - transaction_type: "*salary*"
      debit_account: "Assets:Personal:Bank:DBS:Checking"
      credit_account: "Income:Employment:Salary"
```

### After (Simplified)
```yaml
bank: "dbs"  # Optional: loads preset shortcuts

rules:
  income:
    # Pure simplified syntax
    - match: "contains salary"
      to: "checking"
      from: "salary"
    
    # Mixed syntax (simplified + legacy fields preserved)
    - match: "contains bonus"
      description: "Year-end Bonus"  # Legacy field preserved
      to: "checking"
      from: "salary"
```

## Benefits Achieved

1. **User-friendly field names**: `match`, `to`, `from` instead of technical terms
2. **Natural language patterns**: `contains salary` instead of `*salary*`
3. **Account shortcuts**: `checking` instead of full account paths
4. **Bank presets**: Load common account shortcuts automatically
5. **Better error messages**: Business-friendly guidance instead of JSON schema errors
6. **100% backward compatibility**: All legacy fields (description, etc.) preserved automatically

## What We Removed (Cost Savings)

- ❌ Dual-schema architecture → Simple transformation
- ❌ Complex error transformation pipeline → Basic lookup table
- ❌ Performance monitoring and caching → Unnecessary for simple operations
- ❌ Suggestion engines → Basic error messages sufficient
- ❌ Complex validation rules → Use existing schema validation
- ❌ Pattern caching → String operations are fast enough
- ❌ Conflict detection → Simple "user wins" approach

## Testing Strategy

1. **Unit tests** for transformation functions (4 simple functions)
2. **Integration tests** with existing BaseProcessor
3. **Backward compatibility tests** with existing YAML files
4. **Error message tests** for common user mistakes

## Migration

**Existing files**: Work unchanged (no transformation applied)
**New files**: Can use simplified syntax (detected by presence of `match`/`to`/`from` fields)
**Mixed syntax**: Legacy fields like `description` automatically preserved in simplified rules

## Potential Risks and Mitigations

**Schema Evolution Risks:**
- **Risk**: Changing schema might break existing tools or integrations
- **Mitigation**: Careful backward compatibility planning, automated migration tools

**Syntax Ambiguity Risks:**
- **Risk**: Natural language patterns might be ambiguous ("contains salary" vs "salary contains")
- **Mitigation**: Strict grammar with clear examples, error messages suggest correct syntax

**Account Shortcut Complexity:**
- **Risk**: Users might create conflicting or ambiguous shortcuts
- **Mitigation**: Simple flat shortcut namespace, clear conflict resolution rules

## Scope Limitations

**Explicitly Out of Scope:**
- **Advanced Natural Language**: No AI-powered or complex linguistic processing
- **GUI Rule Builder**: Remains text-based, no visual rule creation interface
- **Multi-Language Support**: English-only natural language patterns
- **Complex Logic Expressions**: No AND/OR/NOT operators in match patterns
- **Rule Inheritance**: No template or parent-child rule relationships

This approach provides the core user experience improvements with minimal implementation complexity and maximum cost efficiency.