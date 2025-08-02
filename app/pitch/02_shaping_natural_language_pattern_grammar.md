# Natural Language Pattern Grammar: Business-Friendly Pattern Specification

## Overview and Design Philosophy

This specification defines a formal grammar for converting business-friendly natural language patterns into fnmatch patterns used by the existing BaseProcessor pattern matching system. The design prioritizes readability and business user accessibility while maintaining full compatibility with existing technical pattern capabilities.

### Design Principles
1. **Business Language First**: Patterns read like natural business descriptions
2. **Unambiguous Grammar**: Clear, predictable conversion rules with no ambiguity
3. **Backward Compatibility**: Legacy fnmatch patterns continue to work unchanged
4. **Performance Optimized**: Pattern conversion happens once during rule loading, not per transaction
5. **Error Prevention**: Grammar validation prevents invalid pattern construction

## Pattern Grammar Specification

### Core Grammar Rules

#### Natural Language Pattern Syntax
```
PATTERN := OPERATOR WHITESPACE VALUE
OPERATOR := "contains" | "starts with" | "ends with" | "exactly"
WHITESPACE := /\s+/
VALUE := /[^\r\n]+/
```

#### Conversion Table
| Operator | Input Example | Generated Pattern | Regex Equivalent |
|----------|---------------|-------------------|------------------|
| `contains` | `contains salary` | `*salary*` | `.*salary.*` |
| `starts with` | `starts with GROCERY` | `GROCERY*` | `GROCERY.*` |
| `ends with` | `ends with FEE` | `*FEE` | `.*FEE` |
| `exactly` | `exactly Rent Payment` | `Rent Payment` | `Rent Payment` |

### Advanced Pattern Features

#### Case Sensitivity Handling
All natural language patterns are **case-insensitive** by design:
```yaml
# These are equivalent
match: "contains SALARY"
match: "contains salary"
match: "contains Salary"
# All generate: *salary* (lowercase)
```

#### Whitespace and Special Character Handling
```yaml
# Whitespace is preserved in VALUES
match: "contains salary payment"    # → *salary payment*
match: "starts with GROCERY STORE"  # → GROCERY STORE*

# Special characters are preserved
match: "contains bill-pay"          # → *bill-pay*
match: "ends with (fee)"           # → *(fee)
```

#### Legacy Pattern Passthrough
Patterns not matching natural language grammar pass through unchanged:
```yaml
# Legacy fnmatch patterns (unchanged)
match: "*salary*"           # → *salary*
match: "GROCERY*"          # → GROCERY*
match: "Rent Payment"      # → Rent Payment

# Mixed wildcards (unchanged)
match: "*bill*payment*"    # → *bill*payment*
match: "???-SALARY"       # → ???-SALARY
```

## Pattern Conversion Implementation

### Core Pattern Converter Class

```python
import re
from typing import Optional, Tuple

class PatternConverter:
    """Converts natural language patterns to fnmatch patterns."""

    # Grammar regex for natural language patterns
    NATURAL_PATTERN_REGEX = re.compile(
        r'^(contains|starts\s+with|ends\s+with|exactly)\s+(.+)$',
        re.IGNORECASE
    )

    def __init__(self):
        self.conversion_stats = {
            'natural_language': 0,
            'legacy_passthrough': 0,
            'conversion_errors': 0
        }

    def convert_pattern(self, pattern: str) -> str:
        """
        Convert natural language pattern to fnmatch pattern.

        Args:
            pattern: Input pattern (natural language or legacy fnmatch)

        Returns:
            str: fnmatch pattern ready for BaseProcessor.match_rule()

        Raises:
            PatternConversionError: If pattern is invalid natural language syntax
        """
        if not pattern or not isinstance(pattern, str):
            raise PatternConversionError("Pattern must be a non-empty string")

        pattern = pattern.strip()

        # Try natural language conversion
        converted = self._convert_natural_language(pattern)
        if converted is not None:
            self.conversion_stats['natural_language'] += 1
            return converted.lower()  # Case-insensitive matching

        # Legacy pattern passthrough
        self.conversion_stats['legacy_passthrough'] += 1
        return pattern.lower()  # Maintain case-insensitive behavior

    def _convert_natural_language(self, pattern: str) -> Optional[str]:
        """Convert natural language pattern using grammar rules."""
        match = self.NATURAL_PATTERN_REGEX.match(pattern)
        if not match:
            return None

        operator, value = match.groups()
        operator = operator.lower().replace(' ', '_')  # normalize spacing

        # Apply conversion rules
        conversion_map = {
            'contains': lambda v: f"*{v}*",
            'starts_with': lambda v: f"{v}*",
            'ends_with': lambda v: f"*{v}",
            'exactly': lambda v: v
        }

        if operator in conversion_map:
            return conversion_map[operator](value)

        return None  # Should not reach here with valid regex
```

