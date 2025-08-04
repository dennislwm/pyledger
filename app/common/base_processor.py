from abc import ABC, abstractmethod
from jsonschema import validate, ValidationError
import dateutil.parser
import fnmatch
import re
import json
import yaml
import copy
import pandas as pd
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
      bank_shortcuts = self._load_bank_preset(rules.get('bank', ''))
      user_shortcuts = rules.get('accounts', {})
      combined_shortcuts = {**bank_shortcuts, **user_shortcuts}  # User overrides
      rules = self.transform_rules(rules, combined_shortcuts)

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
    # Filter out rows with null dates in the configured date column
    transactions_df = transactions_df[transactions_df[headers["date"]].notna()].copy()

    transactions_df.loc[:, "sort"] = transactions_df[headers["date"]].apply(
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
      # Convert string amounts to float, handling empty/space values
      def safe_float_convert(x):
        if pd.isna(x) or str(x).strip() == '':
          return 0.0
        try:
          return float(str(x).replace(",", "").strip())
        except (ValueError, TypeError):
          return 0.0

      transactions_df[headers["withdraw"]] = transactions_df[headers["withdraw"]].apply(safe_float_convert)
      transactions_df[headers["deposit"]] = transactions_df[headers["deposit"]].apply(safe_float_convert)

      # Negate withdraw amounts to make them negative
      transactions_df[headers["withdraw"]] = -transactions_df[headers["withdraw"]]
    transactions_df[headers["amount"]] = (
      transactions_df[headers["deposit"]] + transactions_df[headers["withdraw"]]
    )
    return transactions_df

  def transform_transactions(self, transactions_df: any, rules: dict, headers: dict, capture_metadata: bool = False):
    """Transform transactions based on specified rules and headers.

    Args:
      transactions_df (any): The DataFrame containing transaction data.
      rules (dict): The rules to be applied for transforming transactions.
      headers (dict): The headers mapping for the DataFrame.
      capture_metadata (bool): Whether to capture metadata for transaction review.

    Returns:
      list: A list of transformed transaction strings when capture_metadata=False.
      tuple: (output, metadata) when capture_metadata=True.
    """
    income_rules = rules["rules"]["income"]
    expense_rules = rules["rules"]["expense"]
    amount_prefix = (
      rules.get("output", {}).get("amount", {}).get("prefix", "$")
    )  # Default to '$' if not defined

    output = []
    transaction_metadata = []
    rule_usage = {}
    confidence_distribution = {"high": 0, "medium": 0, "low": 0}

    for _, row in transactions_df.iterrows():
      date = dateutil.parser.parse(row[headers["date"]])
      formatted_date = date.strftime("%Y/%m/%d")
      description = row[headers["description"]]
      # Handle NaN description values
      if pd.isna(description):
        description = ""

      amount_str = str(row[headers["amount"]])
      # Remove commas from the amount string and convert to float
      amount = float(amount_str.replace(",", ""))
      applicable_rules = income_rules if amount > 0 else expense_rules
      amount_abs = abs(amount)
      rule = self.match_rule(description, applicable_rules)

      # Calculate confidence and rule type for metadata
      confidence_score, matched_rule_type = self._calculate_confidence(rule)

      # Track metadata if requested (for ALL transactions)
      if capture_metadata:
        tx_metadata = {
          "description": description,
          "amount": amount,
          "date": formatted_date,
          "confidence_score": confidence_score,
          "matched_rule_type": matched_rule_type,
          "rule_matched": rule is not None
        }
        transaction_metadata.append(tx_metadata)

        # Update rule usage statistics
        rule_key = rule.get("transaction_type", "no_match") if rule else "no_match"
        rule_usage[rule_key] = rule_usage.get(rule_key, 0) + 1

        # Update confidence distribution
        if confidence_score >= 0.9:
          confidence_distribution["high"] += 1
        elif confidence_score >= 0.5:
          confidence_distribution["medium"] += 1
        else:
          confidence_distribution["low"] += 1

      # Generate output ONLY for matching rules
      if rule:
        debit_account = rule["debit_account"]
        credit_account = rule["credit_account"]
        # Ensure description is a string for regex processing
        desc_for_output = rule.get("description", description)
        if pd.isna(desc_for_output):
          desc_for_output = ""
        output_description = (
          re.sub(r"[^a-zA-Z0-9 ]+", " ", str(desc_for_output))
          .title()
          .replace("\n", " ")
        )
        output.append(
          f"{formatted_date} {output_description}\n\t{debit_account:<50}{amount_prefix}{amount_abs}\n\t{credit_account}"
        )

    # Return appropriate format based on capture_metadata flag
    if capture_metadata:
      metadata = {
        "transactions": transaction_metadata,
        "summary": {
          "total_transactions": len(transaction_metadata),
          "rule_usage": rule_usage,
          "confidence_distribution": confidence_distribution
        }
      }
      return (output, metadata)
    else:
      return output

  def _calculate_confidence(self, rule):
    """Calculate confidence score based on rule match."""
    if not rule:
      return 0.1, "none"
    return (0.5, "wildcard") if "*" in rule.get("transaction_type", "") else (0.9, "specific")

  def match_rule(self, transaction_type, rules):
    """Match a transaction type against defined rules to find applicable processing rule.

    Args:
      transaction_type (str): The description of the transaction type.
      rules (list): The list of rules against which to match the transaction type.

    Returns:
      dict or None: The matching rule if found, otherwise None.
    """
    # Handle null/NaN transaction type values
    if pd.isna(transaction_type):
      transaction_type = ""

    for rule in rules:
      # if fnmatch.fnmatch(transaction_type.lower(), rule['transaction_type'].lower()):
      regex = fnmatch.translate(rule["transaction_type"].lower())
      if re.search(regex, str(transaction_type).lower()) is not None:
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

  def _load_bank_preset(self, bank_name: str) -> dict:
    """Load account shortcuts from bank preset file.

    Args:
      bank_name (str): The bank name to load presets for.

    Returns:
      dict: The bank account shortcuts or empty dict if file not found.
    """
    if not bank_name:
      return {}

    preset_path = f"presets/{bank_name}.yaml"
    try:
      with open(preset_path, 'r') as f:
        preset = yaml.safe_load(f)
        return preset.get('accounts', {}) if preset else {}
    except (FileNotFoundError, yaml.YAMLError):
      return {}  # Graceful degradation
