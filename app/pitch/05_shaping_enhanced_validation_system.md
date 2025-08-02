# Enhanced Validation System Specification: Comprehensive Error Management and User Experience

## Overview and Design Philosophy

This specification defines a comprehensive enhanced validation system that provides intelligent error handling, user-friendly feedback, and contextual guidance for the Ledger application's YAML rules processing. The system bridges the gap between technical JSON schema validation and business user comprehension while supporting both legacy and simplified YAML syntaxes.

### Design Principles
1. **User-Centric Error Messages**: Transform technical validation errors into actionable business guidance
2. **Contextual Intelligence**: Provide relevant suggestions based on error context and user intent  
3. **Backward Compatibility**: Seamlessly support both legacy and simplified YAML schemas
4. **Progressive Enhancement**: Layer intelligent validation on top of existing JSON schema foundation
5. **Performance Optimization**: Maintain sub-50ms validation performance for typical rule files

## Enhanced Validation Architecture

### Dual-Schema Validation System

The validation system supports both legacy and simplified schemas through intelligent detection and transformation:

```python
class EnhancedValidator:
    """Enhanced validation system with dual-schema support and intelligent error handling."""
    
    def __init__(self):
        self.legacy_schema = self._load_schema("schema.json")
        self.simplified_schema = self._load_schema("schema_v2.json")
        self.error_transformer = ValidationErrorTransformer()
        self.suggestion_engine = ContextualSuggestionEngine()
        self.schema_detector = SchemaVersionDetector()
        
    def validate_rules(self, rules: dict, file_path: str = None) -> ValidationResult:
        """
        Comprehensive validation with enhanced error handling.
        
        Args:
            rules: Parsed YAML rules dictionary
            file_path: Optional file path for context in error messages
            
        Returns:
            ValidationResult with success status, errors, and suggestions
        """
        try:
            # Phase 1: Schema Detection
            schema_version = self.schema_detector.detect_version(rules)
            
            # Phase 2: Schema Validation
            if schema_version == 'simplified':
                validation_errors = self._validate_against_schema(rules, self.simplified_schema)
            else:
                validation_errors = self._validate_against_schema(rules, self.legacy_schema)
                
            # Phase 3: Enhanced Validation
            enhanced_errors = self._perform_enhanced_validation(rules, schema_version)
            
            # Phase 4: Error Transformation and Suggestions
            if validation_errors or enhanced_errors:
                user_friendly_errors = self.error_transformer.transform_errors(
                    validation_errors + enhanced_errors, 
                    rules, 
                    file_path
                )
                suggestions = self.suggestion_engine.generate_suggestions(
                    validation_errors + enhanced_errors,
                    rules,
                    schema_version
                )
                
                return ValidationResult(
                    success=False,
                    errors=user_friendly_errors,
                    suggestions=suggestions,
                    schema_version=schema_version
                )
            
            return ValidationResult(
                success=True,
                schema_version=schema_version,
                transformed_rules=self._transform_if_needed(rules, schema_version)
            )
            
        except Exception as e:
            return ValidationResult(
                success=False,
                errors=[f"Unexpected validation error: {str(e)}"],
                suggestions=["Check YAML syntax and file structure"]
            )
```

### Schema Version Detection

```python
class SchemaVersionDetector:
    """Intelligent detection of YAML schema version."""
    
    SIMPLIFIED_INDICATORS = [
        'bank',           # Bank preset field
        'accounts',       # Account shortcuts
    ]
    
    SIMPLIFIED_RULE_FIELDS = [
        'match',          # Natural language patterns
        'to',             # Destination account
        'from'            # Source account
    ]
    
    def detect_version(self, rules: dict) -> str:
        """
        Detect schema version based on content analysis.
        
        Args:
            rules: Parsed YAML rules dictionary
            
        Returns:
            'simplified' or 'legacy'
        """
        # Check for top-level simplified indicators
        for indicator in self.SIMPLIFIED_INDICATORS:
            if indicator in rules:
                return 'simplified'
        
        # Check for simplified fields in rules
        if self._has_simplified_rule_fields(rules):
            return 'simplified'
            
        return 'legacy'
    
    def _has_simplified_rule_fields(self, rules: dict) -> bool:
        """Check if rules contain simplified field names."""
        rules_section = rules.get('rules', {})
        
        for category in ['income', 'expense']:
            for rule in rules_section.get(category, []):
                for field in self.SIMPLIFIED_RULE_FIELDS:
                    if field in rule:
                        return True
        
        return False
```