### Pattern Validation System

```python
class PatternValidator:
    """Validates natural language pattern syntax."""

    VALID_OPERATORS = ['contains', 'starts with', 'ends with', 'exactly']
    MIN_VALUE_LENGTH = 1
    MAX_VALUE_LENGTH = 200

    def validate_pattern(self, pattern: str) -> Tuple[bool, str]:
        """
        Validate pattern syntax and provide error details.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not pattern or not isinstance(pattern, str):
            return False, "Pattern must be a non-empty string"

        pattern = pattern.strip()

        # Check if it's natural language pattern
        if self._is_natural_language_pattern(pattern):
            return self._validate_natural_language(pattern)

        # Legacy pattern - basic validation
        if len(pattern) > self.MAX_VALUE_LENGTH:
            return False, f"Pattern too long (max {self.MAX_VALUE_LENGTH} characters)"

        return True, ""

    def _is_natural_language_pattern(self, pattern: str) -> bool:
        """Check if pattern uses natural language syntax."""
        for operator in self.VALID_OPERATORS:
            if pattern.lower().startswith(operator.lower() + ' '):
                return True
        return False

    def _validate_natural_language(self, pattern: str) -> Tuple[bool, str]:
        """Validate natural language pattern structure."""
        # Extract operator and value
        parts = pattern.split(' ', 2 if 'with' in pattern else 1)

        if len(parts) < 2:
            return False, f"Invalid pattern syntax. Expected: 'operator value'. Got: '{pattern}'"

        # Reconstruct operator
        if len(parts) == 3 and parts[1] == 'with':
            operator = f"{parts[0]} {parts[1]}"
            value = parts[2]
        else:
            operator = parts[0]
            value = ' '.join(parts[1:])

        # Validate operator
        if operator.lower() not in [op.lower() for op in self.VALID_OPERATORS]:
            valid_ops = ', '.join([f"'{op}'" for op in self.VALID_OPERATORS])
            return False, f"Invalid operator '{operator}'. Valid operators: {valid_ops}"

        # Validate value
        if len(value) < self.MIN_VALUE_LENGTH:
            return False, f"Pattern value must be at least {self.MIN_VALUE_LENGTH} character"

        if len(value) > self.MAX_VALUE_LENGTH:
            return False, f"Pattern value too long (max {self.MAX_VALUE_LENGTH} characters)"

        return True, ""
```

### Error Handling and User Feedback

