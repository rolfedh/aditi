The initial idea:

Based on user testing and stakeholder feedback, the `aditi journey` workflow might be too abstract and unnecessary.

I'm considering two new alternatives:

## The simple workflow
1. User cd's to any directory.
2. User runs aditi command and a subcommand. (If user fails to enter subcommand, aditi displays a menu of subcommands that the user can select or enter from.)
3. Aditi performs the subcommand recursively on every adoc file under that directory path.

With this workflow, aditi **just does what you tell it without regard to any other considerations** (i.e., it ignores prerequisites, directory configuration, journey configuration).

## The book workflow
1. User runs `aditi <subcommand> <path>/master.adoc`.
2. Aditi performs the operation on all the files included in the master.adoc recursively down through the tree of included files.

## deprecating parts of the old workflow
Given these two new workflows, I want to deprecate the old workflows, such as "aditi check" and "aditi journey". I might need to disable parts of those workflows by default.

Interview questions and answers (A:)
● Based on my analysis of the current implementation, I need to ask you several
  questions to develop a comprehensive implementation plan:

  Interview Questions

  1. User Experience & Pain Points

  - What specific feedback led to the conclusion that aditi journey is "too  abstract and unnecessary"?

  A: The project sponsor asked me "what if the user could just cd to the directory they want to work on and run a command?" They indicated that users don't want to be shepherded along a trail.

  - What aspects of the journey workflow are problematic for users?

  A: Following the steps of the journey seems slow and difficult. Better to let folks run vale, see a report, and then start fixing the issues they see. Some folks might be responsible for a specific subdirectory. Others might be responsible for a specific book (master.adoc + includes)

  - Are users finding the session management, directory configuration, or guided
   workflow confusing?

   A: Yes.

  2. Simple Workflow Details

  - Should the simple workflow still respect the .vale.ini configuration for
  Vale rules?

  A: Yes. (Side question: Could we consider an enhancement that would add the AsciiDocDITA style to the pre-aditi .vale.ini file if it exists, and then selectively run only the AsciiDocDITA rules?)

  - When you say "ignores prerequisites", does this mean:
    - Skip checking if Vale is initialized?
    A: No.
    - Skip the ContentType rule prerequisite checking?
    A: Yes.
    - Process files even without proper configuration?
    A: Yes.
  - Should it still create backups or git branches?
    A: No.
  - How should error handling work in this simplified mode?
    A: I don't know yet.

  3. Book Workflow Specifics

  - For the book workflow with master.adoc, how should we handle:
    - Nested includes (includes within included files)?
    A: Process all the nested include files.
    - Circular includes?
    A: I believe the current build process already errors and fails if that happens. If not, generate an error message.
    - Missing include files?
    A: I believe the current build process already errors and fails if that happens. If not, generate an error message.


  - Should this workflow process only .adoc files or all included content?
  A: Only .adoc files
  - How deep should the include resolution go?
  A: To the very bottom/to the very last file.

  4. Migration Strategy

  - Do you want to:
    - Keep the old commands but add deprecation warnings?
    A: I don't know yet. Probably no.
    - Remove the old commands entirely?
    A: I don't know yet. Probably yes.

    - Add a feature flag to enable/disable them?
    A: I don't know yet. Maybe yes, if we take the path of deprecating and warning.

  - What about existing users who have active journey sessions?
  A: Good question. I'm not sure. I want your suggestions.
  - Should we preserve any parts of the journey workflow (like git integration)?
  A: There is no git integration. Or if there is, remove it.

  5. Command Structure

  - For the simple workflow, what subcommands do you envision? Examples:

A: Syntax and interactions:

For all operations that modify the files, confirm with user before performing operation. Require user to confirm by entering y: (y/N). Always ignore symlinks.

  - `aditi <subcommand>`: If the command requires a subsubcommand such as `flag` or `fix` notify the user and give them a prompt to choose the subsubcommand. Otherwise, get user confirmation if needed, and then perform the subcommand on all files in current directory and subdirectories.
  - `aditi <subcommand> flag`: Flag all files in current directory and subdirectories with <subcommand> issues.
  - `aditi <subcommand> fix`: Auto-fix all files in current directory and subdirectories with <subcommand> fixes. If no auto-fix exists, notify user.
- `aditi <subcommand> flag <path>/master.adoc`: Flag all files in the master.adoc file's tree of included files with <subcommand> issues.
  - `aditi <subcommand> autofix <path>/master.adoc`: Auto-fix all files in the master.adoc file's tree of included files with <subcommand> fixes.


  Examples:
  - `aditi ValeFlagger`: Flag all files in current directory and subdirectories with all reported issues.
  - `aditi ContentType flag`: Flag all files in current directory and subdirectories with ContentType issues.
  - `aditi ContentType fix`: Auto-fix all files in current directory and subdirectories with ContentType fixes.