## User-Friendly Error Message Transformation

### Error Message Enhancement System

```python
class ValidationErrorTransformer:
    """Transform technical JSON schema errors into user-friendly messages."""
    
    def __init__(self):
        self.field_names = {
            'transaction_type': 'transaction pattern',
            'debit_account': 'destination account (to)',
            'credit_account': 'source account (from)',
            'match': 'transaction pattern',
            'to': 'destination account',
            'from': 'source account'
        }
        
        self.common_patterns = {
            'required property': self._handle_required_field,
            'additionalProperties': self._handle_unknown_field,
            'pattern': self._handle_pattern_mismatch,
            'enum': self._handle_invalid_enum,
            'minItems': self._handle_empty_array,
            'type': self._handle_type_mismatch
        }
    
    def transform_errors(self, errors: list, rules: dict, file_path: str = None) -> list:
        """
        Transform JSON schema errors into user-friendly messages.
        
        Args:
            errors: List of ValidationError objects
            rules: Original rules dictionary for context
            file_path: Optional file path for error context
            
        Returns:
            List of user-friendly error messages
        """
        user_friendly_errors = []
        
        for error in errors:
            transformed = self._transform_single_error(error, rules, file_path)
            user_friendly_errors.extend(transformed)
        
        return user_friendly_errors
    
    def _transform_single_error(self, error, rules: dict, file_path: str) -> list:
        """Transform a single JSON schema error."""
        error_message = str(error.message).lower()
        
        # Match error patterns and apply specific transformations
        for pattern, handler in self.common_patterns.items():
            if pattern in error_message:
                return handler(error, rules, file_path)
        
        # Fallback: generic transformation
        return [self._generic_error_transformation(error, file_path)]
    
    def _handle_required_field(self, error, rules: dict, file_path: str) -> list:
        """Handle missing required field errors."""
        missing_field = error.message.split("'")[1]
        friendly_name = self.field_names.get(missing_field, missing_field)
        
        location_context = self._get_error_location_context(error)
        
        messages = [
            f"❌ Missing required field: {friendly_name}",
            f"📍 Location: {location_context}",
        ]
        
        # Add specific guidance based on field type
        if missing_field in ['transaction_type', 'match']:
            messages.append("💡 Add a pattern like: match: \"contains salary\"")
        elif missing_field in ['debit_account', 'to']:
            messages.append("💡 Add destination account like: to: \"checking\"")
        elif missing_field in ['credit_account', 'from']:
            messages.append("💡 Add source account like: from: \"salary\"")
        
        return messages
    
    def _handle_unknown_field(self, error, rules: dict, file_path: str) -> list:
        """Handle unknown/additional properties errors."""
        # Extract the unknown field name from error message
        unknown_field = self._extract_field_from_error(error.message)
        location_context = self._get_error_location_context(error)
        
        messages = [
            f"❌ Unknown field: '{unknown_field}'",
            f"📍 Location: {location_context}",
        ]
        
        # Suggest corrections for common typos
        suggestions = self._suggest_field_corrections(unknown_field)
        if suggestions:
            messages.append(f"💡 Did you mean: {', '.join(suggestions)}?")
        
        return messages
    
    def _handle_pattern_mismatch(self, error, rules: dict, file_path: str) -> list:
        """Handle pattern validation errors."""
        field_path = '.'.join(str(p) for p in error.absolute_path)
        
        messages = [
            f"❌ Invalid format in field: {field_path}",
            f"📍 Value: {error.instance}",
        ]
        
        # Provide specific guidance based on field type
        if 'match' in field_path or 'transaction_type' in field_path:
            messages.extend([
                "💡 Pattern examples:",
                "   • contains grocery",
                "   • starts with SALARY",
                "   • exactly Payment",
                "   • *grocery* (legacy format)"
            ])
        elif any(account in field_path for account in ['to', 'from', 'debit_account', 'credit_account']):
            messages.extend([
                "💡 Account examples:",
                "   • checking (shortcut)",
                "   • Assets:Personal:Bank:Checking (full path)"
            ])
        
        return messages
    
    def _get_error_location_context(self, error) -> str:
        """Generate human-readable error location context."""
        path_parts = []
        
        for part in error.absolute_path:
            if isinstance(part, int):
                path_parts.append(f"item {part + 1}")
            else:
                path_parts.append(str(part))
        
        if not path_parts:
            return "root level"
        
        return " → ".join(path_parts)
```

