import pandas as pd
import pytest

def test_sort_transactions_standard_dates(base_processor):
  transactions = pd.DataFrame({
    'Date': ['2023-01-01', '2023-02-01', '2023-01-15'],
    'Description': ['Transaction 1', 'Transaction 2', 'Transaction 3'],
    'Amount': [100, 200, 150]
  })
  headers = base_processor.get_header({})

  sorted_transactions = base_processor.sort_transactions(transactions, headers)

  assert sorted_transactions['Date'].values.tolist() == ['2023-01-01', '2023-01-15', '2023-02-01']

def test_sort_transactions_mixed_dates(base_processor):
  transactions = pd.DataFrame({
    'Date': ['2023-01-01', 'invalid_date', '2023-01-15'],
    'Description': ['Transaction 1', 'Transaction 2', 'Transaction 3'],
    'Amount': [100, 200, 150]
  })
  headers = base_processor.get_header({})

  with pytest.raises(ValueError):  # Expecting a ValueError due to the invalid date
    base_processor.sort_transactions(transactions, headers)

def test_sort_transactions_identical_timestamps(base_processor):
  transactions = pd.DataFrame({
    'Date': ['2023-01-01 10:00', '2023-01-01 10:00', '2023-01-01 10:00'],
    'Description': ['Transaction 1', 'Transaction 2', 'Transaction 3'],
    'Amount': [100, 200, 150]
  })
  headers = base_processor.get_header({})

  sorted_transactions = base_processor.sort_transactions(transactions, headers)

  assert (sorted_transactions['Description'].values.tolist() == ['Transaction 1', 'Transaction 2', 'Transaction 3'])

def test_sort_transactions_missing_dates(base_processor):
  transactions = pd.DataFrame({
      'Date': ['2023-01-01', None, '2023-01-15'],
      'Description': ['Transaction 1', 'Transaction 2', 'Transaction 3'],
      'Amount': [100, 200, 150]
  })
  headers = base_processor.get_header({})

  with pytest.raises(TypeError):  # Expecting a TypeError due to the invalid date
    sorted_transactions = base_processor.sort_transactions(transactions, headers)

def test_sort_transactions_empty_dataframe(base_processor):
  headers = base_processor.get_header({})
  transactions = pd.DataFrame(columns=headers.values())

  sorted_transactions = base_processor.sort_transactions(transactions, headers)

  assert sorted_transactions.empty  # The result should also be an empty DataFrame
