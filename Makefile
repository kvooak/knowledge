# Knowledge System Makefile
#
# Targets:
#   extract  - Extract text from PDFs (mechanical, no LLM)
#   chunk    - Chunk extracted text into semantic units (no LLM)
#   embed    - Generate embeddings index (regenerable, not truth)
#   synth    - Generate synthesis drafts using LLM (requires human review)
#   ingest   - Full pipeline: extract → chunk → embed
#
# IMPORTANT:
#   - synth/ is NEVER touched except via 'make synth'
#   - index/ can be regenerated at any time
#   - Truth lives in synth/*.md (curated files)
#

.PHONY: all extract chunk embed synth ingest clean clean-index help

# Default Python interpreter
PYTHON := python3

# Directories
SOURCES_DIR := sources
EXTRACTED_DIR := extracted
CHUNKS_DIR := chunks
INDEX_DIR := index
SYNTH_DIR := synth

# Scripts
EXTRACT_SCRIPT := scripts/extract_pdf.py
CHUNK_SCRIPT := scripts/chunk_text.py
EMBED_SCRIPT := scripts/embed_chunks.py
SYNTH_SCRIPT := scripts/synthesize.py

# Marker files for dependency tracking
EXTRACT_MARKER := $(EXTRACTED_DIR)/.extracted
CHUNK_MARKER := $(CHUNKS_DIR)/.chunked
EMBED_MARKER := $(INDEX_DIR)/.embedded

# Find all source PDFs
PDFS := $(wildcard $(SOURCES_DIR)/*.pdf) $(wildcard $(SOURCES_DIR)/**/*.pdf)

# ============================================================================
# Main Targets
# ============================================================================

all: help

help:
	@echo "Knowledge System - Make Targets"
	@echo "================================"
	@echo ""
	@echo "Pipeline targets:"
	@echo "  make extract   - Extract text from PDFs in sources/"
	@echo "  make chunk     - Chunk extracted text into semantic units"
	@echo "  make embed     - Generate embeddings index"
	@echo "  make ingest    - Run full pipeline: extract → chunk → embed"
	@echo ""
	@echo "Synthesis (LLM required):"
	@echo "  make synth TYPE=glossary TOPIC='topic name'  - Generate draft"
	@echo "  Supported types: glossary, rules, invariants, procedures,"
	@echo "                   contradictions, questions"
	@echo ""
	@echo "Utility targets:"
	@echo "  make clean         - Delete all generated content (except synth/)"
	@echo "  make clean-index   - Delete regenerable index only (safe)"
	@echo "  make clean-all     - Delete all including drafts (keeps curated files)"
	@echo "  make status        - Show current state"
	@echo ""
	@echo "IMPORTANT:"
	@echo "  - synth/ contains curated knowledge (NEVER auto-deleted)"
	@echo "  - index/ can be safely regenerated"
	@echo "  - Synthesis drafts require human review"

# ============================================================================
# Pipeline: extract → chunk → embed
# ============================================================================

# Extract: PDF → Markdown (one file per page)
extract: $(EXTRACT_MARKER)

$(EXTRACT_MARKER): $(PDFS) $(EXTRACT_SCRIPT)
	@echo "=========================================="
	@echo "EXTRACTING: PDFs → Markdown"
	@echo "=========================================="
	@if [ -z "$(PDFS)" ]; then \
		echo "No PDF files found in $(SOURCES_DIR)/"; \
		echo "Add PDFs to $(SOURCES_DIR)/ and run again."; \
		exit 0; \
	fi
	$(PYTHON) $(EXTRACT_SCRIPT) --verbose
	@touch $(EXTRACT_MARKER)
	@echo "Extraction complete."

# Chunk: Markdown → JSON chunks
chunk: $(CHUNK_MARKER)

$(CHUNK_MARKER): $(EXTRACT_MARKER) $(CHUNK_SCRIPT)
	@echo "=========================================="
	@echo "CHUNKING: Markdown → JSON"
	@echo "=========================================="
	$(PYTHON) $(CHUNK_SCRIPT) --verbose
	@touch $(CHUNK_MARKER)
	@echo "Chunking complete."

# Embed: JSON chunks → Vector index
embed: $(EMBED_MARKER)

$(EMBED_MARKER): $(CHUNK_MARKER) $(EMBED_SCRIPT)
	@echo "=========================================="
	@echo "EMBEDDING: Chunks → Index"
	@echo "=========================================="
	@echo "NOTE: Index is NOT truth. It can be regenerated."
	$(PYTHON) $(EMBED_SCRIPT) --verbose --force
	@touch $(EMBED_MARKER)
	@echo "Embedding complete."