### Error Message Templates

```python
class ErrorMessageTemplates:
    """Template system for consistent error messaging."""
    
    TEMPLATES = {
        'missing_rules_section': {
            'title': "❌ Missing rules section",
            'description': "Your YAML file must include a 'rules:' section with 'income:' and 'expense:' arrays.",
            'example': """
rules:
  income:
    - match: "contains salary"
      to: "checking"
      from: "salary"
  expense:
    - match: "contains grocery"  
      to: "groceries"
      from: "checking"
"""
        },
        
        'empty_rule_array': {
            'title': "❌ Empty {category} rules",
            'description': "The {category} section must contain at least one rule.",
            'example': """
{category}:
  - match: "contains {example_pattern}"
    to: "{example_to}"
    from: "{example_from}"
"""
        },
        
        'invalid_account_shortcut': {
            'title': "❌ Invalid account shortcut: '{shortcut}'",
            'description': "Account shortcuts must be lowercase with underscores only.",
            'example': """
accounts:
  checking: "Assets:Personal:Bank:Checking"    # ✓ Valid
  home_loan: "Liabilities:Personal:HomeLoan"   # ✓ Valid
  CheckingAccount: "Assets:..."                # ❌ Invalid (uppercase)
  checking-account: "Assets:..."               # ❌ Invalid (hyphen)
"""
        }
    }
    
    def format_message(self, template_key: str, **kwargs) -> str:
        """Format error message using template with parameters."""
        template = self.TEMPLATES.get(template_key, {})
        
        title = template.get('title', '').format(**kwargs)
        description = template.get('description', '').format(**kwargs)
        example = template.get('example', '').format(**kwargs)
        
        return f"{title}\n{description}\n{example}"
```

## Contextual Suggestion Engine

### Intelligent Suggestion System

```python
class ContextualSuggestionEngine:
    """Generate contextual suggestions based on validation errors and user intent."""
    
    def __init__(self):
        self.typo_detector = TypoDetector()
        self.pattern_analyzer = PatternAnalyzer()
        self.account_suggester = AccountSuggester()
        
    def generate_suggestions(self, errors: list, rules: dict, schema_version: str) -> list:
        """
        Generate contextual suggestions for validation errors.
        
        Args:
            errors: List of validation errors
            rules: Original rules dictionary
            schema_version: Detected schema version
            
        Returns:
            List of actionable suggestions
        """
        suggestions = []
        
        # Analyze errors for suggestion opportunities
        for error in errors:
            error_suggestions = self._analyze_error_for_suggestions(error, rules, schema_version)
            suggestions.extend(error_suggestions)
        
        # Add schema-specific suggestions
        if schema_version == 'legacy':
            suggestions.append(self._suggest_simplified_syntax_migration())
        
        # Remove duplicates and prioritize
        return self._prioritize_suggestions(list(set(suggestions)))
    
    def _analyze_error_for_suggestions(self, error, rules: dict, schema_version: str) -> list:
        """Analyze individual error for suggestion opportunities."""
        suggestions = []
        
        # Field name typo detection
        if 'unknown field' in str(error).lower():
            typo_suggestions = self.typo_detector.suggest_corrections(error, schema_version)
            suggestions.extend(typo_suggestions)
        
        # Pattern format suggestions
        if 'pattern' in str(error).lower():
            pattern_suggestions = self.pattern_analyzer.suggest_pattern_fixes(error)
            suggestions.extend(pattern_suggestions)
        
        # Account resolution suggestions
        if any(keyword in str(error).lower() for keyword in ['account', 'to', 'from']):
            account_suggestions = self.account_suggester.suggest_account_fixes(error, rules)
            suggestions.extend(account_suggestions)
        
        return suggestions
```

