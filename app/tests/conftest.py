import pandas as pd
import pytest
import tempfile
import os
import yaml
from pathlib import Path
from typer.testing import CliRunner
from abc import ABC
from common.base_processor import BaseProcessor, DEFAULT_HEADERS
from common.csv_processor import CsvProcessor

SAMPLE_CSV = """
 Transaction Date,Description,Amount,Balance,
19 Jul 2024,TRANSFER RENT PAYMENT Wyndham Realty,"1,701.80"," 53,371.13"
"""
SAMPLE_RULES = """
input:
  csv:
    header:
      date: "Transaction Date"
      description: "Description"
      amount: "Amount"
  xls:
    header:
      date: " Transaction Date"
rules:
  income:
    - transaction_type: "TRANSFER RENT PAYMENT Wyndham Realty"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Income:AU:Interest"
  expense:
    - transaction_type: "*"
      debit_account: "Expenses:AU"
      credit_account: "Assets:AU:Savings:HSBC"
"""


class TestBaseProcessor(BaseProcessor, ABC):
  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    return pd.DataFrame()  # Return an empty DataFrame for tests

  def get_header(self, rules) -> dict:
    return DEFAULT_HEADERS  # Use default headers for tests


@pytest.fixture
def base_processor():
  """Fixture to create a BaseProcessor instance."""
  return TestBaseProcessor()


@pytest.fixture
def sample_transactions():
  data = {
    "Date": ["2023/08/01", "2023/08/02"],
    "Description": ["Maturity of Fixed Deposit", "Interest"],
    "Amount": [70000, 1575],
  }
  return pd.DataFrame(data)


@pytest.fixture
def sample_rules():
  return yaml.safe_load(SAMPLE_RULES)


@pytest.fixture
def sample_csv_file():
  """Create temporary csv file for testing."""
  csv_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv")

  # Write to temporary CSV file
  with open(csv_file.name, "w") as f:
    f.write(SAMPLE_CSV.strip())

  yield csv_file
  # Cleanup files after test
  os.remove(csv_file.name)


@pytest.fixture
def sample_rules_file(sample_rules):
  """Create temporary rules file for testing."""
  rules_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml")

  # Write to temporary CSV file
  with open(rules_file.name, "w") as f:
    f.write(SAMPLE_RULES.strip())

  yield rules_file
  # Cleanup files after test
  os.remove(rules_file.name)


@pytest.fixture
def sample_output_file():
  """Create temporary output file for testing."""
  output_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt")

  yield output_file
  # Cleanup files after test
  os.remove(output_file.name)


@pytest.fixture
def csv_processor(sample_rules_file, sample_csv_file):
  """Fixture to create a CsvProcessor instance."""
  return CsvProcessor(sample_rules_file.name, sample_csv_file.name)


@pytest.fixture
def runner():
  return CliRunner()



@pytest.fixture
def simplified_rules_data():
    """Test data for simplified syntax rules (using match/to/from fields)"""
    return {
        "rules": {
            "income": [
                {
                    "match": "contains salary",
                    "to": "checking",
                    "from": "salary"
                }
            ],
            "expense": [
                {
                    "match": "starts with GROCERY",
                    "to": "groceries", 
                    "from": "checking"
                }
            ]
        }
    }


@pytest.fixture
def legacy_rules_data():
    """Test data for legacy syntax rules (using transaction_type/debit_account/credit_account fields)"""
    return {
        "rules": {
            "income": [
                {
                    "transaction_type": "*salary*",
                    "debit_account": "Assets:Bank:Checking",
                    "credit_account": "Income:Salary"
                }
            ],
            "expense": [
                {
                    "transaction_type": "*grocery*",
                    "debit_account": "Expenses:Food:Groceries",
                    "credit_account": "Assets:Bank:Checking"
                }
            ]
        }
    }


@pytest.fixture
def shortcuts_data():
    """Test data for account shortcuts"""
    return {
        "checking": "Assets:Bank:Checking",
        "savings": "Assets:Bank:Savings", 
        "salary": "Income:Salary",
        "groceries": "Expenses:Food:Groceries",
        "rent": "Expenses:Housing:Rent"
    }


@pytest.fixture
def comprehensive_simplified_rules():
    """Test data for comprehensive simplified rules with realistic user scenarios"""
    return {
        "rules": {
            "income": [
                {
                    "match": "contains salary",
                    "to": "checking",
                    "from": "salary"
                },
                {
                    "match": "contains bonus", 
                    "to": "savings",
                    "from": "salary"
                }
            ],
            "expense": [
                {
                    "match": "contains grocery",
                    "to": "groceries",
                    "from": "checking"
                },
                {
                    "match": "contains rent",
                    "to": "rent", 
                    "from": "checking"
                }
            ]
        }
    }


@pytest.fixture
def expected_legacy_transformation():
    """Test data for expected legacy format after complete transformation"""
    return {
        "rules": {
            "income": [
                {
                    "transaction_type": "*salary*",
                    "debit_account": "Assets:Bank:Checking",
                    "credit_account": "Income:Salary"
                },
                {
                    "transaction_type": "*bonus*",
                    "debit_account": "Assets:Bank:Savings", 
                    "credit_account": "Income:Salary"
                }
            ],
            "expense": [
                {
                    "transaction_type": "*grocery*",
                    "debit_account": "Expenses:Food:Groceries",
                    "credit_account": "Assets:Bank:Checking"
                },
                {
                    "transaction_type": "*rent*",
                    "debit_account": "Expenses:Housing:Rent",
                    "credit_account": "Assets:Bank:Checking"
                }
            ]
        }
    }


@pytest.fixture
def pattern_conversion_test_data():
    """Test data for pattern conversion functionality"""
    return {
        "input_pattern": "contains salary",
        "expected_output": "*salary*"
    }


@pytest.fixture
def pattern_conversion_test_cases():
    """Test data for all pattern conversion types"""
    return [
        {"input": "contains salary", "expected": "*salary*"},
        {"input": "starts with TRANSFER", "expected": "TRANSFER*"},
        {"input": "ends with PAYMENT", "expected": "*PAYMENT"},
        {"input": "exactly Rent", "expected": "Rent"},
        {"input": "unknown pattern", "expected": "unknown pattern"}
    ]

@pytest.fixture
def bank_preset_test_data():
    """Minimal test data for bank preset functionality"""
    return {
        'preset_accounts': {
            'checking': 'Assets:Bank:DBS:Checking',
            'savings': 'Assets:Bank:DBS:Savings'
        },
        'user_rules': {
            'bank': 'dbs',
            'accounts': {'checking': 'Assets:Personal:Custom:Checking'},
            'rules': {
                'income': [{
                    'match': 'contains salary',
                    'to': 'checking',
                    'from': 'Income:Salary'
                }]
            }
        }
    }
