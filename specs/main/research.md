# Research & Technical Decisions

**Feature**: PDF Monograph to Structured JSON Conversion
**Date**: 2025-10-02

## Research Questions

### 1. Docling PDF Extraction Capabilities

**Decision**: Use Docling library for PDF text, table, and structure extraction

**Rationale**:
- Docling (https://github.com/docling-project/docling) is specifically designed for document understanding
- Supports text extraction, table detection, and layout analysis
- Handles both text-based and OCR-based PDFs (scanned documents)
- Built-in support for complex layouts (multi-column, figures, tables)
- Active development with scientific document focus

**Alternatives Considered**:
- PyPDF2: Basic text extraction only, no table support, poor OCR handling
- pdfplumber: Good table extraction but limited OCR capabilities
- Camelot: Table-focused, requires external dependencies (Ghostscript)
- **Rejected because**: Docling provides comprehensive document understanding vs. basic extraction

**Implementation Notes**:
- Use Docling's document converter for PDF parsing
- Extract document structure for identifying taxonomic sections
- Handle OCR fallback for scanned PDFs automatically

### 2. Darwin Core (DwC) Schema Adoption

**Decision**: Use existing Darwin Core (DwC) standard schema with `structuredDescription` extension

**Rationale**:
- Project already has established DwC schema (schema-dwc2json-taxa-mongoDBJSON.json)
- DwC is international standard for biodiversity data (https://dwc.tdwg.org)
- Flat taxonomic structure with standard fields: `scientificName`, `family`, `genus`, `specificEpithet`
- Existing fields map directly: `distribution.phytogeographicDomains`, `speciesprofile.lifeForm`
- Interoperability with GBIF, iNaturalist, and other biodiversity platforms
- Schema already includes: nomenclature, distribution, vernacular names, references, type specimens

**Alternatives Considered**:
- Custom nested hierarchy: Non-standard, breaks interoperability, duplicate work
- Graph database (Neo4j): Overkill, DwC is industry standard
- **Rejected because**: DwC provides standardization, existing schema, and ecosystem compatibility

**Model Structure** (DwC + Extension):
```python
DarwinCoreTaxon:
  # DwC Core Fields
  - scientificName: str
  - canonicalName: str
  - scientificNameAuthorship: str
  - taxonRank: str
  - kingdom, phylum, class, order, family, genus: str
  - specificEpithet: Optional[str]
  - higherClassification: str  # Pipe-delimited hierarchy

  # DwC Extensions (existing)
  - distribution: Distribution (phytogeographicDomains, vegetationType, occurrence)
  - speciesprofile: SpeciesProfile (lifeForm, habitat)
  - vernacularname: List[VernacularName]
  - reference: List[Reference]

  # NEW Extension (for PDF monograph descriptions)
  - structuredDescription: StructuredDescription
    - sourcePDF: dict (filePath, fileHash, extractedDate)
    - morphology: dict (habit, height, stems, leaves, flowers, fruits)
    - ecology: dict (habitat, associates, altitudeRange, soilType)
    - phenology: dict (flowering, fruiting)
    - distribution: dict (detailedDescription, states, municipalities)
    - diagnosticCharacters: List[str]
    - uses: dict (economic, medicinal, ornamental)
    - conservationStatus: dict (category, criteria, threats)
```

**Field Mapping** (PDF → DwC):
- "Forma de Vida" → `speciesprofile.lifeForm.lifeForm[]`
- "Substrato" → `speciesprofile.lifeForm.habitat[]`
- "Domínios Fitogeográficos" → `distribution.phytogeographicDomains[]`
- "Tipos de Vegetação" → `distribution.vegetationType[]`
- Morphological descriptions → `structuredDescription.morphology.*`

### 3. Species-Level Filtering Strategy

**Decision**: Rule-based filter using rank detection + keyword exclusion

**Rationale**:
- Spec requires: Only species descriptions, exclude Family/Genus, discard identification keys
- Strategy: Extract rank from section headers → filter by rank level → exclude "chave" keywords
- Docling's structure analysis identifies section boundaries
- Pattern matching for rank indicators: "Espécie:", "sp.", "Species:"

**Alternatives Considered**:
- ML-based classification: Overengineered for well-structured documents
- Manual annotation: Not scalable to large document sets
- **Rejected because**: Rule-based approach is deterministic, debuggable, and sufficient for structured monographs

**Implementation Approach**:
- Section header parsing for taxonomic rank detection
- Keyword blocklist: ["chave de identificação", "identification key", "dicotômica"]
- Validate species nodes have required fields before inclusion

### 4. MongoDB Schema Design (DwC Compliance)

**Decision**: One document per species using Darwin Core schema with extensions

**Rationale**:
- Follows existing DwC schema (schema-dwc2json-taxa-mongoDBJSON.json)
- One MongoDB document per taxon (species-level focus for descriptions)
- Flat taxonomic structure (DwC standard): no nesting, uses `higherClassification` for hierarchy
- Extends DwC with `structuredDescription` for PDF-extracted morphological data
- Extends with `processingMetadata` for tracking extraction status
- Compatible with biodiversity data aggregators (GBIF, iNaturalist)

**Alternatives Considered**:
- Custom nested hierarchy: Breaks DwC standard, no interoperability
- One document per PDF: Loses taxon-level granularity, harder to query individual species
- **Rejected because**: DwC compliance is mandatory, species-level access required

**Schema** (DwC + Extensions):
```json
{
  "_id": ObjectId,
  "taxonID": "unique-taxon-id",
  "scientificName": "Genus species Author",
  "canonicalName": "Genus species",
  "scientificNameAuthorship": "Author",
  "taxonRank": "species",
  "family": "Family name",
  "genus": "Genus name",
  "specificEpithet": "species",
  "higherClassification": "Kingdom|Phylum|Class|Order|Family|Genus",

  "distribution": {
    "phytogeographicDomains": ["Amazônia", "Mata Atlântica"],
    "vegetationType": ["Floresta Ombrófila"],
    "occurrence": ["MG", "SP", "RJ"]
  },

  "speciesprofile": {
    "lifeForm": {
      "lifeForm": ["árvore"],
      "habitat": ["terrícola"]
    }
  },

  "structuredDescription": {  /* NEW EXTENSION */
    "sourcePDF": {
      "filePath": "path/to/file.pdf",
      "fileHash": "md5_hash",
      "extractedDate": ISODate
    },
    "morphology": { /* extracted sections */ },
    "ecology": { /* extracted sections */ },
    "phenology": { /* extracted sections */ }
  },

  "processingMetadata": {  /* NEW EXTENSION */
    "status": "completed|partial|failed",
    "extractedSections": ["morphology", "ecology"],
    "validationWarnings": [],
    "processingDuration": 12.3
  }
}
```

### 5. Error Handling & Progress Reporting

**Decision**: Resilient pipeline with per-file error isolation + structured logging

**Rationale**:
- Spec requires: Continue on errors, report status per document
- Architecture: Try-catch per PDF → log error → continue to next file
- Progress: File counter, success/failure lists, current file display
- Structured output: JSON mode for automation, human-readable for CLI

**Alternatives Considered**:
- Fail-fast: Violates requirement to process all files
- Retry logic: Not specified in requirements, adds complexity
- **Rejected because**: Best-effort processing with visibility is the stated goal

**Implementation**:
```python
ProcessingResult:
  - total_files: int
  - processed: int
  - succeeded: List[str]  # PDF paths
  - failed: List[Tuple[str, str]]  # (PDF path, error message)
  - in_progress: Optional[str]
```

### 6. Testing Strategy

**Decision**: Three-tier testing (contract, integration, unit) with test data fixtures

**Rationale**:
- Contract tests: Validate MongoDB schema matches Pydantic models
- Integration tests: End-to-end PDF → MongoDB using sample monographs
- Unit tests: Individual extractors, validators, parsers
- pytest-mongodb for database fixtures, avoids production DB pollution

**Test Data Requirements**:
- Sample PDFs: Text-based, scanned, malformed, edge cases (no species, missing fields)
- Mock Docling responses for unit tests
- MongoDB test containers for integration tests

**Alternatives Considered**:
- E2E tests only: Slow, hard to debug specific failures
- Mocking MongoDB: Misses real DB behavior (indexing, query performance)
- **Rejected because**: Layered testing catches issues at appropriate levels

## Technical Dependencies

### Core Libraries
- **docling**: PDF extraction and document understanding
- **pymongo**: MongoDB driver (official Python client)
- **pydantic**: Data validation and serialization (v2.x for performance)
- **python-dotenv**: Configuration management (MongoDB connection string)

### CLI & Utilities
- **click** or **argparse**: CLI framework (argparse for zero dependencies)
- **rich**: Terminal progress display and formatting
- **loguru**: Structured logging with rotation

### Testing & Quality
- **pytest**: Test framework
- **pytest-mongodb**: MongoDB fixtures
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **ruff**: Fast linting

## Outstanding Edge Cases

### Addressed in Design
- ✅ Scanned PDFs: Docling handles OCR automatically
- ✅ Complex layouts: Docling's structure analysis
- ✅ Missing fields: Validation marks as warnings, includes partial data
- ✅ Identification keys: Keyword-based exclusion
- ✅ MongoDB failures: Per-file try-catch, report errors

### Deferred to Implementation
- ⚠️ Duplicate detection: Requires MD5 hashing of PDF content (add if needed)
- ⚠️ Synonym resolution: Not specified, include as-is in extracted data
- ⚠️ Connection pooling: Start with single connection, optimize if performance issues arise

## Performance Considerations

**Expected Behavior**:
- Docling processing: ~10-30 seconds per PDF (varies by size, OCR needs)
- MongoDB writes: <100ms per document
- Bottleneck: PDF extraction (CPU-bound)

**Optimization Opportunities** (if needed):
- Parallel processing: multiprocessing.Pool for concurrent PDFs
- Batch MongoDB inserts: Accumulate documents, bulk write
- Streaming: Process large PDFs in chunks (if memory becomes issue)

**Current Approach**: Sequential processing with progress reporting (simplest, meets "best-effort" requirement)

## Configuration Requirements

**Environment Variables** (`.env` file):
```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=taxonomy_db
MONGODB_COLLECTION=monographs
LOG_LEVEL=INFO
```

**CLI Arguments**:
- `--input-dir`: Directory containing PDFs (required)
- `--mongodb-uri`: Override default connection (optional)
- `--output-format`: json|human (default: human)
- `--verbose`: Debug logging (optional)

## Security & Validation

**PDF Safety**:
- Docling sandboxes PDF parsing (no arbitrary code execution)
- File type validation: Verify .pdf extension + magic bytes
- Size limits: Warn on files > 100MB, allow processing

**MongoDB Injection Prevention**:
- Pydantic validation before DB writes
- No raw query construction from user input
- Connection string from environment only

**Data Privacy**:
- No external API calls (local processing only)
- MongoDB credentials in `.env` (not committed to git)

## Next Steps

Phase 1 will generate:
1. **data-model.md**: Detailed Pydantic model specifications
2. **contracts/mongodb-schema.json**: MongoDB document schema
3. **quickstart.md**: Integration test scenarios
4. **tests/contract/**: Schema validation tests

All technical unknowns resolved. Ready for design phase.
