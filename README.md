# Knowledge System

A durable, auditable knowledge system for ingesting large PDFs into structured, human-reviewed knowledge.

## Critical Understanding

### The LLM is Stateless

**The language model has no memory.** Every interaction starts from zero. The LLM:

- Does not remember previous conversations
- Does not learn from your documents
- Does not maintain state between sessions
- Cannot "know" anything it wasn't given in the current context

Any illusion of memory or learning is created by this system, not by the LLM.

### Where Truth Lives

```
synth/
├── glossary.md       ← TRUTH: Human-curated definitions
├── rules.md          ← TRUTH: Human-curated rules
├── invariants.md     ← TRUTH: Human-curated invariants
├── contradictions.md ← TRUTH: Human-identified contradictions
├── open_questions.md ← TRUTH: Human-tracked questions
└── procedures/       ← TRUTH: Human-curated procedures
```

**These files are the authoritative source of knowledge.**

They are:
- Human-reviewed
- Manually curated
- Never auto-modified
- The only files that should be trusted

### What is Safe to Regenerate

```
extracted/   ← Safe to delete and regenerate from sources/
chunks/      ← Safe to delete and regenerate from extracted/
index/       ← Safe to delete and regenerate from chunks/
synth/drafts/← Safe to delete (these are LLM proposals, not truth)
```

To regenerate:
```bash
make clean      # Deletes extracted/, chunks/, index/
make ingest     # Regenerates everything
```

### What Must NEVER Be Auto-Modified

```
synth/glossary.md
synth/rules.md
synth/invariants.md
synth/contradictions.md
synth/open_questions.md
synth/procedures/*.md (files without DRAFT_ prefix)
```

These files:
- Require human review for any change
- Are protected by the synthesis script
- Represent verified, authoritative knowledge

## Human-in-the-Loop Workflow

### 1. Ingest Documents

```bash
# Add PDFs to sources/
cp your-document.pdf sources/

# Run ingestion pipeline
make ingest
```

This extracts text, creates chunks, and builds the search index.
**No LLM is used.** Everything is mechanical and deterministic.

### 2. Generate Synthesis Drafts

```bash
# Generate a glossary draft
make synth TYPE=glossary TOPIC="key terms"

# Generate rules draft
make synth TYPE=rules TOPIC="compliance requirements"
```

This uses the LLM to propose knowledge synthesis.
**Output goes to `synth/drafts/` and is NOT authoritative.**

### 3. Human Review (MANDATORY)

1. Open the draft in `synth/drafts/`
2. Verify every statement against source documents
3. Check every citation
4. Edit for accuracy
5. Move approved content to the appropriate curated file

```bash
# Example: Review and promote definitions
cat synth/drafts/DRAFT_glossary_*.md
# ... review and edit ...
# ... copy approved definitions to synth/glossary.md ...
rm synth/drafts/DRAFT_glossary_*.md
```

### 4. Iterate

Repeat steps 2-3 for:
- Definitions (glossary)
- Rules (IF/WHEN → THEN)
- Invariants (must always be true)
- Procedures (ordered steps)
- Contradictions (conflicts found)
- Open questions (unanswered items)

## Directory Structure

```
knowledge/
├── sources/           # Input PDFs (add your documents here)
├── extracted/         # Mechanical text extraction (one file per page)
├── chunks/            # Semantic chunks with metadata
├── synth/             # Synthesized knowledge
│   ├── drafts/        # LLM-generated proposals (not truth)
│   ├── procedures/    # Curated procedure documents
│   ├── glossary.md    # Curated definitions
│   ├── rules.md       # Curated rules
│   ├── invariants.md  # Curated invariants
│   ├── contradictions.md  # Identified conflicts
│   └── open_questions.md  # Unanswered questions
├── index/             # Search index (regenerable)
├── scripts/           # Processing scripts
├── prompts/           # LLM prompt templates
├── tests/             # Compliance tests
├── Makefile           # Build automation
└── README.md          # This file
```

## Scripts

| Script | LLM? | Purpose |
|--------|------|---------|
| `extract_pdf.py` | NO | Extract text from PDFs (mechanical) |
| `chunk_text.py` | NO | Split text into semantic chunks |
| `embed_chunks.py` | NO | Generate search embeddings |
| `synthesize.py` | YES | Generate synthesis drafts |

**LLM usage is isolated to `synthesize.py` only.**

## Make Targets

```bash
make help        # Show all targets
make extract     # Extract PDFs → Markdown
make chunk       # Chunk Markdown → JSON
make embed       # Generate search index
make ingest      # Run full pipeline (extract → chunk → embed)
make synth       # Generate synthesis draft (requires TYPE and TOPIC)
make status      # Show current state
make clean       # Clean generated content (preserves synth/)
make clean-index # Clean only index/ (safe, regenerable)
```

## Dependencies

```bash
pip install pymupdf           # PDF extraction
pip install sentence-transformers  # Embeddings
pip install numpy             # Array operations
pip install anthropic         # LLM API (for synthesis only)
```

## Prohibitions

This system explicitly does NOT:

- ❌ Use LLM for PDF extraction
- ❌ Use LLM for chunking decisions
- ❌ Silently overwrite curated files
- ❌ Claim to "learn" or "remember"
- ❌ Auto-update long-term knowledge
- ❌ Rely on chat history
- ❌ Use background daemons or watchers
- ❌ Treat databases as source of truth

## Philosophy

1. **Reproducibility > Convenience**: Everything can be regenerated from source
2. **Auditability > Cleverness**: Every claim traces to a source
3. **Human Review > Automation**: Machines propose, humans decide
4. **Explicit > Implicit**: No hidden state, no magic

The LLM is a tool for generating proposals. Humans are the authority on truth.
