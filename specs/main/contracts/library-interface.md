# Library Interface Contract

**Feature**: PDF Monograph to Structured JSON Conversion
**Version**: 1.0.0
**Date**: 2025-10-02

## Public API

### 1. Process Monograph (Core Function)

**Function**: `process_monograph(pdf_path: Path) -> MonographDocument`

**Purpose**: Extract taxonomic data from a single PDF monograph and return structured document

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `pdf_path` | `pathlib.Path` | Yes | Absolute path to PDF file |

**Returns**: `MonographDocument` (validated Pydantic model)

**Raises**:
- `FileNotFoundError`: PDF file does not exist
- `InvalidPDFError`: File is not a valid PDF or corrupted
- `ExtractionError`: Docling parsing failed
- `ValidationError`: Extracted data fails schema validation

**Example**:
```python
from pathlib import Path
from src.lib.processor import process_monograph

result = process_monograph(Path("H:/pdfs/flora.pdf"))
print(f"Extracted {result.metadata.total_species_extracted} species")
print(f"Status: {result.metadata.status}")
```

**Contract Test**: `tests/contract/test_process_monograph.py::test_valid_pdf_returns_document`

---

### 2. Process Directory (Batch Function)

**Function**: `process_directory(input_dir: Path, mongodb_uri: str) -> ProcessingReport`

**Purpose**: Process all PDFs in a directory, store in MongoDB, return batch statistics

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `input_dir` | `pathlib.Path` | Yes | Directory containing PDF files |
| `mongodb_uri` | `str` | Yes | MongoDB connection string (e.g., "mongodb://localhost:27017") |

**Returns**: `ProcessingReport`
```python
@dataclass
class ProcessingReport:
    total_files: int
    succeeded: List[Path]
    failed: List[Tuple[Path, str]]  # (path, error_message)
    processing_time_seconds: float
```

**Raises**:
- `pymongo.errors.ConnectionFailure`: Cannot connect to MongoDB
- `NotADirectoryError`: `input_dir` is not a valid directory