- `aditi ContentType flag <path>/master.adoc`: Flag all files in the master.adoc file's tree of included files with ContentType issues.
  - `aditi ContentType autofix <path>/master.adoc`: Auto-fix all files in the master.adoc file's tree of included files with ContentType fixes.

  - Should the menu system be interactive (using questionary) or just print options?
  Just print options.

  6. Configuration & State

  - Should the simple workflow still use ~/aditi-data/ for any configuration?
  A: I don't know yet. I'd prefer not, but yes, if it's necessary.
  - Do we need any persistent state between runs?
  A: I don't know yet. I'd prefer not, but yes, if it's necessary.

  - How should Vale container management work in the simple workflow?
  A: I don't know yet. What do you mean? I'd like to avoid timeouts. So it would be nice to solve that problem. Earlier, you mentioned using native Vale, if it's installed. Does that help prevent timeouts?


  7. Output & Reporting

  - What kind of output do users expect from the simple workflow?
  A: Notify them when the operation is complete. Otherwise, no detailed reporting. If they used the `flag` subcommand, suggest searching for the comment string, such as `Search your files for '// Error: ContentType <show full comment line>`.

  - Should it still generate detailed reports or just show summary counts?
  A: Not even. Just notify them that the operation is complete as described above. Deprecate any functions that compile stats and generate reports. I  want to strip out all the extras.


  - How verbose should the default output be?
  A: See above.

  8. Backwards Compatibility

  - Are there any critical features from the current workflow that must be
  preserved?
  A: Such as? Give me a list.

  - Do you have users with automation scripts depending on current behavior?
  A: No.

  - What's the timeline for deprecating the old workflows?
  A: Now - I'm going to release this as a major version upgrade (1.0.0). I want to warn users of the earlier version of the breaking changes. I don't want to deprecate anything, I just want to remove old features and keep the bare minimum for the new version.

  9. Book Workflow Integration

  - Should the book workflow support the same operations as the simple workflow?
  A: yes
  - How should it handle files that aren't included in the master but exist in
  subdirectories?
  A: This is important: The master.adoc file can include files that are not in the subdirectories below it. It might rely on symlinks to access adjacent directories that aren't under it.

  - Should it validate the include structure before processing?
  A: I don't know. Why and what would that look like for the user?

  10. Testing & Rollout

  - Do you want to implement both workflows simultaneously or one at a time?
  A: Simple workflow first, debug it, and then implement the book workflow.

  - Should we add a --experimental flag for testing new workflows?
  A: No. This will be a major version change with a warning to users that it contains breaking changes. Prompt the user to confirm (y/N) before continuing.

  - How should we handle the transition period?
  A: See above.

  Please provide answers to these questions so I can create a detailed
  implementation plan that addresses your needs while maintaining code quality
  and user experience.

=========================================================

## Implementation Plan (v1.0.0 - Breaking Changes)

### Overview
This is a complete reimagining of Aditi as a direct, no-nonsense tool that does exactly what users tell it to do. No journeys, no sessions, no hand-holding - just straightforward operations on AsciiDoc files.

### Core Philosophy
- **Direct Action**: cd to directory, run command, get results
- **No State**: Each run is completely independent
- **Minimal Output**: Just confirmation when done
- **User Control**: Always confirm before modifying files

### 1. New Command Structure

#### Primary Commands (Rule-Based)
```bash
# Direct operation on current directory
aditi                     # Lists all special commands and RuleName choices. Same as entering `aditi --help`
aditi <RuleName>          # Prompts for flag/fix choice
aditi <RuleName> flag     # Insert issue comments on line above reported issue
aditi <RuleName> unflag   # Remove issue comments
aditi <RuleName> autofix  # Apply auto-fixes, if available

# Book operation
aditi <RuleName> flag <path>/master.adoc
aditi <RuleName> unflag <path>/master.adoc
aditi <RuleName> autofix <path>/master.adoc

# Special command for all Vale issues
aditi ValeFlagger              # Flag all issues reported by Vale running the AsciiDocDITA style rules.
```

A: Add special command to archive unused files based on /home/rolfedh/doc-utils/archive_unused_files.py

# Special command for all Vale issues
```
aditi ArchiveUnusedFiles         # Display help for Archive unused files

aditi ArchiveUnusedFiles --dry-run # Find unused files, output a list of them. Also output a suggestion to use the:

- `--report` option to find files that aren't used anywhere else in the repo. for a file containing the list of files in an `./archive` directory (create it if needed),
- use `--archive` to create a report and an zip file containing the archived files in an `./archive` directory (create it if needed).
```

#### Examples
```bash
cd ~/docs/my-project
aditi ContentType                   # Prompts: "flag or fix?"
aditi ContentType flag              # Adds // Error: ContentType comments
aditi ContentType autofix       # Auto-fixes content type issues
aditi EntityReference autofix   # Auto-fixes entity references

# For books
aditi ContentType autofix guides/master.adoc
```

