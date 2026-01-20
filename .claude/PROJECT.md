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
├── topics/                # Topic-based knowledge (AUTHORITATIVE)
│   ├── README.md          # Topic system documentation
│   ├── _template.md       # Topic template
│   ├── drafts/            # Topic drafts (NOT authoritative)
│   └── <topic_name>.md    # Curated topics (AUTHORITATIVE)
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
- **Version**: 2.0.0
- **Input**: chunks/**/*.json (recursive)
- **Output**:
  - With `--full`: synth/<type>.md (full document with LLM-generated warning)
  - Without `--full`: synth/drafts/DRAFT_*.md (draft for review)
- **Contract**: Requires human review, includes LLM-generated warnings
- **Updates**:
  - v1.1.0: Added recursive directory support via rglob()
  - v2.0.0: Added --full flag for direct output to curated files
- **Limit**: Dynamically calculated from chunking metadata to process all chunks

### scripts/clean.py
- **Purpose**: Safe cleanup of generated files
- **Location**: /scripts/clean.py
- **Version**: 1.0.0
- **Removes**: extracted/, chunks/, index/ contents
- **Preserves**: sources/, synth/*.md (curated knowledge), synth/procedures/ (non-draft)
- **Options**: --all (also clean drafts), --verbose
- **Contract**: Never deletes source PDFs or curated knowledge

### scripts/topic_lookup.py
- **Purpose**: Look up topics in knowledge base
- **Location**: /scripts/topic_lookup.py
- **Version**: 1.0.0
- **Input**: Topic name (string)
- **Output**: Curated topic file OR menu of options
- **Contract**: NEVER auto-generates topics, ONLY returns curated files as authoritative
- **Guarantees**: No inference, no gap filling, explicit options when topic not found
- **Prohibitions**: Do NOT synthesize on demand, do NOT treat search as authoritative

### scripts/topic_draft.py
- **Purpose**: Generate topic draft from curated knowledge
- **Location**: /scripts/topic_draft.py
- **Version**: 1.0.0
- **Input**: Topic name (string)
- **Output**: Draft in topics/drafts/ (NOT authoritative)
- **Sources**: synth/glossary.md, synth/rules.md, synth/invariants.md, synth/procedures/
- **Contract**: Uses ONLY curated knowledge, raw chunks for citations only
- **Guarantees**: No LLM synthesis, no inference, clearly labeled as DRAFT
- **Prohibitions**: NEVER writes to topics/ (only topics/drafts/)

### scripts/search_chunks.py
- **Purpose**: Search raw chunks (non-authoritative)
- **Location**: /scripts/search_chunks.py
- **Version**: 1.0.0
- **Input**: Search query (string)
- **Output**: Matching chunks with citations
- **Contract**: Clearly labeled as NON-AUTHORITATIVE, shows raw excerpts only
- **Use Cases**: Finding source references, verifying citations, exploring undocumented concepts
- **Warning**: Results are NOT authoritative knowledge

### run.py
- **Purpose**: Cross-platform build script (Python-based alternative to Makefile)
- **Location**: /run.py
- **Version**: 1.0.0
- **Platform**: Windows, Linux, Mac (Python 3.10+)
- **Targets**: All Makefile targets (extract, chunk, embed, ingest, synth, synth-test, clean, status, etc.)
- **Usage**: `python run.py <target> [options]`
- **Contract**: Provides same functionality as Makefile, works on all platforms

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

## Build System (Cross-Platform)

### Python Build Script (Windows & Linux/Mac)
For Windows or when `make` is not available, use `run.py`:

```bash
# Pipeline execution
python run.py extract
python run.py chunk
python run.py embed
python run.py ingest              # Full pipeline

# Synthesis (outputs to synth/<type>.md as full document)
python run.py synth --type glossary --topic "flight systems"

# Synthesis test (outputs to drafts/ with limit=50)
python run.py synth-test --type glossary --topic "test topic"

# Utilities
python run.py clean
python run.py clean-all
python run.py status
python run.py get-chunk-count
python run.py help
```

### Makefile Targets (Linux/Mac)
- `make extract` - Extract text from PDFs in sources/
- `make chunk` - Chunk extracted text into semantic units
- `make embed` - Generate embeddings index
- `make ingest` - Run full pipeline: extract → chunk → embed

### Synthesis (LLM Required)
- `make synth TYPE=<type> TOPIC='<topic>'` - Generate FULL document using ALL chunks (outputs to synth/<type>.md)
- `make synth-test TYPE=<type> TOPIC='<topic>'` - Generate draft with limit=50 (outputs to drafts/)
- Supported types: glossary, rules, invariants, procedures, contradictions, questions
- **Note**: `synth` now outputs "full" documents directly to curated files with LLM-generated warning

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

## Topic-Based Knowledge System

### Overview

The topic system provides **document-grounded, human-reviewed** knowledge organized by concept. Topics are curated files, NOT on-demand syntheses.

**Core Principle**: If a topic doesn't exist as a file, it is not authoritative.

### Directory Structure

```
topics/
├── README.md              # Topic system documentation
├── _template.md           # Template for all topics
├── drafts/                # Draft topics (NOT authoritative)
│   └── DRAFT_*.md         # Generated drafts awaiting review
└── <topic_name>.md        # Curated topics (AUTHORITATIVE)
```

**CRITICAL**: Claude Code NEVER writes to `topics/` directly. Only to `topics/drafts/`.

### Topic Lookup Workflow

1. **User requests topic**: `python scripts/topic_lookup.py "HSI pointers"`

2. **If curated topic exists**:
   - Displays authoritative topic file from `topics/<name>.md`
   - User can trust as verified knowledge

3. **If topic does NOT exist**:
   - Does NOT auto-generate
   - Offers explicit options:
     - Create draft topic
     - Show glossary references (non-authoritative)
     - Show related curated topics
     - Search raw chunks (non-authoritative)

### Topic Draft Generation

**Command**: `python scripts/topic_draft.py "HSI pointers" --verbose`

**Sources (priority order)**:
1. `synth/glossary.md` - for definitions
2. `synth/rules.md` - for rules
3. `synth/invariants.md` - for constraints
4. `synth/procedures/*.md` - for procedures
5. `chunks/**/*.json` - for citations ONLY

**Output**: `topics/drafts/DRAFT_<topic>_<timestamp>.md`

**Critical**: Draft is clearly labeled as NON-AUTHORITATIVE and requires human review.

### Topic Structure

Every topic follows `topics/_template.md`:

- **Definition**: Primary definition with citation, synonyms
- **Related Terms**: Cross-references with relationships
- **Sources**: Primary source documents, coverage assessment
- **Rules**: IF/WHEN → THEN rules (explicit from source only)
- **Behavior**: Normal operation, states/modes
- **Limitations**: Explicit constraints, boundary conditions
- **Procedures**: Step-by-step procedures with preconditions
- **Edge Cases**: Documented edge cases only
- **Open Questions**: Gaps in documentation (NOT assumptions)
- **Verification Status**: Review checklist
- **Metadata**: Source documents, generation info

### Curation Process (Human-Only)

1. Generate draft: `python scripts/topic_draft.py "<topic>"`
2. Review draft thoroughly:
   - [ ] All citations verified against source PDFs
   - [ ] All "NOT SPECIFIED" claims verified
   - [ ] No inferences or assumptions
   - [ ] Related terms cross-referenced
   - [ ] Open questions documented
3. Fill in gaps from source documents
4. Promote to curated: `mv topics/drafts/DRAFT_<topic>_*.md topics/<topic>.md`
5. Update status to CURATED, set reviewer name
6. Commit with review notes

### Truth Hierarchy

1. **Source PDFs** - Ultimate truth
2. **Curated topics/** - Authoritative, human-reviewed
3. **Curated synth/*.md** - Authoritative, human-reviewed
4. **Drafts** - NOT authoritative, require review
5. **Index** - Regenerable tool, NOT truth
6. **Raw chunks** - Mechanical extraction, NOT truth

### Absolute Prohibitions

- ❌ Auto-generate topics on demand
- ❌ Write to `topics/` directory (only `topics/drafts/`)
- ❌ Treat search results as authoritative
- ❌ Infer undocumented behavior
- ❌ Auto-promote drafts to curated status
- ❌ Claim completeness without curated topic file

### Commands Reference

```bash
# Look up topic
python scripts/topic_lookup.py "<topic name>"
python scripts/topic_lookup.py --list-topics "dummy"

