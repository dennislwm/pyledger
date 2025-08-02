# Account Shortcuts System: Simplified Account Management

## Overview and Design Philosophy

This specification defines a user-friendly account aliasing system that allows business users to create meaningful shortcuts for complex Ledger account hierarchies. The system reduces verbosity, prevents typos, and makes YAML rule files more readable while maintaining full compatibility with existing Ledger account structures.

### Design Principles
1. **Business-Friendly Names**: Shortcuts use intuitive names like "checking", "salary", "groceries"
2. **Conflict Prevention**: Clear resolution rules and validation prevent ambiguous shortcuts
3. **Scope Isolation**: Shortcuts defined in one file don't affect others
4. **Full Path Support**: Users can mix shortcuts and full account paths as needed
5. **Error Guidance**: Clear error messages with suggestions for typos and conflicts

## Account Shortcut Specification

### Shortcut Definition Structure

```yaml
accounts:
  # Personal accounts - intuitive names for common account types
  checking: "Assets:Personal:Bank:DBS:Checking"
  savings: "Assets:Personal:Bank:DBS:Savings"
  investment: "Assets:Personal:Investment:Portfolio"

  # Income categories - business-friendly income types
  salary: "Income:Employment:Salary"
  bonus: "Income:Employment:Bonus"
  freelance: "Income:Business:Freelance"
  dividend: "Income:Investment:Dividends"

  # Expense categories - organized by life areas
  groceries: "Expenses:Living:Food:Groceries"
  utilities: "Expenses:Living:Utilities:Electric"
  transport: "Expenses:Living:Transport:Public"
  entertainment: "Expenses:Personal:Entertainment"
  medical: "Expenses:Personal:Healthcare"
```

### Shortcut Naming Conventions

#### Valid Shortcut Names
- **Pattern**: `^[a-z][a-z0-9_]*$` (lowercase, alphanumeric, underscores)
- **Examples**: `checking`, `salary`, `home_loan`, `credit_card_payment`
- **Length**: 1-50 characters

#### Reserved Names (Cannot be used as shortcuts)
- System keywords: `input`, `output`, `rules`, `bank`
- Ledger keywords: `assets`, `liabilities`, `income`, `expenses`, `equity`
- Common conflicts: `from`, `to`, `match`, `type`

### Account Path Validation

#### Valid Account Paths
- **Pattern**: `^[A-Z][A-Za-z0-9:_\-\s]*$`
- **Structure**: Must start with uppercase letter (standard Ledger convention)
- **Separators**: Colons (`:`) separate hierarchy levels
- **Examples**:
  - `Assets:Personal:Bank:Checking`
  - `Income:Employment:Salary`
  - `Expenses:Living:Food:Groceries`

#### Invalid Account Paths
```yaml
# These will be rejected with helpful error messages
accounts:
  bad1: "assets:bank"           # Must start with uppercase
  bad2: "Assets::Bank"          # Double colons not allowed
  bad3: "Assets:Bank:"          # Cannot end with colon
  bad4: ""                      # Empty path not allowed
```

## Account Resolution System

### Resolution Algorithm Implementation

```python
class AccountResolver:
    """Resolves account shortcuts to full Ledger account paths."""

    def __init__(self, accounts: dict = None, bank_presets: dict = None):
        self.accounts = accounts or {}
        self.bank_presets = bank_presets or {}
        self.resolution_cache = {}

        # Validate shortcuts on initialization
        self._validate_shortcuts()

    def resolve_account(self, account_ref: str) -> str:
        """
        Resolve account reference to full Ledger path.

        Args:
            account_ref: Shortcut name or full account path

        Returns:
            str: Full Ledger account path

        Raises:
            AccountResolutionError: If reference cannot be resolved
        """
        if not account_ref or not isinstance(account_ref, str):
            raise AccountResolutionError("Account reference must be a non-empty string")

        account_ref = account_ref.strip()

        # Check cache first
        if account_ref in self.resolution_cache:
            return self.resolution_cache[account_ref]

        resolved_path = self._resolve_uncached(account_ref)
        self.resolution_cache[account_ref] = resolved_path
        return resolved_path

    def _resolve_uncached(self, account_ref: str) -> str:
        """Perform actual resolution without caching."""
        # Priority 1: User-defined shortcuts
        if account_ref in self.accounts:
            return self.accounts[account_ref]

        # Priority 2: Bank preset shortcuts
        if account_ref in self.bank_presets:
            return self.bank_presets[account_ref]

        # Priority 3: Check if it's already a full path
        if self._is_valid_account_path(account_ref):
            return account_ref

        # Priority 4: Error with suggestions
        suggestions = self._generate_suggestions(account_ref)
        raise AccountResolutionError(
            f"Cannot resolve account reference '{account_ref}'",
            account_ref,
            suggestions
        )

    def _is_valid_account_path(self, path: str) -> bool:
        """Check if string is a valid Ledger account path."""
        # Must start with uppercase letter and contain colon
        if not path or not path[0].isupper() or ':' not in path:
            return False

        # Basic structure validation
        parts = path.split(':')
        return all(part.strip() and not part.isspace() for part in parts)

    def _validate_shortcuts(self):
        """Validate all shortcuts on initialization."""
        errors = []

        for shortcut, path in self.accounts.items():
            # Validate shortcut name
            if not self._is_valid_shortcut_name(shortcut):
                errors.append(f"Invalid shortcut name '{shortcut}': must match pattern ^[a-z][a-z0-9_]*$")
                continue

            # Check for reserved names
            if shortcut in self.RESERVED_NAMES:
                errors.append(f"Shortcut name '{shortcut}' is reserved and cannot be used")
                continue

            # Validate account path
            if not self._is_valid_account_path(path):
                errors.append(f"Invalid account path for shortcut '{shortcut}': '{path}'")

        if errors:
            raise AccountValidationError("Account shortcut validation failed:\n" + "\n".join(errors))

    RESERVED_NAMES = {
        'input', 'output', 'rules', 'bank', 'from', 'to', 'match', 'type',
        'assets', 'liabilities', 'income', 'expenses', 'equity'
    }

    def _is_valid_shortcut_name(self, name: str) -> bool:
        """Validate shortcut name format."""
        import re
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name)) and len(name) <= 50
```