### Typo Detection and Correction

```python
class TypoDetector:
    """Detect and suggest corrections for common field name typos."""
    
    FIELD_CORRECTIONS = {
        'legacy': {
            'transaction_pattern': 'transaction_type',
            'transaction': 'transaction_type', 
            'pattern': 'transaction_type',
            'debit': 'debit_account',
            'credit': 'credit_account',
            'to_account': 'debit_account',
            'from_account': 'credit_account'
        },
        'simplified': {
            'transaction_type': 'match',
            'pattern': 'match',
            'transaction': 'match',
            'debit_account': 'to',
            'credit_account': 'from',
            'to_account': 'to',
            'from_account': 'from'
        }
    }
    
    def suggest_corrections(self, error, schema_version: str) -> list:
        """Suggest field name corrections based on detected typos."""
        suggestions = []
        
        # Extract the problematic field name
        field_name = self._extract_field_name_from_error(error)
        if not field_name:
            return suggestions
        
        # Get relevant corrections for schema version
        corrections = self.FIELD_CORRECTIONS.get(schema_version, {})
        
        # Direct correction lookup
        if field_name in corrections:
            suggestions.append(f"Did you mean '{corrections[field_name]}' instead of '{field_name}'?")
        
        # Fuzzy matching for complex typos
        fuzzy_matches = self._find_fuzzy_matches(field_name, list(corrections.values()))
        for match in fuzzy_matches:
            suggestions.append(f"Did you mean '{match}'?")
        
        return suggestions
    
    def _find_fuzzy_matches(self, field_name: str, valid_fields: list) -> list:
        """Find fuzzy matches using edit distance."""
        import difflib
        
        matches = difflib.get_close_matches(
            field_name.lower(),
            [f.lower() for f in valid_fields],
            n=3,
            cutoff=0.6
        )
        
        # Return original case versions
        result = []
        for match in matches:
            original = next((f for f in valid_fields if f.lower() == match), match)
            result.append(original)
        
        return result
```

## Schema Detection and Version Support

### Version Detection Algorithm

