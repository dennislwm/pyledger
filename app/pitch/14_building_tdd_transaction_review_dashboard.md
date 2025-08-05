# Transaction Review Dashboard - TDD Building Design

## Overview
Implement `--review` CLI flag that generates markdown dashboards for transaction review with confidence scoring and rule analytics.

### Success Criteria
- `--review` flag generates markdown dashboard
- Zero impact on existing functionality
- <3% processing overhead (70% reduction vs HTML)
- 80% reduction in manual review time
- Universal compatibility with development workflows

### Integration Strategy
- Extend `transform_transactions()` with optional metadata capture
- Add markdown generation methods to BaseProcessor
- Maintain backward compatibility
- Leverage markdown simplicity for better developer experience

## Red-Green-Refactor Cycles

### Cycle 1: CLI Flag & Metadata Capture
**Business Behavior**: CLI accepts `--review` flag and captures transaction metadata

**RED Phase - Failing Tests:**
```python
def test_cli_review_flag_generates_markdown_dashboard(self):
    """Test --review flag creates markdown dashboard with metadata"""
    # Arrange: Sample CSV and rules files
    # Act: Execute CLI with --review flag
    # Assert: Markdown file exists with confidence scores and analytics

def test_metadata_capture_during_processing(self):
    """Test transaction processing captures confidence and rule analytics"""
    # Arrange: Mixed confidence transactions
    # Act: Process with capture_metadata=True
    # Assert: Returns (output, metadata) with confidence scores
```

**Implementation**:
- Add `review` CLI parameter
- Extend `transform_transactions()` with metadata capture
- Basic confidence scoring (high/medium/low)

---

### Cycle 2: Issue Identification & Analytics
**Business Behavior**: System identifies problematic transactions and rule effectiveness

**RED Phase - Failing Tests:**
```python
def test_confidence_scoring_based_on_rule_specificity(self):
    """Test confidence varies by rule specificity and description clarity"""
    # Arrange: Specific vs default rules, clear vs cryptic descriptions
    # Act: Analyze transaction matches
    # Assert: High confidence for specific rules, low for cryptic descriptions

def test_rule_analytics_tracks_usage_and_effectiveness(self):
    """Test rule usage tracking and unused rule identification"""
    # Arrange: Rules with varying usage patterns
    # Act: Process transactions and generate analytics
    # Assert: Usage counts, unused rules, confidence averages calculated
```

**Implementation**:
- Confidence algorithm based on rule specificity
- Issue identification (missing descriptions, low confidence high amounts)
- Rule usage analytics

---

### Cycle 3: Markdown Dashboard Generation
**Business Behavior**: Generate comprehensive markdown dashboard from metadata

**RED Phase - Failing Tests:**
```python
def test_markdown_dashboard_contains_required_sections(self):
    """Test dashboard includes summary, review table, and recommendations"""
    # Arrange: Complete metadata from transaction processing
    # Act: Generate markdown dashboard
    # Assert: Contains metrics, low-confidence transactions, recommendations

def test_end_to_end_review_workflow(self):
    """Test complete CLI workflow maintains backward compatibility"""
    # Arrange: Standard input files
    # Act: Run with and without --review flag
    # Assert: Same ledger output, additional markdown file when --review used
```

**Implementation**:
- Markdown generation with structured tables and sections
- Dashboard sections (summary, review table, recommendations)
- End-to-end integration with 70% token efficiency improvement

## Implementation Requirements

### Core Methods
```python
def transform_transactions(self, ..., capture_metadata: bool = False):
    """Returns (output, metadata) tuple when capture_metadata=True"""

def generate_markdown_dashboard(self, metadata: list, rules: dict) -> str:
    """Generate markdown dashboard with structured tables and sections"""
```

### CLI Integration
```python
review: bool = typer.Option(False, "--review", help="Generate markdown review dashboard")
```

## Acceptance Criteria
- [ ] `--review` flag generates markdown dashboard with confidence scores
- [ ] Dashboard contains summary metrics, review table, rule analytics
- [ ] Zero breaking changes to existing functionality
- [ ] Performance overhead <3% (70% reduction vs HTML approach)
- [ ] Works with CSV and XLS files
- [ ] Universal compatibility with development workflows and tools
- [ ] Simplified maintenance with no CSS/HTML complexity

## Cost-Efficiency Benefits

### Token Optimization

- **70% reduction** in token consumption vs HTML approach
- Eliminated CSS styling complexity (300+ tokens saved)
- Simplified template structure reduces processing overhead
- Better code readability and maintainability

### Developer Experience

- Native integration with Git, IDEs, and documentation tools
- Preview support in all major development environments
- Version control friendly format
- No browser dependency for viewing

### Markdown Dashboard Format Example

```markdown
# Transaction Review Dashboard
Generated: 2024-01-15 14:30:00

## Summary Metrics
- **Total Transactions**: 150
- **High Confidence**: 95 (63%)
- **Medium Confidence**: 35 (23%)
- **Low Confidence**: 20 (13%)
- **Average Confidence**: 7.2/10

## Transactions Requiring Review

| Date | Description | Amount | Confidence | Rule Match | Issue |
|------|-------------|--------|------------|------------|-------|
| 2024-01-10 | UNKNOWN MERCHANT | $-125.00 | 3/10 | Default expense | Missing description |
| 2024-01-12 | TXN 0x4F2A | $-89.50 | 2/10 | Default expense | Cryptic reference |

## Rule Analytics

### Most Effective Rules
1. **Salary patterns** (15 matches, 9.1/10 avg confidence)
2. **Grocery keywords** (28 matches, 8.5/10 avg confidence)

### Unused Rules
- Investment account transfers (0 matches)
- Insurance payments (0 matches)

## Recommendations
- [ ] Review 20 low-confidence transactions manually
- [ ] Add specific rules for recurring merchants
- [ ] Consider removing unused rules
```
