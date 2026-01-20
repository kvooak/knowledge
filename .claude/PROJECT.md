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
- **Input**: chunks/**/*.json
- **Output**: index/ (embeddings.npy, chunk_ids.json)
- **Contract**: Fully regenerable, NOT truth, search tool only

### scripts/synthesize.py
- **Purpose**: LLM-assisted knowledge synthesis (ONLY script with LLM)
- **Location**: /scripts/synthesize.py
- **Input**: chunks/**/*.json
- **Output**: synth/drafts/DRAFT_*.md
- **Contract**: Drafts only, refuses to overwrite curated files, requires human review

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

*Last updated: Added project-based organization (v2.0.0)*
