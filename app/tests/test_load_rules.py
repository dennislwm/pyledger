from ledger import load_rules

def test_load_rules(tmp_path):
  yaml_file = tmp_path / "rules.yaml"
  rules_yaml = """
  rules:
    - transaction_type: "Maturity of Fixed Deposit"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Assets:AU:Term:HSBC:Aug23"
    - transaction_type: "Interest"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Income:AU:Interest"
  """
  yaml_file.write_text(rules_yaml)
  rules = load_rules(yaml_file)
  assert "rules" in rules
  assert len(rules["rules"]) == 2

