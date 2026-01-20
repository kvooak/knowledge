# Project: knowledge

## Overview

> A durable, auditable knowledge system for ingesting large PDFs (thousands of pages) into structured, human-reviewed knowledge. The system is designed with the understanding that LLMs are stateless and have no memory - any persistence must be created externally with mandatory human review.

## Tech Stack

- **Language**: Python 3.10+
- **PDF Extraction**: PyMuPDF (fitz)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM API**: Anthropic Claude (synthesis only)
- **Testing**: pytest
- **Build**: Make

## Architecture

> Clean separation between mechanical processing (no LLM) and synthesis (LLM with human review). Truth lives in human-curated synth/*.md files, never in generated indices or automated outputs.

### Directory Structure

```
knowledge/
├── sources/               # Input PDFs (organized by project)
│   ├── ProjectA/          # Project = first-level subfolder
│   │   ├── manual.pdf
│   │   └── subfolder/     # Nested folders supported
│   │       └── guide.pdf
│   └── ProjectB/
│       └── spec.pdf
├── extracted/             # Mechanical text extraction (mirrors sources/)
│   ├── ProjectA/
│   │   ├── manual/
│   │   │   ├── page_0001.md
│   │   │   └── _extraction_metadata.json
│   │   └── subfolder/guide/
│   └── ProjectB/
├── chunks/                # Semantic chunks (mirrors extracted/)
│   ├── ProjectA/
│   │   └── manual/
│   │       ├── manual_chunk_0001.json
│   │       └── _chunking_metadata.json
│   └── ProjectB/
├── synth/                 # Synthesized knowledge
│   ├── drafts/            # LLM proposals (NOT truth)
│   ├── procedures/        # Curated procedures
│   ├── glossary.md        # Curated definitions
│   ├── rules.md           # Curated rules (IF/WHEN → THEN)
│   ├── invariants.md      # Curated invariants (must always be true)
│   ├── contradictions.md  # Identified conflicts
│   └── open_questions.md  # Unanswered questions
├── index/                 # Search embeddings (regenerable, NOT truth)
├── scripts/               # Processing scripts
├── prompts/               # LLM prompt contracts
├── tests/                 # Compliance tests
├── Makefile               # Build automation
└── README.md              # Documentation
```

### Project Organization

- **Project** = direct subfolder under `sources/`
- Project name is tracked in all metadata files
- Nested subfolders within projects are supported
- Directory structure is mirrored from sources/ → extracted/ → chunks/

## Key Components

### scripts/extract_pdf.py
- **Purpose**: Mechanical PDF text extraction (NO LLM)
- **Location**: /scripts/extract_pdf.py
- **Version**: 2.0.0
- **Input**: sources/<project>/**/*.pdf (recursive)
- **Output**: extracted/<project>/<relative_path>/<doc_name>/page_NNNN.md
- **Contract**: One file per page, deterministic, preserves headings, tracks project name

### scripts/chunk_text.py
- **Purpose**: Split text into semantic chunks (NO LLM)
- **Location**: /scripts/chunk_text.py
- **Version**: 2.0.0
- **Input**: extracted/<project>/<relative_path>/<doc_name>/*.md
- **Output**: chunks/<project>/<relative_path>/<doc_name>/*.json
- **Contract**: 300-800 tokens per chunk, includes source/page citations, includes project name

### scripts/embed_chunks.py
- **Purpose**: Generate search index (NO LLM)
- **Location**: /scripts/embed_chunks.py
- **Version**: 1.1.0
- **Input**: chunks/**/*.json (recursive)
- **Output**: index/ (embeddings.npy, chunk_ids.json, metadata.json, _INDEX_IS_NOT_TRUTH)
- **Contract**: Fully regenerable, NOT truth, search tool only
- **Updates**: v1.1.0 added recursive directory support via rglob()

### scripts/synthesize.py
- **Purpose**: LLM-assisted knowledge synthesis (ONLY script with LLM)
- **Location**: /scripts/synthesize.py
- **Version**: 1.1.0
- **Input**: chunks/**/*.json (recursive)
- **Output**: synth/drafts/DRAFT_*.md
- **Contract**: Drafts only, refuses to overwrite curated files, requires human review
- **Updates**: v1.1.0 added recursive directory support via rglob()
- **Limit**: Dynamically calculated from chunking metadata to process all chunks

