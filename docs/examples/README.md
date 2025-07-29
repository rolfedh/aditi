# AsciiDoc Example Files

This directory contains example AsciiDoc files that demonstrate each AsciiDocDITA rule. Use these to understand what triggers each rule and how fixes are applied.

## File Organization

- **`rule-examples/`** - Individual files showing each rule
- **`comprehensive-example.adoc`** - Single file triggering multiple rules
- **`clean-example.adoc`** - DITA-compliant example showing best practices

## Testing Examples

You can test these examples with Aditi:

```bash
cd docs/examples/
aditi init
aditi check rule-examples/
aditi fix --dry-run rule-examples/
```

## Rule Coverage

All 27 AsciiDocDITA rules are demonstrated:

### Fully Deterministic (Auto-fixable)
- EntityReference

### Partially Deterministic (Partial auto-fix)  
- ContentType

### Non-Deterministic (Manual review required)
- AdmonitionTitle, AuthorLine, BlockTitle, ConditionalCode
- CrossReference, DiscreteHeading, EquationFormula, ExampleBlock
- IncludeDirective, LineBreak, LinkAttribute, NestedSection
- PageBreak, RelatedLinks, ShortDescription, SidebarBlock
- TableFooter, TagDirective, TaskDuplicate, TaskExample
- TaskSection, TaskStep, TaskTitle, ThematicBreak