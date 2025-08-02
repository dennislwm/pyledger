# YAML Schema Design: Simplified Syntax with Smart Defaults

## Overview and Design Philosophy

This specification defines a new YAML schema that transforms rule authoring from technical configuration to business-friendly rule definition. The design maintains full backward compatibility while introducing intuitive field names, smart defaults, and reduced boilerplate.

### Design Principles
1. **Business Language Over Technical Terms**: Replace `transaction_type`, `debit_account`, `credit_account` with `match`, `to`, `from`
2. **Progressive Disclosure**: Complex features remain available but simple cases require minimal configuration
3. **Schema Evolution**: Extend existing schema rather than replace, ensuring migration path exists
4. **Validation Enhancement**: Schema provides foundation for improved error messaging

## New YAML Schema Structure

### Current Schema vs. Simplified Schema

**Current Format:**
```yaml
rules:
  income:
    - transaction_type: "*salary*"
      debit_account: "Assets:DL:Multiplier:DBS"
      credit_account: "Income:DL:DBS:Rebate"
  expense:
    - transaction_type: "*grocery*"
      debit_account: "Expenses:DBS:Multiplier"
      credit_account: "Assets:DL:Multiplier:DBS"
```

**New Simplified Format:**
```yaml
bank: "dbs"  # Optional preset loading
accounts:
  checking: "Assets:DL:Multiplier:DBS"
  salary: "Income:DL:DBS:Rebate"
  groceries: "Expenses:DBS:Multiplier"

rules:
  income:
    - match: "contains salary"
      to: "checking"
      from: "salary"
  expense:
    - match: "contains grocery"
      to: "groceries"
      from: "checking"
```

### Field Mapping Specification

#### Core Field Transformations
| Current Field | New Field | Purpose | Notes |
|--------------|-----------|---------|-------|
| `transaction_type` | `match` | Pattern matching | Supports natural language syntax |
| `debit_account` | `to` | Destination account | Maps to account shortcuts |
| `credit_account` | `from` | Source account | Maps to account shortcuts |
| `description` | `description` | Output description | Unchanged, optional |

#### New Top-Level Fields
| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `bank` | string | No | Loads bank-specific presets |
| `accounts` | object | No | Account shortcut definitions |
| `rules` | object | Yes | Transaction rules (existing structure) |
| `input` | object | No | Input configuration (unchanged) |
| `output` | object | No | Output configuration (unchanged) |

## Schema Evolution Strategy

### Dual-Schema Support Architecture

The system will support both legacy and simplified schemas through a schema detection and transformation layer:

```python
class SchemaDetector:
    def detect_schema_version(self, rules_dict: dict) -> str:
        """Detect whether rules use legacy or simplified schema."""
        if 'bank' in rules_dict or 'accounts' in rules_dict:
            return 'simplified'
        if self._has_simplified_fields(rules_dict):
            return 'simplified'
        return 'legacy'

    def _has_simplified_fields(self, rules_dict: dict) -> bool:
        """Check for simplified field names in rules."""
        for category in ['income', 'expense']:
            for rule in rules_dict.get('rules', {}).get(category, []):
                if 'match' in rule or 'to' in rule or 'from' in rule:
                    return True
        return False
```

### Schema Transformation Layer

```python
class SchemaTransformer:
    def transform_to_legacy(self, simplified_rules: dict) -> dict:
        """Transform simplified schema to legacy format for processing."""
        legacy_rules = {}

        # Resolve account shortcuts
        accounts = simplified_rules.get('accounts', {})

        # Transform rules
        for category in ['income', 'expense']:
            legacy_rules.setdefault('rules', {})[category] = []
            for rule in simplified_rules.get('rules', {}).get(category, []):
                legacy_rule = {
                    'transaction_type': self._convert_match_pattern(rule['match']),
                    'debit_account': self._resolve_account(rule['to'], accounts),
                    'credit_account': self._resolve_account(rule['from'], accounts)
                }
                if 'description' in rule:
                    legacy_rule['description'] = rule['description']
                legacy_rules['rules'][category].append(legacy_rule)

        return legacy_rules
```

