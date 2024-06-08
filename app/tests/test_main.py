from ledger import app, main

def test_main(tmp_path, runner):
  input_csv = tmp_path / "input.csv"
  rules_yaml = tmp_path / "rules.yaml"
  output_txt = tmp_path / "output.txt"

  input_csv.write_text("Date,Description,Amount\n2023/08/01,Maturity of Fixed Deposit,70000\n2023/08/02,Interest,1575\n")
  rules_yaml.write_text("""
  rules:
    - transaction_type: "Maturity of Fixed Deposit"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Assets:AU:Term:HSBC:Aug23"
    - transaction_type: "Interest"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Income:AU:Interest"
  """)

  result = runner.invoke(app, [str(input_csv), str(rules_yaml), str(output_txt)])
  assert result.exit_code == 0
  assert output_txt.read_text() == (
    "2023/08/01 Maturity of Fixed Deposit\n"
    "\tAssets:AU:Savings:HSBC                            70000\n"
    "\tAssets:AU:Term:HSBC:Aug23\n"
    "2023/08/02 Interest\n"
    "\tAssets:AU:Savings:HSBC                            1575\n"
    "\tIncome:AU:Interest"
  )
