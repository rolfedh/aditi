# 🚀 Aditi: AsciiDoc to DITA Migration Tool

## 📋 Presentation Outline for Technical Writers

---

## 1. Introduction: Name and Purpose

### 🎯 **What is Aditi?**
- **Mission**: Streamline AsciiDoc-to-DITA migration for technical writers

### 💡 **Core Purpose**
- Automated CLI tool for DITA migration preparation
- Detects and fixes compatibility issues systematically

### 👥 **Target Audience**
- Technical writers using AsciiDoc
- Documentation teams planning DITA migration

---

## 2. Key Features

### 🔧 **Automated Rule Engine**
- **27+ Rules** specifically for AsciiDoc-to-DITA compatibility
- **Smart Detection** of mod-docs compliance issues
- **Current** gets AsciiDocDITA style from jhradilek/asciidoctor-dita-vale
- **Intelligent Processing** with dependency-aware rule ordering

### 🎨 **Three Fix Categories**

| Fix Type | Description | Example |
|----------|-------------|----------|
| **✅ Fully Deterministic** | Automatic fixes with 100% confidence | `->` becomes `&#8594;` |
| **⚡ Partially Deterministic** | Fixes with placeholder values | Missing content type gets `<PLACEHOLDER>` |
| **📝 Non-Deterministic** | Manual review required | Comment flags added for complex issues |

### 🛠️ **Core Capabilities**
- **Vale Integration**: Containerized linting with AsciiDocDITA rules
- **Session Management**: Pause and resume migration workflows
- **Batch Processing**: Handle entire documentation repositories
- **Progress Tracking**: Real-time status updates and reporting

---

## 3. Getting Started: `aditi init`

### 🏁 **One-Time Setup Command**
```bash
cd <doc_repo_directory>
aditi init
```

### ⚙️ **What It Does**
1. **Downloads Vale**: Fetches latest AsciiDocDITA ruleset
2. **Configures Container**: Pulls vale container for Podman/Docker
3. **Creates Config**: Generates `.vale.ini` in project root
4. **Verifies Setup**: Tests container connectivity

### ✨ **Key Benefits**
- **Zero Manual Config**: Everything automated
- **Visual Progress**: Rich terminal UI shows setup status
- **Smart Detection**: Finds Podman or Docker automatically
- **Project-Specific**: Each project gets its own configuration

---

## 4. The Migration Journey: `aditi journey`

### 🗺️ **Interactive Migration Workflow**
```bash
aditi journey              # Start new migration
aditi journey     # Continue previous session
```

### 📁 **Repository Configuration**
- **Directory Selection**: Choose which folders to process
- **Exclusion Rules**: Block generated or vendor directories
- **Smart Defaults**: Sensible settings out-of-the-box

### ⚡ **Processing Pipeline**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Scan Files  │ ──> │ Run Vale     │ ──> │ Apply Fixes │
│ (*.adoc)    │     │ (Linting)    │     │ (By Type)   │
└─────────────┘     └──────────────┘     └─────────────┘
        │                    │                    │
        v                    v                    v
   Find AsciiDoc      Detect Issues         Fix or Flag
```

### 💾 **Session Management**
- **Auto-Save**: Progress saved after each step
- **Interruption-Safe**: Resume exactly where you left off
- **7-Day Retention**: Sessions expire after one week
- **Unique IDs**: Each journey gets tracking identifier

---

## 5. Live Demo Flow

### 🎬 **Demo Sequence** (10-15 minutes)

#### **Part 1: Setup** (2 min)
```bash
# Show clean project state
ls -la

# Run initialization
aditi init
```

#### **Part 2: Migration Journey** (5-7 min)
```bash
# Start interactive journey
aditi journey

# Show directory selection
# Demonstrate rule processing
# Display progress tracking
```

#### **Part 3: Results** (3-5 min)
- Show **before/after** file comparisons
- Highlight **automatic fixes** applied
- Point out **manual review** comments
- Demonstrate **session resume** capability


---

## 6. Benefits for Technical Writers

### 🎯 **Immediate Value**

| Benefit | Impact |
|---------|--------|
| **⏱️ Time Savings** | 80% reduction in manual conversion work |
| **🎨 Consistency** | Uniform application of DITA standards |
| **📚 Scalability** | Process 1000s of files in minutes |
| **🔍 Transparency** | See exactly what changes are made |

### 💪 **Empowerment Features**
- **Clear Guidance**: Explanatory comments for manual fixes
- **Full Control**: Review all changes before applying
- **Learning Tool**: Understand DITA requirements through examples
- **Safety Net**: Resume capability prevents lost work

---

## 7. Getting Started Today

### 📋 **Prerequisites**
- ✅ Python 3.11 or later
- ✅ Git (for version control)
- ✅ Podman or Docker (for Vale container)

### 🚀 **Installation**
```bash
# When released to PyPI
pip install aditi

# For development/testing
git clone <repository-url>
cd aditi
pip install -e ".[dev]"
```

### 🎯 **Quick Start Guide**
```bash
# Step 1: Initialize Aditi in your project
aditi init

# Step 2: Start the migration journey
aditi journey

# Step 3: Follow the interactive prompts
# Step 4: Review and apply changes
```

### 📚 **Resources**
- **Documentation**: Comprehensive guides and API docs
- **Issue Tracker**: Report bugs and request features
- **Community**: Join discussions and share experiences
- **Examples**: Sample migrations and best practices

---

## 📧 Questions?

**Thank you for your attention!**

*Ready to streamline your DITA migration?*