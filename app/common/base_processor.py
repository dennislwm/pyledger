from abc import ABC, abstractmethod
from jsonschema import validate, ValidationError
import dateutil.parser
import fnmatch, re
import json, yaml

DEFAULT_HEADERS= {
  "date": "Date",
  "description": "Description",
  "income": "Deposit",
  "withdraw": "Withdrawal",
  "deposit": "Amount"
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

  def load_rules(self, file_path: str, schema_path: str="schema.json") -> dict:
    """Load validation rules from a YAML file and validate against a JSON schema.

    Args:
      file_path (str): Path to the rules file in YAML format.
      schema_path (str): Path to the JSON schema file for validation.

    Returns:
      dict: The validated rules.

    Raises:
      ValidationError: If the rules do not conform to the schema.
    """
    with open(file_path, 'r') as file:
      rules = yaml.safe_load(file)
      file.close()
    with open(schema_path, 'r') as sf:
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
    transactions_df['sort'] = transactions_df[headers['date']].apply(dateutil.parser.parse)
    transactions_df = transactions_df.sort_values(by='sort')
    return transactions_df

  def normalize_transactions(self, transactions_df: any, headers: dict) -> any:
    """Normalize transactions for income and expense.

    Args:
      transactions_df (any): The DataFrame containing transaction data.
      headers (dict): The headers mapping for the DataFrame.

    Returns:
      any: The normalized DataFrame with properly categorized amounts.
    """
    if headers['amount'] in transactions_df.columns:
      transactions_df[headers['withdraw']] = transactions_df[headers['amount']].apply(lambda x: float(x.replace(',', '')) if (float(x.replace(',', ''))<0) else 0)
      transactions_df[headers['deposit']] = transactions_df[headers['amount']].apply(lambda x: float(x.replace(',', '')) if (float(x.replace(',', ''))>0) else 0)
    else:
      transactions_df[headers['withdraw']] = -transactions_df[headers['withdraw']]
    transactions_df[headers['amount']] = transactions_df[headers['deposit']] + transactions_df[headers['withdraw']]
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
    income_rules = rules['rules']['income']
    expense_rules = rules['rules']['expense']
    amount_prefix = rules.get('output', {}).get('amount', {}).get('prefix', '$')  # Default to '$' if not defined

    output = []
    for _, row in transactions_df.iterrows():
      date = dateutil.parser.parse(row[headers['date']])
      formatted_date = date.strftime('%Y/%m/%d')
      description = row[headers['description']]
      amount_str = str(row[headers['amount']])
      # Remove commas from the amount string and convert to float
      amount = float(amount_str.replace(',', ''))
      applicable_rules = income_rules if amount > 0 else expense_rules
      amount = abs(amount)
      rule = self.match_rule(description, applicable_rules)
      if rule:
        debit_account = rule['debit_account']
        credit_account = rule['credit_account']
        output_description = re.sub(r'[^a-zA-Z0-9 ]+', ' ', rule.get('description', description)).title().replace('\n', ' ')
        output.append(f"{formatted_date} {output_description}\n\t{debit_account:<50}{amount_prefix}{amount}\n\t{credit_account}")
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
      regex = fnmatch.translate(rule['transaction_type'].lower())
      if not re.search(regex, transaction_type.lower()) is None:
        return rule
    return None
