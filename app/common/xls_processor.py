from abc import ABC
from pathlib import Path
from common.base_processor import BaseProcessor, DEFAULT_HEADERS
import pandas as pd

class XlsProcessor(BaseProcessor, ABC):
  def __init__(self, rules_file_path: Path, input_file_path: Path):
    self.rules = self.load_rules(rules_file_path)
    self.headers = self.get_header(self.rules)
    self.transactions = self.load_input_file(input_file_path)

  def load_input_file(self, file_path: Path) -> pd.DataFrame:
    return pd.read_excel(file_path)

  def get_header(self, rules) -> dict:
    headers = {**DEFAULT_HEADERS}
    if 'input' in rules and 'csv' in rules['input'] and 'header' in rules['input']['csv']:
      for header in rules['input']['csv']['header']:
        key, value = next(iter(header.items()))
        headers[key] = value
    return headers
