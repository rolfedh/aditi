# Automate creating fixes for issues

## Overview

This document proposes a comprehensive solution for automating the creation of fixes for AsciiDocDITA violations detected by Vale. The system leverages AI assistance to analyze rules and generate implementation strategies for deterministic and partially-deterministic fixes.

## Current State Analysis

### Existing Architecture
- **Rule Framework**: Robust base classes (`Rule`, `Fix`, `FixType`) with clear abstractions
- **Rule Registry**: Dynamic discovery and dependency management
- **Processing Pipeline**: `RuleProcessor` handles Vale integration and fix application
- **Fix Types**: Clear categorization (fully deterministic, partially deterministic, non-deterministic)
- **Implemented Rules**: 27 rules covering various AsciiDocDITA compliance checks

### Key Strengths
1. Clean separation of concerns between detection (Vale) and fixing (Aditi)
2. Extensible rule system with dependency management
3. Thread-safe processing with proper error handling
4. Rich CLI interface with progress tracking

## Proposed Solution: AI-Assisted Rule Development Pipeline

### 1. Dossier Structure

I recommend a **hybrid approach** combining structured JSON metadata with organized file storage:

```
aditi-rule-dossiers/
├── manifest.json                    # Master index of all rules
├── rules/
│   ├── EntityReference/
│   │   ├── metadata.json           # Rule-specific metadata
│   │   ├── vale_rule.yaml          # Copy of Vale rule definition
│   │   ├── fixtures/
│   │   │   ├── report_entity_reference.adoc
│   │   │   └── ignore_entity_reference.adoc
│   │   ├── examples/
│   │   │   ├── before/             # Real-world examples before fix
│   │   │   └── after/              # Examples after fix
│   │   └── implementation.py       # Generated fix implementation
│   └── ContentType/
│       └── ... (similar structure)
└── templates/
    ├── rule_template.py            # Template for new rule implementations
    └── test_template.py            # Template for rule tests
```

#### manifest.json Structure
```json
{
  "version": "1.0",
  "last_updated": "2025-08-01",
  "rules": [
    {
      "name": "EntityReference",
      "fix_type": "fully_deterministic",
      "status": "implemented",
      "description": "Replaces unsupported HTML entities with DITA-compatible ones",
      "vale_rule_url": "https://github.com/jhradilek/asciidoctor-dita-vale/blob/main/styles/AsciiDocDITA/EntityReference.yml",
      "implementation_status": {
        "automated": true,
        "confidence": 0.95,
        "last_ai_review": "2025-07-30"
      }
    }
  ]
}
```

#### Rule metadata.json Structure
```json
{
  "name": "EntityReference",
  "fix_type": "fully_deterministic",
  "description": "Detects and replaces unsupported HTML entities",
  "vale_rule": {
    "extends": "existence",
    "message": "DITA supports only 5 character entity references",
    "tokens": ["&nbsp;", "&ndash;", "..."]
  },
  "fix_strategy": {
    "type": "simple_replacement",
    "mapping": {
      "&nbsp;": "{nbsp}",
      "&ndash;": "{ndash}"
    },
    "exceptions": ["code_blocks", "inline_code"]
  },
  "test_cases": {
    "positive": ["report_entity_reference.adoc"],
    "negative": ["ignore_entity_reference.adoc"]
  },
  "ai_analysis": {
    "model": "claude-opus-4",
    "timestamp": "2025-07-30T10:00:00Z",
    "confidence_score": 0.95,
    "implementation_notes": "Handle AsciiDoc substitution contexts"
  }
}
```

### 2. Automation Pipeline Architecture

```python
# aditi/automation/rule_generator.py
class RuleGenerator:
    """Generates rule implementations using AI assistance."""
    
    def __init__(self, ai_client, dossier_path: Path):
        self.ai_client = ai_client
        self.dossier_path = dossier_path
        
    async def analyze_rule(self, rule_name: str) -> RuleAnalysis:
        """Analyze a rule and generate implementation strategy."""
        dossier = self.load_dossier(rule_name)
        
        # Prepare AI prompt with all relevant context
        prompt = self.build_analysis_prompt(dossier)
        
        # Get AI analysis
        analysis = await self.ai_client.analyze(prompt)
        
        # Validate and refine analysis
        return self.validate_analysis(analysis, dossier)
    
    async def generate_implementation(self, analysis: RuleAnalysis) -> str:
        """Generate Python implementation from analysis."""
        template = self.load_template(analysis.fix_type)
        
        # Generate implementation code
        implementation = await self.ai_client.generate_code(
            template=template,
            analysis=analysis
        )
        
        # Validate implementation
        return self.validate_implementation(implementation)
```

