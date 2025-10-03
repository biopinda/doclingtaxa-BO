# Data Model Specification

**Feature**: PDF Monograph to Structured JSON Conversion
**Date**: 2025-10-02 (Updated)
**Schema Base**: Darwin Core (DwC) Standard - schema-dwc2json-taxa-mongoDBJSON.json

## Overview

This system extends the existing Darwin Core MongoDB schema to include structured species descriptions extracted from PDF monographs. The base schema follows DwC standard with additional fields for parsed morphological and ecological data.

**Architecture**:
1. **MongoDB Documents**: Store taxonomic data following DwC schema (flat structure, one document per taxon)
2. **Pydantic Models**: Validate data before MongoDB insertion (Python classes: DarwinCoreTaxon, StructuredDescription, etc.)
3. **Schema Extensions**: New fields (structuredDescription, processingMetadata) extend base DwC schema

## Section 1: MongoDB Document Schema (Darwin Core)

### 1.1 Base DwC Taxon Document (schema-dwc2json-taxa-mongoDBJSON.json)

**Core Taxonomic Fields** (Required):
| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | MongoDB unique identifier |
| `taxonID` | string | Unique taxon identifier |
| `scientificName` | string | Full scientific name with authorship |
| `canonicalName` | string | Scientific name without authorship |
| `scientificNameAuthorship` | string | Author citation |
| `taxonRank` | string | Taxonomic rank (species, genus, family, etc.) |
| `kingdom` | string | Kingdom classification |
| `phylum` | string | Phylum classification |
| `class` | string | Class classification (optional) |
| `order` | string | Order classification (optional) |
| `family` | string | Family classification |
| `genus` | string | Genus classification |
| `specificEpithet` | string | Species epithet |
| `infraspecificEpithet` | string | Subspecies/variety epithet (optional) |

**Nomenclatural Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `bibliographicCitation` | string | Full citation for taxon |
| `namePublishedIn` | string | Publication where name was published |
| `namePublishedInYear` | string | Year of publication |
| `nomenclaturalStatus` | string | Nomenclatural status |
| `taxonomicStatus` | string | Taxonomic status (accepted, synonym) |

**Hierarchical Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `higherClassification` | string | Pipe-delimited classification hierarchy |
| `parentNameUsage` | string | Parent taxon name |
| `parentNameUsageID` | string | Parent taxon ID |
| `flatScientificName` | string | Flattened name representation |

**Distribution Fields** (Object):
```json
{
  "distribution": {
    "occurrence": ["state1", "state2", null],  // Geographic occurrence
    "countryCode": ["BR", "AR"],               // ISO country codes
    "phytogeographicDomains": ["Amazônia", "Mata Atlântica"],
    "vegetationType": ["Floresta Ombrófila Densa", "Cerrado"],
    "origin": "native|introduced",
    "Endemism": "endemic|non-endemic"
  }
}
```

**Species Profile Fields** (Object or Array):
```json
{
  "speciesprofile": {
    "lifeForm": {
      "lifeForm": ["arvoreta", "arbusto"],     // Life forms
      "habitat": ["terrícola", "rupícola"]      // Substrate/habitat
    }
  }
}
```

**Vernacular Names** (Array):
```json
{
  "vernacularname": [
    {
      "vernacularName": "ipê-amarelo",
      "language": "pt",
      "locality": "Brasil"
    }
  ]
}
```

**References** (Array):
```json
{
  "reference": [
    {
      "bibliographicCitation": "Author, Year. Title...",
      "title": "Publication title",
      "creator": "Author name",
      "date": "2023",
      "identifier": "DOI or URL",
      "type": "article|book|chapter"
    }
  ]
}
```

**Synonyms/Other Names** (Array):
```json
{
  "othernames": [
    {
      "scientificName": "Synonym name",
      "taxonID": "synonym-id",
      "taxonomicStatus": "synonym|homonym"
    }
  ]
}
```

**Type Specimens** (Array):
```json
{
  "typesandspecimen": [
    {
      "typeStatus": "holotype|paratype",
      "catalogNumber": "Specimen number",
      "collectionCode": "Herbarium code",
      "locality": "Collection locality",
      "recordedBy": "Collector name",
      "source": "Institution"
    }
  ]
}
```

### 1.2 Schema Extensions for PDF Monographs

#### 1.2.1 structuredDescription (New Field)

**Purpose**: Store parsed, structured species descriptions extracted from PDF monographs

