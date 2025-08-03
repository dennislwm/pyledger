import pytest
from common.base_processor import BaseProcessor


class TestBaseProcessorSimplifiedSyntax:
    """Test BaseProcessor simplified syntax functionality"""

    def test_syntax_detection(self, base_processor):
        """Test simplified vs legacy syntax detection"""
        simplified = {"rules": {"income": [{"match": "contains salary", "to": "checking", "from": "salary"}]}}
        legacy = {"rules": {"income": [{"transaction_type": "*salary*", "debit_account": "Assets:Bank:Checking"}]}}
        
        assert base_processor.has_simplified_syntax(simplified)
        assert not base_processor.has_simplified_syntax(legacy)

    def test_pattern_conversion(self, base_processor):
        """Test pattern conversion for all types"""
        cases = [
            ("contains salary", "*salary*"),
            ("starts with TRANSFER", "TRANSFER*"),
            ("ends with PAYMENT", "*PAYMENT"),
            ("exactly Rent", "Rent"),
            ("unknown pattern", "unknown pattern")
        ]
        
        for input_pattern, expected in cases:
            assert base_processor.convert_pattern(input_pattern) == expected

    def test_rules_transformation(self, base_processor):
        """Test complete rules transformation with field preservation"""
        simplified = {
            'rules': {
                'income': [{
                    'match': 'contains bonus',
                    'description': 'Annual Bonus',
                    'category': 'Employment',
                    'to': 'checking', 
                    'from': 'salary'
                }],
                'expense': [{
                    'match': 'contains grocery',
                    'note': 'Weekly shopping',
                    'to': 'groceries',
                    'from': 'checking'
                }]
            }
        }
        
        shortcuts = {
            'checking': 'Assets:Bank:Checking',
            'salary': 'Income:Salary',
            'groceries': 'Expenses:Food:Groceries'
        }
        
        result = base_processor.transform_rules(simplified, shortcuts)
        
        # Verify transformation
        income_rule = result['rules']['income'][0]
        expense_rule = result['rules']['expense'][0]
        
        # Check field transformations
        assert income_rule['transaction_type'] == '*bonus*'
        assert income_rule['debit_account'] == 'Assets:Bank:Checking'
        assert income_rule['credit_account'] == 'Income:Salary'
        
        assert expense_rule['transaction_type'] == '*grocery*'
        assert expense_rule['debit_account'] == 'Expenses:Food:Groceries'
        assert expense_rule['credit_account'] == 'Assets:Bank:Checking'
        
        # Check field preservation
        assert income_rule['description'] == 'Annual Bonus'
        assert income_rule['category'] == 'Employment'
        assert expense_rule['note'] == 'Weekly shopping'
        
        # Check field removal
        for rule in [income_rule, expense_rule]:
            assert 'match' not in rule
            assert 'to' not in rule
            assert 'from' not in rule
