---
layout: post
title: "Setting Up GitHub Pages: Lessons from Configuring Aditi's Documentation Site"
date: 2025-07-27 08:32:48 -0400
author: Aditi Development Team
tags: [aditi, github-pages, jekyll, documentation, setup]
summary: "Step-by-step lessons learned while configuring GitHub Pages for the Aditi project documentation site."
---

# Setting Up GitHub Pages: Lessons from Configuring Aditi's Documentation Site

Today I configured GitHub Pages for the Aditi project, and learned several valuable lessons about Jekyll, themes, and avoiding common pitfalls. Here's what worked and what didn't.

## The Initial Confusion: Multiple Jekyll Configurations

After looking at the initial set of published pages, I decided to improve the look a bit. I wanted to reuse the theme I had chosen for asciidoc-dita-toolbox, so I asked claude to "borrow" from its configuration files.

My request created Jekyll configuration files in both the root directory and the `/docs` subdirectory. This led to:
- Conflicting configurations
- Theme mismatches: Just the Docs (the old theme I like) vs Minima (the new default theme)
- Uncertainty about which files GitHub Pages was actually using

**Lesson learned**: Pick one location and stick with it. Either use the root directory OR a subdirectory like `/docs`, never both.

## Choosing the Right Theme

I initially mixed two different themes:
- **Minima**: A simple blog-focused theme
- **Just the Docs**: A documentation-focused theme with powerful search and navigation

For a technical project like Aditi, Just the Docs proved to be the better choice because it offers:
- Built-in search functionality
- Hierarchical navigation
- Clean, professional documentation layout
- Better code syntax highlighting

## The Correct Setup Process

Here's the streamlined process that actually works:

### 1. Enable GitHub Pages in Repository Settings
Navigate to Settings → Pages and select your source branch and directory.

### 2. Create Your Jekyll Configuration
In your chosen directory (I used `/docs`), create `_config.yml`:

```yaml
title: Your Project Name
description: Your project description
baseurl: "/your-repo-name"
url: "https://yourusername.github.io"

# Theme configuration
remote_theme: just-the-docs/just-the-docs@v0.8.2
plugins:
  - jekyll-remote-theme
```

### 3. Create a Gemfile
This specifies your Ruby dependencies:

```ruby
source 'https://rubygems.org'

gem "jekyll", "~> 4.3.0"

group :jekyll_plugins do
  gem "jekyll-remote-theme"
  gem "jekyll-seo-tag"
  gem "jekyll-include-cache"
end
```

### 4. Update the GitHub Actions Workflow
If building from a subdirectory, modify `.github/workflows/jekyll-gh-pages.yml`:

```yaml
- name: Build with Jekyll
  uses: actions/jekyll-build-pages@v1
  with:
    source: ./docs  # Changed from ./
    destination: ./_site
```

## Common Pitfalls to Avoid

1. **Don't create duplicate workflows**: GitHub automatically creates `jekyll-gh-pages.yml` when you enable Pages. Don't create your own competing workflow.

2. **Watch your baseurl**: It should match your repository name (e.g., `/aditi` for `github.io/aditi`).

3. **Add Jekyll build artifacts to .gitignore**:
   ```
   _site/
   .sass-cache/
   .jekyll-cache/
   .jekyll-metadata
   Gemfile.lock
   ```

4. **Choose GitHub's automated workflow**: Instead of manually configuring Ruby and Jekyll, use GitHub's `actions/jekyll-build-pages` action.

## Final Thoughts

Setting up GitHub Pages is straightforward once you understand the architecture. The key is consistency: one location, one theme, one workflow. With Just the Docs theme and proper configuration, you get a professional documentation site with minimal effort.

The Aditi project now has a clean, searchable documentation site that will grow alongside the codebase. Sometimes the best solutions come from simplifying and choosing the right tools for the job.