```python
class SchemaVersionDetector:
    """Detect YAML schema version with high accuracy."""
    
    def __init__(self):
        self.simplified_confidence_threshold = 0.7
        
    def detect_version(self, rules: dict) -> str:
        """
        Detect schema version using weighted scoring system.
        
        Returns:
            'simplified' or 'legacy'
        """
        simplified_score = self._calculate_simplified_score(rules)
        
        if simplified_score >= self.simplified_confidence_threshold:
            return 'simplified'
        else:
            return 'legacy'
    
    def _calculate_simplified_score(self, rules: dict) -> float:
        """Calculate confidence score for simplified schema."""
        indicators = []
        
        # Top-level field indicators (high confidence)
        if 'bank' in rules:
            indicators.append(0.8)
        if 'accounts' in rules:
            indicators.append(0.8)
        
        # Rule field indicators (medium confidence)
        simplified_rule_fields = self._count_simplified_rule_fields(rules)
        total_rule_fields = self._count_total_rule_fields(rules)
        
        if total_rule_fields > 0:
            rule_field_ratio = simplified_rule_fields / total_rule_fields
            indicators.append(rule_field_ratio * 0.6)
        
        # Natural language pattern indicators (medium confidence)
        natural_language_patterns = self._count_natural_language_patterns(rules)
        total_patterns = self._count_total_patterns(rules)
        
        if total_patterns > 0:
            pattern_ratio = natural_language_patterns / total_patterns
            indicators.append(pattern_ratio * 0.5)
        
        # Calculate weighted average
        return sum(indicators) / len(indicators) if indicators else 0.0
    
    def _count_simplified_rule_fields(self, rules: dict) -> int:
        """Count usage of simplified field names in rules."""
        count = 0
        simplified_fields = ['match', 'to', 'from']
        
        rules_section = rules.get('rules', {})
        for category in ['income', 'expense']:
            for rule in rules_section.get(category, []):
                for field in simplified_fields:
                    if field in rule:
                        count += 1
        
        return count
    
    def _count_natural_language_patterns(self, rules: dict) -> int:
        """Count patterns using natural language syntax."""
        import re
        
        natural_language_regex = re.compile(
            r'^(contains|starts\s+with|ends\s+with|exactly)\s+.+$',
            re.IGNORECASE
        )
        
        count = 0
        rules_section = rules.get('rules', {})
        
        for category in ['income', 'expense']:
            for rule in rules_section.get(category, []):
                pattern = rule.get('match') or rule.get('transaction_type', '')
                if natural_language_regex.match(pattern):
                    count += 1
        
        return count
```

### Backward Compatibility Support

```python
class BackwardCompatibilityManager:
    """Ensure seamless support for legacy YAML files."""
    
    def __init__(self):
        self.legacy_validator = LegacyValidator()
        self.migration_suggester = MigrationSuggester()
        
    def validate_legacy_file(self, rules: dict) -> ValidationResult:
        """Validate legacy YAML file with enhanced error messages."""
        # Perform standard legacy validation
        legacy_errors = self.legacy_validator.validate(rules)
        
        # Enhance error messages for legacy context
        enhanced_errors = self._enhance_legacy_errors(legacy_errors, rules)
        
        # Suggest migration opportunities
        migration_suggestions = self.migration_suggester.analyze_migration_potential(rules)
        
        if legacy_errors:
            return ValidationResult(
                success=False,
                errors=enhanced_errors,
                suggestions=migration_suggestions,
                schema_version='legacy'
            )
        
        return ValidationResult(
            success=True,
            schema_version='legacy',
            suggestions=migration_suggestions
        )
    
    def _enhance_legacy_errors(self, errors: list, rules: dict) -> list:
        """Enhance legacy validation errors with modern context."""
        enhanced = []
        
        for error in errors:
            enhanced_error = {
                'original': str(error),
                'enhanced': self._modernize_error_message(error),
                'legacy_context': True
            }
            enhanced.append(enhanced_error)
        
        return enhanced
```

## Performance Requirements and Monitoring

### Performance Benchmarks

| Component | Target Performance | Measurement Method |
|-----------|-------------------|-------------------|
| Schema Detection | < 5ms | Single rules file analysis |
| JSON Schema Validation | < 20ms | 50-rule file validation |
| Error Transformation | < 10ms | Complex error message generation |
| Suggestion Generation | < 15ms | Contextual suggestion analysis |
| Total Validation Time | < 50ms | End-to-end validation process |

### Performance Monitoring System

```python
class ValidationPerformanceMonitor:
    """Monitor and report validation performance metrics."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.thresholds = {
            'schema_detection': 5.0,      # ms
            'json_validation': 20.0,      # ms
            'error_transformation': 10.0,  # ms
            'suggestion_generation': 15.0, # ms
            'total_validation': 50.0       # ms
        }
    
    @contextmanager
    def measure_operation(self, operation_name: str):
        """Context manager for measuring operation performance."""
        start_time = time.perf_counter()
        yield
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        self.metrics[operation_name].append(duration_ms)
        
        # Check threshold violations
        threshold = self.thresholds.get(operation_name)
        if threshold and duration_ms > threshold:
            self._log_performance_warning(operation_name, duration_ms, threshold)
    
    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance report."""
        report = {}
        
        for operation, measurements in self.metrics.items():
            if measurements:
                report[operation] = {
                    'count': len(measurements),
                    'avg_ms': statistics.mean(measurements),
                    'max_ms': max(measurements),
                    'min_ms': min(measurements),
                    'p95_ms': self._percentile(measurements, 0.95),
                    'threshold_violations': sum(1 for m in measurements if m > self.thresholds.get(operation, float('inf')))
                }
        
        return report
    
    def _percentile(self, data: list, percentile: float) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = int(percentile * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
```

