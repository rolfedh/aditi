#!/usr/bin/env python3
"""
Script to analyze Vale rules from AsciiDocDITA and generate corresponding Aditi rule implementations.

This script:
1. Fetches Vale rule files from the AsciiDocDITA repository
2. Analyzes their structure and patterns
3. Generates Python rule implementations for Aditi
4. Categorizes rules by fix type (deterministic, partial, non-deterministic)
"""

import re
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class ValeRuleAnalyzer:
    """Analyzes Vale rules and determines how they can be automated in Aditi."""
    
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/jhradilek/asciidoctor-dita-vale/main/styles/AsciiDocDITA"
    
    # Mapping of Vale rule types to potential fix types
    RULE_TYPE_MAPPING = {
        "existence": "non_deterministic",  # Usually requires human judgment
        "occurrence": "partial_deterministic",  # Can often add placeholders
        "substitution": "fully_deterministic",  # Direct replacements
        "script": "complex",  # Requires deeper analysis
        "sequence": "non_deterministic",  # Order issues need human review
        "capitalization": "fully_deterministic",  # Can be automated
        "spelling": "fully_deterministic",  # If we have correct spelling
    }
    
    def __init__(self):
        self.rules_data = {}
        
    def fetch_rule_list(self) -> List[str]:
        """Fetch list of all Vale rules from the repository."""
        # For now, return the known list. In production, this would query GitHub API
        return [
            "AdmonitionTitle", "AttributeReference", "AuthorLine", "BlockTitle",
            "ConditionalCode", "ContentType", "CrossReference", "DiscreteHeading",
            "EntityReference", "EquationFormula", "ExampleBlock", "IncludeDirective",
            "LineBreak", "LinkAttribute", "NestedSection", "PageBreak",
            "RelatedLinks", "ShortDescription", "SidebarBlock", "TableFooter",
            "TagDirective", "TaskDuplicate", "TaskExample", "TaskSection",
            "TaskStep", "TaskTitle", "ThematicBreak"
        ]
    
    def fetch_rule_content(self, rule_name: str) -> Optional[Dict]:
        """Fetch and parse a Vale rule YAML file."""
        url = f"{self.GITHUB_RAW_BASE}/{rule_name}.yml"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return yaml.safe_load(response.text)
        except Exception as e:
            print(f"Error fetching {rule_name}: {e}")
            return None
    
    def analyze_rule_type(self, rule_data: Dict) -> Tuple[str, str]:
        """Analyze a Vale rule and determine its type and potential fix type."""
        extends = rule_data.get("extends", "")
        
        # Determine Vale rule type
        vale_type = extends
        
        # Determine potential fix type
        if extends == "substitution" and "swap" in rule_data:
            fix_type = "fully_deterministic"
        elif extends == "existence":
            # Check if it's just detecting presence/absence
            if "tokens" in rule_data:
                fix_type = "non_deterministic"
            else:
                fix_type = "partial_deterministic"
        elif extends == "script":
            # Scripts are complex and need manual analysis
            fix_type = "complex"
        else:
            fix_type = self.RULE_TYPE_MAPPING.get(extends, "non_deterministic")
            
        return vale_type, fix_type
    
    def generate_python_rule(self, rule_name: str, rule_data: Dict) -> str:
        """Generate Python code for an Aditi rule based on Vale rule data."""
        vale_type, fix_type = self.analyze_rule_type(rule_data)
        message = rule_data.get("message", "No message provided")
        level = rule_data.get("level", "warning")
        
        # Convert snake_case
        snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', rule_name).lower()
        
        template = f'''"""
{rule_name} rule implementation.

Auto-generated from Vale rule: {rule_name}.yml
Original message: {message}
Vale type: {vale_type}
"""

from typing import Optional
from .base import Rule, FixType, Fix
from ..vale_parser import Violation


class {rule_name}Rule(Rule):
    """{message}"""
    
    @property
    def name(self) -> str:
        return "{rule_name}"
    
    @property
    def fix_type(self) -> FixType:
        return FixType.{fix_type.upper()}
    
    @property
    def description(self) -> str:
        return "{message}"
    
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation."""
        # TODO: Implement based on Vale rule logic
        return violation.rule_name == self.name
    
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation."""
        if not self.can_fix(violation):
            return None
'''
        
        # Add specific logic based on rule type
        if vale_type == "substitution" and "swap" in rule_data:
            # Generate substitution logic
            template += self._generate_substitution_logic(rule_data)
        elif vale_type == "occurrence" and fix_type == "partial_deterministic":
            # Generate occurrence/addition logic
            template += self._generate_occurrence_logic(rule_data)
        else:
            # Generic template
            template += '''        
        # TODO: Implement fix generation logic
        # This is a {vale_type} rule with {fix_type} fixes
        
        return None
'''.format(vale_type=vale_type, fix_type=fix_type)
        
        return template
    
    def _generate_substitution_logic(self, rule_data: Dict) -> str:
        """Generate code for substitution rules."""
        swap_dict = rule_data.get("swap", {})
        
        code = '''        
        # Substitution mappings
        REPLACEMENTS = {
'''
        for old, new in swap_dict.items():
            code += f'            "{old}": "{new}",\n'
        
        code += '''        }
        
        # Get the matched text
        matched_text = violation.original_text
        replacement = self.REPLACEMENTS.get(matched_text)
        
        if not replacement:
            return None
            
        return Fix(
            violation=violation,
            replacement_text=replacement,
            confidence=1.0,
            requires_review=False,
            description=f"Replace '{matched_text}' with '{replacement}'"
        )
'''
        return code
    
    def _generate_occurrence_logic(self, rule_data: Dict) -> str:
        """Generate code for occurrence rules (missing content)."""
        token = rule_data.get("token", "")
        
        code = f'''        
        # This rule checks for missing content
        # Token pattern: {token}
        
        # For partial deterministic rules, we can add a placeholder
        # TODO: Implement logic to determine where to add the missing content
        
        placeholder = "<PLACEHOLDER: Add required content here>"
        
        return Fix(
            violation=violation,
            replacement_text=placeholder,
            confidence=0.5,
            requires_review=True,
            description="Add missing required content"
        )
'''
        return code
    
    def analyze_all_rules(self):
        """Analyze all Vale rules and generate a summary."""
        rule_names = self.fetch_rule_list()
        
        summary = {
            "fully_deterministic": [],
            "partial_deterministic": [],
            "non_deterministic": [],
            "complex": [],
            "errors": []
        }
        
        for rule_name in rule_names:
            print(f"Analyzing {rule_name}...")
            rule_data = self.fetch_rule_content(rule_name)
            
            if not rule_data:
                summary["errors"].append(rule_name)
                continue
                
            vale_type, fix_type = self.analyze_rule_type(rule_data)
            self.rules_data[rule_name] = {
                "data": rule_data,
                "vale_type": vale_type,
                "fix_type": fix_type
            }
            
            summary[fix_type].append({
                "name": rule_name,
                "type": vale_type,
                "message": rule_data.get("message", ""),
                "level": rule_data.get("level", "")
            })
        
        return summary
    
    def generate_rule_files(self, output_dir: Path):
        """Generate Python rule files for all analyzed rules."""
        output_dir.mkdir(exist_ok=True)
        
        for rule_name, rule_info in self.rules_data.items():
            snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', rule_name).lower()
            output_file = output_dir / f"{snake_name}_generated.py"
            
            python_code = self.generate_python_rule(rule_name, rule_info["data"])
            output_file.write_text(python_code)
            print(f"Generated {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate Aditi rules from Vale rules")
    parser.add_argument("--analyze", action="store_true", 
                        help="Analyze all rules and print summary")
    parser.add_argument("--generate", type=str, 
                        help="Generate Python rules in specified directory")
    parser.add_argument("--rule", type=str,
                        help="Analyze or generate a specific rule")
    
    args = parser.parse_args()
    
    analyzer = ValeRuleAnalyzer()
    
    if args.analyze:
        summary = analyzer.analyze_all_rules()
        
        print("\n=== Rule Analysis Summary ===\n")
        
        print(f"Fully Deterministic ({len(summary['fully_deterministic'])} rules):")
        for rule in summary['fully_deterministic']:
            print(f"  - {rule['name']} ({rule['type']}): {rule['message'][:50]}...")
            
        print(f"\nPartial Deterministic ({len(summary['partial_deterministic'])} rules):")
        for rule in summary['partial_deterministic']:
            print(f"  - {rule['name']} ({rule['type']}): {rule['message'][:50]}...")
            
        print(f"\nNon-Deterministic ({len(summary['non_deterministic'])} rules):")
        for rule in summary['non_deterministic']:
            print(f"  - {rule['name']} ({rule['type']}): {rule['message'][:50]}...")
            
        print(f"\nComplex ({len(summary['complex'])} rules):")
        for rule in summary['complex']:
            print(f"  - {rule['name']} ({rule['type']}): {rule['message'][:50]}...")
    
    elif args.generate:
        output_dir = Path(args.generate)
        analyzer.analyze_all_rules()
        analyzer.generate_rule_files(output_dir)
        
    elif args.rule:
        # Analyze a specific rule
        rule_data = analyzer.fetch_rule_content(args.rule)
        if rule_data:
            vale_type, fix_type = analyzer.analyze_rule_type(rule_data)
            print(f"\nRule: {args.rule}")
            print(f"Vale Type: {vale_type}")
            print(f"Fix Type: {fix_type}")
            print(f"Message: {rule_data.get('message', '')}")
            print(f"\nRule Data:")
            print(yaml.dump(rule_data, default_flow_style=False))
            
            if args.generate:
                # Generate just this rule
                output_dir = Path(args.generate)
                output_dir.mkdir(exist_ok=True)
                analyzer.rules_data[args.rule] = {
                    "data": rule_data,
                    "vale_type": vale_type,
                    "fix_type": fix_type
                }
                python_code = analyzer.generate_python_rule(args.rule, rule_data)
                snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', args.rule).lower()
                output_file = output_dir / f"{snake_name}_generated.py"
                output_file.write_text(python_code)
                print(f"\nGenerated {output_file}")


if __name__ == "__main__":
    main()