### scripts/clean.py
- **Purpose**: Safe cleanup of generated files
- **Location**: /scripts/clean.py
- **Version**: 1.0.0
- **Removes**: extracted/, chunks/, index/ contents
- **Preserves**: sources/, synth/*.md (curated knowledge), synth/procedures/ (non-draft)
- **Options**: --all (also clean drafts), --verbose
- **Contract**: Never deletes source PDFs or curated knowledge

## Data Models

### Chunk (JSON)
```
id: string - Unique identifier (doc_name_chunk_NNNN)
project_name: string|null - Project name (first subfolder under sources/)
source_document: string - Original PDF name
relative_path: string|null - Path within project (e.g., "subfolder" or ".")
section: string|null - Heading text if detected
page_start: int - First page number
page_end: int - Last page number
raw_text: string - Actual content
token_count_estimate: int - Estimated tokens (300-800)
chunk_index: int - Position in document
total_chunks: int - Total chunks in document
created_at: string - ISO timestamp
```

### Extraction Metadata (_extraction_metadata.json)
```
source_file: string - Full path to original PDF
source_hash: string - SHA-256 hash for reproducibility
project_name: string|null - Project name
relative_path: string|null - Path within project
document_name: string - PDF stem name
extraction_time: string - ISO timestamp
extractor: string - Script name
extractor_version: string - Version (e.g., "2.0.0")
pages_extracted: int - Total pages
output_directory: string - Full output path
```

### Chunking Metadata (_chunking_metadata.json)
```
source_document: string - Document name
project_name: string|null - Project name
relative_path: string|null - Path within project
input_directory: string - Path to extracted pages
output_directory: string - Path to chunk output
processing_time: string - ISO timestamp
processor: string - Script name ("chunk_text.py")
processor_version: string - Version (e.g., "2.0.0")
pages_processed: int - Total pages chunked
chunks_created: int - Total chunks created
token_range: object - {min: int, max: int} token counts
```

### Index Metadata (index/metadata.json)
```
created_at: string - ISO timestamp
generator: string - "embed_chunks.py"
generator_version: string - Version
model: string - Embedding model name (e.g., "all-MiniLM-L6-v2")
chunk_count: int - Total chunks indexed
embedding_dimension: int - Vector dimension (e.g., 384)
is_truth: boolean - Always false (explicit)
regenerable: boolean - Always true
warning: string - Reminder that index is search tool only
```

## Makefile Targets

### Pipeline Execution
- `make extract` - Extract text from PDFs in sources/
- `make chunk` - Chunk extracted text into semantic units
- `make embed` - Generate embeddings index
- `make ingest` - Run full pipeline: extract → chunk → embed

### Synthesis (LLM Required)
- `make synth TYPE=<type> TOPIC='<topic>'` - Generate draft using ALL chunks
- `make synth-test TYPE=<type> TOPIC='<topic>'` - Generate draft with limit=50 (for testing)
- Supported types: glossary, rules, invariants, procedures, contradictions, questions

### Utilities
- `make clean` - Delete all generated content (preserves synth/)
- `make clean-index` - Delete regenerable index only
- `make clean-all` - Delete all including drafts (keeps curated files)
- `make status` - Show current pipeline state
- `make get-chunk-count` - Display total chunk count from metadata

## Testing

### Test Suite (124 tests total)
- **Compliance Tests** (75 tests): tests/test_compliance.py
  - Directory structure validation
  - File naming conventions
  - Contract enforcement (LLM isolation, deterministic output)
  - Protected file safety
  - Citation requirements
  - Prompt contract validation

- **Unit Tests** (49 tests):
  - tests/test_clean.py (9 tests) - Clean script functionality
  - tests/test_extract_pdf.py (10 tests) - PDF extraction
  - tests/test_chunk_text.py (11 tests) - Text chunking
  - tests/test_embed_chunks.py (12 tests) - Embeddings generation
  - tests/test_synthesize.py (11 tests) - LLM synthesis

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_compliance.py -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html
```

## Environment Variables

```
ANTHROPIC_API_KEY=Required for synthesis only
```

## Conventions

- LLM usage ONLY in synthesize.py
- All other scripts are mechanical and deterministic
- Drafts prefixed with DRAFT_ are non-authoritative
- Curated files in synth/ require human review
- Index is regenerable and NOT truth
- Every synthesized statement must cite source

## Key Dependencies

- `pymupdf`: PDF text extraction
- `sentence-transformers`: Embedding generation
- `numpy`: Array operations for embeddings
- `anthropic`: LLM API for synthesis
- `pytest`: Compliance testing

---

*Last updated: 2026-01-20*
- Added comprehensive test suite (124 tests: 75 compliance + 49 unit)
- Created scripts/clean.py for safe cleanup of generated files
- Updated embed_chunks.py and synthesize.py to v1.1.0 (recursive directory support)
- Enhanced Makefile with dynamic chunk limit calculation for synthesis
- Added synth-test target for quick testing with limit=50
- Documented all metadata structures (extraction, chunking, index)
- Documented all Makefile targets and testing procedures
