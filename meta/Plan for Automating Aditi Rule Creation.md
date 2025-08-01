# Plan for Automating Aditi Rule Creation from AsciiDocDITA Vale Rules

  Overview

  This document outlines a comprehensive strategy for automating the
  creation of Aditi rule "plugins" based on the upstream AsciiDocDITA Vale
  rules, including systematic monitoring for changes and automated updates.

  Architecture Overview

  Current State

  - Aditi relies on Vale + AsciiDocDITA style to detect issues
  - Aditi flags issues and applies fixes only when deterministic or
  partially-deterministic
  - Manual rule implementation and maintenance

  Target State

  - Automated rule generation from upstream Vale rules and fixtures
  - Test-driven development using fixture files as test cases
  - Continuous monitoring and updates from upstream changes
  - Self-contained rule "plugins" with metadata tracking

  Test-Driven Rule Generation Architecture

  AsciiDocDITA Repository
  ├── styles/AsciiDocDITA/
  │   └── *.yml (Vale rule definitions)
  └── fixtures/
      ├── RuleName/
      │   ├── ignore_*.adoc (patterns that should NOT trigger)
      │   └── report_*.adoc (patterns that SHOULD trigger)

      ↓ Automated Conversion Pipeline ↓

  Aditi Rules
  ├── src/aditi/rules/
  │   └── rule_name.py (generated implementation)
  └── tests/fixtures/
      └── rule_name/
          ├── valid_cases.adoc (from ignore_*)
          └── violation_cases.adoc (from report_*)

  Rule Generation Pipeline

  Phase 1: Analysis

  - Parse Vale YAML rule definition for:
    - Rule type (existence, substitution, occurrence, script)
    - Patterns and tokens
    - Severity level and scope
    - Custom logic (for script-based rules)
  - Parse fixture files to understand:
    - What patterns trigger violations (report_*.adoc)
    - What patterns should be ignored (ignore_*.adoc)
    - Edge cases and context sensitivity
    - Real-world usage examples

  Phase 2: Classification

  Analyze patterns to determine fix type:

  - Fully Deterministic: Clear 1:1 mappings
    - Example: &copy; → {copy}
    - Simple substitution rules
    - Pattern-based replacements with known outputs
  - Partially Deterministic: Can add placeholders
    - Example: Missing :_mod-docs-content-type: attribute
    - Structural additions with user selection needed
    - Template insertions
  - Non-Deterministic: Only flag, no fix possible
    - Semantic rules requiring human judgment
    - Cross-reference validation
    - Complex structural changes

  Phase 3: Implementation Generation

  Generate Python rule class with:
  - Pattern matching logic derived from fixtures
  - Fix logic based on classification
  - Context awareness (code blocks, comments, etc.)
  - Comprehensive test cases from fixture files
  - Metadata tracking for upstream sync

  Systematic Update Checking Strategies

  Option A: GitHub Actions Workflow (Recommended)

  name: Check Vale Rules Updates
  on:
    schedule:
      - cron: '0 0 * * 0'  # Weekly check
    workflow_dispatch:  # Manual trigger

  jobs:
    check-updates:
      steps:
        1. Checkout both repositories
        2. Compare rule files (hash/diff)
        3. Compare fixture files
        4. Generate change report
        5. Run automated rule generation
        6. Create PR if changes detected
        7. Run full test suite

  Benefits:
  - Automated monitoring
  - Integrated with existing CI/CD
  - Clear audit trail through PRs
  - No manual intervention needed

  Option B: Git Submodule Approach

  # Add AsciiDocDITA as submodule
  git submodule add https://github.com/jhradilek/asciidoctor-dita-vale.git
  upstream-vale

  # Update script checks for changes
  ./scripts/check-upstream-changes.py

  Benefits:
  - Direct tracking of upstream changes
  - Version pinning capabilities
  - Local development flexibility

  Option C: Dependency Management Integration

  # pyproject.toml
  [tool.aditi.upstream]
  vale-rules-repo = "jhradilek/asciidoctor-dita-vale"
  vale-rules-version = "v1.2.3"  # Pin to release
  auto-check-updates = true
  update-frequency = "weekly"

  Benefits:
  - Integrated with Python packaging
  - Version management built-in
  - Configuration-driven updates

  Change Detection and Update Process

  Update Detection Algorithm

  class ValeRulesSyncChecker:
      def check_for_updates(self):
          changes = {
              "new_rules": [],           # Rules added upstream
              "modified_rules": [],      # Rules changed upstream
              "deleted_rules": [],       # Rules removed upstream
              "fixture_changes": [],     # Test cases modified
              "breaking_changes": []     # Changes requiring manual review
          }

          # 1. Compare rule YAML files by hash
          # 2. Compare fixture directories
          # 3. Analyze semantic changes
          # 4. Generate compatibility report
          # 5. Determine update strategy

          return UpdateReport(changes)

  Update Prioritization

  1. High Priority: New rules, critical fixes
  2. Medium Priority: Modified fixtures, enhanced patterns
  3. Low Priority: Documentation updates, minor tweaks

  Rule Plugin Architecture

  Self-Contained Rule Structure

  # src/aditi/rules/entity_reference.py
  class EntityReferenceRule(Rule):
      """Auto-generated rule implementation."""

      # Upstream tracking metadata
      upstream_version = "2024-01-15"
      upstream_rule_hash = "abc123..."
      upstream_fixtures_hash = "def456..."

      # Generated from fixtures analysis
      IGNORE_PATTERNS = [...]  # From ignore_*.adoc
      REPORT_PATTERNS = [...]  # From report_*.adoc

      # Generated test cases
      @classmethod
      def get_test_cases(cls):
          return {
              "should_ignore": [...],  # From ignore fixtures
              "should_report": [...],  # From report fixtures
          }

  Plugin Metadata Tracking

  @dataclass
  class RuleMetadata:
      """Metadata for tracking upstream sync status."""
      rule_name: str
      vale_style_version: str
      last_sync_date: str
      fixture_count: int
      fix_type: str
      compatibility_notes: List[str]
      breaking_changes: List[str]

  Continuous Integration Strategy

  Development Workflow

  1. Upstream Monitor (GitHub Actions)
    - Runs weekly or on-demand
    - Monitors AsciiDocDITA repository for changes
    - Triggers update pipeline when changes detected
  2. Change Detector
    - Compares rule definitions and fixtures
    - Classifies changes by impact level
    - Generates detailed change report
  3. Rule Generator
    - Creates/updates rule implementations
    - Maintains backward compatibility
    - Preserves manual customizations
  4. Test Generator
    - Creates comprehensive test suites from fixtures
    - Validates rule behavior against examples
    - Ensures no regressions
  5. Validation Suite
    - Runs full test suite
    - Validates against known AsciiDoc documents
    - Performance benchmarking
  6. PR Generator
    - Creates pull request with changes
    - Includes detailed change summary
    - Links to upstream commits

  Quality Assurance Process

  - Automated Testing: All fixture cases become unit tests
  - Regression Prevention: Existing behavior preserved
  - Performance Monitoring: Track rule execution time
  - Documentation Updates: Auto-generate rule documentation

  Implementation Priorities

  High Priority Rules (Fully Automatable)

  - ✅ EntityReference (already implemented)
  - AttributeReference (simple substitutions)
  - ContentType (already implemented)
  - Rules with clear substitution patterns
  - Rules with deterministic fixes

  Medium Priority (Partially Automatable)

  - Missing attribute rules
  - Structure addition rules
  - Template insertion rules
  - Rules that can add meaningful placeholders

  Low Priority (Flag Only)

  - TaskSection (semantic rules)
  - CrossReference (validation rules)
  - Complex structural rules
  - Rules requiring human judgment

  Benefits of This Approach

  For Development

  - Reduced Manual Work: Automated rule creation and updates
  - Higher Quality: Test-driven development from real examples
  - Consistency: Standardized implementation patterns
  - Maintainability: Clear tracking of upstream changes

  For Users

  - Always Current: Rules stay in sync with Vale standards
  - Better Coverage: All Vale rules have corresponding Aditi implementations
  - Improved Reliability: Extensive testing from fixture examples
  - Transparency: Clear understanding of rule behavior

  For Project

  - Scalability: Easy to add support for new rules
  - Sustainability: Automated maintenance reduces burden
  - Compatibility: Maintains alignment with Vale ecosystem
  - Innovation: Enables focus on advanced features vs. rule maintenance

  Risk Mitigation

  Potential Risks

  - Breaking Changes: Upstream changes could break existing functionality
  - Over-Automation: Complex rules may need manual review
  - Performance Impact: Large number of rules could slow processing
  - Maintenance Overhead: Automation system itself needs maintenance

  Mitigation Strategies

  - Gradual Rollout: Test changes in isolation before deployment
  - Manual Review Gates: Require approval for breaking changes
  - Performance Monitoring: Track and optimize rule execution
  - Fallback Mechanisms: Ability to disable problematic rules
  - Version Pinning: Control when to adopt upstream changes

  Future Enhancements

  Machine Learning Integration

  - Learn from user corrections to improve fix suggestions
  - Analyze patterns in manual reviews to enhance automation
  - Predict which rules are most likely to need updates

  Advanced Context Awareness

  - Cross-rule dependencies and interactions
  - Document-wide consistency checking
  - Project-specific customizations

  Community Contributions

  - Allow users to contribute rule improvements
  - Share successful automation patterns
  - Collaborative fixture development

  This comprehensive plan provides a roadmap for creating a robust,
  maintainable system that automatically generates and maintains Aditi rules
   based on the upstream AsciiDocDITA Vale rules, ensuring ongoing
  compatibility and reducing manual maintenance overhead.