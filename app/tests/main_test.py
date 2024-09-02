import pytest
import tempfile
from ledger import app


def test_unsupported_file_format(runner, sample_rules_file, sample_output_file):
  unsupported_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")

  with pytest.raises(ValueError):
    runner.invoke(
      app, unsupported_file.name, sample_rules_file.name, sample_output_file.name
    )