### Conflict Detection and Resolution

```python
class ConflictDetector:
    """Detect and resolve conflicts in account shortcuts."""

    def detect_conflicts(self, user_accounts: dict, bank_presets: dict) -> list:
        """
        Detect conflicts between user shortcuts and bank presets.

        Returns:
            list: List of conflict descriptions with resolution suggestions
        """
        conflicts = []

        for shortcut in user_accounts:
            if shortcut in bank_presets:
                user_path = user_accounts[shortcut]
                preset_path = bank_presets[shortcut]

                if user_path \!= preset_path:
                    conflicts.append({
                        'type': 'override',
                        'shortcut': shortcut,
                        'user_path': user_path,
                        'preset_path': preset_path,
                        'resolution': 'User definition takes precedence'
                    })

        return conflicts

    def detect_circular_references(self, accounts: dict) -> list:
        """
        Detect circular references in account definitions.

        Note: This is for future extension if we add shortcut-to-shortcut references
        """
        # Current implementation doesn't support shortcut references
        # This is a placeholder for potential future functionality
        return []

    def suggest_alternatives(self, conflicted_shortcut: str, existing_shortcuts: list) -> list:
        """Suggest alternative shortcut names for conflicts."""
        base_name = conflicted_shortcut.rstrip('_0123456789')
        suggestions = []

        # Add descriptive suffixes
        common_suffixes = ['_main', '_primary', '_personal', '_business', '_alt']
        for suffix in common_suffixes:
            candidate = base_name + suffix
            if candidate not in existing_shortcuts and len(candidate) <= 50:
                suggestions.append(candidate)

        # Add numbered alternatives
        for i in range(2, 6):
            candidate = f"{base_name}_{i}"
            if candidate not in existing_shortcuts and len(candidate) <= 50:
                suggestions.append(candidate)

        return suggestions[:3]  # Limit to 3 suggestions
```

### Suggestion Engine for Typos

