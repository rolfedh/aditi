---
layout: page
title: "Phase 2: Rule Engine Implementation for Aditi"
permalink: /design/phase-2-next-steps/
---

# Phase 2: Rule Engine Implementation for Aditi

## ✅ Phase 1 Completion Summary

Phase 1 has been successfully completed! Here's what we accomplished:

### Infrastructure Built
1. **Modern Python Package** (`pyproject.toml`) with proper dependencies and tool configuration
2. **Complete CLI Framework** (`src/aditi/cli.py`) with Typer, Rich output, and all command placeholders
3. **Configuration Management** (`src/aditi/config.py`) with Pydantic models and JSON persistence
4. **Workflow Guidance Module** (`src/aditi/workflow.py`) for high-level process guidance
5. **Comprehensive Testing** (94% test success rate) with unit and integration tests
6. **Package Structure** with proper exports and metadata

### Validation Results
- ✅ `pip install -e .` - Package installs successfully
- ✅ `aditi --help` - Shows comprehensive command documentation
- ✅ `aditi --version` - Displays version 0.1.0
- ✅ `aditi init` - Initializes Vale configuration successfully
- ✅ Placeholder commands - All show helpful "not yet implemented" messages

## 🚀 Phase 2: Rule Engine Implementation

Phase 2 focuses on building the core rule processing engine that parses Vale output and applies fixes to AsciiDoc files.

### Step 1: Vale Output Parser
Start your next session with:
```
Create src/aditi/vale_parser.py that:
- Parses Vale JSON output from ValeContainer
- Creates structured Violation objects
- Handles different violation severities and types
- Groups violations by file and rule
- Includes comprehensive error handling
```

### Step 2: Rule Framework
```
Create src/aditi/rules/ package with:
- Abstract base Rule class with detect/fix methods
- FixType enum (FULLY_DETERMINISTIC, PARTIALLY_DETERMINISTIC, NON_DETERMINISTIC)
- Violation and Fix data classes
- Rule registry for discovery and execution
```

### Step 3: EntityReference Rule Implementation
```
Implement src/aditi/rules/entity_reference.py that:
- Detects unsupported HTML entities in AsciiDoc
- Maps entities to DITA-compatible replacements (&nbsp; → {nbsp})
- Applies fully deterministic fixes
- Validates fixes maintain document structure
```

### Step 4: ContentType Rule Implementation
```
Implement src/aditi/rules/content_type.py that:
- Detects missing/invalid :_mod-docs-content-type: attributes
- Analyzes filename prefixes for content type hints
- Inserts appropriate content types or TBD placeholders
- Handles partially deterministic scenarios
```

### Step 5: File Processing Engine
```
Create src/aditi/processor.py that:
- Orchestrates rule execution in dependency order
- Manages file reading and writing operations
- Tracks changes and generates reports
- Handles rollback scenarios
- Provides progress feedback with Rich
```

### Step 6: Check Command Implementation
```
Implement the check command that:
- Runs Vale against specified files or directories
- Parses output and applies rule detection
- Displays violations categorized by fix type
- Shows detailed reports with file locations
- Respects configuration permissions
```

## 📋 Recommended Implementation Order

1. **Start with Vale Parser** - Essential for all subsequent features
2. **Build Rule Framework** - Provides structure for all rule implementations
3. **Implement EntityReference Rule** - Simplest fully deterministic rule
4. **Add ContentType Rule** - More complex partially deterministic rule
5. **Create Processing Engine** - Orchestrates the workflow
6. **Wire up Check Command** - Provides user-facing functionality

## 💡 Implementation Guidelines

### Data Structures

```python
@dataclass
class Violation:
    file_path: Path
    rule_name: str
    line: int
    column: int
    message: str
    severity: str
    original_text: str
    suggested_fix: Optional[str] = None

@dataclass
class Fix:
    violation: Violation
    replacement_text: str
    confidence: float
    requires_review: bool = False

class FixType(Enum):
    FULLY_DETERMINISTIC = "fully_deterministic"
    PARTIALLY_DETERMINISTIC = "partially_deterministic" 
    NON_DETERMINISTIC = "non_deterministic"
```

