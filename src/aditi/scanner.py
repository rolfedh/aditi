"""Directory scanner for finding AsciiDoc files."""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

from rich.console import Console

console = Console()


class DirectoryScanner:
    """Scans directories for AsciiDoc files."""
    
    def __init__(self, ignore_symlinks: bool = True):
        """Initialize the scanner.
        
        Args:
            ignore_symlinks: Whether to ignore symbolic links
        """
        self.ignore_symlinks = ignore_symlinks
        self._gitignore_patterns: Set[str] = set()
        
    def scan_for_adoc_files(self, root_path: Path) -> Dict[Path, int]:
        """Recursively scan for directories containing .adoc files.
        
        Args:
            root_path: Root path to start scanning from
            
        Returns:
            Dictionary mapping directory paths to count of .adoc files
        """
        adoc_dirs: Dict[Path, int] = {}
        
        # Load .gitignore patterns if available
        gitignore_path = root_path / ".gitignore"
        if gitignore_path.exists():
            self._load_gitignore(gitignore_path)
        
        # Walk the directory tree
        for dirpath, dirnames, filenames in os.walk(root_path, followlinks=not self.ignore_symlinks):
            current_dir = Path(dirpath)
            
            # Skip hidden directories and common build/vendor directories
            dirnames[:] = [
                d for d in dirnames 
                if not d.startswith('.') 
                and d not in {'node_modules', 'vendor', 'build', 'dist', 'target', '__pycache__'}
            ]
            
            # Skip if path matches gitignore patterns
            if self._should_ignore(current_dir, root_path):
                dirnames.clear()  # Don't recurse into ignored directories
                continue
            
            # Count .adoc files in current directory
            adoc_count = sum(1 for f in filenames if f.endswith('.adoc') and not f.startswith('.'))
            
            if adoc_count > 0:
                # Store relative path for display
                rel_path = current_dir.relative_to(root_path)
                adoc_dirs[rel_path] = adoc_count
                
        return adoc_dirs
    
    def find_documentation_roots(self, adoc_dirs: Dict[Path, int]) -> List[Tuple[Path, int, int]]:
        """Find common documentation root directories.
        
        This groups nested directories under their common roots to simplify selection.
        
        Args:
            adoc_dirs: Dictionary of directories with .adoc file counts
            
        Returns:
            List of tuples (root_path, direct_count, total_count)
        """
        # Sort paths by depth (fewer parts = higher level)
        sorted_paths = sorted(adoc_dirs.keys(), key=lambda p: len(p.parts))
        
        doc_roots: List[Tuple[Path, int, int]] = []
        processed_paths: Set[Path] = set()
        
        for path in sorted_paths:
            if path in processed_paths:
                continue
                
            # Count files in this directory and all subdirectories
            direct_count = adoc_dirs[path]
            total_count = direct_count
            
            # Find all subdirectories
            for sub_path, count in adoc_dirs.items():
                if sub_path != path and self._is_subdirectory(sub_path, path):
                    total_count += count
                    processed_paths.add(sub_path)
            
            doc_roots.append((path, direct_count, total_count))
            
        return doc_roots
    
    def _is_subdirectory(self, potential_sub: Path, parent: Path) -> bool:
        """Check if potential_sub is a subdirectory of parent.
        
        Args:
            potential_sub: Path that might be a subdirectory
            parent: Parent path to check against
            
        Returns:
            True if potential_sub is under parent
        """
        try:
            potential_sub.relative_to(parent)
            return True
        except ValueError:
            return False
    
    def _load_gitignore(self, gitignore_path: Path) -> None:
        """Load patterns from .gitignore file.
        
        Args:
            gitignore_path: Path to .gitignore file
        """
        self._gitignore_patterns.clear()
        
        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        self._gitignore_patterns.add(line.rstrip('/'))
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read .gitignore:[/yellow] {e}")
    
    def _should_ignore(self, path: Path, root: Path) -> bool:
        """Check if a path should be ignored based on gitignore patterns.
        
        Args:
            path: Path to check
            root: Repository root path
            
        Returns:
            True if path should be ignored
        """
        try:
            rel_path = path.relative_to(root)
            path_str = str(rel_path).replace(os.sep, '/')
            
            # Check exact matches and prefixes
            for pattern in self._gitignore_patterns:
                if path_str == pattern or path_str.startswith(pattern + '/'):
                    return True
                    
            # Check if any parent directory is ignored
            for parent in rel_path.parents:
                parent_str = str(parent).replace(os.sep, '/')
                if parent_str in self._gitignore_patterns:
                    return True
                    
        except ValueError:
            # Path is not relative to root
            pass
            
        return False