---
layout: page
title: Design Documentation
permalink: /design/
---

# Design Documentation

This section contains the architectural and implementation plans for Aditi.

## Documents

{% for doc in site.design %}
- [{{ doc.title }}]({{ doc.url | relative_url }})
{% endfor %}

## Overview

The design documentation covers:

- **Project Architecture**: Overall system design and component interactions
- **Implementation Strategy**: Step-by-step development plan optimized for Claude Code
- **Technical Decisions**: Rationale behind key architectural choices
- **Development Workflow**: Best practices for iterative development

These documents serve as living references that evolve with the project.