---
layout: post
title: "Fixing Jekyll Front Matter: How Inconsistent Blog Post Headers Broke GitHub Pages"
date: 2025-07-29 06:07:35 -0400
author: Claude Code
tags: [jekyll, github-pages, front-matter, debugging, standardization, yaml]
summary: "Diagnosing and fixing Jekyll build failures caused by inconsistent front matter and template files with placeholder dates."
---

# Fixing Jekyll Front Matter: How Inconsistent Blog Post Headers Broke GitHub Pages

## The Problem

After several successful blog posts, our Aditi documentation site on GitHub Pages suddenly stopped updating. New posts weren't appearing, and the recent commits section remained stale. The "Update Recent Commits" workflow succeeded, but the "Deploy Jekyll with GitHub Pages" workflow consistently failed with a cryptic error:

```
Liquid Exception: Invalid Date: '"YYYY-MM-DD HH:MM:SS -0400"' is not a valid datetime. in /_layouts/default.html
```

## The Investigation

The error message pointed to an invalid date format, but Jekyll was parsing something that looked like a template placeholder rather than an actual date. This suggested a file somewhere contained literal `YYYY-MM-DD HH:MM:SS -0400` text that Jekyll was trying to process as a real datetime.

### Finding the Culprits

A systematic search revealed multiple issues:

1. **Template files with placeholder dates**: Blog post templates contained `date: YYYY-MM-DD HH:MM:SS -0400` (placeholder format) which Jekyll tried to parse
2. **Inconsistent front matter**: Posts had mixed front matter formats - some with `layout: post`, others without
3. **Mixed field usage**: Some posts used `categories`, others used `tags`, creating inconsistent metadata

### The Hidden Draft File

The most elusive issue was a draft file in `docs/drafts/YYYY-MM-DD-hhmm-how-to-make-plans.md` that wasn't excluded from Jekyll processing. Even after fixing the main template, this hidden file continued causing build failures.

## The Solution

### 1. Standardized Front Matter Format

We established a consistent front matter structure for all posts:

```yaml
---
layout: post
title: "Your Post Title"
date: YYYY-MM-DD HH:MM:SS -0400  # placeholder format
author: Author Name
tags: [tag1, tag2, tag3]
summary: "Brief description"
---
```

### 2. Updated All Existing Posts

Applied the standard format to all 9 existing blog posts:
- Added `layout: post` to posts missing it
- Converted `categories` fields to `tags` arrays
- Added `summary` fields where missing
- Ensured consistent author attribution

### 3. Fixed Template Management

- Removed problematic `YYYY-MM-DD-hhmm-post-template.md`
- Created new `post-template.md` with valid date format
- Added template exclusions to `_config.yml`:

```yaml
exclude:
  - _posts/post-template.md
  - drafts/
```

### 4. Cleaned Up Jekyll Configuration

Updated `_config.yml` to exclude all template files and draft directories from processing, preventing future similar issues.

## Results

After implementing these fixes:

✅ **Jekyll builds succeed** - All GitHub Pages deployments now complete successfully  
✅ **Missing posts appear** - The two July 28th blog posts are now visible  
✅ **Recent commits update** - The commits section reflects current repository state  
✅ **Consistent metadata** - All posts follow the same front matter structure  
✅ **Template safety** - Template files are excluded from Jekyll processing  

## Key Lessons Learned

### 1. Jekyll Is Strict About Date Formats
Even placeholder text in template files can break builds if Jekyll tries to parse it as a date. Always exclude template files from processing.

### 2. Front Matter Consistency Matters
Mixed front matter formats can cause subtle issues. Establish a standard format early and stick to it.

### 3. Hidden Files Can Cause Problems
Files in subdirectories like `drafts/` need explicit exclusion. Jekyll processes everything by default.

### 4. Diagnostic Approach Works
When facing build failures:
1. Check the specific error message
2. Search for the problematic content systematically
3. Fix root causes, not just symptoms
4. Test incrementally

## Template for Future Posts

We now have a reliable template structure:

```yaml
---
layout: post
title: "Your Blog Post Title Here"
date: 2025-07-29 10:00:00 -0400
author: Your Name
tags: [aditi, asciidoc, dita, migration, technical-writing]
summary: "A brief 1-2 sentence summary of your blog post that will appear in listings."
---
```

## Impact on Development Workflow

This fix ensures that:
- New blog posts follow consistent conventions
- GitHub Pages deployments are reliable
- Template files won't break builds
- The documentation site stays current with development progress

## Next Steps

- Monitor Jekyll builds to ensure continued stability
- Consider adding automated front matter validation
- Document the standard format for future contributors
- Create helper scripts for generating properly formatted posts

## Conclusion

What started as a mysterious GitHub Pages deployment failure turned into an opportunity to standardize our Jekyll front matter and improve our documentation workflow. The systematic approach of identifying root causes rather than applying quick fixes resulted in a more robust and maintainable blog setup.

Technical debt in content management systems often manifests as build failures. Taking time to standardize and document conventions prevents future issues and makes the system more approachable for contributors.

---

### Resources

- [Jekyll Front Matter Documentation](https://jekyllrb.com/docs/front-matter/)
- [GitHub Pages Jekyll Configuration](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll)
- [YAML Front Matter Best Practices](https://jekyllrb.com/docs/configuration/front-matter-defaults/)

### About the Author

This post was generated by Claude Code while debugging and fixing the Aditi project's GitHub Pages deployment issues, demonstrating real-world Jekyll troubleshooting and standardization workflow.