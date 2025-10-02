# Schema Update: Darwin Core Compliance

**Date**: 2025-10-02
**Status**: Design Updated

## Summary

The implementation plan has been updated to use the existing **Darwin Core (DwC) standard schema** (`schema-dwc2json-taxa-mongoDBJSON.json`) as the base MongoDB structure, with extensions for structured species descriptions extracted from PDF monographs.

## Key Changes

### 1. Base Schema Adoption

**Before**: Custom hierarchical taxonomy schema (Kingdom → Species nested structure)

**After**: Darwin Core (DwC) standard schema with flat taxonomic fields:
- Core taxonomic fields: `scientificName`, `family`, `genus`, `specificEpithet`, etc.
- Nomenclatural fields: `scientificNameAuthorship`, `bibliographicCitation`, `namePublishedIn`
- Hierarchical reference: `higherClassification`, `parentNameUsage`, `parentNameUsageID`
- Existing extensions: `distribution`, `speciesprofile`, `vernacularname`, `reference`, `typesandspecimen`

### 2. New Schema Extensions

#### 2.1. structuredDescription (NEW)

Stores parsed species descriptions from PDF monographs:

```json
{
  "structuredDescription": {
    "sourcePDF": {
      "filePath": "path/to/pdf",
      "fileHash": "md5_hash",
      "extractedDate": ISODate(),
      "pageReferences": [45, 46, 47]
    },
    "morphology": {
      "generalDescription": "...",
      "habit": "...",
      "height": "...",
      "stems": "...",
      "leaves": "...",
      "inflorescence": "...",
      "flowers": "...",
      "fruits": "...",
      "seeds": "...",
      "rootSystem": "..."
    },
    "ecology": {
      "habitat": "...",
      "associates": ["species1", "species2"],
      "altitudeRange": "...",
      "soilType": "...",
      "luminosity": "..."
    },
    "phenology": {
      "flowering": "...",
      "fruiting": "...",
      "leafShedding": "..."
    },
    "distribution": {
      "detailedDescription": "...",
      "states": ["MG", "RJ", "SP"],
      "municipalities": ["São Paulo", "Rio de Janeiro"],
      "coordinates": [
        {"latitude": -23.5, "longitude": -46.6, "locality": "São Paulo"}
      ]
    },
    "diagnosticCharacters": ["character1", "character2"],
    "uses": {
      "economic": "...",
      "medicinal": "...",
      "ornamental": "...",
      "ecological": "..."
    },
    "conservationStatus": {
      "category": "EN",
      "criteria": "B1ab(iii)",
      "threats": ["habitat loss", "deforestation"]
    },
    "rawText": "Full extracted text from PDF"
  }
}
```

#### 2.2. processingMetadata (NEW)

Tracks PDF extraction status:

```json
{
  "processingMetadata": {
    "status": "completed|partial|failed",
    "extractedSections": ["morphology", "ecology", "phenology"],
    "validationWarnings": ["Missing substrato field"],
    "extractionErrors": [],
    "processingDuration": 12.3,
    "doclingVersion": "1.0.0"
  }
}
```

### 3. Data Mapping Strategy

| PDF Extracted Data | Target DwC Field | Notes |
|-------------------|------------------|-------|
| Scientific name | `scientificName`, `canonicalName` | Parse author separately |
| Author citation | `scientificNameAuthorship` | Extract from full name |
| Family | `family` | DwC core field |
| Genus | `genus` | DwC core field |
| Common names | `vernacularname[]` | Existing DwC array |
| **Forma de Vida** | `speciesprofile.lifeForm.lifeForm[]` | Map to existing field |
| **Substrato** | `speciesprofile.lifeForm.habitat[]` | Map to existing field |
| **Domínios Fitogeográficos** | `distribution.phytogeographicDomains[]` | Existing DwC field |
| **Tipos de Vegetação** | `distribution.vegetationType[]` | Existing DwC field |
| **Distribuição Geográfica** | `distribution.occurrence[]` | Parse to state codes |
| **Morphological description** | `structuredDescription.morphology.*` | **NEW extension** |
| **Ecological notes** | `structuredDescription.ecology.*` | **NEW extension** |
| **Phenology** | `structuredDescription.phenology.*` | **NEW extension** |
| **Uses** | `structuredDescription.uses.*` | **NEW extension** |
| References | `reference[]` | Existing DwC array |