### Caching Strategy for Performance

```python
class ValidationCache:
    """Intelligent caching for validation components."""
    
    def __init__(self, max_size: int = 1000):
        self.schema_cache = {}
        self.error_cache = {}
        self.suggestion_cache = {}
        self.max_size = max_size
        
    def get_cached_validation(self, rules_hash: str) -> Optional[ValidationResult]:
        """Retrieve cached validation result."""
        return self.error_cache.get(rules_hash)
    
    def cache_validation(self, rules_hash: str, result: ValidationResult):
        """Cache validation result with LRU eviction."""
        if len(self.error_cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.error_cache))
            del self.error_cache[oldest_key]
        
        self.error_cache[rules_hash] = result
    
    def get_cache_stats(self) -> dict:
        """Return cache performance statistics."""
        return {
            'schema_cache_size': len(self.schema_cache),
            'error_cache_size': len(self.error_cache),
            'suggestion_cache_size': len(self.suggestion_cache),
            'total_memory_kb': self._estimate_memory_usage()
        }
```

## Integration with BaseProcessor

### Enhanced BaseProcessor.load_rules() Method

```python
def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """
    Load and validate rules with enhanced error handling.
    
    Args:
        file_path: Path to YAML rules file
        schema_path: Path to JSON schema file (legacy compatibility)
        
    Returns:
        dict: Validated and potentially transformed rules
        
    Raises:
        EnhancedValidationError: With user-friendly error messages and suggestions
    """
    try:
        # Load raw YAML
        with open(file_path, "r") as file:
            raw_rules = yaml.safe_load(file)
        
        # Enhanced validation
        validator = EnhancedValidator()
        result = validator.validate_rules(raw_rules, file_path)
        
        if not result.success:
            # Format and raise enhanced validation error
            error_message = self._format_validation_errors(result.errors, result.suggestions)
            raise EnhancedValidationError(error_message, file_path, result.suggestions)
        
        # Return transformed rules for processing
        return result.transformed_rules or raw_rules
        
    except yaml.YAMLError as e:
        raise EnhancedValidationError(
            f"YAML syntax error in {file_path}: {str(e)}",
            file_path,
            ["Check YAML indentation and syntax", "Validate YAML format online"]
        )
    except FileNotFoundError:
        raise EnhancedValidationError(
            f"Rules file not found: {file_path}",
            file_path,
            ["Check file path spelling", "Ensure file exists in expected location"]
        )

def _format_validation_errors(self, errors: list, suggestions: list) -> str:
    """Format validation errors and suggestions for user display."""
    message_parts = [
        "❌ Validation failed for rules file:",
        "",
        "🔍 Errors found:",
    ]
    
    for i, error in enumerate(errors, 1):
        message_parts.append(f"   {i}. {error}")
    
    if suggestions:
        message_parts.extend([
            "",
            "💡 Suggestions:",
        ])
        for suggestion in suggestions:
            message_parts.append(f"   • {suggestion}")
    
    message_parts.extend([
        "",
        "📖 For help with YAML syntax, see documentation or examples."
    ])
    
    return "\n".join(message_parts)
```

### Custom Exception Classes

