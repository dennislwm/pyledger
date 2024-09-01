import pandas as pd
import pytest
from pandas.errors import EmptyDataError
from pathlib import Path

def test_load_valid_csv(csv_processor):
  assert isinstance(csv_processor.transactions, pd.DataFrame)
  assert not csv_processor.transactions.empty

def test_load_non_existent_file(csv_processor):
  input_file_path = Path('non_existent_file.csv')
  with pytest.raises(FileNotFoundError):
    csv_processor.load_input_file(input_file_path)

def test_load_empty_csv(csv_processor, sample_output_file):
  with pytest.raises(EmptyDataError):
    csv_processor.load_input_file(sample_output_file.name)
