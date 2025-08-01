# EntityReference Rule - Code Block Handling

This document explains how Aditi's EntityReference rule handles HTML entities in different contexts, particularly in code blocks.

## Overview

The EntityReference rule converts unsupported HTML entities (like `&nbsp;`, `&copy;`, etc.) to DITA-compatible AsciiDoc attributes (like `{nbsp}`, `{copy}`). However, entities in code contexts should often remain literal.

## Code Block Behavior

### Default Behavior

By default, entities in code blocks are **NOT** converted:

```asciidoc
[source,html]
----
<p>Hello&nbsp;World</p>  <!-- &nbsp; remains literal -->
----
```

### With Substitutions Enabled

When the `subs` attribute includes `replacements`, entities **ARE** converted:

```asciidoc
[source,html,subs="replacements"]
----
<p>Hello&nbsp;World</p>  <!-- &nbsp; becomes {nbsp} -->
----
```

### Common Substitution Patterns

1. **`subs="attributes+"`** - Only processes attribute references, NOT entities:
   ```asciidoc
   [source,terminal,subs="attributes+"]
   ----
   echo "Version {version}"    # {version} is replaced
   echo "Hello&nbsp;World"     # &nbsp; remains literal
   ----
   ```

2. **`subs="attributes+,replacements"`** - Processes both:
   ```asciidoc
   [source,html,subs="attributes+,replacements"]
   ----
   <p>{product}&nbsp;v{version}</p>  # Both {product} and &nbsp; are processed
   ----
   ```

3. **`subs="normal"`** - All normal substitutions including replacements:
   ```asciidoc
   [listing,subs="normal"]
   ----
   Text with &copy; symbol  # &copy; becomes {copy}
   ----
   ```

4. **`subs="none"`** - No substitutions at all:
   ```asciidoc
   [source,html,subs="none"]
   ----
   <p>&trade; {version}</p>  # Nothing is processed
   ----
   ```

## Inline Code

Entities in inline code (backticks) are **NEVER** converted:

```asciidoc
Use the `&nbsp;` entity in HTML.  # &nbsp; remains literal
```

## Why This Matters

This behavior ensures that:
1. Code examples remain accurate and don't have their entities converted
2. When you DO want entities processed in code blocks (e.g., for documentation), you can enable it with `subs="replacements"`
3. Aditi respects AsciiDoc's substitution model

## Known Limitations

- Nested code blocks are not fully supported. The outer block's settings may affect inner blocks.
- Complex substitution patterns (like conditional processing) follow AsciiDoc's standard rules.

## Related Issues

- [Vale Issue #98](https://github.com/jhradilek/asciidoctor-dita-vale/issues/98) - Vale incorrectly flags entities in code blocks
- [Aditi Issue #13](https://github.com/rolfedh/aditi/issues/13) - Aditi correctly handles these cases