## Enhanced JSON Schema Definition

### New Schema Structure (schema_v2.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["rules"],
  "additionalProperties": false,
  "properties": {
    "bank": {
      "type": "string",
      "enum": ["dbs", "uob", "ocbc", "hsbc", "maybank"],
      "description": "Bank preset for default configurations"
    },
    "accounts": {
      "type": "object",
      "patternProperties": {
        "^[a-z][a-z0-9_]*$": {
          "type": "string",
          "pattern": "^[A-Za-z][A-Za-z0-9:_\\-]*$"
        }
      },
      "description": "Account shortcut definitions"
    },
    "rules": {
      "type": "object",
      "required": ["income", "expense"],
      "additionalProperties": false,
      "properties": {
        "income": {
          "type": "array",
          "items": {"$ref": "#/$defs/simplified_transaction"},
          "minItems": 1
        },
        "expense": {
          "type": "array",
          "items": {"$ref": "#/$defs/simplified_transaction"},
          "minItems": 1
        }
      }
    }
  },
  "$defs": {
    "simplified_transaction": {
      "type": "object",
      "required": ["match", "to", "from"],
      "additionalProperties": false,
      "properties": {
        "match": {
          "type": "string",
          "pattern": "^(contains|starts with|ends with|exactly)\\s+.+$|^\\*.+\\*$|^.+\\*$|^\\*.+$|^[^*]+$",
          "description": "Natural language or fnmatch pattern"
        },
        "to": {
          "type": "string",
          "description": "Destination account (shortcut or full path)"
        },
        "from": {
          "type": "string",
          "description": "Source account (shortcut or full path)"
        },
        "description": {
          "type": "string",
          "description": "Output description override"
        }
      }
    }
  }
}
```

### Legacy Schema Compatibility (schema.json)

The existing `schema.json` remains unchanged to support legacy YAML files. The system will:

1. Attempt validation against simplified schema first
2. Fall back to legacy schema if simplified validation fails
3. Transform simplified to legacy format for processing

## Natural Language Pattern Conversion

### Pattern Grammar Specification

| Natural Language | Generated Pattern | Example |
|-----------------|-------------------|---------|
| `contains X` | `*X*` | `contains salary` → `*salary*` |
| `starts with X` | `X*` | `starts with GROCERY` → `GROCERY*` |
| `ends with X` | `*X` | `ends with FEE` → `*FEE` |
| `exactly X` | `X` | `exactly Rent Payment` → `Rent Payment` |

### Pattern Conversion Implementation

```python
class PatternConverter:
    PATTERN_REGEX = re.compile(r'^(contains|starts with|ends with|exactly)\s+(.+)$', re.IGNORECASE)

    def convert_natural_language(self, pattern: str) -> str:
        """Convert natural language pattern to fnmatch pattern."""
        match = self.PATTERN_REGEX.match(pattern.strip())
        if not match:
            # Return as-is if not natural language (legacy fnmatch pattern)
            return pattern

        operator, value = match.groups()
        operator = operator.lower()

        if operator == 'contains':
            return f"*{value}*"
        elif operator == 'starts with':
            return f"{value}*"
        elif operator == 'ends with':
            return f"*{value}"
        elif operator == 'exactly':
            return value

        return pattern  # Fallback
```

## Account Resolution System

### Account Shortcut Specification

Account shortcuts provide a simple alias system for complex Ledger account hierarchies:

```yaml
accounts:
  # Personal accounts
  checking: "Assets:Personal:Bank:Checking"
  savings: "Assets:Personal:Bank:Savings"
  investment: "Assets:Personal:Investment:Portfolio"

  # Income categories
  salary: "Income:Employment:Salary"
  bonus: "Income:Employment:Bonus"
  dividend: "Income:Investment:Dividends"

  # Expense categories
  groceries: "Expenses:Living:Food:Groceries"
  utilities: "Expenses:Living:Utilities"
  transport: "Expenses:Living:Transport"
