import pandas as pd


def create_test_transaction(date="2024-07-19", description="TEST", amount="100.00"):
    """Helper to create test transaction DataFrame."""
    return pd.DataFrame({
        "Transaction Date": [date],
        "Description": [description],
        "Amount": [amount]
    })


def test_transform_transactions_basic(csv_processor, sample_rules):
  transactions_df = create_test_transaction(
      "2024-07-19", "TRANSFER RENT PAYMENT Wyndham Realty", "1,701.80"
  )

  # Transform transactions
  output = csv_processor.transform_transactions(
    transactions_df, sample_rules, csv_processor.headers
  )

  assert len(output) == 1
  assert "2024/07/19 Transfer Rent Payment Wyndham Realty" in output[0]
  assert "Assets:AU:Savings:HSBC" in output[0]
  assert "Income:AU:Interest" in output[0]


def test_transform_transactions_no_matching_rules(csv_processor, sample_rules):
  transactions_df = create_test_transaction(
      "2024-07-19", "UNKNOWN TRANSACTION", "1,000.00"
  )

  # Transform transactions
  output = csv_processor.transform_transactions(
    transactions_df, sample_rules, csv_processor.headers
  )

  assert len(output) == 0  # No output as there are no matching rules


def test_transform_transactions_negative_amount(csv_processor, sample_rules):
  transactions_df = create_test_transaction(
      "2024-07-19", "RENT PAID", "-1,000.00"
  )

  # Transform transactions
  output = csv_processor.transform_transactions(
    transactions_df, sample_rules, csv_processor.headers
  )

  assert len(output) == 1
  assert "2024/07/19 Rent Paid" in output[0]
  assert "Expenses:AU" in output[0]
  assert "Assets:AU:Savings:HSBC" in output[0]


def test_transform_transactions_empty_data(csv_processor, sample_rules):
  # Preparing empty DataFrame
  transactions_df = pd.DataFrame(columns=["Transaction Date", "Description", "Amount"])

  # Transform transactions
  output = csv_processor.transform_transactions(
    transactions_df, sample_rules, csv_processor.headers
  )

  assert len(output) == 0  # Expecting empty output


def test_transform_transactions_different_date_format(csv_processor, sample_rules):
  transactions_df = create_test_transaction(
      "07-19-2024", "HONORABLE EXPENSE", "-1,200.00"
  )

  # Transform transactions
  output = csv_processor.transform_transactions(
    transactions_df, sample_rules, csv_processor.headers
  )

  assert len(output) == 1
  assert "2024/07/19 Honorable Expense" in output[0]
  assert "Expenses:AU" in output[0]
  assert "Assets:AU:Savings:HSBC" in output[0]


def test_metadata_capture_during_processing(csv_processor, sample_rules):
    """Test transaction processing captures confidence and rule analytics."""
    # Arrange: Custom rules for testing with mixed confidence scenarios
    test_rules = {
        "input": sample_rules["input"],
        "rules": {
            "income": [
                {
                    "transaction_type": "TRANSFER RENT PAYMENT Wyndham Realty",
                    "debit_account": "Assets:AU:Savings:HSBC",
                    "credit_account": "Income:AU:Interest"
                }
            ],
            "expense": [
                {
                    "transaction_type": "*PAYMENT*",  # More specific pattern that won't match "CRYPTIC CODE"
                    "debit_account": "Expenses:AU",
                    "credit_account": "Assets:AU:Savings:HSBC"
                }
            ]
        }
    }
    
    # Mixed confidence transactions for testing confidence scoring
    data = {
        "Transaction Date": ["2024-07-19", "2024-07-20", "2024-07-21"],
        "Description": [
            "TRANSFER RENT PAYMENT Wyndham Realty",  # High confidence: specific rule match
            "MISC PAYMENT",                          # Medium confidence: matches wildcard rule  
            "CRYPTIC CODE XYZ123"                    # Low confidence: no clear pattern, uses default
        ],
        "Amount": ["1,701.80", "-500.00", "-25.00"],
    }
    transactions_df = pd.DataFrame(data)

    # Act: Process with capture_metadata=True
    result = csv_processor.transform_transactions(
        transactions_df, test_rules, csv_processor.headers, capture_metadata=True
    )

    # Assert: Returns (output, metadata) tuple when capture_metadata=True
    assert isinstance(result, tuple), "Expected tuple (output, metadata) when capture_metadata=True"
    output, metadata = result
    
    # Verify output structure
    assert isinstance(output, list), "Output should be list of transaction strings"
    assert len(output) == 2, "Expected 2 processed transactions (1 income, 1 expense with matching rules)"
    
    # Verify metadata structure 
    assert isinstance(metadata, dict), "Metadata should be dictionary"
    assert "transactions" in metadata, "Metadata should contain transactions list"
    assert "summary" in metadata, "Metadata should contain summary statistics"
    
    # Verify transaction metadata details
    transaction_metadata = metadata["transactions"]
    assert len(transaction_metadata) == 3, "Should have metadata for all 3 input transactions"
    
    # Test high confidence transaction (specific rule match)
    high_conf_tx = transaction_metadata[0]
    assert high_conf_tx["confidence_score"] >= 0.9, "Specific rule match should have high confidence"
    assert high_conf_tx["matched_rule_type"] == "specific", "Should identify specific rule match"
    assert "TRANSFER RENT PAYMENT" in high_conf_tx["description"]
    
    # Test medium confidence transaction (wildcard rule match)  
    med_conf_tx = transaction_metadata[1]
    assert 0.5 <= med_conf_tx["confidence_score"] < 0.9, "Wildcard rule should have medium confidence"
    assert med_conf_tx["matched_rule_type"] == "wildcard", "Should identify wildcard rule match"
    
    # Test low confidence transaction (no rule match)
    low_conf_tx = transaction_metadata[2] 
    assert low_conf_tx["confidence_score"] < 0.5, "No rule match should have low confidence"
    assert low_conf_tx["matched_rule_type"] == "none", "Should identify no rule match"
    
    # Verify summary analytics
    summary = metadata["summary"]
    assert "total_transactions" in summary
    assert "rule_usage" in summary
    assert "confidence_distribution" in summary
    assert summary["total_transactions"] == 3


def test_backward_compatibility_without_metadata_capture(csv_processor, sample_rules):
    """Test transform_transactions maintains backward compatibility when capture_metadata=False."""
    transactions_df = create_test_transaction(
        "2024-07-19", "TRANSFER RENT PAYMENT Wyndham Realty", "1,701.80"
    )

    # Act: Process without capture_metadata (default behavior)
    output = csv_processor.transform_transactions(
        transactions_df, sample_rules, csv_processor.headers
    )

    # Assert: Returns list directly (not tuple) for backward compatibility  
    assert isinstance(output, list), "Should return list directly when capture_metadata=False"
    assert len(output) == 1, "Should process transaction normally"
    assert "2024/07/19 Transfer Rent Payment Wyndham Realty" in output[0]
    
    # Act: Explicitly test capture_metadata=False
    output_explicit = csv_processor.transform_transactions(
        transactions_df, sample_rules, csv_processor.headers, capture_metadata=False
    )
    
    # Assert: Same behavior with explicit False
    assert isinstance(output_explicit, list), "Should return list when capture_metadata=False"
    assert output == output_explicit, "Default and explicit False should produce identical results"