```python
class PatternConversionError(Exception):
    """Exception raised for pattern conversion errors."""

    def __init__(self, message: str, pattern: str = None, suggestions: list = None):
        self.pattern = pattern
        self.suggestions = suggestions or []
        super().__init__(message)

class PatternSuggestionEngine:
    """Provides helpful suggestions for pattern errors."""

    def suggest_corrections(self, invalid_pattern: str) -> list:
        """Generate suggestions for invalid patterns."""
        suggestions = []
        pattern_lower = invalid_pattern.lower().strip()

        # Common typos in operators
        typo_corrections = {
            'contain': 'contains',
            'start with': 'starts with',
            'startswith': 'starts with',
            'endswith': 'ends with',
            'end with': 'ends with',
            'exact': 'exactly',
            'equals': 'exactly'
        }

        for typo, correction in typo_corrections.items():
            if pattern_lower.startswith(typo + ' '):
                corrected = pattern_lower.replace(typo + ' ', correction + ' ', 1)
                suggestions.append(f"Did you mean: '{corrected}'?")

        # Suggest natural language if pattern looks like description
        if not any(op in pattern_lower for op in ['contains', 'starts', 'ends', 'exactly']):
            if '*' not in invalid_pattern and '?' not in invalid_pattern:
                suggestions.append(f"Try: 'contains {invalid_pattern}'")
                suggestions.append(f"Try: 'exactly {invalid_pattern}'")

        return suggestions[:3]  # Limit to 3 suggestions
```

## Integration with BaseProcessor

### Modified Pattern Matching Flow

```python
# In BaseProcessor.load_rules()
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load rules with pattern conversion."""
    # ... existing loading logic ...

    # Convert patterns during rule loading
    pattern_converter = PatternConverter()
    self._convert_rule_patterns(rules, pattern_converter)

    return rules

def _convert_rule_patterns(self, rules: dict, converter: PatternConverter):
    """Convert all patterns in rules structure."""
    for category in ['income', 'expense']:
        for rule in rules.get('rules', {}).get(category, []):
            # Handle both legacy and simplified field names
            pattern_field = 'match' if 'match' in rule else 'transaction_type'

            if pattern_field in rule:
                try:
                    original_pattern = rule[pattern_field]
                    converted_pattern = converter.convert_pattern(original_pattern)

                    # Store converted pattern in legacy field for processing
                    rule['transaction_type'] = converted_pattern

                    # Keep original for debugging/logging
                    rule['_original_pattern'] = original_pattern

                except PatternConversionError as e:
                    raise ValidationError(
                        f"Invalid pattern in {category} rule: {e}\n"
                        f"Pattern: '{original_pattern}'\n"
                        f"Suggestions: {', '.join(e.suggestions)}"
                    )
```

### Performance Optimization

```python
class CachedPatternConverter(PatternConverter):
    """Pattern converter with caching for repeated patterns."""

    def __init__(self):
        super().__init__()
        self._pattern_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def convert_pattern(self, pattern: str) -> str:
        """Convert pattern with caching."""
        if pattern in self._pattern_cache:
            self._cache_hits += 1
            return self._pattern_cache[pattern]

        self._cache_misses += 1
        converted = super().convert_pattern(pattern)
        self._pattern_cache[pattern] = converted
        return converted

    def get_cache_stats(self) -> dict:
        """Return cache performance statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0

        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate,
            'conversion_stats': self.conversion_stats
        }
```

## Pattern Testing Framework

### Comprehensive Test Suite

