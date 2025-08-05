# Analytics Recommender Agent

## Purpose
Provide specific improvement suggestions based on transaction analytics data to translate generic analytics into actionable next steps for rule optimization.

## Core Functionality
- Analyze transaction processing analytics and rule effectiveness data
- Generate specific, actionable recommendations for rule configuration improvements
- Identify patterns in unmatched transactions that suggest new rules
- Recommend configuration cleanup opportunities
- Provide concrete next steps with transaction counts and examples

## Key Capabilities

### Rule Creation Recommendations
- Identify frequently occurring transaction patterns without specific rules
- Suggest new rule patterns based on transaction descriptions
- Provide usage frequency data to justify new rules
- Example: "Add rule for 'PAYPAL TRANSFER' (8 occurrences)" 

### Configuration Cleanup
- Identify unused rules that can be safely removed
- Recommend rule consolidation opportunities
- Suggest rule refinements for low-performing patterns
- Example: "Remove 3 unused rules: income.*A200 DST*, income.*SELL A200*, expense.*Manor*"

### Performance Optimization
- Recommend rule specificity improvements for better confidence scores
- Suggest pattern refinements for wildcard rules with low confidence
- Identify rules that could be more targeted
- Example: "Replace 'expense.*' with 'expense.*grocery*' for 5 grocery transactions"

### Priority-Based Recommendations
- Rank recommendations by potential impact (transaction frequency × confidence improvement)
- Focus on high-volume, low-confidence transaction patterns first
- Provide implementation priority guidance

## Input Requirements
- Transaction metadata with confidence scores
- Rule analytics including usage counts and effectiveness metrics
- Unmatched transaction patterns
- Rule performance data

## Output Format
- Prioritized list of specific recommendations
- Implementation effort estimates (easy/medium/hard)
- Expected impact metrics (confidence improvement, transaction coverage)
- Concrete examples with transaction counts

## Usage Context
This agent should be used after processing transaction data to provide users with clear, actionable steps for improving their rule configuration based on actual usage patterns and performance metrics.