**Schema Extension**:
```json
{
  "structuredDescription": {
    "bsonType": "object",
    "properties": {
      "sourcePDF": {
        "bsonType": "object",
        "properties": {
          "filePath": {"bsonType": "string"},
          "fileHash": {"bsonType": "string"},
          "extractedDate": {"bsonType": "date"},
          "pageReferences": {"bsonType": "array", "items": {"bsonType": "int"}}
        },
        "required": ["filePath", "fileHash", "extractedDate"]
      },
      "morphology": {
        "bsonType": "object",
        "properties": {
          "generalDescription": {"bsonType": "string"},
          "habit": {"bsonType": "string"},
          "height": {"bsonType": "string"},
          "stems": {"bsonType": "string"},
          "leaves": {"bsonType": "string"},
          "inflorescence": {"bsonType": "string"},
          "flowers": {"bsonType": "string"},
          "fruits": {"bsonType": "string"},
          "seeds": {"bsonType": "string"},
          "rootSystem": {"bsonType": "string"}
        }
      },
      "ecology": {
        "bsonType": "object",
        "properties": {
          "habitat": {"bsonType": "string"},
          "associates": {"bsonType": "array", "items": {"bsonType": "string"}},
          "altitudeRange": {"bsonType": "string"},
          "soilType": {"bsonType": "string"},
          "luminosity": {"bsonType": "string"}
        }
      },
      "phenology": {
        "bsonType": "object",
        "properties": {
          "flowering": {"bsonType": "string"},
          "fruiting": {"bsonType": "string"},
          "leafShedding": {"bsonType": "string"}
        }
      },
      "distribution": {
        "bsonType": "object",
        "properties": {
          "detailedDescription": {"bsonType": "string"},
          "states": {"bsonType": "array", "items": {"bsonType": "string"}},
          "municipalities": {"bsonType": "array", "items": {"bsonType": "string"}},
          "coordinates": {
            "bsonType": "array",
            "items": {
              "bsonType": "object",
              "properties": {
                "latitude": {"bsonType": "double"},
                "longitude": {"bsonType": "double"},
                "locality": {"bsonType": "string"}
              }
            }
          }
        }
      },
      "diagnosticCharacters": {
        "bsonType": "array",
        "items": {"bsonType": "string"}
      },
      "uses": {
        "bsonType": "object",
        "properties": {
          "economic": {"bsonType": "string"},
          "medicinal": {"bsonType": "string"},
          "ornamental": {"bsonType": "string"},
          "ecological": {"bsonType": "string"}
        }
      },
      "conservationStatus": {
        "bsonType": "object",
        "properties": {
          "category": {"bsonType": "string"},
          "criteria": {"bsonType": "string"},
          "threats": {"bsonType": "array", "items": {"bsonType": "string"}}
        }
      },
      "rawText": {"bsonType": "string"}
    },
    "required": ["sourcePDF"]
  }
}
```

#### 1.2.2 processingMetadata (New Field)

**Purpose**: Track PDF extraction and processing status

**Schema Extension**:
```json
{
  "processingMetadata": {
    "bsonType": "object",
    "properties": {
      "status": {
        "enum": ["completed", "partial", "failed"]
      },
      "extractedSections": {
        "bsonType": "array",
        "items": {"bsonType": "string"}
      },
      "validationWarnings": {
        "bsonType": "array",
        "items": {"bsonType": "string"}
      },
      "extractionErrors": {
        "bsonType": "array",
        "items": {"bsonType": "string"}
      },
      "processingDuration": {"bsonType": "double"},
      "doclingVersion": {"bsonType": "string"}
    },
    "required": ["status"]
  }
}
```

### 1.3 Example Complete MongoDB Document

**Note**: This is a MongoDB document stored in the database. See Section 2 for corresponding Pydantic validation models.

