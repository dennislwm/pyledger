import pandas as pd
import yaml
import typer
from pathlib import Path

app = typer.Typer()

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

def transform_transactions(transactions_df, rules):
  output = []
  for _, row in transactions_df.iterrows():
    date = row['Date']
    description = row['Description']
    amount = row['Amount']
    for rule in rules['rules']:
      if rule['transaction_type'] in description:
        debit_account = rule['debit_account']
        credit_account = rule['credit_account']
        output.append(f"{date} {description}\n\t{debit_account:<50}{amount}\n\t{credit_account}")
        break
  return output

@app.command()
def main(input_file: Path = typer.Argument(..., help="Path to the input CSV or XLSX file"),
     rules_file: Path = typer.Argument(..., help="Path to the rules YAML file"),
     output_file: Path = typer.Argument("output.txt", help="Path to the output TXT file")):
  transactions_df = load_input_file(input_file)
  rules = load_rules(rules_file)
  output = transform_transactions(transactions_df, rules)

  with open(output_file, 'w') as file:
    file.write("\n".join(output))

  typer.echo(f"Output has been saved to {output_file}")

if __name__ == "__main__":
  app()