### Rule Interface

```python
class Rule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Rule identifier matching Vale rule name."""
        
    @property
    @abstractmethod
    def fix_type(self) -> FixType:
        """Classification of fix determinism."""
        
    @abstractmethod
    def can_fix(self, violation: Violation) -> bool:
        """Check if this rule can fix the violation."""
        
    @abstractmethod
    def generate_fix(self, violation: Violation, file_content: str) -> Optional[Fix]:
        """Generate a fix for the violation."""
```

### Processing Pipeline

```python
class RuleProcessor:
    def __init__(self, vale_container: ValeContainer, config: AditiConfig):
        self.vale_container = vale_container
        self.config = config
        self.rules = self._load_rules()
    
    def process_files(self, file_paths: List[Path]) -> ProcessingResult:
        """Process files through the rule pipeline."""
        # 1. Run Vale against files
        # 2. Parse violations
        # 3. Apply rules in dependency order
        # 4. Generate fixes
        # 5. Return results
```

## 🎯 Success Criteria for Phase 2

By the end of Phase 2, you should be able to:
- Run `aditi check path/to/files` and see detailed violation reports
- Process EntityReference violations with automatic fixes
- Handle ContentType violations with smart detection and placeholders
- See progress indicators and rich console output during processing
- Have comprehensive test coverage for all rule processing logic

## 📚 Key Design Decisions

### Rule Dependencies
ContentType must run before other content-type-dependent rules:
```python
RULE_DEPENDENCIES = {
    "ContentType": [],  # No dependencies
    "TaskSection": ["ContentType"],  # Depends on content type
    "TaskExample": ["ContentType"],
}
```

### File Safety
- Always create backups before applying fixes
- Validate fixes don't break AsciiDoc syntax
- Provide rollback capabilities
- Use atomic operations where possible

### Error Recovery
- Graceful handling of Vale container failures
- Recovery from malformed Vale output
- File permission and access error handling
- User-friendly error messages with suggested actions

## 🔄 Integration with Phase 1

Phase 2 builds directly on Phase 1 infrastructure:

- **Vale Container**: Use existing `ValeContainer` class for Vale execution
- **Configuration**: Leverage `ConfigManager` for user settings and session state
- **CLI Framework**: Implement check command using established Typer patterns
- **Workflow Guidance**: Provide high-level guidance after applying fixes
- **Testing**: Extend existing test framework with rule-specific tests

## 📝 Example Usage After Phase 2

```bash
# Check files for violations
aditi check docs/

# Check specific files
aditi check docs/concept.adoc docs/procedure.adoc

# Check with specific rules
aditi check --rule EntityReference docs/

# Show violation details
aditi check --verbose docs/
```

Expected output:
```
📊 Analysis Results for docs/

🔴 EntityReference (2 violations)
  docs/concept.adoc:15  Replace '&nbsp;' with '{nbsp}'
  docs/concept.adoc:23  Replace '&mdash;' with '{mdash}'

🟡 ContentType (1 violation)  
  docs/procedure.adoc:1  Missing content type attribute (detected: PROCEDURE)

📈 Summary:
  Files processed: 2
  Fully deterministic fixes: 2
  Partially deterministic fixes: 1
  Manual review required: 0

Next steps:
  Run 'aditi fix' to apply deterministic fixes
  Use 'aditi journey' for guided workflow
```

## 🚦 Phase 2 Exit Criteria

Phase 2 is complete when:
1. Vale output parsing is robust and handles all edge cases
2. Rule framework supports different fix types and dependencies
3. EntityReference and ContentType rules are fully implemented
4. Check command provides comprehensive violation reporting
5. File processing is safe with backup and rollback capabilities
6. Test coverage is comprehensive for all rule processing logic
7. Integration with existing CLI and configuration is seamless

Ready to transform Aditi from a CLI framework into a functional AsciiDoc-to-DITA migration tool!