```python
class EnhancedValidationError(Exception):
    """Enhanced validation error with context and suggestions."""
    
    def __init__(self, message: str, file_path: str = None, suggestions: list = None):
        self.file_path = file_path
        self.suggestions = suggestions or []
        super().__init__(message)

class ValidationResult:
    """Result object for validation operations."""
    
    def __init__(self, success: bool, errors: list = None, suggestions: list = None, 
                 schema_version: str = None, transformed_rules: dict = None):
        self.success = success
        self.errors = errors or []
        self.suggestions = suggestions or []
        self.schema_version = schema_version
        self.transformed_rules = transformed_rules
```

## Testing Framework

### Comprehensive Test Suite Structure

```python
class TestEnhancedValidation:
    """Comprehensive test suite for enhanced validation system."""
    
    def test_schema_detection_accuracy(self):
        """Test schema version detection accuracy across various inputs."""
        test_cases = [
            # Simplified schema indicators
            ({'bank': 'dbs', 'rules': {'income': [], 'expense': []}}, 'simplified'),
            ({'accounts': {'checking': 'Assets:Bank'}, 'rules': {'income': [], 'expense': []}}, 'simplified'),
            
            # Legacy schema patterns  
            ({'rules': {'income': [{'transaction_type': '*salary*', 'debit_account': 'Assets', 'credit_account': 'Income'}], 'expense': []}}, 'legacy'),
            
            # Mixed patterns (should detect as simplified)
            ({'rules': {'income': [{'match': 'contains salary', 'to': 'checking', 'from': 'salary'}], 'expense': []}}, 'simplified'),
        ]
        
        detector = SchemaVersionDetector()
        
        for rules, expected_version in test_cases:
            detected_version = detector.detect_version(rules)
            assert detected_version == expected_version, f"Expected {expected_version}, got {detected_version} for {rules}"
    
    def test_error_message_transformation(self):
        """Test transformation of JSON schema errors to user-friendly messages."""
        transformer = ValidationErrorTransformer()
        
        # Simulate JSON schema validation error
        mock_error = ValidationError("'match' is a required property")
        mock_error.absolute_path = ['rules', 'income', 0]
        
        transformed = transformer._transform_single_error(mock_error, {}, "test.yaml")
        
        assert any("Missing required field" in msg for msg in transformed)
        assert any("match" in msg or "pattern" in msg for msg in transformed)
    
    def test_suggestion_generation(self):
        """Test contextual suggestion generation."""
        engine = ContextualSuggestionEngine()
        
        # Test typo suggestions
        mock_errors = [ValidationError("'mach' is not a valid property")]
        suggestions = engine.generate_suggestions(mock_errors, {}, 'simplified')
        
        assert any("match" in suggestion for suggestion in suggestions)
    
    def test_performance_benchmarks(self):
        """Test that validation meets performance requirements."""
        validator = EnhancedValidator()
        monitor = ValidationPerformanceMonitor()
        
        # Test with realistic rule file
        test_rules = {
            'bank': 'dbs',
            'rules': {
                'income': [
                    {'match': 'contains salary', 'to': 'checking', 'from': 'salary'}
                ] * 25,  # 25 income rules
                'expense': [
                    {'match': 'contains grocery', 'to': 'groceries', 'from': 'checking'}
                ] * 25   # 25 expense rules
            }
        }
        
        with monitor.measure_operation('total_validation'):
            result = validator.validate_rules(test_rules)
        
        report = monitor.generate_performance_report()
        total_time = report['total_validation']['avg_ms']
        
        assert total_time < 50.0, f"Validation took {total_time}ms, exceeding 50ms threshold"
    
    def test_backward_compatibility(self):
        """Test that legacy YAML files continue to work."""
        validator = EnhancedValidator()
        
        legacy_rules = {
            'rules': {
                'income': [
                    {
                        'transaction_type': '*salary*',
                        'debit_account': 'Assets:Personal:Bank:Checking',
                        'credit_account': 'Income:Employment:Salary'
                    }
                ],
                'expense': [
                    {
                        'transaction_type': '*grocery*',
                        'debit_account': 'Expenses:Living:Food:Groceries',
                        'credit_account': 'Assets:Personal:Bank:Checking'
                    }
                ]
            }
        }
        
        result = validator.validate_rules(legacy_rules)
        assert result.success, "Legacy rules should validate successfully"
        assert result.schema_version == 'legacy'
    
    def test_enhanced_error_context(self):
        """Test that errors provide sufficient context for debugging."""
        validator = EnhancedValidator()
        
        # Rules with multiple errors
        invalid_rules = {
            'rules': {
                'income': [
                    {
                        'match': 'contains salary',
                        'to': 'checking',
                        # Missing 'from' field
                    }
                ],
                'expense': []  # Empty array should trigger minItems error
            }
        }
        
        result = validator.validate_rules(invalid_rules, "test.yaml")
        
        assert not result.success
        assert len(result.errors) > 0
        assert len(result.suggestions) > 0
        
        # Check that errors include location context
        error_text = " ".join(result.errors)
        assert "income" in error_text or "item 1" in error_text
```

