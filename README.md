# pyledger

---
# 1. Introduction
## 1.1. Purpose

This document describes the `pyledger` CLI application for Ledger, a CLI application that provides a double-entry accounting system.

## 1.2. Audience

The audience for this document includes:

* Developer who will develop the application, run unit tests, configure build tools and write user documentation.

* DevSecOps Engineer who will shape the workflow, and write playbooks and runbooks.

---
# 2. System Overview
## 2.1. Benefits and Values

1. Currently, creating a Ledger input requires the User to enter a debit and credit record for each transaction, which may be inefficient and error prone.

2. The `pyledger` allows the User to create a rules file that will govern the transformation process of an input file to an output file, hence reducing the error rate, while increasing the reusability and adding version control for a configuration as code.

## 2.2. Workflow

This project uses several methods and products to optimize your workflow.
- Use a version control system (**GitHub**) to track your changes and collaborate with others.
- Use a cloud LLM (**ChatGPT**) to facilitate shaping and writing playbook and runbooks.
- Use a diagram as code tool (**Mermaid**) to draw any system design or diagram.
- Use a Python LLM-enabled CLI (**Aider.chat**) to facilitate coding.
- Use a build tool (**Makefile**) to automate your build tasks.
- Use a package manager (**pipenv**) to manage your dependencies.
- Use a testing framework (**pytest**) to automate your testing.
- Use a linter (**check-jsonschema**) to lint the rules YAML file.
- Use a containerization platform (**Docker**) to run your application in any environment.

---
# 3. User Personas
## 3.1 RACI Matrix

|            Category            |                    Activity                     | Developer | DevSecOps |
|:------------------------------:|:-----------------------------------------------:|:---------:|:---------:|
| Installation and Configuration | Configure `aider.chat` in your local repository |           |    R,A    |
| Installation and Configuration |          Create the project structure           |           |    R,A    |
| Installation and Configuration |               Create a `Makefile`               |           |    R,A    |
|       Shaping by GPT-4o        |           Create a `conftest.py` file           |    R,A    |           |
|       Shaping by GPT-4o        |            Create and run unit tests            |    R,A    |           |
|       Shaping by GPT-4o        |         Create a main `ledger.py` file          |    R,A    |           |

---
# 4. Requirements
## 4.1. Local workstation

- ChatGPT Desktop for macOS
- Python 3.11.6 (`/opt/homebrew/bin/python3`)
  - `aider-chat==0.36.0` (`python3 -m pip install`)
  - `pandas==2.2.2` (`pipenv install`)
  - `typer==0.12.3` (`pipenv install`)
  - `pyyaml==6.0.1` (`pipenv install`)
  - `openpyxl==3.1.3` (`pipenv install`)
  - `pytest==8.2.2` (`pipenv install --dev`)

## 4.2. SaaS accounts

- GitHub account
- OpenAI ChatGPT Plus account

---
# 5. Installation and Configuration
## 5.1. Configure `aider.chat` in your local repository

This runbook should be performed by the DevSecOps Engineer.

1. Open a bash terminal and navigate to your workspace > type the following command.

```sh
git clone https://github.com/dennislwm/pyledger
```

2. Create an file `.env` in your editor and copy and paste the content below, replacing the `<TOKEN>` with your API token.

```txt
export OPENAI_API_KEY=<TOKEN>
```

3. Navigate to your local repository `pyledger`, and type the command:

```sh
source .env
aider --version
```

> Note: You do not need to launch a virtual environment, if the package `aider-chat` was `pip` installed globally.

## 5.2. Create the project structure

This runbook should be performed by the Developer.

1. Create a new directory structure for your project with the following subdirectories and files.

```sh
pyledger/
|- .env
|- .gitignore
|- README.md
+- app/
   |- ledger.py
   |- Makefile
   +- tests/
      |- conftest.py
+- rules/
   |- rules_hsbc.yaml
```

## 5.3. Create a `Makefile`

This runbook should be performed by the Developer.

<details>
    <summary>Click here to create a app/Makefile file.</strong></summary>

1. Create a new file `app/Makefile`.

```Makefile
.PHONY: default install_new install_test run shell shell_clean test test_verbose

default: test

install_new:
	pipenv install pandas==2.2.2 pyyaml==6.0.1 openpyxl==3.1.3 typer==0.12.3
	pipenv install --dev pytest==8.2.2

run:
	python ledger.py

shell:
	pipenv shell

shell_clean:
	pipenv --rm

test:
	PYTHONPATH=.:../ pytest

test_verbose:
	PYTHONPATH=.:../ pytest -v -s
```

</details>

---
# 6. Shaping by GPT-4o
## 6.1. Create a `conftest.py` file