**Behavior**:
- Scans `input_dir` recursively for `*.pdf` files
- Processes each PDF independently (one failure doesn't stop others)
- Inserts successful documents into MongoDB
- Returns report with success/failure lists

**Example**:
```python
from pathlib import Path
from src.lib.processor import process_directory

report = process_directory(
    input_dir=Path("H:/monographs"),
    mongodb_uri="mongodb://localhost:27017"
)
print(f"Processed: {len(report.succeeded)}/{report.total_files}")
for path, error in report.failed:
    print(f"Failed: {path} - {error}")
```

**Contract Test**: `tests/contract/test_process_directory.py::test_batch_processing`

---

### 3. Save to MongoDB (Storage Function)

**Function**: `save_to_mongodb(document: MonographDocument, mongodb_uri: str, database: str = "taxonomy_db", collection: str = "monographs") -> ObjectId`

**Purpose**: Persist MonographDocument to MongoDB with duplicate detection

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `document` | `MonographDocument` | Yes | - | Validated document to store |
| `mongodb_uri` | `str` | Yes | - | Connection string |
| `database` | `str` | No | "taxonomy_db" | Database name |
| `collection` | `str` | No | "monographs" | Collection name |

**Returns**: `ObjectId` - Inserted document ID

**Raises**:
- `pymongo.errors.DuplicateKeyError`: Document with same `source_pdf_hash` already exists
- `pymongo.errors.ConnectionFailure`: MongoDB connection failed
- `ValidationError`: Document fails Pydantic validation

**Behavior**:
- Checks for existing document with same `source_pdf_hash`
- Inserts document with indexes (see contracts/mongodb-schema.json)
- Returns inserted `_id`

**Example**:
```python
from src.lib.processor import process_monograph, save_to_mongodb
from pathlib import Path

doc = process_monograph(Path("flora.pdf"))
doc_id = save_to_mongodb(doc, "mongodb://localhost:27017")
print(f"Saved with ID: {doc_id}")
```

**Contract Test**: `tests/contract/test_mongodb_storage.py::test_save_and_retrieve`

---

## CLI Interface Contract

### Command: `doclingtaxaBO process`

**Usage**: `doclingtaxaBO process --input-dir <path> [--mongodb-uri <uri>] [--output-format <format>] [--verbose]`

**Arguments**:
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--input-dir` | `str` | Yes | - | Directory containing PDF files |
| `--mongodb-uri` | `str` | No | `$MONGODB_URI` env var | MongoDB connection string |
| `--output-format` | `str` | No | `human` | Output format: `json` or `human` |
| `--verbose` | `flag` | No | `False` | Enable debug logging |

**Output (human format)**:
```
Processing PDFs from: H:/monographs
MongoDB: mongodb://localhost:27017

[1/5] flora_brazil.pdf ... ✓ (47 species, 12.3s)
[2/5] fauna_mammals.pdf ... ✓ (23 species, 8.1s)
[3/5] corrupted.pdf ... ✗ (Invalid PDF format)
[4/5] empty.pdf ... ⚠ (0 species, 2.1s)
[5/5] large_monograph.pdf ... ✓ (156 species, 45.7s)

Summary:
  Total:     5 files
  Succeeded: 3 files (226 species)
  Failed:    1 file
  Warnings:  1 file

Processing time: 68.2 seconds
```

**Output (json format)**:
```json
{
  "total_files": 5,
  "succeeded": [
    {"path": "H:/monographs/flora_brazil.pdf", "species": 47, "duration": 12.3},
    {"path": "H:/monographs/fauna_mammals.pdf", "species": 23, "duration": 8.1},
    {"path": "H:/monographs/large_monograph.pdf", "species": 156, "duration": 45.7}
  ],
  "failed": [
    {"path": "H:/monographs/corrupted.pdf", "error": "Invalid PDF format"}
  ],
  "warnings": [
    {"path": "H:/monographs/empty.pdf", "message": "No species extracted"}
  ],
  "processing_time_seconds": 68.2
}
```

**Exit Codes**:
- `0`: All files processed successfully
- `1`: Some files failed (but processing completed)
- `2`: Fatal error (e.g., MongoDB connection failed, invalid arguments)

**Contract Test**: `tests/contract/test_cli_interface.py::test_process_command`

---

## Error Handling Contract

### Exception Hierarchy

```
TaxonomyExtractionError (base)
├── InvalidPDFError
├── ExtractionError
│   ├── DoclingParserError
│   └── TaxonomyStructureError
├── ValidationError (from Pydantic)
└── StorageError
    ├── MongoDBConnectionError
    └── DuplicateDocumentError
```

### Error Messages

All errors must include:
1. **Context**: What operation failed (file path, function name)
2. **Reason**: Why it failed (specific error from library)
3. **Action**: What user should do (if applicable)

**Example**:
```
ExtractionError: Failed to extract taxonomy from 'H:/pdfs/flora.pdf'
  Reason: Docling parser could not detect document structure
  Action: Verify PDF is not corrupted and contains text (not scanned images)
```

---

## Performance Contract

### Processing Speed Targets

| PDF Type | Expected Duration | Notes |
|----------|-------------------|-------|
| Text-based (< 50 pages) | 5-15 seconds | Fast path, no OCR |
| Scanned (< 50 pages) | 20-60 seconds | OCR required |
| Large monographs (100+ pages) | 1-3 minutes | Acceptable for batch processing |

**Timeout**: No hard timeout (spec requires "best-effort" for any size)

### Memory Usage

- **Single PDF**: < 200MB peak memory
- **Batch processing**: Sequential processing (no parallel execution in v1.0)

---

## Validation Contract

### Input Validation

**PDF File Checks**:
1. File exists and is readable
2. File extension is `.pdf` (case-insensitive)
3. File size > 0 bytes
4. File magic bytes match PDF format (`%PDF-`)

**MongoDB URI Checks**:
1. Valid URI format (handled by pymongo)
2. Connection test before batch processing

### Output Validation

**MonographDocument Checks**:
1. Pydantic schema validation (see data-model.md)
2. Taxonomy hierarchy consistency (parent-child ranks)
3. Species nodes have required fields (scientific_name, description, biological_attributes)
4. Family/Genus nodes have null descriptions

---

## Testing Requirements

### Contract Tests (Must Pass Before Implementation)

1. **Schema Validation**: `test_mongodb_schema_matches_pydantic`
   - Generate JSON from Pydantic model
   - Validate against contracts/mongodb-schema.json
   - Assert 100% schema compatibility

2. **Library Interface**: `test_process_monograph_signature`
   - Verify function signature matches contract
   - Test with valid/invalid inputs
   - Assert correct exceptions raised

3. **CLI Interface**: `test_cli_help_output`
   - Run `doclingtaxaBO process --help`
   - Assert all documented arguments present

4. **Error Handling**: `test_error_messages_include_context`
   - Trigger each exception type
   - Assert error messages contain context, reason, action

### Integration Tests (Test Scenarios)

See `quickstart.md` for detailed integration test scenarios.

---

## Versioning & Compatibility

**Version**: 1.0.0 (initial release)

**Breaking Changes** (require major version bump):
- Changing MonographDocument schema (add/remove required fields)
- Changing function signatures (parameters, return types)
- Changing CLI argument names

**Non-Breaking Changes** (minor/patch):
- Adding optional fields to models
- Adding new CLI flags
- Performance improvements
- Bug fixes

**MongoDB Schema Migration**: Future schema changes must include migration script in `migrations/` directory.
