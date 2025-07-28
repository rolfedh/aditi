---
layout: page
title: "Workflow Feedback and Suggestions"
permalink: /design/workflow-feedback/
---

# Workflow Feedback and Suggestions

## Questions About the Current Workflow

### 1. Workflow Granularity
The current 3-phase workflow provides a solid high-level structure. However, would it be helpful to add more specific examples or sub-steps for common scenarios? For instance:

- **Phase 1**: What specific types of clarifying questions work best?
- **Phase 2**: What makes an MVP breakdown effective vs. overwhelming?
- **Phase 3**: How to know when to stop iterating?

### 2. Pre-Flight Checklist
Should we add a "Phase 0" that covers preparation before engaging with Claude? This could include:
- Gathering relevant context (existing code, requirements docs)
- Identifying success criteria upfront
- Preparing example inputs/outputs

### 3. Common Pitfalls Section
Would it be valuable to add a section on what NOT to do? For example:
- Asking for complete implementations without iteration
- Skipping the validation phase
- Not providing enough context

## Suggestions for Enhancement

### 1. Add Concrete Examples
Consider adding real-world examples for each phase:

```markdown
### Phase 1 Example: Building a CLI Tool
**Initial brain dump**: "I need a tool that converts markdown to PDF"
**Clarifying questions**: "What markdown features? What PDF customization?"
**Options explored**: "Python with markdown2/pdfkit vs Node with marked/puppeteer"
**Specific requirements**: "Must support tables, code highlighting, custom CSS"
```

### 2. Include Decision Points
Add explicit decision gates between phases:
- Phase 1 → Phase 2: "Do I have enough clarity to define an MVP?"
- Phase 2 → Phase 3: "Is the plan technically feasible and aligned with goals?"

### 3. Add Feedback Loops
Emphasize the iterative nature with explicit feedback mechanisms:
- After each prototype iteration, what questions to ask
- How to communicate what's working/not working
- When to pivot vs. persevere

### 4. Template Prompts
Provide starter prompts for each phase:

**Phase 1 Starter**: "I'm trying to [goal]. My constraints are [X, Y, Z]. What approaches should we consider?"

**Phase 2 Starter**: "Based on our discussion, can you provide an MVP plan that focuses on [core feature]?"

**Phase 3 Starter**: "Let's implement [specific component]. Start with the simplest working version."

## Integration with Existing Patterns

The workflow aligns well with the Aditi project's emphasis on:
- **Structured approaches** (like the Vale integration patterns)
- **Clear phases** (similar to the rule processing stages)
- **User guidance** (matching the git workflow philosophy)

Consider cross-referencing this workflow in other documentation sections where users might benefit from understanding the Claude.ai collaboration process.

## Questions for Consideration

1. Should this workflow be tool-agnostic or specifically tailored for Claude.ai?
2. How does this workflow adapt for different project types (new features vs. debugging vs. refactoring)?
3. Would visual diagrams help illustrate the workflow phases and decision points?
4. Should we include time estimates or effort indicators for each phase?

## Next Steps

1. Gather feedback on these suggestions
2. Create concrete examples from actual Aditi development sessions
3. Test the workflow with different types of development tasks
4. Refine based on real-world usage patterns