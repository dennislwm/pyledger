from abc import ABC, abstractmethod
import dateutil.parser
import fnmatch, re
import yaml

DEFAULT_HEADERS= {
  "date": "Date",
  "description": "Description",
  "income": "Deposit",
  "withdraw": "Withdrawal",
  "deposit": "Amount"
}

class BaseProcessor(ABC):
  def __init__(self):
    self.rules: dict = {}
    self.headers: dict = {}
    self.transactions: any

  @abstractmethod
  def load_input_file(self, file_path) -> any:
    """Load input file and return as a DataFrame."""
    pass

  @abstractmethod
  def get_header(self, rules: dict) -> dict:
    """Return the headers attribute."""
    pass

  def load_rules(self, file_path) -> dict:
    with open(file_path, 'r') as file:
      return yaml.safe_load(file)

  def sort_transactions(self, transactions_df: any, headers: dict) -> any:
    # Sort the transactions by date in ascending order
    transactions_df['sort'] = transactions_df[headers['date']].apply(dateutil.parser.parse)
    transactions_df = transactions_df.sort_values(by='sort')
    return transactions_df

  def normalize_transactions(self, transactions_df: any, headers: dict) -> any:
    # Normalize amount, income and expense.
    if headers['amount'] in transactions_df.columns:
      transactions_df[headers['withdraw']] = transactions_df[headers['amount']].apply(lambda x: float(x.replace(',', '')) if (float(x.replace(',', ''))<0) else 0)
      transactions_df[headers['deposit']] = transactions_df[headers['amount']].apply(lambda x: float(x.replace(',', '')) if (float(x.replace(',', ''))>0) else 0)
    else:
      transactions_df[headers['withdraw']] = -transactions_df[headers['withdraw']]
    transactions_df[headers['amount']] = transactions_df[headers['deposit']] + transactions_df[headers['withdraw']]
    return transactions_df

  def transform_transactions(self, transactions_df: any, rules: dict, headers: dict):
    income_rules = rules['rules']['income']
    expense_rules = rules['rules']['expense']

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
        output_description = rule.get('description', description).replace('\n', ' ')
        output.append(f"{formatted_date} {output_description}\n\t{debit_account:<50}${amount}\n\t{credit_account}")
    return output

  def match_rule(self, transaction_type, rules):
    for rule in rules:
      # if fnmatch.fnmatch(transaction_type.lower(), rule['transaction_type'].lower()):
      regex = fnmatch.translate(rule['transaction_type'].lower())
      if not re.search(regex, transaction_type.lower()) is None:
        return rule
    return None
