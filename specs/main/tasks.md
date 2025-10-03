# Tasks: PDF Monograph to Structured JSON Conversion

**Input**: Design documents from `H:\git\doclingtaxaBO\specs\main\`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Extracted: Python 3.11+, Docling, pymongo, pydantic, DwC schema
2. Load optional design documents ✓
   → data-model.md: 6 entities (DarwinCoreTaxon, StructuredDescription, etc.)
   → contracts/: 2 contracts (mongodb-schema-dwc-extended.json, library-interface.md)
   → quickstart.md: 6 integration scenarios
3. Generate tasks by category ✓
4. Apply task rules ✓
5. Number tasks sequentially (T001-T040) ✓
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate task completeness ✓
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- File paths shown for single project structure (src/, tests/)

---

## Phase 3.1: Setup & Infrastructure

- [ ] **T001** Create project structure per plan.md
  - Create `src/models/`, `src/extractors/`, `src/storage/`, `src/cli/`, `src/lib/`
  - Create `tests/contract/`, `tests/integration/`, `tests/unit/`
  - Create root files: `pyproject.toml`, `.env.template`, `README.md`

- [ ] **T002** Initialize Python project with dependencies
  - Create `pyproject.toml` with Python 3.11+ requirement
  - Add dependencies: `docling`, `pymongo`, `pydantic>=2.0`, `python-dotenv`, `click`, `rich`, `loguru`
  - Add dev dependencies: `pytest`, `pytest-mongodb`, `pytest-cov`, `black`, `ruff`
  - Create `requirements.txt` from pyproject.toml

- [ ] **T003** [P] Configure linting and formatting tools
  - Create `.ruff.toml` (linting config)
  - Create `pyproject.toml` black config section
  - Create `.pre-commit-config.yaml` (optional)
  - File: `.ruff.toml`, `pyproject.toml`

- [ ] **T004** [P] Setup MongoDB test fixtures
  - Create `tests/conftest.py` with MongoDB fixtures
  - Implement `mongodb_test_client` fixture (session scope)
  - Implement `clean_test_db` fixture (function scope)
  - Implement `sample_pdf_dir` fixture
  - File: `tests/conftest.py`

- [ ] **T005** [P] Create environment configuration template
  - Create `.env.template` with required variables
  - Add: `MONGODB_URI`, `MONGODB_DATABASE`, `MONGODB_COLLECTION`, `LOG_LEVEL`
  - Create `.gitignore` (exclude `.env`, `venv/`, `__pycache__/`, `.pytest_cache/`)
  - Files: `.env.template`, `.gitignore`

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (DwC Schema Compliance)

- [ ] **T005.5** [P] Contract test: Species-level filtering (FR-010b)
  - Test species-level records (taxonRank="species") MUST have populated structuredDescription
  - Test family-level records (taxonRank="family") MUST have structuredDescription=null
  - Test genus-level records (taxonRank="genus") MUST have structuredDescription=null
  - Test identification key text excluded from all description fields
  - Verify keyword blocklist: "chave de identificação", "identification key", "dicotômica"
  - File: `tests/contract/test_species_filtering.py`
  - **MUST FAIL before T024 implementation**

- [ ] **T006** [P] Contract test: DwC schema validation and core fields (FR-010a)
  - Test Pydantic models serialize to valid DwC JSON
  - Validate against `specs/main/contracts/mongodb-schema-dwc-extended.json`
  - Test all required DwC fields present: scientificName, taxonRank, family, genus
  - Test all 5 core extracted fields present (FR-010a): Forma de Vida, Substrato, Domínios Fitogeográficos, Tipos de Vegetação, Distribuição Geográfica
  - Verify mapping: Forma de Vida → speciesprofile.lifeForm.lifeForm[], Substrato → speciesprofile.lifeForm.habitat[]
  - Verify mapping: Domínios Fitogeográficos → distribution.phytogeographicDomains[], Tipos de Vegetação → distribution.vegetationType[]
  - Verify mapping: Distribuição Geográfica → distribution.occurrence[]
  - File: `tests/contract/test_dwc_schema_validation.py`

- [ ] **T007** [P] Contract test: Pydantic model serialization
  - Test DarwinCoreTaxon → MongoDB document conversion
  - Test StructuredDescription serialization
  - Test ProcessingMetadata serialization
  - Validate JSON Schema compliance
  - File: `tests/contract/test_pydantic_serialization.py`

- [ ] **T008** [P] Contract test: Library interface - process_monograph
  - Test function signature matches `contracts/library-interface.md`
  - Test with valid PDF path → returns DarwinCoreTaxon
  - Test FileNotFoundError raised for missing PDF
  - Test InvalidPDFError raised for corrupted PDF
  - File: `tests/contract/test_process_monograph.py`

- [ ] **T009** [P] Contract test: Library interface - process_directory
  - Test function signature matches contract
  - Test batch processing returns ProcessingReport
  - Test MongoDB connection failure handling
  - Test NotADirectoryError for invalid path
  - File: `tests/contract/test_process_directory.py`

- [ ] **T010** [P] Contract test: CLI interface
  - Test `doclingtaxa process --help` output
  - Validate all documented arguments present
  - Test `--input-dir`, `--mongodb-uri`, `--output-format`, `--verbose` flags
  - File: `tests/contract/test_cli_interface.py`

- [ ] **T011** [P] Contract test: Error message format
  - Test each exception type includes context, reason, action
  - Test ExtractionError message structure
  - Test ValidationError message structure
  - Test StorageError message structure
  - File: `tests/contract/test_error_messages.py`

### Integration Tests (Quickstart Scenarios)

- [ ] **T012** [P] Integration test: Scenario 1 - Single PDF processing
  - Test processing single text-based PDF
  - Verify MongoDB document inserted
  - Verify `metadata.status = "completed"`
  - Verify DwC fields populated correctly
  - Verify structuredDescription present
  - File: `tests/integration/test_single_pdf.py`

- [ ] **T013** [P] Integration test: Scenario 2 - Batch processing
  - Test processing directory with multiple PDFs
  - Verify each successful PDF has MongoDB document
  - Verify source_pdf_hash unique per document
  - Verify processing continues after individual failures
  - File: `tests/integration/test_batch_processing.py`

- [ ] **T014** [P] Integration test: Scenario 3 - Error handling
  - Test corrupted PDF reports error and continues
  - Test malformed PDF handling
  - Test empty PDF file handling
  - Verify error messages include file path and reason
  - File: `tests/integration/test_error_handling.py`

- [ ] **T015** [P] Integration test: Scenario 4 - Species filtering
  - Test Family descriptions excluded (description=null)
  - Test Genus descriptions excluded (description=null)
  - Test Species descriptions included
  - Test identification keys excluded
  - File: `tests/integration/test_species_filtering.py`

- [ ] **T016** [P] Integration test: Scenario 5 - MongoDB queries
  - Test query by taxonID
  - Test query by scientificName
  - Test aggregation for total species count
  - Test duplicate hash detection
  - File: `tests/integration/test_mongodb_queries.py`

- [ ] **T017** [P] Integration test: Scenario 6 - Partial extraction
  - Test PDF with missing optional fields
  - Verify status="partial" with warnings
  - Verify species still included with null optional fields
  - Verify required fields always present
  - File: `tests/integration/test_partial_extraction.py`

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Models (DwC Pydantic Models)

- [ ] **T018** [P] Implement DwC base models
  - Create `Distribution` model (phytogeographicDomains, vegetationType, occurrence)
  - Create `SpeciesProfile` model (lifeForm, habitat)
  - Create `VernacularName` model
  - Create `Reference` model
  - Create `OtherName` model (synonyms)
  - Create `TypeSpecimen` model
  - File: `src/models/dwc_taxon.py`

- [ ] **T019** [P] Implement StructuredDescription models
  - Create `SourcePDF` model (filePath, fileHash, extractedDate, pageReferences)
  - Create `Morphology` model (generalDescription, habit, height, stems, leaves, flowers, fruits, seeds)
  - Create `Ecology` model (habitat, associates, altitudeRange, soilType, luminosity)
  - Create `Phenology` model (flowering, fruiting, leafShedding)
  - Create `DistributionDetail` model (detailedDescription, states, municipalities, coordinates)
  - Create `Uses` model (economic, medicinal, ornamental, ecological)
  - Create `ConservationStatus` model (category, criteria, threats)
  - Create `StructuredDescription` model (aggregates all above)
  - File: `src/models/structured_description.py`

- [ ] **T020** [P] Implement ProcessingMetadata and DarwinCoreTaxon
  - Create `ProcessingMetadata` model (status, extractedSections, validationWarnings, extractionErrors, processingDuration, doclingVersion)
  - Create `DarwinCoreTaxon` model (all DwC core fields + extensions)
  - Add Pydantic validators for DwC compliance
  - Add custom serializers for MongoDB ObjectId
  - File: `src/models/processing.py` and update `src/models/dwc_taxon.py`

### Extractors (PDF Processing)

- [ ] **T021** Implement Docling parser wrapper
  - Create `DoclingParser` class
  - Implement `parse_pdf(pdf_path: Path) -> dict` method
  - Handle text-based and scanned PDFs (OCR)
  - Extract document structure (sections, tables)
  - Handle errors (corrupted PDFs, parsing failures)
  - File: `src/extractors/docling_parser.py`
  - **Dependency**: Requires T002 (docling installed)

- [ ] **T022** Implement taxonomic field mapper
  - Create `TaxonomicMapper` class
  - Implement `extract_dwc_fields(parsed_data: dict) -> dict` method
  - Extract: scientificName, canonicalName, scientificNameAuthorship
  - Extract: family, genus, specificEpithet, higherClassification
  - Extract: distribution.phytogeographicDomains, distribution.vegetationType, distribution.occurrence
  - Extract: speciesprofile.lifeForm, speciesprofile.habitat
  - Extract: vernacularname array
  - File: `src/extractors/taxonomic_mapper.py`
  - **Dependency**: Requires T021 (DoclingParser)

- [ ] **T023** Implement description extractor
  - Create `DescriptionExtractor` class
  - Implement `extract_structured_description(parsed_data: dict, pdf_path: Path) -> StructuredDescription` method
  - Extract morphology sections (habit, height, stems, leaves, flowers, fruits)
  - Extract ecology sections (habitat, associates, altitude, soil, luminosity)
  - Extract phenology (flowering, fruiting periods)
  - Extract distribution details (states, municipalities)
  - Extract diagnostic characters
  - Extract uses (economic, medicinal, ornamental)
  - Store raw text in `rawText` field
  - File: `src/extractors/description_extractor.py`
  - **Dependency**: Requires T021 (DoclingParser), T019 (StructuredDescription model)

- [ ] **T024** Implement species-level filter
  - Create `SpeciesFilter` class
  - Implement `filter_by_rank(data: dict) -> bool` method (only taxonRank="species")
  - Implement `exclude_identification_keys(text: str) -> str` method
  - Keyword blocklist: ["chave de identificação", "identification key", "dicotômica"]
  - Implement `exclude_family_genus_descriptions(rank: str, description: str) -> Optional[str]`
  - Return null descriptions for Family/Genus ranks
  - File: `src/extractors/species_filter.py`
  - **Dependency**: Requires T022 (TaxonomicMapper)

- [ ] **T025** Implement DwC field validator
  - Create `DwCValidator` class
  - Implement `validate_required_fields(taxon: DarwinCoreTaxon) -> List[str]` (returns warnings)
  - Check: scientificName, taxonRank, family, genus required
  - Check: species rank requires specificEpithet, structuredDescription
  - Check: structuredDescription.sourcePDF required
  - Generate validation warnings for missing optional fields
  - File: `src/extractors/field_validator.py`
  - **Dependency**: Requires T020 (DarwinCoreTaxon model)

### Storage Layer (MongoDB Persistence)

- [ ] **T026** Implement MongoDB client
  - Create `MongoDBClient` class
  - Implement `connect(uri: str, database: str) -> pymongo.database.Database`
  - Implement `get_collection(collection_name: str) -> pymongo.collection.Collection`
  - Implement connection pooling
  - Implement error handling (ConnectionFailure, ServerSelectionTimeout)
  - File: `src/storage/mongodb_client.py`
  - **Dependency**: Requires T002 (pymongo installed)

- [ ] **T027** Implement DwC repository
  - Create `DwCRepository` class
  - Implement `save(taxon: DarwinCoreTaxon) -> ObjectId` method
  - Check for duplicate via `structuredDescription.sourcePDF.fileHash` index
  - Raise `DuplicateDocumentError` if hash exists
  - Implement `find_by_taxon_id(taxon_id: str) -> Optional[DarwinCoreTaxon]`
  - Implement `find_by_scientific_name(name: str) -> List[DarwinCoreTaxon]`
  - Create MongoDB indexes (taxonID unique, fileHash unique, scientificName text)
  - File: `src/storage/dwc_repository.py`
  - **Dependency**: Requires T026 (MongoDBClient), T020 (DarwinCoreTaxon)

### Library Interface (Core Processing)

- [ ] **T028** Implement process_monograph function
  - Create `src/lib/processor.py`
  - Implement `process_monograph(pdf_path: Path) -> DarwinCoreTaxon`
  - Orchestrate: DoclingParser → TaxonomicMapper → DescriptionExtractor → SpeciesFilter → DwCValidator
  - Generate ProcessingMetadata (status, duration, warnings, errors)
  - Raise FileNotFoundError, InvalidPDFError, ExtractionError as appropriate
  - Return validated DarwinCoreTaxon
  - File: `src/lib/processor.py`
  - **Dependency**: Requires T021-T025 (all extractors)

- [ ] **T029** Implement process_directory function
  - Update `src/lib/processor.py`
  - Implement `process_directory(input_dir: Path, mongodb_uri: str) -> ProcessingReport`
  - Scan directory recursively for `*.pdf` files
  - Process each PDF independently (one failure doesn't stop others)
  - Save successful documents to MongoDB via DwCRepository
  - Collect success/failure lists with error messages
  - Return ProcessingReport (total_files, succeeded, failed, processing_time_seconds)
  - File: `src/lib/processor.py`
  - **Dependency**: Requires T028 (process_monograph), T027 (DwCRepository)

### CLI Interface

- [ ] **T030** Implement CLI entry point
  - Create `src/cli/main.py`
  - Use `argparse` to define CLI arguments
  - Arguments: `--input-dir` (required), `--mongodb-uri` (optional, defaults to env var), `--output-format` (json|human, default human), `--verbose` (flag)
  - Implement `process` command
  - Load `.env` file for environment variables
  - Call `process_directory()` from lib/processor.py
  - File: `src/cli/main.py`
  - **Dependency**: Requires T029 (process_directory)

- [ ] **T031** Implement CLI output formatters
  - Update `src/cli/main.py`
  - Implement `format_human_output(report: ProcessingReport) -> str`
  - Show progress: [1/5] filename.pdf ... ✓ (species count, duration)
  - Show summary: Total, Succeeded, Failed counts
  - Implement `format_json_output(report: ProcessingReport) -> str`
  - Output: {"total_files": N, "succeeded": [...], "failed": [...], "processing_time_seconds": X}
  - Use `rich` library for colored terminal output (human format)
  - File: `src/cli/main.py`
  - **Dependency**: Requires T030 (CLI entry point)

---

## Phase 3.4: Integration & Middleware

- [ ] **T032** Create MongoDB collection with DwC schema validation
  - Write script to apply `specs/main/contracts/mongodb-schema-dwc-extended.json` to collection
  - Create validation rules in MongoDB
  - Create indexes: taxonID (unique), fileHash (unique), scientificName (text), family+genus (compound)
  - Script: `scripts/setup_mongodb_schema.py`
  - **Dependency**: Requires T027 (DwCRepository)

- [ ] **T033** Implement structured logging
  - Configure `loguru` in `src/lib/processor.py`
  - Log levels: INFO (processing start/end), WARNING (validation warnings), ERROR (extraction failures)
  - Log format: JSON structured logs with context (pdf_path, taxon_id, duration)
  - Rotate logs: daily rotation, 30-day retention
  - File: `src/lib/processor.py`, `src/cli/main.py`
  - **Dependency**: Requires T028 (processor)

- [ ] **T034** Implement progress reporting
  - Update `process_directory()` to yield progress events
  - Emit events: processing_started, processing_completed, processing_failed
  - Update CLI to display real-time progress using `rich.progress`
  - Show: current file, success/failure count, estimated time remaining
  - File: `src/lib/processor.py`, `src/cli/main.py`
  - **Dependency**: Requires T031 (CLI formatters)

---

## Phase 3.5: Polish & Documentation

- [ ] **T035** [P] Unit tests for extractors
  - Test `DoclingParser` with mock PDFs
  - Test `TaxonomicMapper` field extraction logic
  - Test `DescriptionExtractor` section parsing
  - Test `SpeciesFilter` exclusion rules
  - Test `DwCValidator` validation logic
  - Files: `tests/unit/test_docling_parser.py`, `tests/unit/test_taxonomic_mapper.py`, `tests/unit/test_description_extractor.py`, `tests/unit/test_species_filter.py`, `tests/unit/test_dwc_validator.py`
  - **Dependency**: Requires T021-T025

- [ ] **T036** [P] Unit tests for storage layer
  - Test `MongoDBClient` connection handling
  - Test `DwCRepository` CRUD operations with mocks
  - Test duplicate detection logic
  - Test index creation
  - Files: `tests/unit/test_mongodb_client.py`, `tests/unit/test_dwc_repository.py`
  - **Dependency**: Requires T026-T027

- [ ] **T037** [P] Create sample test PDFs
  - Create `tests/fixtures/sample_pdfs/` directory
  - Add `flora_example.pdf` (12 species, text-based)
  - Add `fauna_mammals.pdf` (8 species, text-based)
  - Add `large_monograph.pdf` (50+ species)
  - Add `incomplete.pdf` (missing optional fields)
  - Add `filtering_test.pdf` (Family/Genus/Species/Identification Key sections)
  - Add `corrupted.pdf` (invalid PDF for error testing)
  - File: `tests/fixtures/sample_pdfs/` (directory with files)

- [ ] **T038** [P] Performance benchmark baseline
  - Create `tests/performance/test_benchmarks.py`
  - Benchmark: Text PDF (20 pages) < 10 seconds
  - Benchmark: Scanned PDF (20 pages) < 40 seconds
  - Benchmark: Large monograph (100 pages) < 120 seconds
  - Generate `benchmark.json` report
  - File: `tests/performance/test_benchmarks.py`
  - **Dependency**: Requires T028 (process_monograph)

- [ ] **T039** [P] Update README with installation and usage
  - Create `README.md` with:
    - Project description
    - Installation instructions (Python 3.11+, MongoDB, dependencies)
    - Quick start guide (from quickstart.md)
    - CLI usage examples
    - DwC schema reference
    - Contributing guidelines
  - File: `README.md`

- [ ] **T040** Final validation and cleanup
  - Run all tests: `pytest tests/ -v --cov=src`
  - Verify coverage > 80%
  - Run linting: `ruff check src/ tests/`
  - Run formatting: `black src/ tests/`
  - Remove any debugging code, print statements
  - Verify all contract tests pass
  - Verify all integration tests pass
  - Run quickstart scenarios manually
  - **Dependency**: Requires all previous tasks

---

## Dependencies Graph

```
Setup (T001-T005) → Tests (T006-T017) → Models (T018-T020) → Extractors (T021-T025) → Storage (T026-T027) → Library (T028-T029) → CLI (T030-T031) → Integration (T032-T034) → Polish (T035-T040)