```python
class AccountSuggestionEngine:
    """Generate helpful suggestions for account resolution errors."""

    def __init__(self, resolver: AccountResolver):
        self.resolver = resolver

    def generate_suggestions(self, failed_reference: str) -> list:
        """Generate suggestions for failed account reference."""
        suggestions = []
        available_shortcuts = list(self.resolver.accounts.keys()) + list(self.resolver.bank_presets.keys())

        # Fuzzy matching for typos
        suggestions.extend(self._fuzzy_match_shortcuts(failed_reference, available_shortcuts))

        # Pattern-based suggestions
        suggestions.extend(self._pattern_suggestions(failed_reference))

        # Account path suggestions
        suggestions.extend(self._account_path_suggestions(failed_reference))

        return list(dict.fromkeys(suggestions))[:5]  # Remove duplicates, limit to 5

    def _fuzzy_match_shortcuts(self, reference: str, shortcuts: list) -> list:
        """Find shortcuts similar to the failed reference."""
        suggestions = []
        reference_lower = reference.lower()

        # Exact substring matches
        for shortcut in shortcuts:
            if reference_lower in shortcut.lower() or shortcut.lower() in reference_lower:
                suggestions.append(f"Did you mean '{shortcut}'?")

        # Levenshtein distance for typos
        import difflib
        close_matches = difflib.get_close_matches(reference_lower,
                                                [s.lower() for s in shortcuts],
                                                n=3, cutoff=0.6)

        for match in close_matches:
            # Find original case version
            original = next(s for s in shortcuts if s.lower() == match)
            suggestions.append(f"Did you mean '{original}'?")

        return suggestions

    def _pattern_suggestions(self, reference: str) -> list:
        """Suggest based on common patterns."""
        suggestions = []

        # Common account type patterns
        account_patterns = {
            'check': 'checking',
            'save': 'savings',
            'invest': 'investment',
            'sal': 'salary',
            'grocery': 'groceries',
            'util': 'utilities',
            'transport': 'transport'
        }

        ref_lower = reference.lower()
        for pattern, suggestion in account_patterns.items():
            if pattern in ref_lower:
                suggestions.append(f"Try '{suggestion}' for {pattern}-related accounts")

        return suggestions

    def _account_path_suggestions(self, reference: str) -> list:
        """Suggest account path format if reference looks like partial path."""
        suggestions = []

        # If it contains colon but doesn't start with uppercase
        if ':' in reference and not reference[0].isupper():
            fixed = reference[0].upper() + reference[1:]
            suggestions.append(f"Account paths must start with uppercase: '{fixed}'")

        # If it looks like account path but missing structure
        if reference[0].isupper() and ':' not in reference:
            suggestions.append(f"Use full path like: '{reference}:SubAccount:Detail'")
            suggestions.append("Or define a shortcut in 'accounts:' section")

        return suggestions
```

## Integration with Schema and Rules Processing

### Enhanced Schema Validation

```yaml
# Updated schema_v2.json fragment for accounts section
"accounts": {
  "type": "object",
  "patternProperties": {
    "^[a-z][a-z0-9_]*$": {
      "type": "string",
      "pattern": "^[A-Z][A-Za-z0-9:_\\-\\s]*[A-Za-z0-9_\\-\\s]$",
      "minLength": 1,
      "maxLength": 200
    }
  },
  "additionalProperties": false,
  "not": {
    "anyOf": [
      {"properties": {"input": true}},
      {"properties": {"output": true}},
      {"properties": {"rules": true}},
      {"properties": {"bank": true}},
      {"properties": {"from": true}},
      {"properties": {"to": true}},
      {"properties": {"match": true}},
      {"properties": {"assets": true}},
      {"properties": {"liabilities": true}},
      {"properties": {"income": true}},
      {"properties": {"expenses": true}},
      {"properties": {"equity": true}}
    ]
  }
}
```

### Rules Processing Integration

```python
# In schema transformer
class SchemaTransformer:
    def __init__(self):
        self.account_resolver = None

    def transform_to_legacy(self, simplified_rules: dict) -> dict:
        """Transform simplified rules with account resolution."""
        # Initialize resolver with user accounts and bank presets
        user_accounts = simplified_rules.get('accounts', {})
        bank_presets = self._load_bank_presets(simplified_rules.get('bank'))

        self.account_resolver = AccountResolver(user_accounts, bank_presets)

        # Transform rules with account resolution
        legacy_rules = {'rules': {'income': [], 'expense': []}}

        for category in ['income', 'expense']:
            for rule in simplified_rules.get('rules', {}).get(category, []):
                try:
                    legacy_rule = {
                        'transaction_type': self._convert_pattern(rule['match']),
                        'debit_account': self.account_resolver.resolve_account(rule['to']),
                        'credit_account': self.account_resolver.resolve_account(rule['from'])
                    }

                    if 'description' in rule:
                        legacy_rule['description'] = rule['description']

                    legacy_rules['rules'][category].append(legacy_rule)

                except AccountResolutionError as e:
                    raise ValidationError(
                        f"Account resolution failed in {category} rule: {e}\n"
                        f"Rule: {rule}\n"
                        f"Suggestions: {', '.join(e.suggestions)}"
                    )

        # Copy other sections unchanged
        for section in ['input', 'output']:
            if section in simplified_rules:
                legacy_rules[section] = simplified_rules[section]

        return legacy_rules
```

## Error Handling and User Feedback

### Comprehensive Error Types

```python
class AccountResolutionError(Exception):
    """Raised when account reference cannot be resolved."""

    def __init__(self, message: str, account_ref: str = None, suggestions: list = None):
        self.account_ref = account_ref
        self.suggestions = suggestions or []
        super().__init__(message)

class AccountValidationError(Exception):
    """Raised when account shortcuts fail validation."""
    pass

class CircularReferenceError(AccountValidationError):
    """Raised when circular references detected in account definitions."""
    pass
```

### User-Friendly Error Messages

