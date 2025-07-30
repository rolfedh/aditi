# 🚀 Aditi Command Cheat Sheet

Quick reference for the Aditi CLI tool - your AsciiDoc to DITA migration assistant.

---

## 📋 Prerequisites

```bash
# Required software
python --version    # 3.11 or later
git --version       # Any recent version
podman --version    # OR docker --version
```

---

## 🏁 Initial Setup

### Initialize Aditi in Your Project

```bash
# Navigate to your documentation repository
cd /path/to/your/docs

# One-time setup (downloads Vale, configures container)
aditi init
```

**What it does:**
- Downloads AsciiDocDITA Vale styles
- Configures Podman/Docker container
- Creates `.vale.ini` configuration file
- Verifies everything works

---

## 🎯 Core Commands

### Start Interactive Migration Journey

```bash
# Start a new migration session
aditi journey

# Resume an interrupted session
aditi journey
```

**Interactive workflow includes:**
- Repository configuration
- Directory selection
- Automated rule processing
- Progress tracking with session persistence

### Quick Rule Checking

```bash
# Check all AsciiDoc files for issues
aditi check

# Check specific directory
aditi check docs/modules/

# Check single file
aditi check docs/getting-started.adoc
```

### Apply Specific Rule Fixes

```bash
# Fix character entity references (fully deterministic)
aditi fix --rule EntityReference

# Fix missing content types (partially deterministic)
aditi fix --rule ContentType

# Show available rules
aditi fix --list-rules
```

### Vale Integration

```bash
# Run Vale directly with AsciiDocDITA styles
aditi vale

# Vale on specific files
aditi vale docs/tutorials/*.adoc

# Get Vale version and config info
aditi vale --version
```

---

## 🔧 Common Workflows

### First-Time Migration

```bash
cd your-docs-repo/
aditi init                    # Setup (once per project)
aditi journey                 # Start interactive migration
# Follow prompts to configure and process files
```

### Regular Maintenance

```bash
# Check new/modified files
aditi check

# Fix deterministic issues automatically
aditi fix --rule EntityReference
aditi fix --rule ContentType

# Review flagged issues manually
# (Look for ADITI-ERROR comments in files)
```

### Resuming Interrupted Work

```bash
# If migration was interrupted
aditi journey

# Check session status
ls ~/aditi-data/sessions/
```

---

## 📁 File Organization

### Aditi Configuration

```
your-project/
├── .vale.ini                 # Vale configuration (created by init)
└── ~/aditi-data/
    ├── config.json           # User preferences
    ├── sessions/             # Session state files
    └── logs/                 # Debug logs
```

---

## ⚡ Rule Categories

### Fully Deterministic (Auto-Fixed)
```bash
aditi fix --rule EntityReference    # -> becomes &#8594;
aditi fix --rule LineBreak          # + becomes proper breaks
aditi fix --rule ThematicBreak      # *** becomes ---
```

### Partially Deterministic (Placeholders Added)
```bash
aditi fix --rule ContentType        # Adds :_mod-docs-content-type: <PLACEHOLDER>
aditi fix --rule ShortDescription   # Adds placeholder short descriptions
```

### Non-Deterministic (Manual Review Required)
- Rules that add `// ADITI-ERROR:` comments
- TaskSection, TaskStep, TaskTitle
- NestedSection, DiscreteHeading
- Complex structural issues

---

## 🎨 Example Fixes

### Before & After: Entity References

```asciidoc
# Before
Use the -> arrow and (R) symbol.

# After (automatic fix)
Use the &#8594; arrow and &#174; symbol.
```

### Before & After: Content Type

```asciidoc
# Before
= Installing the Software
```

```
# After

:_mod-docs-content-type: <type>

= Installing the Software
```

Replace `<type>` with `ASSEMBLY`, `CONCEPT`, `PROCEDURE`, `REFERENCE`, or `SNIPPET`

### Manual Review Required

```asciidoc
# Non-deterministic flagging
// ADITI-ERROR: TaskSection - Task sections must use specific heading syntax
== Installing the Software
```

---

## 🔍 Troubleshooting

### Common Issues

```bash
# Container not found
aditi init --force            # Re-download container

# Permission errors
sudo chmod -R 755 ~/aditi-data/

# Config corruption
rm ~/aditi-data/config.json   # Will recreate on next run

# Session issues
rm -rf ~/aditi-data/sessions/ # Clear all sessions
```

### Debug Information

```bash
# Verbose output
aditi --verbose journey

# Check logs
tail -f ~/aditi-data/logs/aditi.log

# Container status
podman ps -a | grep vale      # or docker ps -a
```

---

## 📊 Progress Tracking

### Session Management

```bash
# Sessions are auto-saved every step
# Resume with:
aditi journey

# Session files location:
ls ~/aditi-data/sessions/

# Sessions expire after 7 days
```

### Understanding Output

```
✅ Fully Deterministic: Auto-fixed
⚡ Partially Deterministic: Placeholder added
📝 Non-Deterministic: Manual review needed
🔄 Processing: In progress
⏭️  Skipped: Already processed
```

---

## 🚀 Advanced Usage

### Configuration Customization

```bash
# Edit user configuration
vim ~/aditi-data/config.json

# Project-specific Vale config
vim .vale.ini
```

### Batch Processing

```bash
# Process specific file patterns
aditi check "docs/modules/proc_*.adoc"

# Exclude directories
# Configure in journey interactive mode
```

### Integration with CI/CD

```bash
# Non-interactive checking
aditi check --exit-code     # Exit with non-zero on issues

# Format for parsing
aditi check --format json   # Machine-readable output
```

---

## 📚 Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `aditi init` | One-time setup | `aditi init` |
| `aditi journey` | Interactive migration | `aditi journey` |
| `aditi check` | Scan for issues | `aditi check docs/` |
| `aditi fix` | Apply rule fixes | `aditi fix --rule EntityReference` |
| `aditi vale` | Run Vale directly | `aditi vale *.adoc` |

---

## 🆘 Getting Help

```bash
# Command help
aditi --help
aditi journey --help
aditi fix --help

# List available rules
aditi fix --list-rules

# Show rule details
aditi fix --rule EntityReference --help
```

---

**📖 For detailed documentation, visit the project repository**

**🐛 Report issues or request features through the issue tracker**