Key Dependencies:
- T006-T017 (Tests) MUST fail before starting T018+
- T018-T020 (Models) block T021-T025 (Extractors)
- T021 (DoclingParser) blocks T022-T024
- T026-T027 (Storage) block T028-T029 (Library)
- T028 (process_monograph) blocks T029 (process_directory)
- T029 blocks T030-T031 (CLI)
- T031 blocks T034 (Progress reporting)
```

---

## Parallel Execution Examples

### Group 1: Contract Tests (T006-T011) - Run in Parallel
```bash
# Launch all contract tests simultaneously (different files, no dependencies)
Task: "Contract test: DwC schema validation in tests/contract/test_dwc_schema_validation.py"
Task: "Contract test: Pydantic model serialization in tests/contract/test_pydantic_serialization.py"
Task: "Contract test: Library interface - process_monograph in tests/contract/test_process_monograph.py"
Task: "Contract test: Library interface - process_directory in tests/contract/test_process_directory.py"
Task: "Contract test: CLI interface in tests/contract/test_cli_interface.py"
Task: "Contract test: Error message format in tests/contract/test_error_messages.py"
```

### Group 2: Integration Tests (T012-T017) - Run in Parallel
```bash
# Launch all integration tests simultaneously (independent scenarios)
Task: "Integration test: Scenario 1 - Single PDF processing in tests/integration/test_single_pdf.py"
Task: "Integration test: Scenario 2 - Batch processing in tests/integration/test_batch_processing.py"
Task: "Integration test: Scenario 3 - Error handling in tests/integration/test_error_handling.py"
Task: "Integration test: Scenario 4 - Species filtering in tests/integration/test_species_filtering.py"
Task: "Integration test: Scenario 5 - MongoDB queries in tests/integration/test_mongodb_queries.py"
Task: "Integration test: Scenario 6 - Partial extraction in tests/integration/test_partial_extraction.py"
```

### Group 3: Models (T018-T020) - Run in Parallel
```bash
# Launch model creation tasks simultaneously (different files)
Task: "Implement DwC base models in src/models/dwc_taxon.py"
Task: "Implement StructuredDescription models in src/models/structured_description.py"
# T020 depends on T018 completion for DarwinCoreTaxon, so run after T018
```

### Group 4: Polish (T035-T039) - Run in Parallel
```bash
# Launch polish tasks simultaneously (independent files)
Task: "Unit tests for extractors in tests/unit/"
Task: "Unit tests for storage layer in tests/unit/"
Task: "Create sample test PDFs in tests/fixtures/sample_pdfs/"
Task: "Performance benchmark baseline in tests/performance/test_benchmarks.py"
Task: "Update README with installation and usage in README.md"
```

---

## Validation Checklist
*GATE: All items checked before tasks are complete*

- [x] All contracts have corresponding tests (T006-T011)
- [x] All entities have model tasks (T018-T020: DarwinCoreTaxon, StructuredDescription, ProcessingMetadata)
- [x] All tests come before implementation (T006-T017 before T018+)
- [x] Parallel tasks truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] DwC schema compliance validated (T006, T025)
- [x] All quickstart scenarios covered (T012-T017 map to Scenarios 1-6)
- [x] Integration tests for all user stories (6 scenarios from quickstart.md)

---

## Notes

- **[P] Tasks**: Can run in parallel (40 total tasks, 24 marked [P])
- **TDD Enforced**: Tests T006-T017 MUST fail before implementing T018+
- **DwC Compliance**: T006, T025 ensure Darwin Core standard adherence
- **Test Coverage Target**: >80% (verified in T040)
- **Commit Strategy**: Commit after each completed task with descriptive message
- **Avoid**: Vague task descriptions, same-file conflicts, skipping tests

---

## Task Execution Status
*Update as tasks are completed*

**Progress**: 0/40 tasks completed

**Next Task**: T001 - Create project structure per plan.md