### 2. Minimal Implementation

#### What to Keep
- Vale container integration (but optimize for speed)
- Rule engine (but remove prerequisites and fix-tracking)
- Basic file scanning
- Auto-fix logic for deterministic rules


#### What to Remove
- All journey workflow code
- Session management
- Configuration management (except Vale)
- Progress tracking
- Detailed reporting
- Git integration
- Directory permission configuration and checks
- Statistics gathering

### 3. User Interaction Model

#### When No Subcommand Provided
```
$ aditi ContentType
This operation requires a subcommand.
Choose an action:
1. flag - Add issue comments to files
2. autofix  - Apply automatic fixes (if available)

Enter your choice (1 or 2):
```

#### Confirmation Before Modifications
```
$ aditi ContentType fix
This will modify 23 files in /home/user/docs and subdirectories.
Continue? (y/N):
```

#### Operation Complete Messages
```
# For flag operations
Operation complete.
Search your files for '// Error: ContentType' to find flagged issues.

# For autofix operations
Operation complete.
23 files modified.

# For rules without fixes
No automatic fixes available for TaskSection.
Use 'aditi TaskSection flag' to mark issues for manual fixing.
```

### 4. Book Workflow Implementation

#### Include Resolution
- Parse `include::` directives recursively
- Follow symlinks when resolving includes
- Support relative and absolute paths
- Handle includes outside the master.adoc directory tree
- Stop on missing files with clear error

#### Error Handling
```
Error: Cannot find included file: ../shared/common.adoc
Referenced from: guides/master.adoc:45
```

### 5. Vale Integration Optimization

#### Native Vale Support
```python
def get_vale_command():
    # Check for native Vale first
    if shutil.which("vale"):
        return ["vale"]
    else:
        # Fall back to container
        return get_container_command()
```

#### Smart .vale.ini Handling
- Check for existing .vale.ini
- Add AsciiDocDITA styles if missing
- Use `--filter` to run only our rules
- Create minimal config if needed

### 6. Migration Plan

#### Immediate Changes (v1.0.0)
1. **Remove Completely**:
   - journey command
   - check command (replaced by ValeFlagger)
   - Session management
   - Config management (except Vale)
   - All reporting features

2. **Simplify**:
   - init command → only Vale setup
   - autofix command → removed (functionality moved to rule-specific commands)

3. **Add**:
   - Rule-specific commands
   - ValeFlagger command
   - Book workflow support

#### Breaking Change Notice
```
$ aditi
WARNING: Aditi v1.0.0 contains breaking changes!
- 'aditi journey' has been removed
- 'aditi check' has been removed
- New syntax: 'aditi <RuleName> [flag|fix]'

This is a complete redesign for simplicity.
Continue? (y/N):
```

### 7. Technical Details

#### Simplified Architecture
```
src/aditi/
├── cli.py                  # Minimal CLI
├── rules/                  # Keep existing rules
├── vale_runner.py          # Simplified Vale execution
├── include_parser.py       # Book include resolution
└── file_utils.py          # Basic file operations
```

#### Key Simplifications
- No ConfigManager class
- No session/state persistence
- Direct file operations only
- Minimal error handling
- No progress bars or fancy output

### 8. Performance Optimizations

#### Container Startup
- Keep container running between operations
- Use native Vale when available
- Minimal container mounts (only necessary directories)

#### File Processing
- Stream processing (don't load all files into memory)
- Process files as Vale reports them
- No pre-scanning or statistics gathering

## Remaining Questions

### 1. Rule Discovery
- How should users know what rules are available?
- Should `aditi --help` list all available rules?
- Or add `aditi list-rules` command?

A:

### 2. ValeFlagger Behavior
- Should ValeFlagger run ALL Vale rules or just AsciiDocDITA?
- How to handle if user has other Vale styles configured?

A:

### 3. Issue Comments Format
- Current: `// <Type>: <RuleName> - <message>`

A:

### 4. Container Timeouts
- Current timeout is 2 minutes - is this the issue?
- Should we increase it or make it configurable?
- Native Vale would eliminate this problem entirely

A:

### 5. Feature Preservation
From current features, should we keep any of these?
- Dry-run mode (show what would change)
- Verbose mode (detailed error output)
- Rule descriptions/help
- Ability to exclude certain directories

A:

### 6. Exit Codes
For scripting/automation:
- 0 = success
- 1 = errors found (for flag operations)
- 2 = operation failed
- Is this sufficient?

A:

### 7. Future Considerations
After v1.0.0 ships, would you consider:
- Watch mode for continuous checking
- Editor/IDE plugins
- GitHub Actions integration
- Rule customization

A:


### 8. Documentation
- Should we keep the Jekyll docs site?
- Or simplify to just README + man page?
- What examples would be most helpful?

A:
