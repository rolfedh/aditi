# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-29

### Added
- Initial release of Aditi
- Complete implementation of all 26 AsciiDocDITA rules
- CLI commands: init, check, journey, fix, vale
- Vale container integration with Podman/Docker support
- Git workflow guidance for creating branches and pull requests
- Interactive rule application with flag/skip options
- Progress tracking with Rich console output
- Configuration management for repository settings
- Comprehensive test suite with 47% code coverage
- Documentation site with Jekyll and GitHub Pages
- Support for Python 3.11, 3.12, and 3.13

### Rule Coverage
- Error level rules: ContentType, EntityReference, ExampleBlock, NestedSection, TaskSection, TaskExample, TaskStep, TaskTitle, TaskDuplicate, ShortDescription
- Warning level rules: AdmonitionTitle, AuthorLine, BlockTitle, CrossReference, DiscreteHeading, EquationFormula, LineBreak, LinkAttribute, PageBreak, RelatedLinks, SidebarBlock, TableFooter, ThematicBreak
- Suggestion level rules: AttributeReference, ConditionalCode, IncludeDirective, TagDirective

[0.1.0]: https://github.com/rolfedh/aditi/releases/tag/v0.1.0