# Enhanced Validation System: Simple Error Message Lookup

## Overview

This specification defines a simple error message lookup system that converts common JSON schema errors to user-friendly messages.

## Implementation

### Error Message Lookup
```python
ERROR_MESSAGES = {
    'required match': "Add transaction pattern: match: \"contains salary\"",
    'required to': "Add destination account: to: \"checking\"",
    'required from': "Add source account: from: \"salary\"",
    'required transaction_type': "Add transaction pattern: transaction_type: \"*salary*\"",
    'required debit_account': "Add destination account: debit_account: \"Assets:Bank:Checking\"",
    'required credit_account': "Add source account: credit_account: \"Income:Salary\"",
    'unknown field': "Unknown field '{}'. Valid fields: match, to, from"
}

def get_friendly_error(error_key: str, field_name: str = None) -> str:
    """Get user-friendly error message."""
    if field_name and '{}' in ERROR_MESSAGES.get(error_key, ''):
        return ERROR_MESSAGES[error_key].format(field_name)
    return ERROR_MESSAGES.get(error_key, f"Validation error: {error_key}")
```

### Enhanced BaseProcessor Error Handling
```python
def _validate_rules(self, rules: dict, schema_path: str):
    """Validate rules with enhanced error messages."""
    try:
        # Existing JSON schema validation
        with open(schema_path, 'r') as file:
            schema = json.load(file)
        
        jsonschema.validate(rules, schema)
        
    except jsonschema.ValidationError as e:
        # Convert to friendly error message
        error_key = self._extract_error_key(e)
        friendly_message = get_friendly_error(error_key)
        
        raise ValidationError(f"Rule validation failed:\n{friendly_message}")

def _extract_error_key(self, validation_error) -> str:
    """Extract simple error key from JSON schema validation error."""
    message = str(validation_error.message).lower()
    
    if 'required property' in message:
        # Extract field name from error
        if "'match'" in message:
            return 'required match'
        elif "'transaction_type'" in message:
            return 'required transaction_type'
        # ... etc for other fields
    
    return 'validation error'
```

## Error Message Examples

### Before (Technical)
```
ValidationError: 'match' is a required property at rules.income[0]
```

### After (User-Friendly)
```
Rule validation failed:
Add transaction pattern: match: "contains salary"
```

### Before (Technical)
```
ValidationError: Additional properties are not allowed ('mach' was unexpected)
```

### After (User-Friendly)
```
Rule validation failed:
Unknown field 'mach'. Valid fields: match, to, from
```

## Integration

Add to BaseProcessor.load_rules():
```python
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load and validate rules with enhanced error messages."""
    try:
        # Load and transform rules (existing logic)
        rules = self._load_and_transform_rules(file_path)
        
        # Validate with enhanced error handling
        self._validate_rules(rules, schema_path)
        
        return rules
        
    except ValidationError:
        raise  # Re-raise with friendly message
    except Exception as e:
        raise ValidationError(f"Error loading rules: {str(e)}")
```

## Benefits

1. **User-friendly**: Business language instead of technical JSON schema errors
2. **Actionable**: Shows exactly what to add to fix the error
3. **Simple**: Basic string lookup, no complex error transformation
4. **Examples**: Provides concrete examples in error messages
5. **Minimal code**: Single lookup function handles all error improvement

This approach improves error messages with minimal implementation complexity using a simple lookup table.