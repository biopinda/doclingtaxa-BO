
# Implementation Plan: PDF Monograph to Structured JSON Conversion

**Branch**: `main` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `H:\git\doclingtaxaBO\specs\main\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Process scientific monographs (PDFs) containing fauna and flora taxonomic data, extract taxonomic information and structured species descriptions following Darwin Core (DwC) standard, and store in MongoDB. System uses Docling library for PDF extraction, maps data to existing DwC schema with new `structuredDescription` field for morphological/ecological data, validates species-level records, and processes directories of PDFs with progress reporting.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: Docling (PDF extraction), pymongo (MongoDB driver), pydantic (data validation)
**Storage**: MongoDB with Darwin Core (DwC) schema (schema-dwc2json-taxa-mongoDBJSON.json) + structuredDescription extension
**Testing**: pytest (unit/integration), pytest-mongodb (database fixtures)
**Target Platform**: Cross-platform (Windows/Linux/macOS desktop/server)
**Project Type**: single (CLI tool + library)
**Performance Goals**: Best-effort processing without artificial limits, handle PDFs of any size
**Constraints**: Species-level structured descriptions only, map to DwC fields, exclude Family/Genus descriptions and identification keys
**Scale/Scope**: Directory-based batch processing, unlimited file count, progress reporting required, DwC compliance mandatory

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ⚠️ Constitution template not populated - project has placeholder constitution

Since the constitution file contains only placeholders (`[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`, etc.), no specific architectural principles are enforced. Default best practices will be applied:
- ✅ Library-first approach: Core PDF processing as reusable library
- ✅ CLI interface: Command-line tool for directory processing
- ✅ Test-first development: Contract tests before implementation
- ✅ Error handling: Graceful failures with meaningful messages
- ✅ Simplicity: Direct MongoDB storage, no unnecessary abstraction layers

**Recommendation**: Run `/constitution` to define project-specific principles before scaling.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/              # Pydantic models following DwC schema
│   ├── dwc_taxon.py     # DarwinCoreTaxon, Distribution, SpeciesProfile
│   ├── structured_description.py  # StructuredDescription, Morphology, Ecology
│   └── processing.py    # ProcessingMetadata, ProcessingResult
├── extractors/          # PDF processing logic
│   ├── docling_parser.py         # Docling integration
│   ├── taxonomic_mapper.py       # Extract DwC fields from PDF
│   ├── description_extractor.py  # Parse structured descriptions
│   └── field_validator.py        # DwC compliance validation
├── storage/             # MongoDB persistence
│   ├── mongodb_client.py     # Connection management
│   └── dwc_repository.py     # DwC-specific CRUD operations
├── cli/                 # Command-line interface
│   └── main.py          # argparse CLI entry point
└── lib/                 # Core library interface
    └── processor.py     # High-level processing orchestration

tests/
├── contract/            # DwC schema compliance tests
├── integration/         # End-to-end directory processing tests
└── unit/                # Individual component tests

specs/main/
└── schema-dwc2json-taxa-mongoDBJSON.json  # Base DwC schema (reference)
```

**Structure Decision**: Single project (CLI tool + library). Python package with library-first design following Darwin Core standard. Models strictly map to DwC schema with `structuredDescription` extension. Extractors separate taxonomic data (→ DwC fields) from species descriptions (→ structuredDescription).

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. **Setup & Infrastructure** (5 tasks):
   - Project structure creation (src/, tests/)
   - Dependencies installation (docling, pymongo, pydantic)
   - MongoDB test fixtures setup
   - Environment configuration (.env template)
   - Linting/formatting setup (black, ruff)

2. **Contract Tests** (6 tasks marked [P]):
   - MongoDB schema validation test
   - Pydantic model serialization test
   - Library interface signature test (process_monograph)
   - Library interface signature test (process_directory)
   - CLI interface help output test
   - Error message format test

3. **Core Models** (3 tasks marked [P]):
   - TaxonomicRank and ProcessingStatus enums
   - TaxonNode and BiologicalAttributes models
   - MonographDocument and ProcessingMetadata models

4. **Extraction Services** (5 tasks, sequential):
   - Docling parser wrapper (src/extractors/docling_parser.py)
   - Taxonomy extractor (hierarchical structure extraction)
   - Field validator (species-level validation)
   - Biological attributes extractor
   - Species-level filter (exclude Family/Genus/keys)

5. **Storage Layer** (2 tasks, sequential):
   - MongoDB client and connection management
   - Repository with CRUD and duplicate detection

6. **Library Interface** (2 tasks, sequential):
   - process_monograph() function implementation
   - process_directory() batch function implementation

7. **CLI Interface** (2 tasks, sequential):
   - argparse CLI setup with progress display
   - JSON and human-readable output formatters

8. **Integration Tests** (6 tasks marked [P]):
   - Single PDF processing test (Scenario 1)
   - Batch processing test (Scenario 2)
   - Error handling test (Scenario 3)
   - Species filtering test (Scenario 4)
   - MongoDB query test (Scenario 5)
   - Partial extraction test (Scenario 6)

9. **Polish & Documentation** (4 tasks):
   - Unit tests for individual components
   - README with installation instructions
   - Sample test PDFs creation
   - Performance benchmark baseline

**Ordering Strategy**:
- Setup → Contract tests → Models → Services → Storage → Library → CLI → Integration tests → Polish
- TDD enforced: Contract tests before implementation
- [P] marked for: Contract tests (different test files), Core models (different model files), Integration tests (independent scenarios)
- Sequential for: Services (shared extractor dependencies), Storage (client before repository), Library/CLI (layered)

**Estimated Output**: 35 numbered tasks in tasks.md

**Parallel Execution Groups**:
- Group 1 (contract tests): T006-T011 can run in parallel
- Group 2 (models): T012-T014 can run in parallel
- Group 3 (integration tests): T029-T034 can run in parallel

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (default principles applied)
- [x] Post-Design Constitution Check: PASS (no violations detected)
- [x] All NEEDS CLARIFICATION resolved (research.md completed)
- [x] Complexity deviations documented (none - design follows KISS principle)

**Artifacts Generated**:
- [x] plan.md (this file - updated with DwC schema)
- [x] research.md (technical decisions)
- [x] data-model.md (DwC entity specifications with structuredDescription extension)
- [x] contracts/mongodb-schema-dwc-extended.json (Extended DwC MongoDB schema)
- [x] contracts/library-interface.md (API contracts)
- [x] quickstart.md (integration test scenarios)
- [x] CLAUDE.md (agent context file)
- [x] schema-dwc2json-taxa-mongoDBJSON.json (Base DwC schema reference)

**Next Command**: Run `/tasks` to generate tasks.md

---
*Based on Constitution v2.1.1 - See `.specify/memory/constitution.md`*
