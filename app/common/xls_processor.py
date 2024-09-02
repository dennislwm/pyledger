from abc import ABC
from pathlib import Path
from common.base_processor import BaseProcessor, DEFAULT_HEADERS
import pandas as pd


class XlsProcessor(BaseProcessor, ABC):
  """
  A class to process Excel files based on specific rules defined in a rules file.

  Attributes:
    rules (dict): The processing rules loaded from the rules file.
    headers (dict): The headers to use for processing the transactions.
    first_row (int): The row number from which to start reading the transactions.
    transactions (pd.DataFrame): The loaded transactions from the input Excel file.
  """

  def __init__(self, rules_file_path: Path, input_file_path: Path):
    """
    Initializes the XlsProcessor with the provided rules file and input file paths.

    Args:
      rules_file_path (Path): The file path to the rules file.
      input_file_path (Path): The file path to the input Excel file.
    """
    self.rules = self.load_rules(rules_file_path)
    self.headers = self.get_header(self.rules)
    self.first_row = self.__get_first_row(self.rules)
    self.transactions = self.load_input_file(input_file_path)

  def __get_first_row(self, rules):
    """
    Determines the first row to read from the Excel sheet based on the provided rules.

    Args:
      rules (dict): The processing rules.

    Returns:
      int: The first row number to start reading from the sheet.
    """
    if (
      "input" in rules and "xls" in rules["input"] and "sheet" in rules["input"]["xls"]
    ):
      first_row = rules["input"]["xls"]["sheet"].get(
        "first_row", 1
      )  # Default to 1 if not specified
      return first_row
    return 1  # Default to 1 if not specified

  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    """
    Loads the input Excel file into a DataFrame, skipping rows as specified.

    Args:
      file_path (Path): The path to the input Excel file.

    Returns:
      pd.DataFrame: The loaded transactions as a DataFrame.

    Raises:
      Exception: If there is an error loading the Excel file.
    """
    try:
      df = pd.read_excel(file_path, skiprows=self.first_row - 1)
      return df
    except Exception:
      raise

  def get_header(self, rules) -> dict:
    """
    Retrieves the headers for the DataFrame based on the defined rules.

    Args:
      rules (dict): The processing rules.

    Returns:
      dict: A dictionary containing the headers for the transactions.
    """
    headers = {**DEFAULT_HEADERS}
    if (
      "input" in rules and "xls" in rules["input"] and "header" in rules["input"]["xls"]
    ):
      headers.update(rules["input"]["xls"]["header"])
    return headers