# Generate draft
python scripts/topic_draft.py "<topic name>" --verbose

# Search raw chunks (non-authoritative)
python scripts/search_chunks.py "<query>" --limit 20
```

See `topics/README.md` for complete documentation.

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

*Last updated: 2026-01-21*

**Recent Changes:**
- **Topic-Based Knowledge System** (v1.0.0):
  - Created `topics/` directory structure with curated topics and drafts
  - Implemented `topic_lookup.py` - authoritative topic lookup with explicit options
  - Implemented `topic_draft.py` - draft generation from curated knowledge only
  - Implemented `search_chunks.py` - raw chunk search (non-authoritative)
  - Created topic template (`_template.md`) with mandatory structure
  - Documented complete topic workflow with curation process
  - Enforced human review requirement before topic curation
  - Prohibited auto-generation and auto-promotion of topics
- Created run.py v1.0.0 - Cross-platform Python build script for Windows/Linux/Mac compatibility
- Updated synthesize.py to v2.0.0 with --full flag for direct output to curated files
- Modified `make synth` to output full documents (synth/<type>.md) instead of drafts
- Added comprehensive test suite (124 tests: 75 compliance + 49 unit)
- Created scripts/clean.py for safe cleanup of generated files
- Updated embed_chunks.py and synthesize.py to v1.1.0 (recursive directory support)
- Enhanced Makefile with dynamic chunk limit calculation for synthesis
- Added synth-test target for quick testing with limit=50
- Documented all metadata structures (extraction, chunking, index)
- Documented all Makefile targets and testing procedures
- Created universal rules sync mechanism (sync-rules.py) for automatic rule propagation
