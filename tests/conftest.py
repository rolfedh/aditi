"""Pytest configuration and shared fixtures."""

import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.
    
    Yields:
        Path to temporary directory
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_git_repo(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary git repository for testing.
    
    Args:
        temp_dir: Temporary directory fixture
        
    Yields:
        Path to temporary git repository
    """
    import subprocess
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )
    
    # Create initial commit
    (temp_dir / "README.md").write_text("# Test Repository")
    subprocess.run(["git", "add", "README.md"], cwd=temp_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )
    
    yield temp_dir


@pytest.fixture
def sample_adoc_content() -> str:
    """Sample AsciiDoc content for testing.
    
    Returns:
        Sample AsciiDoc content with various issues
    """
    return """= Sample Document
:_mod-docs-content-type: CONCEPT

== Overview

This document contains &nbsp; and &mdash; entities.

[source,bash]
----
echo "Hello, World!"
----

.Example procedure
. First step
. Second step with &trade; symbol
. Third step

== Reference Section

Some text with &copy; copyright symbol.
"""


@pytest.fixture
def mock_vale_output() -> dict:
    """Mock Vale output for testing.
    
    Returns:
        Sample Vale JSON output
    """
    return {
        "test.adoc": [
            {
                "Action": "replace",
                "Check": "AsciiDocDITA.EntityReference",
                "Description": "",
                "Line": 5,
                "Link": "",
                "Message": "Replace '&nbsp;' with '{nbsp}'",
                "Severity": "error",
                "Span": [25, 30],
                "Match": "&nbsp;"
            },
            {
                "Action": "replace",
                "Check": "AsciiDocDITA.EntityReference",
                "Description": "",
                "Line": 5,
                "Link": "",
                "Message": "Replace '&mdash;' with '{mdash}'",
                "Severity": "error",
                "Span": [36, 42],
                "Match": "&mdash;"
            }
        ]
    }