### Integration Test Coverage

```python
class TestValidationIntegration:
    """Integration tests for validation system with BaseProcessor."""
    
    def test_enhanced_validation_in_base_processor(self):
        """Test enhanced validation integrated with BaseProcessor."""
        from common.csv_processor import CsvProcessor
        
        processor = CsvProcessor()
        
        # Test with invalid rules file
        with pytest.raises(EnhancedValidationError) as exc_info:
            processor.load_rules("test_data/invalid_rules.yaml")
        
        error = exc_info.value
        assert error.suggestions, "Enhanced validation should provide suggestions"
        assert error.file_path, "Error should include file path context"
    
    def test_performance_impact_on_existing_workflows(self):
        """Test that enhanced validation doesn't significantly impact existing performance."""
        import time
        from common.csv_processor import CsvProcessor
        
        processor = CsvProcessor()
        
        # Measure validation time for typical rules file
        start_time = time.perf_counter()
        rules = processor.load_rules("test_data/typical_rules.yaml")
        end_time = time.perf_counter()
        
        validation_time_ms = (end_time - start_time) * 1000
        
        # Should be under 100ms for typical usage (allowing overhead for integration)
        assert validation_time_ms < 100.0, f"Validation took {validation_time_ms}ms, too slow for production"
```

## Acceptance Criteria

### Enhanced Validation Functionality
- [ ] Dual-schema support validates both legacy and simplified YAML formats correctly
- [ ] Schema detection achieves > 95% accuracy on test corpus of 100+ YAML files
- [ ] Error message transformation provides actionable guidance for 100% of JSON schema error types
- [ ] Suggestion engine generates relevant suggestions for > 80% of validation failures

### User Experience Requirements
- [ ] Error messages use business-friendly language without technical jargon
- [ ] Validation failures include specific location context (rule category, item number)
- [ ] Suggestions include concrete examples and "did you mean" corrections
- [ ] Critical errors (missing rules, syntax errors) provide step-by-step resolution guidance

### Performance Requirements
- [ ] Total validation time < 50ms for typical rule files (50 rules)
- [ ] Schema detection < 5ms for any valid YAML structure
- [ ] Error transformation < 10ms for complex multi-error scenarios
- [ ] Memory overhead < 5MB for validation components and caches

### Backward Compatibility
- [ ] All existing legacy YAML files validate without modification
- [ ] Legacy error handling maintains same behavior for valid files
- [ ] Performance impact < 10% overhead for legacy-only rule files
- [ ] No breaking changes to BaseProcessor public interface

### Integration Requirements
- [ ] Enhanced validation integrates seamlessly with existing BaseProcessor architecture
- [ ] Error handling maintains consistency with existing exception patterns
- [ ] Validation cache reduces repeated validation overhead by > 50%
- [ ] Performance monitoring provides actionable metrics for optimization

### Testing Coverage
- [ ] Unit test coverage > 90% for all validation components
- [ ] Integration tests cover all BaseProcessor workflows
- [ ] Performance tests validate all benchmark requirements
- [ ] Error scenario tests cover > 50 common user mistakes and edge cases