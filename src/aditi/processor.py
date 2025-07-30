"""File processing engine for Aditi.

This module orchestrates rule execution, manages file operations,
and tracks changes made to AsciiDoc files.
"""

import json
import signal
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from .config import AditiConfig
from .vale_container import ValeContainer
from .vale_parser import ValeParser, Violation, Severity
from .rules import RuleRegistry, FixType, Fix

console = Console()


@dataclass
class FileChange:
    """Represents a change made to a file."""
    file_path: Path
    rule_name: str
    line: int
    original_text: str
    replacement_text: str
    timestamp: datetime = field(default_factory=datetime.now)
    

@dataclass
class ProcessingResult:
    """Results from processing files through the rule pipeline."""
    violations_found: List[Violation]
    fixes_applied: List[Fix] 
    fixes_skipped: List[Fix]
    files_processed: Set[Path]
    files_modified: Set[Path]
    errors: List[str]
    
    @property
    def total_violations(self) -> int:
        return len(self.violations_found)
        
    @property
    def total_fixes_applied(self) -> int:
        return len(self.fixes_applied)
        
    @property
    def total_fixes_available(self) -> int:
        return len(self.fixes_applied) + len(self.fixes_skipped)
        
    def get_violations_by_severity(self) -> Dict[Severity, int]:
        """Get violation counts by severity."""
        counts = {severity: 0 for severity in Severity}
        for violation in self.violations_found:
            counts[violation.severity] += 1
        return counts
        
    def get_violations_by_rule(self) -> Dict[str, int]:
        """Get violation counts by rule."""
        counts = {}
        for violation in self.violations_found:
            counts[violation.rule_name] = counts.get(violation.rule_name, 0) + 1
        return counts


