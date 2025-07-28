---
layout: post
title: "Removing Git Integration from Aditi CLI Design"
date: 2025-07-27 20:35:54 -0400
categories: [development, design]
tags: [architecture, git, cli, workflow]
author: Development Team
summary: "Major design change: Aditi will provide high-level workflow guidance instead of prescriptive git commands."
---

# Removing Git Integration from Aditi CLI Design

We've made a significant design decision for Aditi: **removing all git integration from the CLI interface and design documentation**.

## The Change

Instead of providing specific git commands like:
```bash
git checkout -b aditi/migration-branch
git add docs/file.adoc
git commit -m "Fix EntityReference issues"
```

Aditi will now offer high-level workflow guidance:
- "Create a pull request with your changes"
- "Review and address any issues identified in the PR"
- "Merge the PR once all issues are resolved"

## Rationale

**Users have existing git knowledge** - Technical writers using Aditi are expected to understand version control workflows.

**Workflow diversity** - Teams use vastly different git approaches (GitFlow, GitHub Flow, trunk-based, etc.). Prescriptive commands become unreliable across environments.

**Reduced support burden** - Git-related issues create support complexity that distracts from Aditi's core mission: AsciiDoc-to-DITA preparation.

**Future flexibility** - Git integration may be reconsidered for future versions based on user feedback.

## Impact

This change affects:
- **CLI Commands**: No git prompts or command suggestions
- **Journey Workflow**: High-level process guidance only
- **Documentation**: All design docs updated to reflect new approach
- **Code Architecture**: `git.py` becomes `workflow.py` with different responsibilities

## Result

Aditi remains focused on its core strength: identifying and fixing AsciiDoc compatibility issues for DITA migration, while respecting that users know how to manage their code changes.

This decision keeps Aditi lightweight and reduces complexity while maintaining its value as a migration preparation tool.