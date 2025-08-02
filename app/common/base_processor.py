from abc import ABC, abstractmethod
from jsonschema import validate, ValidationError
import dateutil.parser
import fnmatch
import re
import json
import yaml
import copy
DEFAULT_HEADERS = {
  "date": "Date",
  "description": "Description",
  "income": "Deposit",
  "withdraw": "Withdrawal",
  "deposit": "Amount",
}


class BaseProcessor(ABC):
  """Abstract Base Class for processing financial transaction data."""

  def __init__(self):
    """Initialize the BaseProcessor with empty rules, headers, and transactions."""
    self.rules: dict = {}
    self.headers: dict = {}
    self.transactions: any

  @abstractmethod
  def load_input_file(self, file_path) -> any:
    """Load input file and return it as a DataFrame.

    Args:
      file_path (str): Path to the input file to be loaded.

    Returns:
      any: Loaded data as a DataFrame (specific type depends on implementation).
    """
    pass

  @abstractmethod
  def get_header(self, rules: dict) -> dict:
    """Return the headers attribute.

    Args:
      rules (dict): A dictionary of rules that may influence header selection.

    Returns:
      dict: The headers to be used for processing transactions.
    """
    pass

  def load_rules(self, file_path: str, schema_path: str = "schema.json") -> dict:
    """Load validation rules from a YAML file and validate against a JSON schema.

    Args:
      file_path (str): Path to the rules file in YAML format.
      schema_path (str): Path to the JSON schema file for validation.

    Returns:
      dict: The validated rules.

    Raises:
      ValidationError: If the rules do not conform to the schema.
    """
    with open(file_path, "r") as file:
      rules = yaml.safe_load(file)
      file.close()
    
    # Transform simplified syntax if present
    if self.has_simplified_syntax(rules):
      shortcuts = rules.get('accounts', {})
      rules = self.transform_rules(rules, shortcuts)
    
    with open(schema_path, "r") as sf:
      schema = json.load(sf)
      sf.close()
    errors = validate(rules, schema)
    if errors:
      raise ValidationError(f"Validation Errors: {errors}")
    return rules

  def sort_transactions(self, transactions_df: any, headers: dict) -> any:
    """Sort transactions by date in ascending order.

    Args:
      transactions_df (any): The DataFrame containing transaction data.
      headers (dict): The headers mapping for the DataFrame.

    Returns:
      any: The DataFrame sorted by date.
    """
    transactions_df["sort"] = transactions_df[headers["date"]].apply(
      dateutil.parser.parse
    )
    transactions_df = transactions_df.sort_values(by="sort")
    return transactions_df

  def normalize_transactions(self, transactions_df: any, headers: dict) -> any:
    """Normalize transactions for income and expense.

    Args:
      transactions_df (any): The DataFrame containing transaction data.
      headers (dict): The headers mapping for the DataFrame.

    Returns:
      any: The normalized DataFrame with properly categorized amounts.
    """
    if headers["amount"] in transactions_df.columns:
      transactions_df[headers["withdraw"]] = transactions_df[headers["amount"]].apply(
        lambda x: float(x.replace(",", "")) if (float(x.replace(",", "")) < 0) else 0
      )
      transactions_df[headers["deposit"]] = transactions_df[headers["amount"]].apply(
        lambda x: float(x.replace(",", "")) if (float(x.replace(",", "")) > 0) else 0
      )
    else:
      transactions_df[headers["withdraw"]] = -transactions_df[headers["withdraw"]]
    transactions_df[headers["amount"]] = (
      transactions_df[headers["deposit"]] + transactions_df[headers["withdraw"]]
    )
    return transactions_df

  def transform_transactions(self, transactions_df: any, rules: dict, headers: dict):
    """Transform transactions based on specified rules and headers.

    Args:
      transactions_df (any): The DataFrame containing transaction data.
      rules (dict): The rules to be applied for transforming transactions.
      headers (dict): The headers mapping for the DataFrame.

    Returns:
      list: A list of transformed transaction strings ready for output.
    """
    income_rules = rules["rules"]["income"]
    expense_rules = rules["rules"]["expense"]
    amount_prefix = (
      rules.get("output", {}).get("amount", {}).get("prefix", "$")
    )  # Default to '$' if not defined

    output = []
    for _, row in transactions_df.iterrows():
      date = dateutil.parser.parse(row[headers["date"]])
      formatted_date = date.strftime("%Y/%m/%d")
      description = row[headers["description"]]
      amount_str = str(row[headers["amount"]])
      # Remove commas from the amount string and convert to float
      amount = float(amount_str.replace(",", ""))
      applicable_rules = income_rules if amount > 0 else expense_rules
      amount = abs(amount)
      rule = self.match_rule(description, applicable_rules)
      if rule:
        debit_account = rule["debit_account"]
        credit_account = rule["credit_account"]
        output_description = (
          re.sub(r"[^a-zA-Z0-9 ]+", " ", rule.get("description", description))
          .title()
          .replace("\n", " ")
        )
        output.append(
          f"{formatted_date} {output_description}\n\t{debit_account:<50}{amount_prefix}{amount}\n\t{credit_account}"
        )
    return output

  def match_rule(self, transaction_type, rules):
    """Match a transaction type against defined rules to find applicable processing rule.

    Args:
      transaction_type (str): The description of the transaction type.
      rules (list): The list of rules against which to match the transaction type.

    Returns:
      dict or None: The matching rule if found, otherwise None.
    """
    for rule in rules:
      # if fnmatch.fnmatch(transaction_type.lower(), rule['transaction_type'].lower()):
      regex = fnmatch.translate(rule["transaction_type"].lower())
      if re.search(regex, transaction_type.lower()) is not None:
        return rule
    return None

  def has_simplified_syntax(self, rules: dict) -> bool:
    """Detect if YAML rules use simplified syntax with 'match' field.

    Args:
      rules (dict): The rules dictionary to analyze.

    Returns:
      bool: True if simplified syntax is detected, False otherwise.
    """
    # Check if rules is None or empty (empty YAML file case)
    if not rules or 'rules' not in rules:
      return False
      
    for rule_type in ['income', 'expense']:
      if rule_type in rules['rules']:
        for rule in rules['rules'][rule_type]:
          if 'match' in rule:
            return True
    
    return False

  def convert_pattern(self, pattern: str) -> str:
    """Convert simplified syntax patterns to legacy wildcard patterns.
    
    Args:
      pattern (str): The pattern in simplified syntax (e.g., "contains salary").
      
    Returns:
      str: The converted pattern in legacy wildcard format (e.g., "*salary*").
    """
    if pattern.startswith('contains '):
      return f"*{pattern[9:]}*"
    elif pattern.startswith('starts with '):
      return f"{pattern[12:]}*"
    elif pattern.startswith('ends with '):
      return f"*{pattern[10:]}"
    elif pattern.startswith('exactly '):
      return pattern[8:]
    
    # Return pattern unchanged if no conversion is needed
    return pattern

  def resolve_account(self, account: str, shortcuts: dict) -> str:
    """Resolve account shortcuts to full account paths.
    
    Args:
      account (str): The account shortcut or full path.
      shortcuts (dict): Dictionary mapping shortcuts to full account paths.
      
    Returns:
      str: The full account path if shortcut found, otherwise returns original input.
    """
    return shortcuts.get(account, account)

  def transform_rules(self, rules: dict, shortcuts: dict) -> dict:
    """Transform simplified syntax rules to legacy format rules.
    
    This function orchestrates the complete transformation pipeline:
    1. Convert patterns from simplified to wildcard format
    2. Resolve account shortcuts to full account paths
    3. Transform field names from simplified to legacy format
    
    Args:
      rules (dict): Rules dictionary in simplified syntax format.
      shortcuts (dict): Dictionary mapping shortcuts to full account paths.
      
    Returns:
      dict: Transformed rules dictionary in legacy format.
    """
    # Create a deep copy to avoid modifying the original rules
    transformed_rules = copy.deepcopy(rules)
    
    # Process both income and expense rules
    for rule_type in ['income', 'expense']:
      if rule_type in transformed_rules['rules']:
        for rule in transformed_rules['rules'][rule_type]:
          # Step 1: Convert pattern from simplified to wildcard format
          if 'match' in rule:
            rule['transaction_type'] = self.convert_pattern(rule['match'])
            del rule['match']
          
          # Step 2: Resolve account shortcuts to full paths
          if 'to' in rule:
            rule['debit_account'] = self.resolve_account(rule['to'], shortcuts)
            del rule['to']
            
          if 'from' in rule:
            rule['credit_account'] = self.resolve_account(rule['from'], shortcuts)
            del rule['from']
    
    return transformed_rules
