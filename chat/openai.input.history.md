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