# Full ingestion pipeline
ingest: extract chunk embed
	@echo ""
	@echo "=========================================="
	@echo "INGESTION COMPLETE"
	@echo "=========================================="
	@echo "- Extracted: $(EXTRACTED_DIR)/"
	@echo "- Chunks:    $(CHUNKS_DIR)/"
	@echo "- Index:     $(INDEX_DIR)/"
	@echo ""
	@echo "Next: Run 'make synth' to generate drafts for review."

# ============================================================================
# Synthesis (LLM - requires human review)
# ============================================================================

# Synth requires explicit TYPE and TOPIC
synth:
	@if [ -z "$(TYPE)" ]; then \
		echo "ERROR: TYPE is required"; \
		echo "Usage: make synth TYPE=glossary TOPIC='your topic'"; \
		echo "Types: glossary, rules, invariants, procedures, contradictions, questions"; \
		exit 1; \
	fi
	@if [ -z "$(TOPIC)" ]; then \
		echo "ERROR: TOPIC is required"; \
		echo "Usage: make synth TYPE=$(TYPE) TOPIC='your topic'"; \
		exit 1; \
	fi
	@echo "=========================================="
	@echo "SYNTHESIS: Generating $(TYPE) draft"
	@echo "=========================================="
	@echo "WARNING: This uses an LLM. Output requires human review."
	@echo ""
	$(PYTHON) $(SYNTH_SCRIPT) $(TYPE) --topic "$(TOPIC)" --verbose

# ============================================================================
# Utility Targets
# ============================================================================

# Status: Show current state
status:
	@echo "Knowledge System Status"
	@echo "======================="
	@echo ""
	@echo "Sources ($(SOURCES_DIR)/):"
	@find $(SOURCES_DIR) -name "*.pdf" 2>/dev/null | wc -l | xargs echo "  PDFs:"
	@echo ""
	@echo "Extracted ($(EXTRACTED_DIR)/):"
	@if [ -d "$(EXTRACTED_DIR)" ]; then \
		find $(EXTRACTED_DIR) -name "*.md" 2>/dev/null | wc -l | xargs echo "  Pages:"; \
	else echo "  Not yet extracted"; fi
	@echo ""
	@echo "Chunks ($(CHUNKS_DIR)/):"
	@if [ -d "$(CHUNKS_DIR)" ]; then \
		find $(CHUNKS_DIR) -name "*.json" ! -name "_*" 2>/dev/null | wc -l | xargs echo "  Chunks:"; \
	else echo "  Not yet chunked"; fi
	@echo ""
	@echo "Index ($(INDEX_DIR)/):"
	@if [ -f "$(INDEX_DIR)/embeddings.npy" ]; then \
		echo "  Exists (regenerable)"; \
	else echo "  Not yet created"; fi
	@echo ""
	@echo "Synth ($(SYNTH_DIR)/):"
	@find $(SYNTH_DIR)/drafts -name "DRAFT_*.md" 2>/dev/null | wc -l | xargs echo "  Drafts:"
	@echo "  Curated files: $(SYNTH_DIR)/*.md"

# Clean all generated content EXCEPT synth/
# synth/ contains human-curated knowledge and is NEVER auto-deleted
clean:
	@echo "Using clean.py script..."
	$(PYTHON) scripts/clean.py --verbose
	rm -f $(EXTRACT_MARKER) $(CHUNK_MARKER) $(EMBED_MARKER)

# Clean index only (safe - fully regenerable)
clean-index:
	@echo "Removing index/ (safe - fully regenerable)"
	rm -rf $(INDEX_DIR)/*
	rm -f $(EMBED_MARKER)
	@echo "Index cleaned. Run 'make embed' to regenerate."

# Clean all including drafts
clean-all:
	@echo "Using clean.py script with --all flag..."
	$(PYTHON) scripts/clean.py --all --verbose
	rm -f $(EXTRACT_MARKER) $(CHUNK_MARKER) $(EMBED_MARKER)

# ============================================================================
# Dependencies
# ============================================================================

# Ensure scripts exist
$(EXTRACT_SCRIPT) $(CHUNK_SCRIPT) $(EMBED_SCRIPT) $(SYNTH_SCRIPT):
	@echo "ERROR: Script not found: $@"
	@exit 1
