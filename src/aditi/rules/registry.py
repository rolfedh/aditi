"""Rule registry for discovering and managing rules."""

from typing import Dict, List, Type, Optional
import importlib
import pkgutil
from pathlib import Path

from .base import Rule
from ..vale_parser import Violation
from rich.console import Console

console = Console()


class RuleRegistry:
    """Registry for managing and discovering rules."""
    
    def __init__(self):
        self._rules: Dict[str, Type[Rule]] = {}
        self._instances: Dict[str, Rule] = {}
        
    def register(self, rule_class: Type[Rule]) -> None:
        """Register a rule class.
        
        Args:
            rule_class: The rule class to register
        """
        # Create an instance to get the name
        instance = rule_class()
        self._rules[instance.name] = rule_class
        self._instances[instance.name] = instance
        
    def get_rule(self, name: str) -> Optional[Rule]:
        """Get a rule instance by name.
        
        Args:
            name: The rule name
            
        Returns:
            The rule instance or None if not found
        """
        return self._instances.get(name)
    
    def get_rule_for_violation(self, violation: Violation) -> Optional[Rule]:
        """Get the appropriate rule for a violation.
        
        Args:
            violation: The violation to process
            
        Returns:
            The rule that can handle this violation, or None
        """
        # Try exact match first
        rule = self.get_rule(violation.rule_name)
        if rule and rule.can_fix(violation):
            return rule
            
        # Try all rules to see if any can handle it
        for rule in self._instances.values():
            if rule.can_fix(violation):
                return rule
                
        return None
    
    def get_all_rules(self) -> List[Rule]:
        """Get all registered rules.
        
        Returns:
            List of all rule instances
        """
        return list(self._instances.values())
    
    def get_rules_in_dependency_order(self) -> List[Rule]:
        """Get rules sorted by their dependencies.
        
        Returns:
            List of rules in the order they should be executed
        """
        # Build dependency graph
        rules = self.get_all_rules()
        rule_map = {rule.name: rule for rule in rules}
        
        # Topological sort
        visited = set()
        result = []
        
        def visit(rule_name: str):
            if rule_name in visited:
                return
            visited.add(rule_name)
            
            rule = rule_map.get(rule_name)
            if not rule:
                return
                
            # Visit dependencies first
            for dep in rule.dependencies:
                if dep in rule_map:
                    visit(dep)
                    
            result.append(rule)
        
        # Visit all rules
        for rule_name in rule_map:
            visit(rule_name)
            
        return result
    
    def auto_discover(self, package_path: Optional[Path] = None) -> None:
        """Auto-discover and register rules from the rules package with caching.
        
        Args:
            package_path: Optional path to the rules package
        """
        # Skip if already discovered to avoid repeated work
        if self._rules:
            return
            
        if package_path is None:
            package_path = Path(__file__).parent
            
        discovered_count = 0
        failed_count = 0
        
        # Import all modules in the rules package
        for module_info in pkgutil.iter_modules([str(package_path)]):
            if module_info.name in ['base', 'registry', '__init__']:
                continue
                
            try:
                module = importlib.import_module(f'.{module_info.name}', package='aditi.rules')
                
                # Find all Rule subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Rule) and 
                        attr != Rule and
                        not getattr(attr, '__abstractmethods__', None)):
                        try:
                            self.register(attr)
                            discovered_count += 1
                        except Exception as e:
                            console.print(f"[yellow]Warning: Failed to register rule {attr_name}:[/yellow] {e}")
                            failed_count += 1
                        
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to load rule module {module_info.name}:[/yellow] {e}")
                failed_count += 1
        
        # Show summary instead of individual messages for cleaner output
        if discovered_count > 0:
            console.print(f"[green]✅ Discovered {discovered_count} rules[/green]" + 
                         (f" ({failed_count} failed)" if failed_count > 0 else ""))


# Global registry instance
_registry = RuleRegistry()


def get_rule_registry() -> RuleRegistry:
    """Get the global rule registry instance.
    
    Returns:
        The global RuleRegistry instance
    """
    return _registry