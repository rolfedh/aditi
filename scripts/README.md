# Aditi Scripts

Utility scripts for the Aditi project.

## Blog Post Creation

### `new-blog-post.sh`

Creates a new blog post with correct filename and timestamp formatting.

**Usage:**
```bash
./scripts/new-blog-post.sh "Your Blog Post Title"
```

**What it does:**
- Generates filename: `YYYY-MM-DD-HHMM-post-title.md`
- Creates proper timestamp in front matter with current timezone
- Uses the blog post template as a starting point
- Provides next steps for editing and publishing

**Example:**
```bash
./scripts/new-blog-post.sh "Implementing New Feature"
# Creates: 2025-07-27-1423-implementing-new-feature.md
# With timestamp: 2025-07-27 14:23:45 -0400
```

**Benefits:**
- Ensures chronological sorting in Jekyll
- Prevents filename/timestamp mismatches
- Consistent formatting across all blog posts
- Reduces manual errors in date/time formatting

## Future Scripts

Additional utility scripts will be added here as the project grows.