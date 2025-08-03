# Transaction Review Dashboard - Shaping Specification

## Expiration
**Project Cycle**: 6 cups of coffee (2-3 weeks)
**Status**: Ready for building phase

## Motivation

### User Pain Points
- **Manual review burden**: 15-30 minutes scanning 50+ lines of text output per statement
- **Hidden issues**: Default rule matches and unused YAML rules invisible in standard output
- **Error detection**: 40% of errors from undetected misclassifications
- **No feedback loop**: Trial-and-error rule optimization without guidance

### Target Workflow
- **Current**: Manual text scanning → visual pattern identification → trial-and-error adjustments
- **Target**: `--review` flag → HTML dashboard → specific recommendations → optimized rules
- **Time savings**: 30 minutes → 5 minutes with actionable feedback

## Appetite
**Resource**: 6 cups of coffee (2-3 weeks)

**Constraints:**
- Single bank processing only
- Static HTML (no server components)
- Extend existing transform_transactions() method
- Reuse CSS from example_review_dashboard.html

**Success Criteria:**
- `--review` flag generates HTML dashboard
- Actionable rule optimization recommendations
- Confidence scoring identifies misclassifications
- Rule usage statistics show effectiveness

## Solution Elements

### 1. CLI Enhancement
Add `--review` flag to existing Typer CLI:
```bash
python ledger.py input.csv rules.yaml --review        # HTML dashboard only
python ledger.py input.csv rules.yaml --review --output  # Both formats
```

### 2. Metadata Capture
Extend `BaseProcessor.transform_transactions()` with optional metadata collection:
- Capture rule matches, confidence scores, and potential issues during processing
- Return tuple: `(ledger_output, metadata)` when `capture_metadata=True`

**Confidence Scoring:**
- **High**: Specific pattern matches
- **Medium**: Default rule with recognizable patterns
- **Low**: Default rule with unusual/missing descriptions

### 3. HTML Dashboard
**Components:**
- Summary metrics (total transactions, match confidence, rule usage)
- Critical review table (low/medium confidence transactions)
- Rule effectiveness analytics
- Actionable recommendations

**Template:**
- Embedded CSS from example_review_dashboard.html
- Card-based layout with color-coded confidence indicators
- Static HTML generation via string formatting

### 4. Integration
- Add `generate_review_dashboard()` method to BaseProcessor
- Output: `{input_filename}_review.html` in same directory as standard output
- Maintain 100% backward compatibility

## Rabbit Holes
**Avoid:**
- Multi-bank batch processing (single CSV + rules only)
- Real-time rule editing (read-only dashboard)
- Advanced analytics/ML (simple pattern analysis only)
- Database integration (stateless file processing)
- Custom styling (single embedded theme)

## No-Goes
**Explicitly excluded:**
- Multi-bank batch processing
- Interactive features (editing, JavaScript)
- Server-side components or APIs
- Historical data tracking
- Machine learning capabilities
- Custom configuration options
- Mobile/PWA features

## Technical Specifications

### Implementation Details
**New BaseProcessor methods:**
- `_analyze_transaction_match()` - rule matching and confidence scoring
- `_identify_issues()` - transaction problem detection
- `generate_review_dashboard()` - HTML generation from metadata

**CLI Integration:**
- Add `--review` flag to existing Typer structure
- Conditional metadata capture when flag present
- Output: `{input_filename}_review.html`

**Performance:**
- Minimal overhead (metadata during existing iteration)
- HTML generation < 1 second
- Linear memory scaling with transaction count

## Risk Mitigation
**Technical Risks:**
- Use proven HTML/CSS from existing example
- Extend BaseProcessor methods (no architectural changes)
- Distinct filename patterns prevent conflicts

**UX Risks:**
- Follow established patterns from example dashboard
- Supplementary feature (doesn't replace existing workflow)

## Success Metrics
**Implementation validation:**
- `--review` flag generates HTML dashboard
- Zero impact on existing functionality
- Confidence scoring identifies problem transactions
- Actionable rule optimization recommendations

**Business value:**
- 80% reduction in manual review time (30 min → 5 min)
- Visual issue identification replaces text scanning
- No additional tools required (offline HTML)

## Handoff Specifications

**Dependencies:**
- No new packages (existing Typer/pandas/YAML stack)
- HTML generation via string templating
- Embedded CSS (no external dependencies)

**File Structure:**
```
app/
├── ledger.py                    # CLI --review flag
├── common/base_processor.py     # Enhanced transform_transactions()
├── templates/review_dashboard.html  # HTML template
└── tests/review_dashboard_test.py   # Dashboard tests
```

**Testing:**
- Unit tests for metadata capture
- Integration tests for HTML generation
- CLI flag behavior validation
- Backward compatibility verification

## Implementation Reference

### HTML Template Structure
```html
<!-- Summary Metrics Card Layout -->
<div class="summary">
    <div class="metric-card">
        <div class="metric-number">17</div>
        <div class="metric-label">Total Transactions</div>
    </div>
    <!-- Repeat for: Successfully Matched, Needs Review, Match Confidence -->
</div>

<!-- Transaction Review Table -->
<table class="transaction-table">
    <thead>
        <tr>
            <th>Date</th><th>Description</th><th>Amount</th>
            <th>Matched Rule</th><th>Confidence</th><th>Issue</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2025/07/16</td>
            <td class="description">Revddt25071611048169838</td>
            <td class="amount">$97.70</td>
            <td>Default (*)</td>
            <td class="confidence-low">Low</td>
            <td>Unusual description pattern</td>
        </tr>
    </tbody>
</table>
```

### Essential CSS Classes
```css
.confidence-high { color: #27ae60; font-weight: bold; }    /* Green */
.confidence-medium { color: #f39c12; font-weight: bold; }  /* Orange */
.confidence-low { color: #e74c3c; font-weight: bold; }     /* Red */
.rule-unused { background-color: #fff3cd; }               /* Yellow background */
.rule-frequent { background-color: #d1ecf1; }             /* Blue background */
.amount { text-align: right; font-family: monospace; }
```

### Dashboard Sections (Order)
1. **Header**: Bank, period, rules file, generation timestamp
2. **Summary Cards**: 4 metrics in flex layout
3. **Needs Review**: Critical transactions requiring attention
4. **Successfully Matched**: Verification of correct categorization
5. **Rule Statistics**: Usage patterns and optimization opportunities
6. **Recommendations**: Actionable improvement suggestions

---

## Summary
**Investment**: 6 cups of coffee (2-3 weeks)
**Value**: 80% reduction in review time + immediate error detection + actionable recommendations
**ROI**: 9:1 through systematic workflow improvement
