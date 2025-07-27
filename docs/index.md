---
layout: home
title: Blog
---

# Welcome to Aditi

Aditi (short for "asciidoc dita integration") is a CLI tool designed to help technical writers prepare AsciiDoc files for migration to DITA. This blog chronicles the development journey, architectural decisions, and lessons learned along the way.

## Recent Posts

{% for post in site.posts %}
  <article class="post-preview">
    <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
    <p class="post-meta">{{ post.date | date: "%B %d, %Y" }} by {{ post.author }}</p>
    <p>{{ post.summary }}</p>
  </article>
{% endfor %}

## About Aditi

Aditi is a complete reboot of asciidoc-dita-toolkit, designed from the ground up with modern software architecture principles. The tool provides an interactive CLI experience that automates the detection and fixing of AsciiDocDITA rule violations.

### Key Features

- **Interactive CLI**: Guided workflows for migration tasks
- **Automated Fixes**: Deterministic rule violations are fixed automatically
- **Git Integration**: Automated branch creation, commits, and pull requests
- **Docker-based Vale**: Consistent linting environment across platforms
- **Comprehensive Reporting**: Detailed violation reports and fix summaries

### Get Started

```bash
pip install aditi
aditi journey
```

For more information, check out the [design documentation](/aditi/design/) or visit the [GitHub repository](https://github.com/rolfedh/aditi).