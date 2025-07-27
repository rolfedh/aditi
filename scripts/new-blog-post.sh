#!/bin/bash

# Aditi Blog Post Creator
# Creates a new blog post with correct filename and timestamp

set -e

# Check if title is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"Your Blog Post Title\""
    echo "Example: $0 \"Implementing New Feature\""
    exit 1
fi

TITLE="$1"
BLOG_DIR="$(dirname "$0")/../docs/_posts"

# Generate timestamp components
DATE_TIME=$(date '+%Y-%m-%d-%H%M')
FULL_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %z')
CURRENT_YEAR=$(date '+%Y')

# Convert title to URL-friendly format
URL_TITLE=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')

# Create filename
FILENAME="${DATE_TIME}-${URL_TITLE}.md"
FILEPATH="${BLOG_DIR}/${FILENAME}"

# Check if file already exists
if [ -f "$FILEPATH" ]; then
    echo "Error: File $FILENAME already exists!"
    exit 1
fi

# Create blog post from template
cat > "$FILEPATH" << EOF
---
title: "$TITLE"
date: $FULL_TIMESTAMP
author: Your Name
tags: [aditi, asciidoc, dita, migration, technical-writing]
summary: "A brief 1-2 sentence summary of your blog post that will appear in listings."
---

# $TITLE

## Introduction

Start with a compelling hook that explains why readers should care about this topic. Set the context and outline what you'll cover in the post.

## The Problem

Describe the specific challenge or pain point that led to this solution or discovery. Use concrete examples when possible.

## The Solution

### Key Implementation Details

Explain your approach, methodology, or key insights. Break down complex topics into digestible sections.

\`\`\`python
# Include code examples when relevant
def example_function():
    """Demonstrate concepts with working code."""
    pass
\`\`\`

## Results and Impact

Share outcomes, metrics, or feedback that demonstrates the value of your solution.

## Lessons Learned

Reflect on what worked well and what could be improved. Be honest about challenges faced.

## Next Steps

Outline future work, upcoming features, or how readers can get involved.

## Conclusion

Summarize key takeaways and reinforce the main message of your post.

---

### Resources

- [Link to relevant documentation]()
- [Link to related tools or projects]()
- [Link to further reading]()

### About the Author

Brief bio and contact information.
EOF

echo "✅ Created blog post: $FILENAME"
echo "📁 Location: $FILEPATH"
echo "🕒 Timestamp: $FULL_TIMESTAMP"
echo ""
echo "Next steps:"
echo "1. Edit the file to add your content"
echo "2. Update the summary, author, and tags"
echo "3. Test locally with: cd docs && bundle exec jekyll serve"
echo "4. Commit when ready"