### 3. AI Integration Strategy

#### Phase 1: Analysis and Strategy Generation
1. **Input Collection**: Gather Vale rule, fixtures, and examples
2. **Context Building**: Create comprehensive prompt with:
   - Rule definition and purpose
   - Positive/negative test cases
   - Existing similar rule implementations
   - AsciiDoc parsing considerations
3. **Strategy Generation**: AI proposes fix strategy with:
   - Algorithm description
   - Edge cases handling
   - Performance considerations
   - Confidence score

#### Phase 2: Implementation Generation
1. **Code Generation**: AI creates rule implementation based on:
   - Existing rule patterns (EntityReference, ContentType)
   - Base class requirements
   - Strategy from Phase 1
2. **Test Generation**: Create comprehensive test suite
3. **Documentation**: Generate rule documentation

#### Phase 3: Validation and Refinement
1. **Automated Testing**: Run against fixtures
2. **Performance Testing**: Ensure scalability
3. **Human Review**: Expert validation of edge cases
4. **Integration**: Add to rule registry

### 4. Implementation Roadmap

#### Stage 1: Infrastructure (Week 1-2)
- [ ] Create dossier directory structure
- [ ] Implement dossier loader/manager
- [ ] Set up AI client integration
- [ ] Create rule analysis prompts

#### Stage 2: Analysis Pipeline (Week 3-4)
- [ ] Implement `RuleGenerator` class
- [ ] Create analysis prompt templates
- [ ] Build validation framework
- [ ] Generate first 5 rule analyses

#### Stage 3: Code Generation (Week 5-6)
- [ ] Implement code generation pipeline
- [ ] Create rule implementation templates
- [ ] Generate test suite templates
- [ ] Validate generated implementations

#### Stage 4: Integration (Week 7-8)
- [ ] Integrate with existing rule registry
- [ ] Add CI/CD for automated rule testing
- [ ] Create rule contribution guidelines
- [ ] Document the automation process

### 5. Priority Rules for Automation

Based on the existing codebase analysis, prioritize these rules:

**Fully Deterministic** (High Priority):
1. ✅ EntityReference (already implemented)
2. LineBreak - Replace hard breaks with proper syntax
3. PageBreak - Convert to DITA-compatible breaks
4. ThematicBreak - Transform horizontal rules
5. AttributeReference - Fix attribute syntax

**Partially Deterministic** (Medium Priority):
1. ✅ ContentType (already implemented)
2. ShortDescription - Detect and format descriptions
3. TaskTitle - Standardize task titles
4. AuthorLine - Format author metadata
5. CrossReference - Fix internal references

**Non-Deterministic** (Low Priority for Automation):
- TaskSection - Requires semantic understanding
- NestedSection - Complex structure analysis
- ConditionalCode - Context-dependent decisions

### 6. Example AI Prompt Template

```markdown
# Rule Implementation Request: {rule_name}

## Context
You are implementing a fix for the AsciiDocDITA rule "{rule_name}" in the Aditi project.

## Vale Rule Definition
```yaml
{vale_rule_content}
```

## Test Fixtures
### Should Report (Positive Cases)
```asciidoc
{report_fixture_content}
```

### Should Ignore (Negative Cases)
```asciidoc
{ignore_fixture_content}
```

## Existing Similar Implementation
```python
{similar_rule_implementation}
```

## Requirements
1. Implement a Rule subclass following the existing pattern
2. Classify fix_type appropriately
3. Handle all edge cases from fixtures
4. Consider AsciiDoc parsing contexts (code blocks, attributes, etc.)
5. Provide clear fix descriptions

## Generate
Please provide:
1. Complete Python implementation
2. Algorithm explanation
3. Edge case handling strategy
4. Confidence score (0-1) for automation feasibility
```

### 7. Benefits of This Approach

1. **Scalability**: Rapidly develop new rule fixes
2. **Consistency**: AI learns from existing patterns
3. **Documentation**: Automatic generation of rule docs
4. **Quality**: Comprehensive test coverage
5. **Maintainability**: Structured dossier system
6. **Transparency**: Human-reviewable AI decisions

### 8. Risk Mitigation

1. **AI Hallucination**: Validate all generated code against fixtures
2. **Edge Cases**: Maintain comprehensive test suites
3. **Performance**: Profile generated implementations
4. **Maintainability**: Ensure generated code follows project standards
5. **Version Control**: Track AI model versions and prompts

## Conclusion

This hybrid approach combines the best of structured data (JSON) with organized file storage, enabling efficient AI-assisted rule development while maintaining human oversight and quality control. The system can scale to handle all AsciiDocDITA rules while ensuring reliability and maintainability.