This runbook should be performed by the Developer with the [help](./chat/openai.input.history.md#creating-unit-tests) of GPT-4o.

<details>
    <summary>Click here to create a app/tests/conftest.py file.</strong></summary>

1. Create a `app/tests/conftest.py` file.

```py
import pytest
import pandas as pd
import yaml
from typer.testing import CliRunner

@pytest.fixture
def sample_transactions():
    data = {
        "Date": ["2023/08/01", "2023/08/02"],
        "Description": ["Maturity of Fixed Deposit", "Interest"],
        "Amount": [70000, 1575]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_rules():
    rules_yaml = """
    rules:
      - transaction_type: "Maturity of Fixed Deposit"
        debit_account: "Assets:AU:Savings:HSBC"
        credit_account: "Assets:AU:Term:HSBC:Aug23"
      - transaction_type: "Interest"
        debit_account: "Assets:AU:Savings:HSBC"
        credit_account: "Income:AU:Interest"
    """
    return yaml.safe_load(rules_yaml)

@pytest.fixture
def runner():
    return CliRunner()
```

</details>

## 6.2. Create and run unit tests

This runbook should be performed by the Developer with the [help](./chat/openai.input.history.md#create-unit-tests) of GPT-4o.

1. Create unit test files.

- **Testing function `load_input()`**

  <details>
      <summary>Click here to create a tests/test_load_input.py file.</strong></summary>

  ```py
  import pandas as pd
  import pytest

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
  ```

  </details>

- **Testing function `load_rules()`**

  <details>
      <summary>Click here to create a app/tests/test_load_rules.py file.</strong></summary>

  ```py
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
  ```

  </details>

- **Testing function `transform_transactions()`**

  <details>
      <summary>Click here to create a app/tests/test_transform_transactions.py file.</strong></summary>

  ```py
  def test_transform_transactions(sample_transactions, sample_rules):
      output = transform_transactions(sample_transactions, sample_rules)
      assert len(output) == 2
      assert "2023/08/01 Maturity of Fixed Deposit" in output[0]
      assert "2023/08/02 Interest" in output[1]
  ```

  </details>

- **Testing function `main()`**

  <details>
      <summary>Click here to create a app/tests/test_main.py file.</strong></summary>

  ```py
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
  ```

  </details>

2. Run the unit tests by typing `make test`.

```sh
PYTHONPATH=.:../ pytest -v -s
================================================= test session starts ==================================================
platform darwin -- Python 3.11.6, pytest-8.2.2, pluggy-1.5.0 -- /Users/dennislwm/.local/share/virtualenvs/app-M3_O-iuZ/bin/python
cachedir: .pytest_cache
rootdir: /Users/dennislwm/fx-git-pull/13pyledger/app
collected 5 items

tests/test_load_input.py::test_load_input_file_csv PASSED
tests/test_load_input.py::test_load_input_file_xlsx PASSED
tests/test_load_rules.py::test_load_rules PASSED
tests/test_main.py::test_main PASSED
tests/test_transform_transactions.py::test_transform_transactions PASSED

================================================== 5 passed in 0.05s ===================================================
```

## 6.3. Create a main `ledger.py` file

This runbook should be performed by the Developer with the [help](./chat/openai.input.history.md) of GPT-4o.

1. Create a `app/ledger.py` file.

  <details>
      <summary>Click here to create a app/ledger.py file.</strong></summary>

  ```sh
  import pandas as pd
  import yaml
  import typer
  from pathlib import Path

  app = typer.Typer()

  def load_input_file(file_path: Path):
      if file_path.suffix == '.csv':
          return pd.read_csv(file_path)
      elif file_path.suffix == '.xlsx':
          return pd.read_excel(file_path)
      else:
          raise ValueError("Unsupported file format. Please provide a CSV or XLSX file.")

  def load_rules(file_path: Path):
      with open(file_path, 'r') as file:
          return yaml.safe_load(file)

  def transform_transactions(transactions_df, rules):
      output = []
      for _, row in transactions_df.iterrows():
          date = row['Date']
          description = row['Description']
          amount = row['Amount']
          for rule in rules['rules']:
              if rule['transaction_type'] in description:
                  debit_account = rule['debit_account']
                  credit_account = rule['credit_account']
                  output.append(f"{date} {description}\n\t{debit_account:<50}{amount}\n\t{credit_account}")
                  break
      return output

  @app.command()
  def main(input_file: Path = typer.Argument(..., help="Path to the input CSV or XLSX file"),
          rules_file: Path = typer.Argument(..., help="Path to the rules YAML file"),
          output_file: Path = typer.Argument("output.txt", help="Path to the output TXT file")):
      transactions_df = load_input_file(input_file)
      rules = load_rules(rules_file)
      output = transform_transactions(transactions_df, rules)

      with open(output_file, 'w') as file:
          file.write("\n".join(output))

      typer.echo(f"Output has been saved to {output_file}")

  if __name__ == "__main__":
      app()
  ```

  </details>