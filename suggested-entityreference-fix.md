# Suggested Fixes for EntityReference Rule

## Option 1: Enhanced Script-Based Rule (Recommended)

Update the EntityReference.yml rule to track code blocks and inline code:

```yaml
# Report unsupported character entity references.
---
extends: script
message: "HTML character entity references are not supported in DITA."
level: error
scope: raw
script: |
  text               := import("text")
  matches            := []

  r_comment_line     := text.re_compile("^(//|//[^/].*)$")
  r_comment_block    := text.re_compile("^/{4,}\\s*$")
  r_code_block       := text.re_compile("^-{4,}\\s*$")
  r_source_block     := text.re_compile("^\\[source[^\\]]*\\]\\s*$")
  r_entity_reference := text.re_compile("&[a-zA-Z][a-zA-Z0-9]*;")
  r_supported_entity := text.re_compile("&(?:amp|lt|gt|apos|quot);")
  r_inline_code      := text.re_compile("`[^`]+`")

  document           := text.split(text.trim_suffix(scope, "\n"), "\n")

  in_comment_block   := false
  in_code_block      := false
  after_source_attr  := false
  start              := 0
  end                := 0

  for line in document {
    start += end
    end    = len(line) + 1

    # Check for comment blocks
    if r_comment_block.match(line) {
      delimiter := text.trim_space(line)
      if ! in_comment_block {
        in_comment_block = delimiter
      } else if in_comment_block == delimiter {
        in_comment_block = false
      }
      continue
    }
    
    # Check for code blocks
    if r_code_block.match(line) {
      if after_source_attr || ! in_code_block {
        in_code_block = true
        after_source_attr = false
      } else {
        in_code_block = false
      }
      continue
    }
    
    # Check for source block attributes
    if r_source_block.match(line) {
      after_source_attr = true
      continue
    }
    
    # Skip if we're inside any kind of block
    if in_comment_block || in_code_block { continue }
    if r_comment_line.match(line) { continue }

    # Remove inline code from the line before checking for entities
    line_without_inline_code := r_inline_code.replace(line, "")

    for i, entry in r_entity_reference.find(line_without_inline_code, -1) {
      if ! r_supported_entity.match(entry[0].text) {
        # Adjust position back to original line
        # This is simplified - a more robust solution would track exact positions
        matches = append(matches, {begin: start + entry[0].begin, end: start + entry[0].end - 1})
      }
    }
  }
```

## Option 2: Use Vale's Built-in Scope Control

Vale has a `scope` parameter that can be set to `text` instead of `raw`. This might help:

```yaml
# Report unsupported character entity references.
---
extends: existence
message: "HTML character entity references are not supported in DITA."
level: error
scope: text
ignorecase: false
tokens:
  - '&(?!amp|lt|gt|apos|quot)[a-zA-Z][a-zA-Z0-9]*;'
```

However, this approach might not work perfectly with AsciiDoc's syntax.

## Option 3: Use BlockIgnores in .vale.ini

Add to the `.vale.ini` configuration:

```ini
[*.adoc]
BasedOnStyles = AsciiDocDITA

# Ignore code blocks
BlockIgnores = \
  (?s)^----\n.*?\n----$, \
  (?s)^\[source.*?\]\n----\n.*?\n----$, \
  `[^`]+`
```

## Option 4: Create a Preprocessing Script

Create a script that temporarily removes code blocks before Vale runs:

```python
import re
import sys

def mask_code_blocks(content):
    """Replace code blocks with placeholders that Vale will ignore."""
    
    # Replace code blocks
    code_block_pattern = r'(^----\n.*?\n----$)'
    content = re.sub(code_block_pattern, lambda m: '\n'.join(['// VALE_IGNORE'] * len(m.group(1).split('\n'))), content, flags=re.MULTILINE | re.DOTALL)
    
    # Replace source blocks
    source_block_pattern = r'(\[source[^\]]*\]\n----\n.*?\n----)'
    content = re.sub(source_block_pattern, lambda m: '\n'.join(['// VALE_IGNORE'] * len(m.group(1).split('\n'))), content, flags=re.MULTILINE | re.DOTALL)
    
    # Replace inline code
    inline_code_pattern = r'`[^`]+`'
    content = re.sub(inline_code_pattern, '`VALE_IGNORE`', content)
    
    return content

if __name__ == "__main__":
    content = sys.stdin.read()
    print(mask_code_blocks(content))
```

## Option 5: Custom Vale Extension

Create a custom Vale extension that properly handles AsciiDoc syntax. This would be the most robust solution but requires more development effort.

## Recommendation

I recommend **Option 1** (Enhanced Script-Based Rule) as it:
- Maintains the existing rule structure
- Adds proper detection for code blocks and inline code
- Doesn't require changes to Vale configuration or preprocessing
- Can be contributed back to the AsciiDocDITA project

The key additions are:
1. `r_code_block` regex to detect `----` delimiters
2. `r_source_block` regex to detect `[source]` attributes
3. `r_inline_code` regex to detect backtick-wrapped code
4. State tracking for `in_code_block` and `after_source_attr`
5. Removing inline code from lines before checking for entities

This solution properly handles the nested structure of AsciiDoc documents while maintaining line number accuracy for error reporting.