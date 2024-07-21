from abc import ABC
from pathlib import Path
from common.base_processor import BaseProcessor, DEFAULT_HEADERS
import pandas as pd

class XlsProcessor(BaseProcessor, ABC):
  def __init__(self, rules_file_path: Path, input_file_path: Path):
    self.rules = self.load_rules(rules_file_path)
    self.headers = self.get_header(self.rules)
    self.first_row = self.__get_first_row(self.rules)
    self.transactions = self.load_input_file(input_file_path)

  def __get_first_row(self, rules):
    if 'input' in rules and 'xls' in rules['input'] and 'sheet' in rules['input']['xls']:
      first_row = rules['input']['xls']['sheet'].get('first_row', 1)  # Default to 1 if not specified
      return first_row
    return 1  # Default to 1 if not specified

  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    try:
      df = pd.read_excel(file_path, skiprows=self.first_row - 1)
      return df
    except Exception as e:
      raise

  def get_header(self, rules) -> dict:
    headers = {**DEFAULT_HEADERS}
    if 'input' in rules and 'xls' in rules['input'] and 'header' in rules['input']['xls']:
        headers.update(rules['input']['xls']['header'])
    return headers
