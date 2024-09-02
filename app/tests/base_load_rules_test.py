import os
import pytest
import tempfile
import yaml
from jsonschema import ValidationError

# Valid and invalid YAML strings for testing
valid_yaml = """
rules:
  income:
    - transaction_type: "Salary"
      debit_account: "Cash"
      credit_account: "Income"
  expense:
    - transaction_type: "Groceries"
      debit_account: "Expenses"
      credit_account: "Cash"
"""
invalid_yaml = """
rules:
  income:
    - transaction_type: "Salary"
      debit_account: "Cash"
      credit_account: "Income"
  expense:
    - transaction_type: "Invalid entry
      debit_account: "Expenses"
      credit_account: "Cash"
"""
fabrication = """
"""


def test_load_rules_valid_file(base_processor):
  with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
    temp_file.write(valid_yaml.encode())
    temp_file.close()

    result = base_processor.load_rules(temp_file.name)
    os.remove(temp_file.name)
    assert "rules" in result


def test_load_rules_invalid_yaml(base_processor):
  with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
    temp_file.write(invalid_yaml.encode())
    temp_file.close()

    with pytest.raises(yaml.YAMLError):
      base_processor.load_rules(temp_file.name)
    os.remove(temp_file.name)


def test_load_rules_validation_failure(base_processor):
  # Create a rules file that is invalid according to schema
  wrong_schema_yaml = """
  rules:
    income:
      - transaction_type: "Salary"
        debit_account: "Cash"
        credit_account:
    expense:
      - transaction_type: "Groceries"
        debit_account: "Expenses"
        credit_account: "Cash"
  """
  with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
    temp_file.write(wrong_schema_yaml.encode())
    temp_file.close()

  with pytest.raises(ValidationError):
    base_processor.load_rules(temp_file.name)
  os.remove(temp_file.name)


def test_load_rules_non_existent_file(base_processor):
  with pytest.raises(FileNotFoundError):
    base_processor.load_rules("non_existent_file.yaml")


def test_load_rules_empty_file(base_processor):
  with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
    temp_file.write(b"")
    temp_file.close()

    with pytest.raises(ValidationError):
      base_processor.load_rules(temp_file.name)
    os.remove(temp_file.name)