```python
class AccountErrorFormatter:
    """Format account-related errors for user consumption."""

    @staticmethod
    def format_resolution_error(error: AccountResolutionError) -> str:
        """Format account resolution error with helpful context."""
        message = [f"❌ Cannot resolve account reference: '{error.account_ref}'"]

        if error.suggestions:
            message.append("\n💡 Suggestions:")
            for suggestion in error.suggestions:
                message.append(f"   • {suggestion}")

        # Add help text for first-time users
        message.extend([
            "\n📖 Quick Help:",
            "   • Define shortcuts: accounts: {checking: 'Assets:Bank:Checking'}",
            "   • Use full paths: 'Assets:Personal:Bank:Checking'",
            "   • Check spelling and available shortcuts"
        ])

        return "\n".join(message)

    @staticmethod
    def format_validation_error(error: AccountValidationError) -> str:
        """Format account validation error with examples."""
        message = [f"❌ Account validation failed: {str(error)}"]

        message.extend([
            "\n📖 Account Definition Rules:",
            "   • Shortcut names: lowercase, underscore allowed (checking, home_loan)",
            "   • Account paths: start with uppercase, use colons (Assets:Bank:Checking)",
            "   • Reserved names: input, output, rules, bank, from, to, match"
        ])

        return "\n".join(message)
```

## Performance Considerations

### Caching Strategy

```python
class AccountResolutionCache:
    """Cache for account resolution to improve performance."""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []

    def get(self, key: str) -> str:
        """Get cached resolution result."""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def put(self, key: str, value: str):
        """Cache resolution result with LRU eviction."""
        if key in self.cache:
            # Update existing
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # Add new
            if len(self.cache) >= self.max_size:
                # Evict least recently used
                oldest = self.access_order.pop(0)
                del self.cache[oldest]

            self.cache[key] = value
            self.access_order.append(key)
```

### Performance Benchmarks

| Operation | Target Performance | Measurement |
|-----------|-------------------|-------------|
| Account Resolution | < 0.1ms per lookup | Single account resolution |
| Cache Hit Rate | > 90% | Typical rule file processing |
| Validation Time | < 5ms | 50 account shortcuts |
| Memory Overhead | < 10KB | Account resolver + cache |

## Testing Framework

### Comprehensive Test Coverage

```python
class TestAccountShortcuts:
    """Test suite for account shortcuts system."""

    def test_basic_resolution(self):
        """Test basic shortcut resolution."""
        accounts = {
            'checking': 'Assets:Personal:Bank:Checking',
            'salary': 'Income:Employment:Salary'
        }
        resolver = AccountResolver(accounts)

        assert resolver.resolve_account('checking') == 'Assets:Personal:Bank:Checking'
        assert resolver.resolve_account('salary') == 'Income:Employment:Salary'

    def test_full_path_passthrough(self):
        """Test that full paths pass through unchanged."""
        resolver = AccountResolver({})

        full_path = 'Assets:Personal:Bank:Checking'
        assert resolver.resolve_account(full_path) == full_path

    def test_error_suggestions(self):
        """Test error message suggestions."""
        accounts = {'checking': 'Assets:Bank:Checking'}
        resolver = AccountResolver(accounts)

        with pytest.raises(AccountResolutionError) as exc_info:
            resolver.resolve_account('chekcing')  # typo

        error = exc_info.value
        assert 'checking' in ' '.join(error.suggestions)

    def test_reserved_name_validation(self):
        """Test that reserved names are rejected."""
        with pytest.raises(AccountValidationError):
            AccountResolver({'input': 'Assets:Bank:Checking'})
```

## Acceptance Criteria

### Account Resolution Functionality
- [ ] User shortcuts resolve to correct full account paths
- [ ] Full account paths pass through unchanged
- [ ] Bank preset shortcuts merge correctly with user shortcuts
- [ ] User shortcuts override bank presets with same name
- [ ] Unresolved shortcuts produce clear error messages with suggestions

### Validation and Error Handling
- [ ] Invalid shortcut names are rejected with helpful errors
- [ ] Reserved names cannot be used as shortcuts
- [ ] Invalid account paths are detected and explained
- [ ] Typos in shortcuts generate "did you mean" suggestions
- [ ] Circular references are prevented (future-proofing)

### Performance Requirements
- [ ] Account resolution < 0.1ms per lookup (cached)
- [ ] Cache hit rate > 90% for typical usage patterns
- [ ] Memory overhead < 10KB for resolver and cache
- [ ] Validation time < 5ms for 50 shortcuts

### Integration Compatibility
- [ ] Schema validation enforces shortcut naming rules
- [ ] Rules processing correctly resolves all account references
- [ ] Error messages integrate with enhanced validation system
- [ ] No performance impact on rules without shortcuts
