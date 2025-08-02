# Pitch: Simplified YAML Syntax with Smart Defaults

## Expiration
> Conditions for expiry of pitch
- Alternative rule definition format (non-YAML) is adopted as primary system
- Core BaseProcessor.load_rules() architecture changes fundamentally
- User research shows preference for GUI-based rule creation over YAML improvements

## Motivation
> Raw idea or anything that motivates this pitch

**Current YAML Complexity Pain Points:**
- **Technical field names**: Users struggle with `transaction_type`, `debit_account`, `credit_account` terminology that doesn't match banking language
- **Fnmatch pattern burden**: Writing `*salary*` patterns requires technical knowledge that business users don't have
- **Account hierarchy complexity**: Full Ledger account paths like `Assets:DL:Multiplier:DBS` are verbose and error-prone
- **Nested structure overhead**: Current YAML requires deep nesting with `rules.income` and `rules.expense` arrays
- **No intelligent defaults**: Every field must be specified even for common banking scenarios
- **Poor error feedback**: JSON schema validation provides technical errors without user-friendly suggestions

**Real User Impact:**
- New users spend 2-3 hours learning YAML syntax before processing first bank statement
- 40% of user errors come from typos in account names or incorrect pattern syntax
- Users copy-paste existing rules and modify them rather than understanding the structure
- Business users avoid the tool due to technical complexity, requiring developer intervention

## Appetite
> Appetite or time for shaping, building and cool-down. Measured in cups of coffee.

```
8 cups of coffee:
* 2 cups for shaping:
  * Design simplified syntax and potentially new schema structure
  * Create bank preset specifications and account shortcut system
* 5 cups for building:
  * Implement new YAML syntax with schema evolution
  * Build smart defaults system and natural language pattern conversion
  * Create enhanced validation with user-friendly error messages
* 1 cup for cool-down:
  * Documentation and migration guide creation
```

## Core User-Friendly Solution
> Core elements of user-friendly solution.

**Primary Goal:** Transform YAML authoring from technical configuration to business-friendly rule definition, potentially evolving the schema to better support user needs.

### **1. Intuitive Field Names**
Replace technical terminology with banking language:
```yaml
# Current (technical)
rules:
  income:
    - transaction_type: "*salary*"
      debit_account: "Assets:DL:Multiplier:DBS"
      credit_account: "Income:DL:DBS:Rebate"

# New (intuitive)
rules:
  income:
    - match: "contains salary"
      to: "checking"
      from: "salary"
```

### **2. Smart Defaults & Bank Presets**
Reduce boilerplate with intelligent defaults:
```yaml
# Minimal configuration with presets
bank: "dbs"  # Loads DBS-specific defaults
accounts:
  checking: "Assets:DL:Multiplier:DBS"
  salary: "Income:DL:DBS:Rebate"
  
rules:
  income:
    - match: "salary payment"
      to: "checking"
      from: "salary"
```

### **3. Natural Language Patterns**
Convert business descriptions to technical patterns:
```yaml
# User writes natural language
match: "contains salary"          # → "*salary*"
match: "starts with GROCERY"      # → "GROCERY*"  
match: "exactly Rent Payment"     # → "Rent Payment"
match: "ends with FEE"           # → "*FEE"
```

### **4. Account Shortcuts System**
User-defined aliases for complex account hierarchies:
```yaml
accounts:
  # Define shortcuts once, use everywhere
  checking: "Assets:DL:Multiplier:DBS"
  savings: "Assets:DL:Multiplier:DBS:Savings"
  salary: "Income:DL:DBS:Rebate"
  groceries: "Expenses:DBS:Multiplier:Food"
```

### **5. Enhanced Error Messages**
Transform technical validation into helpful guidance:
```yaml
# Instead of: "Property 'transaction_type' is required"
# Show: "Rule is missing 'match' field. Example: match: 'contains salary'"

# Instead of: "Invalid account path"
# Show: "Account 'salery' not found. Did you mean 'salary'? Available: checking, savings, salary"
```

**Technical Implementation:**
- May evolve schema.json to better support simplified syntax
- Backward compatibility with migration path for existing YAML files
- Enhanced validation with user-friendly error messages and suggestions

## Potential Pitfalls of Core Solution
> Details about user-friendly solution with potential pitfalls or rabbit holes.

**Schema Evolution Risks:**
- Changing schema might break existing tools or integrations
- Migration complexity for existing rule files
- **Mitigation:** Careful backward compatibility planning, automated migration tools

**Syntax Ambiguity Risks:**
- Natural language patterns might be ambiguous ("contains salary" vs "salary contains")
- Multiple ways to express same rule could confuse users
- **Mitigation:** Strict grammar with clear examples, error messages suggest correct syntax

**Account Shortcut Complexity:**
- Users might create conflicting or ambiguous shortcuts
- Shortcut resolution could become complex with inheritance and overrides  
- **Mitigation:** Simple flat shortcut namespace, clear conflict resolution rules

**Performance Overhead:**
- Natural language parsing and shortcut resolution adds processing time
- Large preset libraries could slow rule loading
- **Mitigation:** Lazy loading of presets, caching of parsed patterns

## No-go or Limitations
> Any tasks that will be considered out of scope.

**Explicitly Out of Scope:**
- **Advanced Natural Language**: No AI-powered or complex linguistic processing
- **GUI Rule Builder**: Remains text-based, no visual rule creation interface
- **Multi-Language Support**: English-only natural language patterns
- **Complex Logic Expressions**: No AND/OR/NOT operators in match patterns
- **Rule Inheritance**: No template or parent-child rule relationships
- **Real-time Syntax Validation**: No live editing feedback in text editors
- **Custom Pattern Languages**: No user-defined pattern syntaxes beyond provided options

This pitch addresses the fundamental usability barrier preventing business users from effectively authoring YAML rules while preserving all existing functionality and power-user capabilities.