```python
class TestPatternConversion:
    """Test suite for pattern conversion functionality."""

    def test_natural_language_patterns(self):
        """Test all natural language pattern conversions."""
        converter = PatternConverter()

        test_cases = [
            # Contains patterns
            ("contains salary", "*salary*"),
            ("contains GROCERY STORE", "*grocery store*"),
            ("contains bill-pay", "*bill-pay*"),

            # Starts with patterns
            ("starts with SALARY", "salary*"),
            ("starts with Grocery Store", "grocery store*"),

            # Ends with patterns
            ("ends with FEE", "*fee"),
            ("ends with (Monthly)", "*(monthly)"),

            # Exactly patterns
            ("exactly Rent Payment", "rent payment"),
            ("exactly BILL#12345", "bill#12345"),
        ]

        for input_pattern, expected in test_cases:
            result = converter.convert_pattern(input_pattern)
            assert result == expected, f"Pattern '{input_pattern}' converted to '{result}', expected '{expected}'"

    def test_legacy_pattern_passthrough(self):
        """Test that legacy fnmatch patterns pass through unchanged."""
        converter = PatternConverter()

        legacy_patterns = [
            "*salary*",
            "GROCERY*",
            "*FEE",
            "Rent Payment",
            "*bill*payment*",
            "???-SALARY",
            "[Ss]alary*"
        ]

        for pattern in legacy_patterns:
            result = converter.convert_pattern(pattern)
            assert result == pattern.lower(), f"Legacy pattern '{pattern}' should pass through unchanged"

    def test_pattern_validation(self):
        """Test pattern validation and error messages."""
        validator = PatternValidator()

        # Valid patterns
        valid_patterns = [
            "contains salary",
            "starts with GROCERY",
            "ends with FEE",
            "exactly Payment",
            "*salary*",  # legacy
            "GROCERY*"   # legacy
        ]

        for pattern in valid_patterns:
            is_valid, error = validator.validate_pattern(pattern)
            assert is_valid, f"Pattern '{pattern}' should be valid, got error: {error}"

        # Invalid patterns
        invalid_patterns = [
            "",                          # empty
            "contains",                  # missing value
            "invalid operator value",    # bad operator
            "contains " + "x" * 201,    # too long
        ]

        for pattern in invalid_patterns:
            is_valid, error = validator.validate_pattern(pattern)
            assert not is_valid, f"Pattern '{pattern}' should be invalid"
            assert error, f"Invalid pattern '{pattern}' should have error message"
```

## Performance Benchmarks

### Expected Performance Characteristics

| Operation | Target Performance | Measurement |
|-----------|-------------------|-------------|
| Pattern Conversion | < 1ms per pattern | Single pattern conversion |
| Rule Loading | < 10ms additional overhead | 50 rules with mixed patterns |
| Cache Hit Rate | > 80% | In production with typical rule sets |
| Memory Overhead | < 20% increase | Pattern cache and conversion objects |

### Performance Monitoring

```python
class PatternPerformanceMonitor:
    """Monitor pattern conversion performance."""

    def __init__(self):
        self.conversion_times = []
        self.pattern_types = {'natural': 0, 'legacy': 0}

    @contextmanager
    def measure_conversion(self, pattern_type: str):
        """Context manager for measuring conversion time."""
        start_time = time.perf_counter()
        yield
        end_time = time.perf_counter()

        conversion_time = (end_time - start_time) * 1000  # ms
        self.conversion_times.append(conversion_time)
        self.pattern_types[pattern_type] += 1

    def get_performance_report(self) -> dict:
        """Generate performance report."""
        if not self.conversion_times:
            return {'error': 'No performance data collected'}

        return {
            'avg_conversion_time_ms': statistics.mean(self.conversion_times),
            'max_conversion_time_ms': max(self.conversion_times),
            'total_conversions': len(self.conversion_times),
            'pattern_type_breakdown': self.pattern_types.copy()
        }
```

## Acceptance Criteria

### Pattern Conversion Accuracy
- [ ] All natural language patterns convert to correct fnmatch equivalents
- [ ] Legacy fnmatch patterns pass through unchanged (case-insensitive)
- [ ] Pattern conversion is deterministic and reproducible
- [ ] No false positive natural language pattern detection

### Error Handling and Validation
- [ ] Invalid natural language syntax produces clear error messages
- [ ] Pattern validation catches common user errors before processing
- [ ] Suggestion engine provides helpful corrections for typos
- [ ] Error messages include examples of correct syntax

### Performance Requirements
- [ ] Pattern conversion overhead < 10ms for typical rule files (50 rules)
- [ ] Cache hit rate > 80% for repeated pattern usage
- [ ] Memory usage increase < 20% compared to legacy pattern matching
- [ ] No performance degradation for legacy-only rule files

### Integration Compatibility
- [ ] All existing BaseProcessor unit tests pass unchanged
- [ ] Pattern matching behavior identical to current fnmatch implementation
- [ ] Converted patterns produce same transaction matching results
- [ ] No breaking changes to public BaseProcessor interface
