"""Vale output parser for Aditi.

This module parses Vale JSON output and creates structured Violation objects
for processing by the rule engine.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

from rich.console import Console

console = Console()


class Severity(Enum):
    """Vale violation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


@dataclass
class Violation:
    """Represents a Vale violation/issue found in a file."""
    file_path: Path
    rule_name: str
    line: int
    column: int
    message: str
    severity: Severity
    original_text: str
    suggested_fix: Optional[str] = None
    check: str = ""  # The Vale check name (e.g., "AsciiDocDITA.EntityReference")
    link: Optional[str] = None  # Link to documentation

    @classmethod
    def from_vale_alert(cls, file_path: Path, alert: Dict[str, Any]) -> "Violation":
        """Create a Violation from a Vale alert dictionary."""
        # Handle different field names in Vale output
        line = alert.get("Line", 0)
        
        # Get column - Vale might provide Span instead of Column
        column = alert.get("Column", 0)
        if column == 0 and "Span" in alert:
            span = alert["Span"]
            if isinstance(span, list) and len(span) >= 1:
                column = span[0]
        
        return cls(
            file_path=file_path,
            rule_name=alert.get("Check", "").split(".")[-1],  # Extract rule name from check
            line=line,
            column=column,
            message=alert.get("Message", ""),
            severity=Severity(alert.get("Severity", "warning").lower()),
            original_text=alert.get("Match", ""),
            suggested_fix=alert.get("Suggestions", [None])[0] if alert.get("Suggestions") else None,
            check=alert.get("Check", ""),
            link=alert.get("Link", None) or ""
        )


class ValeParser:
    """Parses Vale JSON output and creates structured violations."""

    def __init__(self):
        self.violations: List[Violation] = []

    def parse_json_output(self, json_output: str) -> List[Violation]:
        """Parse Vale JSON output and return list of violations.
        
        Args:
            json_output: Raw JSON output from Vale
            
        Returns:
            List of Violation objects
            
        Raises:
            json.JSONDecodeError: If the output is not valid JSON
            ValueError: If the JSON structure is unexpected
        """
        try:
            vale_results = json.loads(json_output)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing Vale output:[/red] {e}")
            raise

        violations = []
        
        # Vale output is a dictionary with file paths as keys
        for file_path_str, file_data in vale_results.items():
            file_path = Path(file_path_str)
            # Convert relative paths back to absolute paths
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            
            # Handle both dictionary format (with "Alerts" key) and array format
            if isinstance(file_data, dict):
                alerts = file_data.get("Alerts", [])
            elif isinstance(file_data, list):
                alerts = file_data
            else:
                continue
            
            for alert in alerts:
                try:
                    violation = Violation.from_vale_alert(file_path, alert)
                    violations.append(violation)
                except (KeyError, ValueError) as e:
                    console.print(f"[yellow]Warning: Skipping malformed alert:[/yellow] {e}")
                    continue
        
        return violations

    def group_by_file(self, violations: List[Violation]) -> Dict[Path, List[Violation]]:
        """Group violations by file path.
        
        Args:
            violations: List of violations to group
            
        Returns:
            Dictionary mapping file paths to their violations
        """
        grouped: Dict[Path, List[Violation]] = {}
        
        for violation in violations:
            if violation.file_path not in grouped:
                grouped[violation.file_path] = []
            grouped[violation.file_path].append(violation)
            
        return grouped

    def group_by_rule(self, violations: List[Violation]) -> Dict[str, List[Violation]]:
        """Group violations by rule name.
        
        Args:
            violations: List of violations to group
            
        Returns:
            Dictionary mapping rule names to their violations
        """
        grouped: Dict[str, List[Violation]] = {}
        
        for violation in violations:
            if violation.rule_name not in grouped:
                grouped[violation.rule_name] = []
            grouped[violation.rule_name].append(violation)
            
        return grouped

    def filter_by_severity(self, violations: List[Violation], severity: Severity) -> List[Violation]:
        """Filter violations by severity level.
        
        Args:
            violations: List of violations to filter
            severity: Severity level to filter by
            
        Returns:
            List of violations matching the severity
        """
        return [v for v in violations if v.severity == severity]

    def get_statistics(self, violations: List[Violation]) -> Dict[str, Any]:
        """Get statistics about the violations.
        
        Args:
            violations: List of violations to analyze
            
        Returns:
            Dictionary with violation statistics
        """
        stats = {
            "total": len(violations),
            "by_severity": {
                Severity.ERROR.value: len(self.filter_by_severity(violations, Severity.ERROR)),
                Severity.WARNING.value: len(self.filter_by_severity(violations, Severity.WARNING)),
                Severity.SUGGESTION.value: len(self.filter_by_severity(violations, Severity.SUGGESTION))
            },
            "by_rule": {},
            "files_affected": len(set(v.file_path for v in violations))
        }
        
        # Count by rule
        rule_groups = self.group_by_rule(violations)
        for rule_name, rule_violations in rule_groups.items():
            stats["by_rule"][rule_name] = len(rule_violations)
            
        return stats