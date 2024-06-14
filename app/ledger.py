import pandas as pd
import yaml
import typer
from pathlib import Path
import fnmatch
import dateutil.parser

app = typer.Typer()

DEFAULT_HEADERS = {
    "date": "Date",
    "description": "Description",
    "amount": "Amount"
}

def load_input_file(file_path: Path):
  if file_path.suffix == '.csv':
    return pd.read_csv(file_path)
  elif file_path.suffix == '.xlsx':
    return pd.read_excel(file_path)
  else:
    raise ValueError("Unsupported file format. Please provide a CSV or XLSX file.")

def load_rules(file_path: Path):
  with open(file_path, 'r') as file:
    return yaml.safe_load(file)

def match_rule(transaction_type, rules):
  for rule in rules:
    if fnmatch.fnmatch(transaction_type.lower(), rule['transaction_type'].lower()):
      return rule
  return None

def transform_transactions(transactions_df, rules, headers):
    income_rules = rules['rules'][0]['income']
    expense_rules = rules['rules'][1]['expense']

    output = []
    for _, row in transactions_df.iterrows():
        date = dateutil.parser.parse(row[headers['date']])
        formatted_date = date.strftime('%Y/%m/%d')
        description = row[headers['description']]
        amount_str = row[headers['amount']]
        # Remove commas from the amount string and convert to float
        amount = float(amount_str.replace(',', ''))
        applicable_rules = income_rules if amount > 0 else expense_rules
        amount = abs(amount)
        rule = match_rule(description, applicable_rules)
        if rule:
            debit_account = rule['debit_account']
            credit_account = rule['credit_account']
            output_description = rule.get('description', description)
            output.append(f"{formatted_date} {output_description}\n\t{debit_account:<50}{amount}\n\t{credit_account}")
    return output

def get_headers(rules):
  headers = {**DEFAULT_HEADERS}
  if 'input' in rules and 'csv' in rules['input'] and 'header' in rules['input']['csv']:
    for header in rules['input']['csv']['header']:
      key, value = next(iter(header.items()))
      headers[key] = value
  return headers

@app.command()
def main(input_file: Path = typer.Argument(..., help="Path to the input CSV or XLSX file"),
     rules_file: Path = typer.Argument(..., help="Path to the rules YAML file"),
     output_file: Path = typer.Argument("output.txt", help="Path to the output TXT file")):
  rules = load_rules(rules_file)
  headers = get_headers(rules)

  transactions_df = load_input_file(input_file)

  # Sort the transactions by date in ascending order
  transactions_df['sort'] = transactions_df[headers['date']].apply(dateutil.parser.parse)
  transactions_df = transactions_df.sort_values(by='sort')

  output = transform_transactions(transactions_df, rules, headers)

  with open(output_file, 'w') as file:
    file.write("\n".join(output))

  typer.echo(f"Output has been saved to {output_file}")

if __name__ == "__main__":
  app()