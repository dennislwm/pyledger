# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI application for automating debit and credit transactions for [Ledger](https://github.com/ledger/ledger), a double-entry accounting system. The application processes CSV and XLS bank statement files using configurable YAML rules to generate Ledger-formatted output files, reducing manual data entry and improving accuracy.

## Development Setup

### Quick Start
```bash
cd app
make install_new     # Install dependencies with pipenv
make test           # Run all tests via pipenv
make run            # Run the application
```

### Key Commands
```bash
# Dependencies: install_new (uses pipenv install)
# Application: run (python ledger.py)
# Testing: test, test_verbose (uses PYTHONPATH=.:../ pipenv run pytest)
# Development: shell (pipenv shell), shell_clean (pipenv --rm), pre-commit
# Analysis: llm, aider, aider_dryrun
```

### Pipenv Integration
The project uses pipenv for Python virtual environment and dependency management:

```bash
# Change to app directory (required for pipenv)
cd app

# Install dependencies
pipenv install pandas==2.2.2 pyyaml==6.0.1 openpyxl==3.1.3 typer==0.12.3
pipenv install --dev pytest==8.2.2

# Activate virtual environment
pipenv shell

# Run tests with proper Python path
PYTHONPATH=.:../ pipenv run pytest

# Run specific test
PYTHONPATH=.:../ pipenv run pytest tests/test_file.py::TestClass::test_method -v

# Clean environment
pipenv --rm
```

### Sample Usage and Output

**Input CSV format (Bank statements):**
```csv
Transaction Date,Client Reference,Amount,Debit Amount,Credit Amount
2023-01-15,SALARY PAYMENT,2500.00,0.00,2500.00
2023-01-16,GROCERY STORE,-45.67,45.67,0.00
```

**Command execution:**
```bash
$ python ledger.py input/dbs.csv rules/rules_dbs.yaml
```

**Output Ledger format:**
```
2023/01/15 Salary Payment
	Assets:DL:Multiplier:DBS                        $2500.00
	Income:DL:DBS:Rebate

2023/01/16 Grocery Store
	Expenses:DBS:Multiplier                         $45.67
	Assets:DL:Multiplier:DBS
```

## Development Patterns

### Project Structure
```
app/
├── ledger.py              # CLI entry point using Typer
├── common/                # Core modules
│   ├── base_processor.py  # Abstract base class for processors
│   ├── csv_processor.py   # CSV file processing
│   └── xls_processor.py   # Excel file processing
├── tests/                 # Unit tests
├── schema.json           # JSON schema for rules validation
├── Makefile             # Build and test commands
└── Pipfile              # Python dependencies
```

### Rules Configuration System

The application uses YAML-based rules files to configure transaction processing:

#### Rules File Structure (YAML)
```yaml
input:
  csv:
    header:
      date: "Transaction Date"
      description: "Client Reference"
      amount: "Amount"
      withdraw: "Debit Amount"
      deposit: "Credit Amount"
output:
  path: "output.txt"
  amount:
    prefix: "$"
rules:
  income:
    - transaction_type: "*salary*"
      debit_account: "Assets:Bank:Checking"
      credit_account: "Income:Salary"
  expense:
    - transaction_type: "*grocery*"
      debit_account: "Expenses:Food:Groceries"
      credit_account: "Assets:Bank:Checking"
```

#### Schema Validation
- **Automatic validation**: Rules files validated against `schema.json` on load
- **Required fields**: `rules.income` and `rules.expense` arrays are mandatory
- **Pattern matching**: Uses fnmatch patterns for transaction type matching
- **Error handling**: ValidationError raised for schema violations

### Testing Requirements
- **Framework**: pytest with comprehensive unit tests
- **Coverage**: All processors and main CLI functionality tested
- **Execution**: `PYTHONPATH=.:../ pipenv run pytest` for proper module imports and virtual environment
- **Test Structure**: Each test class covers specific processor functionality
- **Mock Data**: Tests use sample CSV/XLS data and rule configurations
- **Virtual Environment**: Always use pipenv to ensure consistent Python environment and dependencies

### File Format Support

#### CSV Processing (`CsvProcessor`)
- Handles standard bank CSV exports
- Configurable column mapping via rules file
- Automatic data type conversion and normalization

#### Excel Processing (`XlsProcessor`)
- Supports `.xls` files via xlrd library
- Configurable sheet selection and header row
- Same rule-based processing as CSV files

### Data Transformation Pipeline

1. **Load Input**: Read CSV/XLS file using appropriate processor
2. **Load Rules**: Validate YAML rules against JSON schema
3. **Sort Transactions**: Order by date in ascending order
4. **Normalize**: Convert amounts to consistent format (positive/negative)
5. **Transform**: Apply rules to generate Ledger entries
6. **Output**: Write to file or stdout

### Dependencies
Current dependencies (managed by pipenv):
- `pandas==2.2.2` for data manipulation
- `typer==0.12.3` for CLI interface
- `pyyaml==6.0.1` for rules file parsing
- `openpyxl==3.1.3`, `xlrd>=2.0.1` for Excel file support
- `jsonschema==4.23.0` for rules validation
- `pytest==8.2.2` for testing

**Installation**: Use `make install_new` for complete setup with pinned versions via pipenv

### Development Workflow

**Virtual Environment Management:**
- **Setup**: `cd app && pipenv install` creates virtual environment and installs dependencies
- **Activation**: `cd app && pipenv shell` activates the virtual environment
- **Testing**: `cd app && PYTHONPATH=.:../ pipenv run pytest` runs tests in isolated environment
- **Cleanup**: `cd app && pipenv --rm` removes virtual environment when needed

**Test-Driven Development:**
- Always work from `app/` directory: `cd app`
- Use `PYTHONPATH=.:../ pipenv run pytest tests/module_test.py::TestClass::test_method -v` for specific tests
- Always run tests via pipenv to ensure proper dependency management
- Virtual environment ensures consistent behavior across development machines

### Code Quality Standards

**Use existing patterns**: Follow the abstract base class pattern with `BaseProcessor` for consistent file handling. Prefer composition over inheritance where possible.

**Pattern matching**: Transaction rules use fnmatch patterns converted to regex for flexible matching against transaction descriptions.

**Error handling**: Comprehensive validation with clear error messages for invalid rules files or unsupported file formats.