---
layout: page
title: "Aditi Design Plan"
permalink: /design/aditi-plan/
---

# Aditi Design Plan

## Executive Summary

Aditi ("asciidoc dita integration") is a complete reboot of asciidoc-dita-toolkit, designed from the ground up to help technical writers prepare AsciiDoc files for migration to DITA. This MVP focuses exclusively on the primary user story: providing an interactive CLI experience that automates the detection and fixing of AsciiDocDITA rule violations.

> **Note**: Aditi is a Sanskrit name meaning "boundless" or "unlimited." In Hindu mythology, Aditi is a major goddess, often called the mother of the gods: Adityas. She represents infinity, the cosmos, and the boundless potential of the universe.

## Project Scope & Goals

### Primary Goal
Create an interactive CLI tool that guides technical writers through preparing their AsciiDoc content for DITA migration by:
- Running Vale linter with AsciiDocDITA rules
- Automatically fixing deterministic violations
- Flagging non-deterministic violations for manual review
- Managing the git workflow for changes

### Design Principles
- **White-slate design**: Build from scratch using modern software architecture best practices
- **User-centric**: Provide a Claude Code-like interactive experience
- **Automated workflow**: Minimize manual steps in the migration process
- **Selective reuse**: Only borrow specific, well-tested components from asciidoc-dita-toolkit

### Out of Scope (MVP)
- Use cases beyond AsciiDoc-to-DITA migration
- Windows support
- GUI interface
- Direct DITA conversion

## System Architecture

### Component Overview
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CLI Interface │────▶│   Rule Engine    │────▶│   Git Manager   │
│  (Interactive)  │     │ (Vale Container) │     │  (Automation)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Config Manager  │     │   Fix Processor  │     │ Report Generator│
│  (JSON Store)   │     │  (Deterministic) │     │   (Markdown)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Core Components

1. **CLI Interface**: Interactive command-line interface providing guided workflows
2. **Rule Engine**: Docker-based Vale linter with AsciiDocDITA ruleset
3. **Fix Processor**: Applies deterministic fixes based on rule violations
4. **Git Manager**: Automates branch creation, commits, and pull requests
5. **Config Manager**: Persists user configuration and session state
6. **Report Generator**: Creates detailed violation reports

## Technical Requirements

### System Dependencies

#### Required Software
- **Python**: 3.7 or later (primary implementation language)
- **Docker**: For running Vale linter container
- **Git**: Version control operations
- **GitLab CLI** (`glab`): For GitLab integration
- **GitHub CLI** (`gh`): Optional, for GitHub support

#### Docker Images
- **Production**: `ghcr.io/rolfedh/asciidoc-dita-toolkit-prod`
- **Vale Advanced**: `ghcr.io/rolfedh/asciidoc-dita-toolkit-vale-adv`

