import pandas as pd

def test_transform_transactions_basic(csv_processor, sample_rules):
    # Preparing sample transactions
    data = {
        "Transaction Date": ["2024-07-19"],
        "Description": ["TRANSFER RENT PAYMENT Wyndham Realty"],
        "Amount": ["1,701.80"]
    }
    transactions_df = pd.DataFrame(data)

    # Transform transactions
    output = csv_processor.transform_transactions(transactions_df, sample_rules, csv_processor.headers)

    assert len(output) == 1
    assert "2024/07/19 TRANSFER RENT PAYMENT Wyndham Realty" in output[0]
    assert "Assets:AU:Savings:HSBC" in output[0]
    assert "Income:AU:Interest" in output[0]

def test_transform_transactions_no_matching_rules(csv_processor, sample_rules):
    # Preparing sample transactions with no matching rules
    data = {
        "Transaction Date": ["2024-07-19"],
        "Description": ["UNKNOWN TRANSACTION"],
        "Amount": ["1,000.00"]
    }
    transactions_df = pd.DataFrame(data)

    # Transform transactions
    output = csv_processor.transform_transactions(transactions_df, sample_rules, csv_processor.headers)

    assert len(output) == 0  # No output as there are no matching rules

def test_transform_transactions_negative_amount(csv_processor, sample_rules):
    # Preparing sample transactions with negative amount
    data = {
        "Transaction Date": ["2024-07-19"],
        "Description": ["RENT PAID"],
        "Amount": ["-1,000.00"]
    }
    transactions_df = pd.DataFrame(data)

    # Transform transactions
    output = csv_processor.transform_transactions(transactions_df, sample_rules, csv_processor.headers)

    assert len(output) == 1
    assert "2024/07/19 RENT PAID" in output[0]
    assert "Expenses:AU" in output[0]
    assert "Assets:AU:Savings:HSBC" in output[0]

def test_transform_transactions_empty_data(csv_processor, sample_rules):
    # Preparing empty DataFrame
    transactions_df = pd.DataFrame(columns=["Transaction Date", "Description", "Amount"])

    # Transform transactions
    output = csv_processor.transform_transactions(transactions_df, sample_rules, csv_processor.headers)

    assert len(output) == 0  # Expecting empty output

def test_transform_transactions_different_date_format(csv_processor, sample_rules):
    # Preparing transactions with different date formats
    data = {
        "Transaction Date": ["07-19-2024"],
        "Description": ["HONORABLE EXPENSE"],
        "Amount": ["-1,200.00"]
    }
    transactions_df = pd.DataFrame(data)

    # Transform transactions
    output = csv_processor.transform_transactions(transactions_df, sample_rules, csv_processor.headers)

    assert len(output) == 1
    assert "2024/07/19 HONORABLE EXPENSE" in output[0]
    assert "Expenses:AU" in output[0]
    assert "Assets:AU:Savings:HSBC" in output[0]
