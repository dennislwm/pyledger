import os
import pytest
import pandas as pd
import tempfile
import yaml
from pathlib import Path
from typer.testing import CliRunner
from abc import ABC
from common.base_processor import BaseProcessor, DEFAULT_HEADERS

SAMPLE_RULES = """
  rules:
    - transaction_type: "Maturity of Fixed Deposit"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Assets:AU:Term:HSBC:Aug23"
    - transaction_type: "Interest"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Income:AU:Interest"
  """

class TestProcessor(BaseProcessor, ABC):
  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    return pd.DataFrame()  # Return an empty DataFrame for tests

  def get_header(self, rules) -> dict:
    return DEFAULT_HEADERS  # Use default headers for tests

@pytest.fixture
def base_processor():
  """Fixture to create a BaseProcessor instance."""
  return TestProcessor()

@pytest.fixture
def sample_transactions():
  data = {
    "Date": ["2023/08/01", "2023/08/02"],
    "Description": ["Maturity of Fixed Deposit", "Interest"],
    "Amount": [70000, 1575]
  }
  return pd.DataFrame(data)

@pytest.fixture
def sample_rules():
  return yaml.safe_load(SAMPLE_RULES)

@pytest.fixture
def sample_csv_file():
  """Create temporary csv file for testing."""
  csv_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv')
  csv_content = "column1,column2\nvalue1,value2\nvalue3,value4"

  # Write to temporary CSV file
  with open(csv_file.name, 'w') as f:
    f.write(csv_content)

  yield csv_file

  # Cleanup files after test
  os.remove(csv_file.name)

@pytest.fixture
def sample_rules_file(sample_rules):
  """Create temporary rules file for testing."""
  rules_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.yaml')

  # Write to temporary CSV file
  with open(rules_file.name, 'w') as f:
    f.write(SAMPLE_RULES.strip())
    # yaml.dump(sample_rules, f, default_flow_style=False)

  yield rules_file

  # Cleanup files after test
  os.remove(rules_file.name)

@pytest.fixture
def sample_output_file():
  """Create temporary output file for testing."""
  output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')

  yield output_file

  # Cleanup files after test
  os.remove(output_file.name)

@pytest.fixture
def runner():
  return CliRunner()