### 4. Updated File Structure

```
specs/main/
├── spec.md (updated with DwC clarifications)
├── plan.md (updated with DwC architecture)
├── data-model.md (rewritten for DwC + extensions)
├── research.md (unchanged)
├── quickstart.md (unchanged)
├── contracts/
│   ├── mongodb-schema-dwc-extended.json (NEW - extended DwC schema)
│   └── library-interface.md (unchanged)
└── schema-dwc2json-taxa-mongoDBJSON.json (reference - base DwC schema)
```

### 5. Code Structure Changes

**Before**:
```
src/models/
├── taxonomy.py       # Custom nested TaxonNode
└── processing.py
```

**After**:
```
src/models/
├── dwc_taxon.py                # DarwinCoreTaxon (DwC compliant)
├── structured_description.py   # StructuredDescription, Morphology, Ecology
└── processing.py               # ProcessingMetadata
```

**Before**:
```
src/extractors/
├── taxonomy_extractor.py  # Hierarchical extraction
```

**After**:
```
src/extractors/
├── taxonomic_mapper.py       # Map to DwC fields
├── description_extractor.py  # Extract structuredDescription
```

## Implementation Impact

### What Stays the Same
- ✅ Docling for PDF extraction
- ✅ MongoDB as database
- ✅ Pydantic for validation
- ✅ Species-level filtering (exclude Family/Genus descriptions)
- ✅ Identification key exclusion
- ✅ CLI interface and progress reporting
- ✅ Integration test scenarios

### What Changes
- 🔄 **Data model**: Custom nested → DwC flat + extensions
- 🔄 **Validation**: Custom rules → DwC compliance + extensions
- 🔄 **MongoDB schema**: Custom → DwC standard + structuredDescription
- 🔄 **Field mapping**: Direct extraction → Map to DwC standard fields
- 🔄 **Pydantic models**: TaxonNode → DarwinCoreTaxon

### New Requirements
- ✨ **DwC compliance validation**: Ensure all required DwC fields populated
- ✨ **Field mapping logic**: PDF text → DwC fields + structuredDescription
- ✨ **Dual storage**: DwC taxonomic data + structured descriptions
- ✨ **Schema validation**: Test Pydantic models against mongodb-schema-dwc-extended.json

## Migration Notes

### For Existing Data (if any)
If the database already contains documents using the old schema:
1. Create migration script to transform custom hierarchy → DwC flat structure
2. Map old fields to new DwC fields
3. Preserve structured descriptions in new `structuredDescription` field
4. Add `processingMetadata` for tracking

### For New Implementation
Start directly with DwC schema:
1. Use `mongodb-schema-dwc-extended.json` for MongoDB collection validation
2. Implement Pydantic models matching DwC structure
3. Extract PDF → map to DwC fields + structuredDescription
4. Validate against both DwC core and extensions

## Testing Strategy

### Contract Tests (Updated)
1. **DwC Schema Compliance**: Validate Pydantic models serialize to valid DwC JSON
2. **MongoDB Schema Validation**: Ensure documents match mongodb-schema-dwc-extended.json
3. **Field Mapping**: Test PDF extraction → DwC field mapping accuracy
4. **Extension Validation**: Verify structuredDescription structure

### Integration Tests (Unchanged)
- Single PDF processing
- Batch directory processing
- Error handling (malformed PDFs)
- Species filtering (exclude Family/Genus)
- MongoDB querying

## References

- **Base Schema**: `specs/main/schema-dwc2json-taxa-mongoDBJSON.json`
- **Extended Schema**: `specs/main/contracts/mongodb-schema-dwc-extended.json`
- **Data Model**: `specs/main/data-model.md`
- **Darwin Core Standard**: https://dwc.tdwg.org/terms/

## Next Steps

1. ✅ **Updated Specifications** (completed)
2. ⏭️ **Run `/tasks`**: Generate implementation tasks based on DwC schema
3. 🔨 **Implement DwC Models**: Create Pydantic models for DarwinCoreTaxon
4. 🔨 **Field Mapping**: Implement PDF → DwC field extraction logic
5. 🧪 **DwC Validation Tests**: Ensure schema compliance
6. 📊 **Test with Sample PDFs**: Validate extraction and mapping accuracy
