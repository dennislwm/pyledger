## Create a main application
Hi,
I want you to assume the role of an accountant that does ledger statements using the accounting rule.
When given an input file in either CSV or XLSX format, you should perform:
a. Prompt for an input file as either CSV or XLSX format.
b. Read the input file and use it as the source of truth for all transactions.
c. Create a rules file in YAML format to govern the transformation of input data to output result.
d. Transform the input data to output result file in TXT format using the rules.yaml file.
e. The output result of must be in the same format as below:

2023/08/01 HSBC AU Maturity of Fixed Deposit
	Assets:AU:Savings:HSBC			  70000
	Assets:AU:Term:HSBC:Aug23
...

---
Can you modify the python script to use the typer library for any parameters used in the main application

---
## Create unit tests
Now create a test_main.py file that tests the main application using pytest

---
This is a modified rules file that applies to income and expenses separately.
A. If the amount is positive, then rules below income will be used, however, if the amount is negative, rules under expense will be used instead.
B. The transaction type allows for wildcards, such as *, ?.
C. Update the code for changes, and also the test cases.

rules:
  - income:
    - transaction_type: "Maturity of Fixed Deposit"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Assets:AU:Term:HSBC:Aug23"
    - transaction_type: "*"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Income:AU:Interest"
  - expense:
    - transaction_type: "*"
      debit_account: "Expenses:AU"
      credit_account: "Assets:AU:Savings:HSBC"

---
I've modifed the rules.yaml file to have an input.csv.header that applies to css files only.
a. The column header names should use the input.csv.header if it exists, otherwise just use the default header names of "Date", "Description", and "Amount".
b. Use a default variable in the code that stores the default header names as a dictionary. This default variable will be compared to the input object, and any specified input will override the default variable dictionary.

input:
  csv:
    header:
      - date: "Transaction Date"
      - description: "Description"
      - amount: "Amount"

---
I got this error how do I resolve it?

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/dennislwm/fx-git-pull/13pyledger/app/ledger.py", line 43, in transform_transactions
    amount = float(row[headers['amount']])
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: could not convert string to float: '1,925.03'

---
The output date is printed as '01 May 2024' but I want it to be in this format '2024/05/01'.

---
I've modified the rules object to include an optional description key:
a. If the description key is specified, then the output description should use the value given in the rules, otherwise use the description from the input file.

rules:
  - income:
    - transaction_type: "Maturity of Fixed Deposit"
      description: "Maturity of Fixed Deposit"
      debit_account: "Assets:AU:Savings:HSBC"
      credit_account: "Assets:AU:Term:HSBC:Aug23"

---
The match_rule function should be case insensitive

---
For the input, I want to sort the transformation_df by date in ascending order, before calling the function transform_transactions.

transactions_df = transactions_df.sort_values(by=headers['parsed_date'])

The above line is giving the error KeyError: parsed_date

---
I want to refactor the code to use object-oriented concepts:
(1) A Parent class BaseProcessor that has the following interface using ABC:
- rules: dict
- headers: dict
- load_rules() -> self.rules
- load_input_file() -> dataframe
- get_header() -> self.header
2) Child classes XlsProcessor for XLS files and CsvProcessor for CSV files that inherit and implement the parent class BaseProcessor.
3) A parent class that has the following interface methods, and a child class that implements:
- validate_header() -> boolean
- transform() -> list(string)

---
I have changed the input rules file, could you update the get_headers method in class CsvProcessor

---
I want to be able to specify the start of row using a rules.yaml file as follows when using a XLS file:

input:
  xls:
    sheet:
      first_row: 5

---
## Create a `schema.json` file

cat ../rules/rules_hsbc.yaml | llm 'Generate a schema.json file using the specification from https://json-schema.org/draft/2020-12/schema'

---
## Enhance the `load_rules` method to validate the rules file against a JSON schema

cat common/base_processor.py | llm 'Edit the python function load_rules to validate the yaml file using a schema.json file and library check-jsonschema'

---
## Suggest test cases for a method and write test functions for each test case

cat common/base_processor.py | llm 'Suggest what to test for sort_transactions method in class BaseProcessor and write test functions for each test case with pytest class TestBaseProcessor but do not use unittest.mock or pandas, and use an existing schema.json file'