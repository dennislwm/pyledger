# Natural Language Pattern Grammar: Simple String Replacement

## Overview

This specification defines simple string replacement rules to convert natural language patterns to fnmatch patterns.

## Pattern Grammar

| Natural Language | Fnmatch Pattern | Example |
|-----------------|----------------|---------|
| `contains X` | `*X*` | `contains salary` → `*salary*` |
| `starts with X` | `X*` | `starts with GROCERY` → `GROCERY*` |
| `ends with X` | `*X` | `ends with FEE` → `*FEE` |
| `exactly X` | `X` | `exactly Rent Payment` → `Rent Payment` |

## Implementation

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

## Examples

### Business-Friendly Patterns
```yaml
rules:
  income:
    - match: "contains salary"      # User writes this
    - match: "starts with BONUS"    # User writes this
  expense:
    - match: "ends with FEE"        # User writes this
    - match: "exactly Rent"         # User writes this
```

### Converted to Legacy Format
```yaml
rules:
  income:
    - transaction_type: "*salary*"    # System converts to this
    - transaction_type: "BONUS*"      # System converts to this
  expense:
    - transaction_type: "*FEE"        # System converts to this
    - transaction_type: "Rent"        # System converts to this
```

## Benefits

1. **User-friendly**: Business language instead of technical patterns
2. **Simple**: Only 4 pattern types to learn
3. **Backward compatible**: Unknown patterns pass through unchanged
4. **No complexity**: Single function handles all conversions

This approach eliminates the need for users to understand fnmatch syntax while maintaining full pattern matching capability.