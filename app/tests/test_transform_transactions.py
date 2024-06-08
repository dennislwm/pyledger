from ledger import transform_transactions

def test_transform_transactions(sample_transactions, sample_rules):
  output = transform_transactions(sample_transactions, sample_rules)
  assert len(output) == 2
  assert "2023/08/01 Maturity of Fixed Deposit" in output[0]
  assert "2023/08/02 Interest" in output[1]
