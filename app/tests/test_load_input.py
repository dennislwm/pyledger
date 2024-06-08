import pandas as pd
from ledger import load_input_file

def test_load_input_file_csv(tmp_path):
  csv_file = tmp_path / "input.csv"
  csv_file.write_text("Date,Description,Amount\n2023/08/01,Maturity of Fixed Deposit,70000\n2023/08/02,Interest,1575\n")
  df = load_input_file(csv_file)
  assert not df.empty
  assert df.shape == (2, 3)

def test_load_input_file_xlsx(tmp_path):
  xlsx_file = tmp_path / "input.xlsx"
  df = pd.DataFrame({
    "Date": ["2023/08/01", "2023/08/02"],
    "Description": ["Maturity of Fixed Deposit", "Interest"],
    "Amount": [70000, 1575]
  })
  df.to_excel(xlsx_file, index=False)
  loaded_df = load_input_file(xlsx_file)
  assert not loaded_df.empty
  assert loaded_df.shape == (2, 3)
