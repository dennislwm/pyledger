import pytest
import tempfile
from ledger import app


def test_unsupported_file_format(runner, sample_rules_file, sample_output_file):
  unsupported_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")

  with pytest.raises(ValueError):
    runner.invoke(
      app, unsupported_file.name, sample_rules_file.name, sample_output_file.name
    )


def test_cli_accepts_review_flag_with_backward_compatibility(runner, sample_csv_file, sample_rules_file):
    """Test that CLI accepts --review flag and maintains backward compatibility"""
    # Test with --review flag - should be accepted and show review dashboard
    result = runner.invoke(
        app, 
        [sample_csv_file.name, sample_rules_file.name, "--review"]
    )
    
    # Should not raise an error and should exit successfully
    assert result.exit_code == 0
    
    # Should contain review dashboard output (not the normal ledger output)
    assert "Transaction Review Dashboard" in result.output
    assert "Assets:AU:Savings:HSBC" not in result.output  # Normal ledger output should not appear
    
    # Test backward compatibility - without --review flag should work as before
    result_normal = runner.invoke(
        app,
        [sample_csv_file.name, sample_rules_file.name]
    )
    
    assert result_normal.exit_code == 0
    # Should contain normal processing message (output goes to file)
    assert "Output has been saved to" in result_normal.output
    assert "Transaction Review Dashboard" not in result_normal.output


def test_review_flag_integrates_with_metadata_capture(runner, sample_csv_file, sample_rules_file):
    """Test --review flag captures metadata and shows confidence information."""
    # Sample CSV contains transaction that matches rules
    
    # Act: Run CLI with --review flag
    result = runner.invoke(
        app, 
        [sample_csv_file.name, sample_rules_file.name, "--review"]
    )
    
    # Assert: Should exit successfully
    assert result.exit_code == 0
    
    # Assert: Should show confidence information (not just static message)
    # This validates integration with metadata capture functionality
    assert "confidence" in result.output.lower() or "score" in result.output.lower(), \
        "Review output should show confidence scores from metadata capture"
    
    # Assert: Should show analytics information from metadata
    assert "matched" in result.output.lower() or "pattern" in result.output.lower() or "rule" in result.output.lower(), \
        "Review output should show rule matching analytics from metadata"
    
    # Assert: Should NOT show static message anymore (integration working)
    assert result.output != "Transaction Review Dashboard\n", \
        "Should show meaningful metadata analysis, not just static message"
    
    # Assert: Should still generate normal ledger output file (business requirement)
    # The review functionality should be additive, not replacing normal processing
    output_path = "output.txt"  # From sample rules file
    import os
    assert os.path.exists(output_path), \
        "Review mode should still generate normal ledger output file"