> **Note**: Currently using manually-triggered workflow from `/home/rolfedh/asciidoc-dita-toolkit/.github/workflows/container-build.yml`. Will transition to upstream images when available (see issue #97).

### Platform Support
- **Supported**: macOS, Linux
- **Not Supported**: Windows

## Rule Classification System

### Fix Categories

#### 1. Fully Deterministic Fixes
Violations that can be fixed automatically with 100% confidence.

**Examples**:
- **EntityReference**: Replace unsupported character entities
- **TrailingWhitespace**: Remove trailing spaces
- **ConsecutiveBlankLines**: Normalize line spacing

**Workflow**:
1. Run rule → Apply fixes → Verify zero violations
2. Commit with descriptive message
3. After all deterministic fixes, create single PR

#### 2. Partially Deterministic Fixes
Violations that can be partially fixed, often requiring placeholders.

**Examples**:
- **ContentType**: Insert/fix `:_mod-docs-content-type:` attribute
  - Detect from deprecated attributes
  - Infer from filename prefixes
  - Insert `TBD` placeholder when uncertain

**Workflow**:
1. Run rule → Apply fixes/placeholders → Flag remaining issues
2. Create PR with partial fixes
3. User manually resolves placeholders
4. Merge when all violations resolved

#### 3. Non-Deterministic Fixes
Violations requiring human judgment to fix.

**Examples**:
- **ExampleBlock**: Section structure violations
- **TaskSection**: Content organization issues
- **ImageAltText**: Context-dependent descriptions

**Workflow**:
1. Run rule → Flag all violations with comments
2. Create PR with flagged issues
3. User manually fixes all violations
4. Merge when complete

## Implementation Details

### Violation Flagging Strategy

When flagging violations, Aditi:
1. Indexes files from bottom to top (prevents line drift)
2. Inserts descriptive comments above violations
3. Includes rule name, instructions, and documentation links

**Comment Format**:
```asciidoc
// Rule: ExampleBlock - DITA 1.3 allows the <section> element to appear only within the main body of the topic. 
// For instructions, see https://docs.asciidoctor.org/asciidoc/latest/sections/titles-and-levels/
```

### Rule Processing Stages

Rules are organized into stages based on dependencies:

1. **Stage 1: Prerequisites**
   - ContentType (required by many other rules)
   - DocumentStructure

2. **Stage 2: Deterministic Fixes**
   - EntityReference
   - TrailingWhitespace
   - ConsecutiveBlankLines

3. **Stage 3: Content-Type Dependent**
   - TaskSection (PROCEDURE only)
   - TaskExample (PROCEDURE only)
   - TaskStep (PROCEDURE only)

4. **Stage 4: Manual Review**
   - ExampleBlock
   - ImageAltText
   - CrossReferences

### Git Workflow Automation

Aditi automates the following git operations:

1. **Branch Management**
   - Check out main/default branch
   - Create feature branches with descriptive names
   - Handle multiple release branches

2. **Commit Strategy**
   - One commit per rule or rule group
   - Descriptive commit messages mentioning rule names
   - Atomic commits for easy review

3. **Pull Request Creation**
   - Automated PR creation with summaries
   - Links to violation reports
   - Clear merge instructions

## User Experience Design

### Interactive CLI Flow

The CLI provides a guided, conversational experience:

```
$ aditi journey

Welcome to Aditi! Let's set up your documentation migration journey.

Step 1: Navigate to your repository root...
Step 2: Configure branches...
Step 3: Set directory permissions...
[etc.]
```

### Configuration Management

User configuration stored in `~/aditi-data/config.json`:

```json
{
  "repo_root": "/path/to/docs",
  "default_branch": "main",
  "release_branches": ["release-1.0", "release-2.0"],
  "subdirectory_permissions": {
    "allow": ["docs/modules", "docs/assemblies"],
    "block": ["docs/archive", "docs/drafts"]
  },
  "feature_branch": "aditi-contenttype-fix",
  "timestamp": "2025-07-27T10:00:00Z"
}
```

### Command Structure

Primary commands:
- `aditi journey` - Start guided migration workflow
- `aditi check <rule>` - Run specific rule check
- `aditi fix <rule>` - Apply fixes for specific rule
- `aditi report` - Generate violation report
- `aditi config` - Manage configuration

## Development Roadmap

### Phase 1: Foundation (MVP)
- [ ] Core CLI framework
- [ ] Docker integration for Vale
- [ ] Configuration management
- [ ] Basic git automation

### Phase 2: Rule Implementation
- [ ] ContentType rule with partial fixes
- [ ] EntityReference rule with full fixes
- [ ] Violation flagging system
- [ ] Report generation

### Phase 3: Workflow Automation
- [ ] Full git workflow automation
- [ ] PR creation with GitLab/GitHub APIs
- [ ] Batch processing for rule stages
- [ ] Progress tracking and resumption

### Phase 4: Enhancement
- [ ] Additional rule support
- [ ] Performance optimization
- [ ] Extended reporting features
- [ ] Plugin architecture for custom rules

## Distribution & Deployment

### PyPI Publishing
- Use existing `make publish` workflow from asciidoc-dita-toolkit
- Maintain semantic versioning
- Automated release process

### Installation
```bash
pip install aditi
```

### Docker Image Management
- Reuse container build workflow
- Transition to upstream images when available
- Version pinning for stability

## Testing Strategy

### Unit Tests
- Rule detection accuracy
- Fix application correctness
- Configuration management
- Git operation safety

### Integration Tests
- Docker container interaction
- Full workflow execution
- Multi-rule processing
- PR creation flow

### Fixture Management
- Reuse fixture fetching from asciidoc-dita-vale
- Weekly updates via GitHub Actions
- Automated PR creation for changes

## Security Considerations

- No credentials stored in configuration
- Git operations use system SSH/HTTPS config
- Docker container runs with minimal privileges
- Temporary files cleaned up automatically

## Future Considerations

### Potential Enhancements
- Rule priority customization
- Parallel processing for large repositories
- Integration with CI/CD pipelines
- Custom rule development framework
- Web-based progress dashboard

### Migration Path
- Gradual transition from asciidoc-dita-toolkit
- Compatibility layer for existing users
- Documentation migration guides
- Training materials

## Appendix: Rule Details

### ContentType Rule

**Purpose**: Ensure proper content type identification for DITA compatibility

**Detection**:
- Missing `:_mod-docs-content-type:` attribute
- Invalid or empty attribute values
- Deprecated attribute formats

**Fixes**:
1. Check for deprecated attributes (`:_content-type:`, `:_module-type:`)
2. Analyze filename prefixes:
   - `assembly_`, `assy_` → ASSEMBLY
   - `con_`, `conc_` → CONCEPT  
   - `proc_`, `task_` → PROCEDURE
   - `ref_` → REFERENCE
   - `snip_` → SNIPPET
3. Insert `TBD` placeholder if undetermined

**Implementation Reference**:
See provided Python code examples for attribute detection and prefix mapping.

### EntityReference Rule

**Purpose**: Replace non-DITA-compliant character entities

**Supported Entities**: `&amp;`, `&lt;`, `&gt;`, `&apos;`, `&quot;`

**Fix Strategy**: Direct replacement with AsciiDoc attributes

---

*This document is a living design plan and will be updated as the project evolves.*