```json
{
  "_id": ObjectId("..."),
  "taxonID": "flora-br-12345",
  "scientificName": "Handroanthus chrysotrichus (Mart. ex DC.) Mattos",
  "canonicalName": "Handroanthus chrysotrichus",
  "scientificNameAuthorship": "(Mart. ex DC.) Mattos",
  "taxonRank": "species",
  "kingdom": "Plantae",
  "phylum": "Tracheophyta",
  "class": "Magnoliopsida",
  "order": "Lamiales",
  "family": "Bignoniaceae",
  "genus": "Handroanthus",
  "specificEpithet": "chrysotrichus",
  "higherClassification": "Plantae|Tracheophyta|Magnoliopsida|Lamiales|Bignoniaceae|Handroanthus",
  "bibliographicCitation": "Mattos 1970. Loefgrenia 48: 1-2.",

  "distribution": {
    "occurrence": ["MG", "RJ", "SP", "PR", "SC", "RS"],
    "countryCode": ["BR"],
    "phytogeographicDomains": ["Mata Atlântica", "Cerrado"],
    "vegetationType": ["Floresta Ombrófila Densa", "Floresta Estacional Semidecidual"],
    "origin": "native",
    "Endemism": "endemic"
  },

  "speciesprofile": {
    "lifeForm": {
      "lifeForm": ["árvore"],
      "habitat": ["terrícola"]
    }
  },

  "vernacularname": [
    {"vernacularName": "ipê-amarelo", "language": "pt", "locality": "Brasil"},
    {"vernacularName": "ipê-tabaco", "language": "pt", "locality": "São Paulo"}
  ],

  "structuredDescription": {
    "sourcePDF": {
      "filePath": "H:/pdfs/bignoniaceae_2023.pdf",
      "fileHash": "5d41402abc4b2a76b9719d911017c592",
      "extractedDate": ISODate("2025-10-02T14:30:00Z"),
      "pageReferences": [45, 46, 47]
    },
    "morphology": {
      "generalDescription": "Árvore 8-25 m alt., tronco 30-60 cm diâm., casca fendida longitudinalmente.",
      "habit": "Árvore decídua",
      "height": "8-25 m",
      "stems": "Ramos cilíndricos, lenticelados, pubescentes quando jovens",
      "leaves": "Folhas compostas palmadas, 5-folioladas, folíolos elípticos, 5-12 cm compr.",
      "inflorescence": "Inflorescência em panícula terminal, multiflora",
      "flowers": "Flores amarelas, tubulares, 6-8 cm compr., cálice campanulado, pubescente",
      "fruits": "Cápsula cilíndrica, 15-35 cm compr., deiscente",
      "seeds": "Sementes aladas, 2-3 cm compr."
    },
    "ecology": {
      "habitat": "Floresta Estacional Semidecidual, preferencial em solos argilosos",
      "associates": ["Aspidosperma polyneuron", "Cariniana estrellensis"],
      "altitudeRange": "200-800 m",
      "soilType": "Argiloso, bem drenado",
      "luminosity": "Heliófita"
    },
    "phenology": {
      "flowering": "Agosto a Setembro (antes da folhação)",
      "fruiting": "Setembro a Novembro",
      "leafShedding": "Julho a Agosto"
    },
    "distribution": {
      "detailedDescription": "Mata Atlântica do sudeste e sul do Brasil, desde Minas Gerais até Rio Grande do Sul",
      "states": ["MG", "RJ", "SP", "PR", "SC", "RS"],
      "municipalities": ["São Paulo", "Campinas", "Curitiba", "Florianópolis"]
    },
    "diagnosticCharacters": [
      "Folhas 5-folioladas com folíolos elípticos",
      "Flores amarelas em inflorescência terminal",
      "Floração antes da folhação",
      "Cápsula cilíndrica longa (15-35 cm)"
    ],
    "uses": {
      "economic": "Madeira de alta qualidade para construção civil e mobiliário",
      "ornamental": "Muito utilizada em arborização urbana pela floração vistosa",
      "ecological": "Importante para fauna (néctar para abelhas e beija-flores)"
    }
  },

  "reference": [
    {
      "bibliographicCitation": "Gentry, A.H. 1992. Bignoniaceae - Part II (Tribe Tecomeae). Flora Neotropica Monograph 25(2): 1-370.",
      "title": "Bignoniaceae - Part II (Tribe Tecomeae)",
      "creator": "Gentry, A.H.",
      "date": "1992",
      "type": "monograph"
    }
  ],

  "processingMetadata": {
    "status": "completed",
    "extractedSections": ["morphology", "ecology", "phenology", "distribution", "uses"],
    "validationWarnings": [],
    "extractionErrors": [],
    "processingDuration": 12.3,
    "doclingVersion": "1.0.0"
  }
}
```

---

## Section 2: Pydantic Validation Models

**Purpose**: Validate taxonomic data BEFORE inserting into MongoDB. These Python classes ensure data conforms to DwC schema.

**Workflow**: PDF → Extraction → Pydantic Model Validation → MongoDB Insert

### 2.1 PDF Extraction → DwC Fields Mapping

