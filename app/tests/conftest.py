import pytest
import pandas as pd
import yaml
from pathlib import Path
from typer.testing import CliRunner
from abc import ABC
from common.base_processor import BaseProcessor

class TestProcessor(BaseProcessor, ABC):
  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    pass

  def get_header(self, rules) -> dict:
    pass

@pytest.fixture
def base_processor():
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
  rules_yaml = """
  rules:
    - transaction_type: "Maturity of Fixed Deposit"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Assets:AU:Term:HSBC:Aug23"
    - transaction_type: "Interest"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Income:AU:Interest"
  """
  return yaml.safe_load(rules_yaml)

@pytest.fixture
def runner():
  return CliRunner()