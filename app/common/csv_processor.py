from abc import ABC
from pathlib import Path
from common.base_processor import BaseProcessor, DEFAULT_HEADERS
import pandas as pd

class CsvProcessor(BaseProcessor, ABC):
  def __init__(self, rules_file_path: Path, input_file_path: Path):
    """
    Initializes the CsvProcessor instance.

    Args:
      rules_file_path (Path): The file path to the rules file to determine how to process the CSV.
      input_file_path (Path): The file path to the input CSV file containing transactions.

    This constructor loads the rules from the provided rules file, retrieves the headers
    based on those rules, and loads the input CSV file into a DataFrame.
    """
    self.rules = self.load_rules(rules_file_path)
    self.headers = self.get_header(self.rules)
    self.transactions = self.load_input_file(input_file_path)

  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    """
    Loads the input CSV file into a pandas DataFrame.

    Args:
      file_path (Path): The file path of the input CSV file.

    Returns:
      pd.DataFrame: A DataFrame containing the data from the CSV file.
    """
    try:
      ret = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
      raise pd.errors.EmptyDataError
    return ret

  def get_header(self, rules) -> dict:
    """
    Retrieves the headers for the CSV based on the provided rules.

    Args:
      rules (dict): The rules loaded from the rules file.

    Returns:
      dict: A dictionary of headers for the CSV formatted according to the rules.

    If the rules specify custom headers for the CSV input, they will replace the default headers.
    Defaults to the headers defined in DEFAULT_HEADERS if no custom headers are found.
    """
    headers = {**DEFAULT_HEADERS}
    if 'input' in rules and 'csv' in rules['input']:
      csv_rules = rules['input']['csv']
      if 'header' in csv_rules:
        headers.update(csv_rules['header'])
    return headers
