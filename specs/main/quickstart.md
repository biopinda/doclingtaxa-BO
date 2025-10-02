# Quickstart Guide & Integration Tests

**Feature**: PDF Monograph to Structured JSON Conversion
**Version**: 1.0.0
**Date**: 2025-10-02

## Purpose

This document provides:
1. **User quickstart**: Step-by-step guide to run the system
2. **Integration test scenarios**: Test cases derived from user stories (spec.md)
3. **Validation criteria**: How to verify correct behavior

---

## Prerequisites

### System Requirements
- Python 3.11 or higher
- MongoDB 5.0+ running locally or remotely
- 2GB available RAM (for PDF processing)
- 500MB disk space (for dependencies)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd doclingtaxaBO

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
doclingtaxaBO --version
```

### MongoDB Setup

**Note**: Configure your own MongoDB server credentials.

```bash
# Verify connection to your MongoDB server
mongosh "mongodb://your_user:your_password@your_host:27017/?authSource=admin" --eval "db.runCommand({ ping: 1 })"

# Verify database and collection exist
mongosh "mongodb://your_user:your_password@your_host:27017/your_database?authSource=admin" --eval "db.your_collection.countDocuments({})"
```

### Environment Configuration

Create `.env` file in project root:
```env
MONGODB_URI=mongodb://your_user:your_password@your_host:27017/?authSource=admin
MONGODB_DATABASE=your_database
MONGODB_COLLECTION=your_collection
LOG_LEVEL=INFO
```

---

## Quickstart Scenarios

### Scenario 1: Process Single PDF (Happy Path)

**User Story**: Process a single text-based PDF with valid taxonomic data

**Steps**:
```bash
# 1. Verify test PDFs exist in monografias directory
ls monografias/*.pdf

# 2. Run processing on first PDF
doclingtaxaBO process --input-dir monografias --verbose

# 3. Verify output
# Expected: Success message with species count
```

**Expected Output**:
```
Processing PDFs from: monografias
MongoDB: mongodb://dwc2json@192.168.1.10:27017/dwc2json (collection: monografias)

[1/N] monograph_001.pdf ... ✓ (12 species, 8.3s)

Summary:
  Total:     1 file
  Succeeded: 1 file (12 species)
  Failed:    0 files

Processing time: 8.3 seconds
```

**Validation**:
```bash
# Query MongoDB to verify data
mongosh "mongodb://your_user:your_password@your_host:27017/your_database?authSource=admin" --eval "
  db.monografias.findOne({}, {
    'structuredDescription.sourcePDF.filePath': 1,
    'processingMetadata.status': 1,
    'scientificName': 1
  })
"
```

**Success Criteria**:
- ✅ Exit code 0
- ✅ MongoDB document inserted
- ✅ `metadata.status = "completed"`
- ✅ `taxonomy_root` has nested structure (Kingdom → Species)
- ✅ All species nodes have `description` and `biological_attributes`

---

### Scenario 2: Batch Processing Multiple PDFs

**User Story**: Process a directory with multiple monographs

**Steps**:
```bash
# 1. List all PDFs in monografias directory
ls -la monografias/*.pdf

# 2. Run batch processing
doclingtaxaBO process --input-dir monografias --output-format json > results.json

# 3. Analyze results
cat results.json | jq '.total_files, .succeeded | length'
```

**Expected Behavior**:
- All valid PDFs processed independently
- Failures don't stop processing of remaining files
- Summary shows success/failure breakdown

**Validation**:
```bash
# Verify document count in MongoDB
mongosh "mongodb://your_user:your_password@your_host:27017/your_database?authSource=admin" --eval "
  db.monografias.countDocuments({})
"
# Expected: Number of succeeded files
```

**Success Criteria**:
- ✅ Each successful PDF has one MongoDB document
- ✅ `source_pdf_hash` unique for each document
- ✅ Processing continues after individual failures

---

### Scenario 3: Corrupted/Malformed PDF Handling

**User Story**: System reports errors for invalid PDFs but continues processing

**Steps**:
```bash
# 1. Process monografias directory (may contain valid and invalid PDFs)
doclingtaxaBO process --input-dir monografias --verbose

# 2. Review output for errors
# Expected: Processing continues despite individual failures
```

**Expected Output**:
```
Processing PDFs from: monografias

[1/N] monograph_001.pdf ... ✓ (8 species, 6.1s)
[2/N] corrupted.pdf ... ✗ (Invalid PDF format: File does not start with %PDF-)
[3/N] valid_monograph.pdf ... ✓ (15 species, 9.2s)

Summary:
  Total:     3 files
  Succeeded: 1 file (8 species)
  Failed:    2 files

Processing time: 6.5 seconds
```

**Validation**:
```python
# Integration test validation
import json
result = json.load(open("results.json"))
assert result["total_files"] == 3
assert len(result["succeeded"]) == 1
assert len(result["failed"]) == 2
assert all("error" in failure for failure in result["failed"])
```

**Success Criteria**:
- ✅ Exit code 1 (partial success)
- ✅ Valid PDF stored in MongoDB
- ✅ Error messages include file path and reason
- ✅ No crash or stack traces in output

---

### Scenario 4: Species-Level Filtering

**User Story**: System excludes Family/Genus descriptions and identification keys

**Test PDF Requirements**:
- Contains Family description (should be excluded)
- Contains Genus description (should be excluded)
- Contains Species description (should be included)
- Contains identification key section (should be excluded)

**Steps**:
```bash
# 1. Process monografias with species filtering
doclingtaxaBO process --input-dir monografias --verbose

# 2. Verify only species-level descriptions are stored
```

**Validation**:
```python
# Query MongoDB and verify filtering
from pymongo import MongoClient
client = MongoClient("mongodb://your_user:your_password@your_host:27017/?authSource=admin")
db = client.dwc2json
doc = db.monografias.find_one({"structuredDescription.sourcePDF.filePath": {"$regex": "filtering_test"}})

# Traverse taxonomy tree
def check_descriptions(node):
    if node["rank"] in ["family", "genus"]:
        assert node["description"] is None, f"{node['rank']} should not have description"
        assert node["biological_attributes"] is None
    elif node["rank"] == "species":
        assert node["description"] is not None, "Species must have description"
        assert node["biological_attributes"] is not None

    for child in node["children"]:
        check_descriptions(child)

check_descriptions(doc["taxonomy_root"])
```

**Success Criteria**:
- ✅ Family nodes: `description = null`, `biological_attributes = null`
- ✅ Genus nodes: `description = null`, `biological_attributes = null`
- ✅ Species nodes: `description` present, `biological_attributes` present
- ✅ No "chave de identificação" text in descriptions

---

### Scenario 5: MongoDB Document Querying

**User Story**: Query database to retrieve taxonomic hierarchy

**Steps**:
```bash
# 1. Process monografias data
doclingtaxaBO process --input-dir monografias

# 2. Query all documents
mongosh mongodb://localhost:27017/taxonomy_db --eval "
  db.monographs.find({}, {
    'monograph_title': 1,
    'metadata.total_species_extracted': 1,
    'processing_timestamp': 1
  }).sort({ processing_timestamp: -1 })
"

# 3. Query specific monograph by species count
mongosh mongodb://localhost:27017/taxonomy_db --eval "
  db.monographs.findOne(
    { 'metadata.total_species_extracted': { \$gt: 50 } },
    { 'taxonomy_root': 1 }
  )
"
```

**Validation Queries**:

```javascript
// Query 1: Find all completed monographs
db.monographs.find({ "metadata.status": "completed" }).count()

// Query 2: Total species across all documents
db.monographs.aggregate([
  { $group: { _id: null, total: { $sum: "$metadata.total_species_extracted" } } }
])

// Query 3: Find duplicate PDF hashes (should be none)
db.monographs.aggregate([
  { $group: { _id: "$source_pdf_hash", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
```

**Success Criteria**:
- ✅ All queries return results in < 1 second
- ✅ Hierarchical structure preserved in `taxonomy_root`
- ✅ Indexes used for queries (check with `.explain()`)

---

### Scenario 6: Partial Extraction with Warnings

**User Story**: System processes PDFs even when optional fields are missing

**Test PDF**: Monograph with species missing optional fields (e.g., "Substrato", "Distribuição Geográfica")

**Steps**:
```bash
# Process monografias (may include PDFs with incomplete optional data)
doclingtaxaBO process --input-dir monografias --output-format json > partial_result.json
```

**Expected Result**:
```json
{
  "succeeded": [
    {
      "path": "test_data/partial_data/incomplete.pdf",
      "species": 5,
      "duration": 7.2
    }
  ],
  "warnings": [
    {
      "path": "test_data/partial_data/incomplete.pdf",
      "message": "3 species missing optional fields (substrato, distribuicao_geografica)"
    }
  ]
}
```

**Validation**:
```python
# Verify document saved with warnings
doc = db.monographs.find_one({"source_pdf_path": {"$regex": "incomplete.pdf"}})
assert doc["metadata"]["status"] == "partial"
assert len(doc["metadata"]["validation_warnings"]) > 0
assert doc["metadata"]["total_species_extracted"] == 5

# Verify species still included despite missing fields
species_nodes = [n for n in doc["taxonomy_root"]["children"] if n["rank"] == "species"]
assert len(species_nodes) == 5
for species in species_nodes:
    assert species["scientific_name"] is not None
    assert species["description"] is not None
```

**Success Criteria**:
- ✅ Document saved with `status = "partial"`
- ✅ `validation_warnings` list populated
- ✅ Species included even with null optional fields
- ✅ Required fields (scientific_name, description) always present

---

## Integration Test Implementation

### Test Structure

```
tests/integration/
├── test_single_pdf.py       # Scenario 1
├── test_batch_processing.py # Scenario 2
├── test_error_handling.py   # Scenario 3
├── test_species_filtering.py # Scenario 4
├── test_mongodb_queries.py  # Scenario 5
└── test_partial_extraction.py # Scenario 6

tests/fixtures/
├── sample_pdfs/
│   ├── flora_example.pdf    # Valid text-based PDF (12 species)
│   ├── fauna_mammals.pdf    # Valid fauna PDF (8 species)
│   ├── large_monograph.pdf  # 50+ species
│   ├── incomplete.pdf       # Missing optional fields
│   ├── filtering_test.pdf   # Family/Genus/Species/Key sections
│   └── corrupted.pdf        # Invalid PDF for error testing
└── expected_outputs/
    └── flora_example.json   # Expected taxonomy structure
```

### Test Fixtures Setup

```python
# tests/conftest.py
import pytest
from pymongo import MongoClient
from pathlib import Path

@pytest.fixture(scope="session")
def mongodb_test_client():
    """Provide test MongoDB client"""
    client = MongoClient("mongodb://localhost:27017")
    yield client
    # Cleanup
    client.drop_database("taxonomy_db_test")
    client.close()

@pytest.fixture(scope="function")
def clean_test_db(mongodb_test_client):
    """Clean test database before each test"""
    mongodb_test_client.taxonomy_db_test.monographs.delete_many({})

@pytest.fixture
def sample_pdf_dir():
    """Path to test PDF fixtures"""
    return Path(__file__).parent / "fixtures" / "sample_pdfs"
```

### Sample Test (Scenario 1)

```python
# tests/integration/test_single_pdf.py
import pytest
from pathlib import Path
from src.lib.processor import process_monograph, save_to_mongodb

def test_process_valid_pdf(clean_test_db, mongodb_test_client, sample_pdf_dir):
    """Test processing a single valid PDF monograph"""
    # Arrange
    pdf_path = sample_pdf_dir / "flora_example.pdf"
    mongodb_uri = "mongodb://localhost:27017"

    # Act
    document = process_monograph(pdf_path)
    doc_id = save_to_mongodb(
        document,
        mongodb_uri,
        database="taxonomy_db_test"
    )

    # Assert
    assert document.metadata.status == "completed"
    assert document.metadata.total_species_extracted == 12
    assert document.taxonomy_root.rank == "kingdom"

    # Verify MongoDB storage
    db = mongodb_test_client.taxonomy_db_test
    stored_doc = db.monographs.find_one({"_id": doc_id})
    assert stored_doc is not None
    assert stored_doc["metadata"]["total_species_extracted"] == 12
```

---

## Performance Benchmarks

Run performance tests to establish baseline:

```bash
# Generate performance report
pytest tests/integration/test_performance.py --benchmark-only --benchmark-json=benchmark.json

# Expected benchmarks (reference hardware: 8-core CPU, 16GB RAM)
# - Text PDF (20 pages): 5-10 seconds
# - Scanned PDF (20 pages): 20-40 seconds
# - Large monograph (100 pages): 60-120 seconds
```

---

## Troubleshooting

### Issue: MongoDB Connection Failed

**Symptom**: `pymongo.errors.ServerSelectionTimeoutError`

**Solution**:
```bash
# Check MongoDB is running
docker ps | grep mongodb

# Test connection
mongosh mongodb://localhost:27017 --eval "db.runCommand({ ping: 1 })"

# Verify firewall allows port 27017
```

### Issue: Docling Parsing Errors

**Symptom**: `ExtractionError: Docling parser could not detect document structure`

**Solution**:
- Verify PDF is not password-protected
- Check PDF is not corrupted: `pdfinfo <file.pdf>`
- For scanned PDFs, ensure sufficient memory (OCR intensive)

### Issue: Zero Species Extracted

**Symptom**: `metadata.total_species_extracted == 0`

**Solution**:
- Check PDF contains species-level sections (not just Family/Genus)
- Verify taxonomic rank detection patterns
- Enable verbose logging: `--verbose` flag
- Review `validation_warnings` in MongoDB document

---

## Next Steps

After verifying quickstart scenarios:

1. **Run full test suite**: `pytest tests/integration/ -v`
2. **Generate coverage report**: `pytest --cov=src tests/`
3. **Review test data**: Add project-specific sample PDFs to `tests/fixtures/`
4. **Benchmark performance**: Establish baselines for typical monographs
5. **Deploy to production**: Follow deployment guide (TBD)

---

## Acceptance Criteria Checklist

Derived from spec.md acceptance scenarios:

- [ ] **Scenario 1 (spec)**: Directory scanning identifies all PDFs
  - Integration test: `test_batch_processing.py::test_recursive_directory_scan`

- [ ] **Scenario 2 (spec)**: Successful processing stores data in MongoDB
  - Integration test: `test_single_pdf.py::test_process_valid_pdf`

- [ ] **Scenario 3 (spec)**: Malformed PDFs report errors and continue
  - Integration test: `test_error_handling.py::test_corrupted_pdf_continues`

- [ ] **Scenario 4 (spec)**: Queried data contains full hierarchical structure
  - Integration test: `test_mongodb_queries.py::test_hierarchy_retrieval`

Run all acceptance tests:
```bash
pytest tests/integration/ -m acceptance -v
```