class RuleProcessor:
    """Main processing engine for applying rules to files."""
    
    def __init__(self, vale_container: ValeContainer, config: AditiConfig):
        self.vale_container = vale_container
        self.config = config
        self.vale_parser = ValeParser()
        self.rule_registry = RuleRegistry()
        self._backup_dir: Optional[Path] = None
        self._file_cache: Dict[Path, str] = {}  # Cache file contents to avoid re-reading
        self._lock = threading.Lock()  # Thread safety for parallel processing
        self._interrupted = False  # Track if processing was interrupted
        self._cleanup_handlers: List[callable] = []  # Cleanup functions to call on interrupt
        
        # Auto-discover and register rules (only once)
        if not hasattr(RuleProcessor, '_rules_discovered'):
            self.rule_registry.auto_discover()
            RuleProcessor._rules_discovered = True
            
        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
    def process_files(self, file_paths: List[Path], dry_run: bool = True, rule_filter: Optional[str] = None) -> ProcessingResult:
        """Process files through the rule pipeline.
        
        Args:
            file_paths: List of files to process
            dry_run: If True, don't apply fixes, just report them
            rule_filter: Optional rule name to filter processing to only that rule
            
        Returns:
            ProcessingResult with all findings and changes
        """
        result = ProcessingResult(
            violations_found=[],
            fixes_applied=[],
            fixes_skipped=[],
            files_processed=set(),
            files_modified=set(),
            errors=[]
        )
        
        # Create backup directory if not dry run
        if not dry_run:
            self._backup_dir = self._create_backup_directory()
            
        try:
            # Step 1: Run Vale on all files
            est_time = len(file_paths) * 0.3  # Rough estimate: 0.3s per file for Vale
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task(
                    f"🔍 Running Vale analysis on {len(file_paths)} files (~{est_time:.0f}s estimated)...",
                    total=None
                )
                vale_output = self._run_vale_on_files(file_paths)
            
            if not vale_output:
                result.errors.append("Failed to run Vale analysis")
                return result
                
            # Step 2: Parse Vale output
            violations = self.vale_parser.parse_json_output(vale_output)
            result.violations_found = violations
            
            # Step 3: Group violations by file
            violations_by_file = self.vale_parser.group_by_file(violations)
            
            # Step 4: Process files with parallel processing for better performance
            max_workers = min(4, len(violations_by_file))  # Limit parallelism
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total} files)"),
                console=console
            ) as progress:
                est_time = len(violations_by_file) * 0.5  # Rough estimate: 0.5s per file
                task_desc = f"Processing {len(violations_by_file)} files (~{est_time:.0f}s estimated)"
                task = progress.add_task(task_desc, total=len(violations_by_file))
                
                # Process files in parallel for better performance
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all file processing tasks
                    future_to_file = {
                        executor.submit(self._process_file_violations, file_path, file_violations, dry_run, rule_filter): file_path
                        for file_path, file_violations in violations_by_file.items()
                    }
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        result.files_processed.add(file_path)
                        
                        try:
                            # Check for interruption before processing results
                            self._check_interrupted()
                            
                            fixes = future.result()
                            
                            if fixes:
                                if not dry_run:
                                    # Backup and apply fixes (thread-safe)
                                    with self._lock:
                                        self._check_interrupted()  # Check again inside critical section
                                        self._backup_file(file_path)
                                        applied = self._apply_fixes_to_file(file_path, fixes)
                                        if applied:
                                            result.fixes_applied.extend(applied)
                                            result.files_modified.add(file_path)
                                        else:
                                            result.fixes_skipped.extend(fixes)
                                else:
                                    # In dry run, all fixes are "skipped"
                                    result.fixes_skipped.extend(fixes)
                                    
                        except KeyboardInterrupt:
                            console.print(f"[yellow]Interrupted while processing {file_path}[/yellow]")
                            break  # Exit the processing loop
                        except Exception as e:
                            result.errors.append(f"Error processing {file_path}: {str(e)}")
                            
                        progress.update(task, advance=1)
                    
        except Exception as e:
            result.errors.append(f"Processing error: {str(e)}")
            console.print(f"[red]Error during processing:[/red] {e}")
            
        return result
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            console.print(f"\n[yellow]Received interrupt signal ({signum}). Cleaning up...[/yellow]")
            self._interrupted = True
            
            # Run cleanup handlers
            for handler in self._cleanup_handlers:
                try:
                    handler()
                except Exception as e:
                    console.print(f"[yellow]Warning: Cleanup handler failed: {e}[/yellow]")
            
            console.print("[yellow]Processing interrupted. Partial results may be available.[/yellow]")
        
        # Register handlers for common interrupt signals
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination request
    
    def _add_cleanup_handler(self, handler: callable) -> None:
        """Add a cleanup handler to be called on interrupt."""
        self._cleanup_handlers.append(handler)
    
    def _check_interrupted(self) -> None:
        """Check if processing was interrupted and raise exception if so."""
        if self._interrupted:
            raise KeyboardInterrupt("Processing was interrupted by user")
    
    def _get_file_content(self, file_path: Path) -> str:
        """Get file content with caching for performance.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        # Check cache first
        if file_path in self._file_cache:
            return self._file_cache[file_path]
            
        # Check file size to avoid loading huge files into memory
        try:
            file_size = file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise RuntimeError(f"File {file_path} is too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 10MB.")
        except OSError as e:
            raise RuntimeError(f"Cannot access file {file_path}: {e}")
            
        # Read and cache the content
        try:
            content = file_path.read_text(encoding='utf-8')
            self._file_cache[file_path] = content
            return content
        except UnicodeDecodeError:
            # Try with fallback encoding
            try:
                content = file_path.read_text(encoding='latin-1')
                self._file_cache[file_path] = content
                return content
            except Exception as e:
                raise RuntimeError(f"Cannot decode file {file_path}: {e}")
        
    def _run_vale_on_files(self, file_paths: List[Path]) -> Optional[str]:
        """Run Vale on the specified files.
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            JSON output from Vale or None on error
        """
        try:
            # Convert paths to relative paths from current working directory
            # since the container mounts the project root at /docs
            project_root = Path.cwd()
            path_args = []
            for p in file_paths:
                try:
                    rel_path = p.relative_to(project_root)
                    path_args.append(str(rel_path))
                except ValueError:
                    # If file is outside project root, use absolute path
                    path_args.append(str(p))
            
            # Run Vale with JSON output using optimized method
            output = self.vale_container.run_vale_raw(
                ["--output=JSON"] + path_args,
                project_root
            )
            
            return output
            
        except Exception as e:
            console.print(f"[red]Vale execution failed:[/red] {e}")
            return None
            
    def _process_file_violations(self, file_path: Path, violations: List[Violation], 
                                dry_run: bool, rule_filter: Optional[str] = None) -> List[Fix]:
        """Process violations for a single file.
        
        Args:
            file_path: Path to the file
            violations: List of violations in the file
            dry_run: Whether this is a dry run
            rule_filter: Optional rule name to filter processing to only that rule
            
        Returns:
            List of fixes to apply
        """
        # Read file content with caching
        try:
            file_content = self._get_file_content(file_path)
        except Exception as e:
            console.print(f"[red]Error reading {file_path}:[/red] {e}")
            return []
            
        fixes = []
        
        # Get rules in dependency order
        rules = self.rule_registry.get_rules_in_dependency_order()
        
        # Process violations with each rule
        for rule in rules:
            # Skip if rule filter is set and this isn't the filtered rule
            if rule_filter and rule.name != rule_filter:
                continue
                
            rule_violations = [v for v in violations if v.rule_name == rule.name]
            
            for violation in rule_violations:
                if rule.can_fix(violation):
                    fix = rule.generate_fix(violation, file_content)
                    if fix:
                        fixes.append(fix)
                        
        return fixes
        
    def _apply_fixes_to_file(self, file_path: Path, fixes: List[Fix]) -> List[Fix]:
        """Apply fixes to a file.
        
        Args:
            file_path: Path to the file
            fixes: List of fixes to apply
            
        Returns:
            List of successfully applied fixes
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            applied_fixes = []
            
            # Sort fixes by line number (reverse order to avoid offset issues)
            sorted_fixes = sorted(fixes, key=lambda f: f.violation.line, reverse=True)
            
            for fix in sorted_fixes:
                # Apply the fix based on its type
                if hasattr(fix, 'line_to_replace'):
                    # Replace a specific line
                    lines = content.splitlines(keepends=True)
                    if 0 < fix.line_to_replace <= len(lines):
                        lines[fix.line_to_replace - 1] = fix.replacement_text + '\n'
                        content = ''.join(lines)
                        applied_fixes.append(fix)
                        
                elif hasattr(fix, 'insert_at_line'):
                    # Insert at a specific line
                    lines = content.splitlines(keepends=True)
                    insert_pos = max(0, min(fix.insert_at_line - 1, len(lines)))
                    lines.insert(insert_pos, fix.replacement_text)
                    content = ''.join(lines)
                    applied_fixes.append(fix)
                    
                else:
                    # Check if this is a comment flag that should be inserted above the line
                    if fix.is_comment_flag:
                        # Insert comment on the line above the violation
                        lines = content.splitlines(keepends=True)
                        line_idx = fix.violation.line - 1
                        
                        if 0 <= line_idx < len(lines):
                            # Insert the comment before the violation line
                            lines.insert(line_idx, fix.replacement_text + '\n')
                            content = ''.join(lines)
                            applied_fixes.append(fix)
                    else:
                        # Standard replacement at position
                        lines = content.splitlines(keepends=True)
                        line_idx = fix.violation.line - 1
                        
                        if 0 <= line_idx < len(lines):
                            line = lines[line_idx]
                            col = fix.violation.column - 1
                            
                            # Find the match in the line
                            match_start = line.find(fix.violation.original_text, col)
                            if match_start >= 0:
                                match_end = match_start + len(fix.violation.original_text)
                                new_line = (line[:match_start] + 
                                          fix.replacement_text + 
                                          line[match_end:])
                                lines[line_idx] = new_line
                                content = ''.join(lines)
                                applied_fixes.append(fix)
                            
            # Write the modified content if changes were made
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                
            return applied_fixes
            
        except Exception as e:
            console.print(f"[red]Error applying fixes to {file_path}:[/red] {e}")
            return []
            
    def _create_backup_directory(self) -> Path:
        """Create a backup directory for this session.
        
        Returns:
            Path to the backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path.home() / "aditi-data" / "backups" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
        
    def _backup_file(self, file_path: Path) -> bool:
        """Create a backup of a file before modifying it.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            True if backup was successful
        """
        if not self._backup_dir:
            return False
            
        try:
            # Calculate relative path from cwd
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # File is outside cwd, use absolute path structure
                rel_path = Path(*file_path.parts[1:])  # Skip root
                
            backup_path = self._backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, backup_path)
            return True
            
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to backup {file_path}:[/yellow] {e}")
            return False
            
    def display_summary(self, result: ProcessingResult):
        """Display a summary of the processing results.
        
        Args:
            result: The processing result to display
        """
        console.print("\n📊 Analysis Results\n")
        
        # Violations by rule
        rule_counts = result.get_violations_by_rule()
        if rule_counts:
            # Group by fix type
            rules = self.rule_registry.get_all_rules()
            rule_fix_types = {rule.name: rule.fix_type for rule in rules}
            
            # Display by fix type
            for fix_type in FixType:
                rules_of_type = [name for name, ft in rule_fix_types.items() 
                               if ft == fix_type and name in rule_counts]
                
                if rules_of_type:
                    if fix_type == FixType.FULLY_DETERMINISTIC:
                        console.print("🔴 [bold]Fully Deterministic Issues[/bold]")
                    elif fix_type == FixType.PARTIALLY_DETERMINISTIC:
                        console.print("🟡 [bold]Partially Deterministic Issues[/bold]")
                    else:
                        console.print("🔵 [bold]Non-Deterministic Issues[/bold]")
                        
                    for rule_name in rules_of_type:
                        count = rule_counts[rule_name]
                        console.print(f"  {rule_name} ({count} {'issue' if count == 1 else 'issues'})")
                    console.print()  # Blank line after each section
            
            # Show unimplemented rules
            implemented_rules = {rule.name for rule in rules}
            unimplemented_rules = [name for name in rule_counts.keys() 
                                 if name not in implemented_rules]
            
            if unimplemented_rules:
                console.print("❓ [bold]Unimplemented Rules[/bold]")
                for rule_name in sorted(unimplemented_rules):
                    count = rule_counts[rule_name]
                    console.print(f"  {rule_name} ({count} {'issue' if count == 1 else 'issues'})")
                console.print()  # Blank line after unimplemented rules section
                    
        # Summary statistics
        console.print("📈 [bold]Summary:[/bold]")
        console.print(f"  Files processed: {len(result.files_processed)}")
        console.print(f"  Total issues: {result.total_violations}")
        
        # Count auto-fixable issues properly
        auto_fixable = 0
        for violation in result.violations_found:
            rule = self.rule_registry.get_rule_for_violation(violation)
            if rule and rule.fix_type in [FixType.FULLY_DETERMINISTIC, FixType.PARTIALLY_DETERMINISTIC]:
                auto_fixable += 1
        
        if auto_fixable > 0:
            console.print(f"  Can be auto-fixed: {auto_fixable}")
            if result.total_fixes_applied > 0:
                console.print(f"  Fixes applied: {result.total_fixes_applied}")
                console.print(f"  Files modified: {len(result.files_modified)}")
                
        # Show percentage of auto-fixable issues
        if result.total_violations > 0 and auto_fixable > 0:
            auto_fix_percentage = (auto_fixable / result.total_violations) * 100
            console.print(f"\n✨ Good news! {auto_fix_percentage:.0f}% of issues can be fixed automatically.")
            
        console.print("\nNext step: Run 'aditi journey' for guided workflow")