| Extracted Data | Target DwC Field | Notes |
|----------------|------------------|-------|
| Scientific name | `scientificName`, `canonicalName` | Parse author from full name |
| Author citation | `scientificNameAuthorship` | Extract from name string |
| Family | `family` | From taxonomic hierarchy section |
| Genus | `genus` | From taxonomic hierarchy section |
| Common names | `vernacularname[]` | Array of objects with language |
| Life form (Forma de Vida) | `speciesprofile.lifeForm.lifeForm[]` | Map to existing array field |
| Substrate | `speciesprofile.lifeForm.habitat[]` | Add to habitat array |
| Phytogeographic domains | `distribution.phytogeographicDomains[]` | Direct mapping |
| Vegetation types | `distribution.vegetationType[]` | Direct mapping |
| Geographic distribution | `distribution.occurrence[]` | Parse states/regions |
| Morphological description | `structuredDescription.morphology.*` | NEW - Structured sections |
| Ecological notes | `structuredDescription.ecology.*` | NEW - Habitat details |
| Phenology | `structuredDescription.phenology.*` | NEW - Flowering/fruiting |
| Uses | `structuredDescription.uses.*` | NEW - Economic/medicinal |
| References | `reference[]` | Bibliography from PDF |

### 2.2 Pydantic Model Definitions (Implementation Reference)

**Implementation Files**:
- `src/models/dwc_taxon.py` - DarwinCoreTaxon, Distribution, SpeciesProfile, VernacularName, Reference, OtherName, TypeSpecimen
- `src/models/structured_description.py` - StructuredDescription, SourcePDF, Morphology, Ecology, Phenology, etc.
- `src/models/processing.py` - ProcessingMetadata

## Section 3: Validation Rules

### Required Fields (DwC Core)
1. `scientificName` - Must be non-empty
2. `taxonRank` - Must be valid rank (species, genus, family, etc.)
3. `family` - Required for species-level records
4. `genus` - Required for species-level records

### Required Fields (Structured Description)
1. `structuredDescription.sourcePDF.filePath` - Source PDF reference
2. `structuredDescription.sourcePDF.fileHash` - Duplicate detection
3. `processingMetadata.status` - Processing outcome

### Conditional Validations
1. If `taxonRank = "species"`:
   - `specificEpithet` required
   - `structuredDescription` should be populated
   - At least one section in `structuredDescription.morphology` or `structuredDescription.ecology`

2. If `distribution.occurrence` populated:
   - Should match `structuredDescription.distribution.states` if both present

### Data Quality Warnings
1. Missing `vernacularname` - Warn but allow
2. Empty `structuredDescription.morphology` - Warn (expected for species)
3. Missing `bibliographicCitation` - Warn
4. No `reference[]` entries - Warn

## Section 4: Exclusion Rules (From Spec)

1. **Family/Genus descriptions**:
   - Do NOT populate `structuredDescription` for `taxonRank != "species"`
   - Only create species-level structured descriptions

2. **Identification keys**:
   - Detect sections with keywords: "chave de identificação", "identification key", "dicotômica"
   - Exclude from all description fields
   - Log in `processingMetadata.extractedSections` as "identification_key_excluded"

## Section 5: MongoDB Indexes

### Existing Indexes (Preserve)
- `taxonID`: Unique index
- `scientificName`: Text index for search
- `family`, `genus`: Compound index for taxonomic queries

### New Indexes (Add)
- `structuredDescription.sourcePDF.fileHash`: Unique index (prevent duplicate PDF processing)
- `processingMetadata.status`: For filtering processing outcomes
- `structuredDescription.sourcePDF.extractedDate`: Descending (recent first)

## Section 6: Implementation Reference (Pydantic Models)

**Note**: Full Pydantic model code is implemented in tasks T018-T020. This section provides a simplified reference.

### Key Pydantic Models

**DarwinCoreTaxon** (Primary validation model):
- Validates all DwC core fields before MongoDB insert
- Includes extensions: structuredDescription, processingMetadata
- Handles field aliasing (_id ↔ id)
- Enforces type constraints (str, List[str], Optional fields)

**StructuredDescription** (PDF extraction validation):
- Validates sourcePDF required fields (filePath, fileHash, extractedDate)
- Validates optional morphology/ecology/phenology sections
- Ensures nested structure conforms to schema

**ProcessingMetadata** (Extraction tracking):
- Validates status enum: "completed" | "partial" | "failed"
- Tracks extraction sections, warnings, errors

**Implementation Details**: See tasks T018-T020 for complete Pydantic model definitions with validators and serializers.

## Next Steps

1. Update `contracts/mongodb-schema.json` with new fields
2. Create migration script for existing records (if any)
3. Update contract tests to validate DwC compliance
4. Map Docling extraction to DwC + structuredDescription fields
