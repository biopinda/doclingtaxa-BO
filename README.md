# DoclingTaxa

PDF Monograph to Structured JSON Conversion following Darwin Core (DwC) standard.

## Overview

DoclingTaxa processes scientific monographs about fauna and flora in PDF format, extracting taxonomic, morphological, and ecological information into structured JSON documents stored in MongoDB. The system follows the Darwin Core (DwC) biodiversity data standard with extensions for detailed species descriptions.

## Features

- 🔬 **Darwin Core Compliance**: Output follows international biodiversity data standard
- 📄 **PDF Processing**: Handles text-based and scanned (OCR) PDFs using Docling
- 🗂️ **Structured Extraction**: Morphology, ecology, phenology, distribution, and diagnostic characters
- 🌿 **Species-Level Focus**: Extracts only species-level descriptions (excludes Family/Genus)
- 🚫 **Smart Filtering**: Automatically excludes identification keys
- 📊 **MongoDB Storage**: Stores hierarchical taxonomic data with validation
- 🔄 **Batch Processing**: Process entire directories with progress reporting
- ✅ **Error Resilience**: Continues processing on individual failures

## Requirements

- Python 3.11 or higher
- MongoDB 5.0+ (local or remote)
- 2GB RAM (for PDF processing)
- 500MB disk space (for dependencies)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd doclingtaxa
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -e .

# Development dependencies (includes testing tools)
pip install -e ".[dev]"
```

### 4. Configure Environment

```bash
# Copy template and edit with your MongoDB connection
cp .env.template .env

# Edit .env with your configuration
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DATABASE=taxonomy_db
# MONGODB_COLLECTION=monographs
```

### 5. Setup MongoDB

**Option 1: Local MongoDB (Docker)**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option 2: MongoDB Atlas (Cloud)**
- Use connection string from Atlas dashboard in `.env`

**Verify Connection**
```bash
mongosh mongodb://localhost:27017 --eval "db.runCommand({ ping: 1 })"
```

## Quick Start

### Process Single Directory

```bash
doclingtaxa process --input-dir /path/to/pdfs
```

### With Custom MongoDB URI

```bash
doclingtaxa process --input-dir /path/to/pdfs --mongodb-uri mongodb://localhost:27017
```

### JSON Output Format

```bash
doclingtaxa process --input-dir /path/to/pdfs --output-format json > results.json
```

### Verbose Logging

```bash
doclingtaxa process --input-dir /path/to/pdfs --verbose
```

## CLI Usage

```
doclingtaxa process [OPTIONS]

Options:
  --input-dir TEXT        Directory containing PDF monographs [required]
  --mongodb-uri TEXT      MongoDB connection string [default: from .env]
  --output-format TEXT    Output format: json|human [default: human]
  --verbose              Enable debug logging
  --help                 Show this message and exit
```

## Output Example

### Human-Readable Format
```
Processing PDFs from: /path/to/pdfs
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

### JSON Format
```json
{
  "total_files": 5,
  "succeeded": [
    {"path": "/path/to/pdfs/flora_brazil.pdf", "species": 47, "duration": 12.3},
    {"path": "/path/to/pdfs/fauna_mammals.pdf", "species": 23, "duration": 8.1}
  ],
  "failed": [
    {"path": "/path/to/pdfs/corrupted.pdf", "error": "Invalid PDF format"}
  ],
  "processing_time_seconds": 68.2
}
```

## Darwin Core Schema

The system stores data using Darwin Core (DwC) standard fields with extensions:

### Core DwC Fields
- `scientificName`, `canonicalName`, `scientificNameAuthorship`
- `kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `specificEpithet`
- `higherClassification` (pipe-delimited hierarchy)
- `distribution` (phytogeographic domains, vegetation types, occurrence)
- `speciesprofile` (life form, habitat/substrate)
- `vernacularname` (common names with language)
- `reference` (bibliographic citations)

### Extensions (New Fields)
- **`structuredDescription`**: Detailed species descriptions
  - `morphology`: habit, height, stems, leaves, flowers, fruits, seeds
  - `ecology`: habitat, associates, altitude, soil, luminosity
  - `phenology`: flowering, fruiting, leaf shedding
  - `distribution`: detailed distribution with states, municipalities
  - `diagnosticCharacters`: key identification features
  - `uses`: economic, medicinal, ornamental, ecological
  - `conservationStatus`: IUCN category, criteria, threats

- **`processingMetadata`**: Extraction status tracking
  - `status`: completed|partial|failed
  - `extractedSections`: list of successfully parsed sections
  - `validationWarnings`: non-fatal issues
  - `extractionErrors`: error messages
  - `processingDuration`: time in seconds

## MongoDB Query Examples

### Query by Scientific Name
```javascript
db.monographs.find({ scientificName: "Handroanthus chrysotrichus" })
```

### Query by Family
```javascript
db.monographs.find({ family: "Bignoniaceae" })
```

### Get Total Species Count
```javascript
db.monographs.countDocuments({ taxonRank: "species" })
```

### Find Species in Specific Domain
```javascript
db.monographs.find({
  "distribution.phytogeographicDomains": "Mata Atlântica"
})
```

## Development

### Run Tests
```bash
# All tests
pytest

# Contract tests only
pytest -m contract

# Integration tests only
pytest -m integration

# With coverage report
pytest --cov=src --cov-report=html
```

### Code Quality
```bash
# Linting
ruff check src/ tests/

# Formatting
black src/ tests/

# Type checking (if using mypy)
mypy src/
```

### Project Structure
```
doclingtaxa/
├── src/
│   ├── models/              # Pydantic models (DwC schema)
│   ├── extractors/          # PDF processing logic
│   ├── storage/             # MongoDB persistence
│   ├── cli/                 # Command-line interface
│   └── lib/                 # Core library interface
├── tests/
│   ├── contract/            # Schema compliance tests
│   ├── integration/         # End-to-end tests
│   └── unit/                # Component tests
├── specs/                   # Design documentation
└── pyproject.toml          # Project configuration
```

## Contributing

1. Read the specification: `specs/main/spec.md`
2. Follow TDD: Write tests first (see `specs/main/tasks.md`)
3. Ensure DwC compliance: Validate against `specs/main/contracts/mongodb-schema-dwc-extended.json`
4. Run tests and linting before committing
5. Update documentation as needed

## License

[Add license information]

## References

- [Darwin Core Standard](https://dwc.tdwg.org)
- [Docling Library](https://github.com/docling-project/docling)
- [MongoDB Python Driver](https://pymongo.readthedocs.io)
- [Pydantic Documentation](https://docs.pydantic.dev)