```

### Resolution Algorithm

```python
class AccountResolver:
    def __init__(self, accounts: dict, bank_presets: dict = None):
        self.accounts = accounts or {}
        self.bank_presets = bank_presets or {}

    def resolve_account(self, account_ref: str) -> str:
        """Resolve account reference to full path."""
        # Direct shortcut lookup
        if account_ref in self.accounts:
            return self.accounts[account_ref]

        # Bank preset lookup
        if account_ref in self.bank_presets:
            return self.bank_presets[account_ref]

        # Return as-is if it looks like a full path
        if ':' in account_ref and account_ref[0].isupper():
            return account_ref

        # Error: unresolved shortcut
        raise ValueError(f"Unresolved account reference: '{account_ref}'")
```

## Integration with BaseProcessor Architecture

### Modified BaseProcessor.load_rules() Method

```python
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load and transform rules with schema detection."""
    # Load raw YAML
    with open(file_path, "r") as file:
        raw_rules = yaml.safe_load(file)

    # Detect schema version
    detector = SchemaDetector()
    schema_version = detector.detect_schema_version(raw_rules)

    if schema_version == 'simplified':
        # Validate against simplified schema
        simplified_schema_path = schema_path.replace('.json', '_v2.json')
        self._validate_schema(raw_rules, simplified_schema_path)

        # Transform to legacy format for processing
        transformer = SchemaTransformer()
        legacy_rules = transformer.transform_to_legacy(raw_rules)

        # Store original for reference
        self.original_rules = raw_rules
        return legacy_rules
    else:
        # Legacy validation and processing
        self._validate_schema(raw_rules, schema_path)
        return raw_rules

def _validate_schema(self, rules: dict, schema_path: str):
    """Validate rules against specified schema."""
    with open(schema_path, "r") as sf:
        schema = json.load(sf)

    try:
        validate(rules, schema)
    except ValidationError as e:
        # Enhanced error handling (see validation specification)
        raise ValidationError(self._enhance_error_message(e, rules))
```

## Implementation Phases

### Phase 1: Schema Foundation (1 cup)
- Create simplified JSON schema (schema_v2.json)
- Implement schema detection logic
- Add dual-schema validation support

### Phase 2: Pattern Conversion (1.5 cups)
- Implement natural language pattern parser
- Add pattern conversion to schema transformer
- Create comprehensive pattern test suite

### Phase 3: Account Resolution (1.5 cups)
- Implement account shortcut system
- Add bank preset loading infrastructure
- Create account resolution validation

### Phase 4: Integration (1 cup)
- Modify BaseProcessor for dual-schema support
- Update existing processors for compatibility
- Create migration utility for existing files

## Acceptance Criteria

### Schema Validation
- [ ] Simplified schema validates all example configurations correctly
- [ ] Legacy schema continues to validate existing files unchanged
- [ ] Schema detection correctly identifies format in 100% of test cases
- [ ] Transformation produces functionally equivalent legacy rules

### Pattern Conversion
- [ ] All natural language patterns convert to correct fnmatch equivalents
- [ ] Legacy fnmatch patterns pass through unchanged
- [ ] Pattern validation prevents invalid syntax
- [ ] Performance impact < 10ms for typical rule sets

### Account Resolution
- [ ] Account shortcuts resolve to correct full paths
- [ ] Unresolved shortcuts produce clear error messages
- [ ] Circular references detected and prevented
- [ ] Bank presets load and merge correctly with user accounts

### Integration Compatibility
- [ ] All existing unit tests pass with dual-schema support
- [ ] BaseProcessor maintains same public interface
- [ ] Performance degradation < 5% for legacy files
- [ ] Memory usage increase < 20% for schema transformation
