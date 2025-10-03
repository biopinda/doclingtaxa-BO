# doclingtaxaBO Constitution

## Core Principles

### I. Library-First Architecture
Every feature starts as a standalone library with clear API boundaries. The core PDF processing functionality MUST be usable as a Python library independently of the CLI interface. Libraries must be:
- Self-contained with explicit dependencies
- Independently testable without CLI wrapper
- Documented with API contracts (library-interface.md)

### II. CLI Interface Standard
Every library function MUST be exposed via CLI for automation and scripting. CLI design requirements:
- Text in/out protocol: arguments/stdin → stdout, errors → stderr
- Support both JSON (machine-readable) and human-readable output formats
- Exit codes: 0 (success), 1 (partial success), 2 (failure)
- Progress reporting for long-running operations

### III. Test-First Development (NON-NEGOTIABLE)
TDD is mandatory for all implementation work:
- Contract tests written BEFORE implementation begins
- Tests MUST fail initially (Red phase)
- Implementation makes tests pass (Green phase)
- Refactor only after tests pass
- No production code without corresponding tests
- Minimum 80% code coverage enforced

### IV. Darwin Core Compliance
All taxonomic data MUST conform to Darwin Core (DwC) standard:
- Use existing DwC schema (schema-dwc2json-taxa-mongoDBJSON.json) as base
- Extensions (structuredDescription, processingMetadata) MUST be documented
- Field mappings from PDF → DwC MUST be explicit and traceable
- MongoDB documents MUST validate against DwC schema
- Interoperability with GBIF, iNaturalist, and biodiversity platforms maintained

### V. Simplicity & YAGNI
Start with the simplest solution that meets requirements:
- No premature optimization (profile first, optimize second)
- No speculative features (YAGNI principle)
- Sequential processing before parallel processing
- Direct MongoDB access before repository patterns (unless complexity justified)
- Flat structures before nested hierarchies (DwC standard enforces this)

### VI. Observability
All operations MUST be observable and debuggable:
- Structured logging with context (pdf_path, taxon_id, duration)
- Log levels: DEBUG (development), INFO (production), WARNING (validation), ERROR (failures)
- JSON structured logs for automation
- Human-readable terminal output for CLI users
- Progress reporting for batch operations

## Data Standards

### Darwin Core Schema Authority
- Base schema: `specs/main/schema-dwc2json-taxa-mongoDBJSON.json`
- Schema changes require documentation in data-model.md
- New fields MUST be justified as DwC extensions
- Flat taxonomic structure (no deep nesting) - use `higherClassification` for hierarchy
- One MongoDB document per taxon (species-level focus)

### Validation Requirements
- Required fields: scientificName, taxonRank, family, genus (for species)
- Species-level records MUST have structuredDescription
- All MongoDB writes validated by Pydantic models
- Validation warnings logged but don't block processing
- Partial extractions allowed with status="partial"

## Quality Gates

### Before Implementation
- [ ] Constitution compliance verified (this document)
- [ ] All NEEDS CLARIFICATION resolved (research.md)
- [ ] Contract tests written and failing
- [ ] User approval of test scenarios

### Before Commit
- [ ] All contract tests passing
- [ ] Integration tests passing
- [ ] Code coverage ≥80%
- [ ] Linting clean (ruff check passes)
- [ ] Formatting applied (black)

### Before Release
- [ ] All quickstart scenarios validated
- [ ] Performance benchmarks within targets
- [ ] DwC schema validation passing
- [ ] Documentation updated (README.md, API docs)

## Development Workflow

### Task Execution Order
1. Setup & Infrastructure (T001-T005)
2. **Contract Tests (T006-T011) - MUST FAIL**
3. **Integration Tests (T012-T017) - MUST FAIL**
4. Models → Extractors → Storage → Library → CLI
5. Pass all tests before moving to next phase
6. Polish & Documentation last

### Error Handling Philosophy
- Per-file error isolation: One PDF failure doesn't stop batch processing
- Meaningful error messages with context (file path, reason, action)
- No silent failures - always log and report
- Best-effort processing - continue on non-critical errors

## Governance

This constitution supersedes all other development practices for the doclingtaxaBO project.

**Amendment Process**:
- Amendments require justification documented in `specs/main/plan.md` Complexity Tracking section
- Must demonstrate why simpler alternative insufficient
- Requires explicit approval before implementation

**Compliance Verification**:
- All PRs/commits must verify constitution compliance
- `/analyze` command enforces constitution as non-negotiable
- Violations block implementation until resolved

**Runtime Guidance**:
- Use `CLAUDE.md` for AI agent development context
- Constitution defines WHAT (principles), CLAUDE.md defines HOW (current state)

**Version**: 1.0.0 | **Ratified**: 2025-10-03 | **Last Amended**: 2025-10-03