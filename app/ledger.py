import typer
from pathlib import Path
from common.csv_processor import CsvProcessor
from common.xls_processor import XlsProcessor

app = typer.Typer()


@app.command()
def main(
  input_file: Path = typer.Argument(..., help="Path to the input CSV or XLSX file"),
  rules_file: Path = typer.Argument(..., help="Path to the rules YAML file"),
):
  if input_file.suffix == ".csv":
    processor = CsvProcessor(rules_file, input_file)
  elif input_file.suffix == ".xls":
    processor = XlsProcessor(rules_file, input_file)
  else:
    raise ValueError("Unsupported file format. Please provide a CSV or XLS file.")

  rules = processor.rules
  headers = processor.headers
  transactions = processor.transactions
  transactions_df = processor.sort_transactions(transactions, headers)
  transactions_df = processor.normalize_transactions(transactions_df, headers)
  output = processor.transform_transactions(transactions_df, rules, headers)

  output_path = rules.get("output", {}).get("path")
  if output_path:
    with open(output_path, "w") as file:
      file.write("\n".join(output))
    typer.echo(f"Output has been saved to {output_path}")
  else:
    typer.echo("\n".join(output))


if __name__ == "__main__":
  app()
