# Topic-Based Knowledge System

> **Philosophy**: Topics are curated files, not on-demand syntheses.
> If a topic doesn't exist as a file, it is not authoritative.

---

## Overview

The topic system provides **document-grounded, human-reviewed** knowledge organized by concept. Each topic is a complete dossier aggregating all explicit information about a named concept from the documentation.

### Key Principles

1. **Topics are FILES** - If it's not a file, it's not a topic
2. **Drafts are NOT authoritative** - Only curated files are truth
3. **No auto-generation** - Drafts require explicit command
4. **No inference** - Only what the source documents explicitly state
5. **Human review mandatory** - Every topic must be reviewed before curation

---

## Directory Structure

```
knowledge/topics/
├── README.md              # This file
├── _template.md           # Template for all topics
├── drafts/                # Draft topics (NOT authoritative)
│   └── DRAFT_*.md         # Generated drafts awaiting review
└── <topic_name>.md        # Curated topics (AUTHORITATIVE)
```

**CRITICAL**: Claude Code NEVER writes to `topics/` directly.
Claude Code may ONLY generate files in `topics/drafts/`.

---

## Workflow

### 1. Looking Up a Topic

**Command**:
```bash
python scripts/topic_lookup.py "HSI pointers"
```

**Behavior**:

- **If curated topic exists** (`topics/hsi_pointers.md`):
  - Displays the authoritative topic file
  - User can trust this as verified knowledge

- **If topic does NOT exist**:
  - Does NOT auto-generate
  - Offers explicit options:
    1. Create draft topic
    2. Show glossary references (non-authoritative)
    3. Show related curated topics
    4. Search raw chunks (non-authoritative)

**Example Output (Topic Not Found)**:
```
============================================================
TOPIC NOT FOUND: 'HSI pointers'
============================================================

This topic does not exist as a curated knowledge file.
Vector search results are NOT authoritative.

OPTIONS:

1. CREATE DRAFT TOPIC
   Generate a draft topic file for human review.
   Command:
   python scripts/topic_draft.py "HSI pointers"

2. GLOSSARY REFERENCES (non-authoritative)
   The following terms were found in glossary.md:
   - HSI (Horizontal Situation Indicator)

3. RELATED CURATED TOPICS (authoritative)
   The following topics have been curated:
   - ADI Display
   - AFCS Modes
   ...

4. SEARCH RAW CHUNKS (non-authoritative)
   Search original document chunks directly.
   Command:
   python scripts/search_chunks.py "HSI pointers"
============================================================
```

---

### 2. Creating a Topic Draft

**Command**:
```bash
python scripts/topic_draft.py "HSI pointers" --verbose
```

**Behavior**:

1. Searches **curated knowledge only**:
   - `synth/glossary.md` - for definitions
   - `synth/rules.md` - for rules
   - `synth/invariants.md` - for constraints
   - `synth/procedures/*.md` - for procedures

2. Uses **raw chunks** for citations only (not synthesis)

3. Generates draft in `topics/drafts/DRAFT_hsi_pointers_YYYYMMDD_HHMMSS.md`

4. Draft is **clearly labeled** as non-authoritative

**Example Output**:
```
============================================================
TOPIC DRAFT GENERATION
============================================================

WARNING: This generates a DRAFT that requires human review.
Drafts are NOT authoritative.

Searching glossary.md...
Searching rules.md...
Searching chunks for citations...

============================================================
DRAFT GENERATED
============================================================
Output: topics/drafts/DRAFT_hsi_pointers_20260121_143052.md

NEXT STEPS (REQUIRED):
1. Review the draft carefully
2. Verify all citations against source documents
3. Fill in missing information from source documents
4. Remove any inferences or assumptions
5. Complete all 'NOT SPECIFIED' sections
6. Add human expertise and context
7. Move to topics/ and remove DRAFT_ prefix when ready

REMEMBER: Only files in topics/ (not drafts/) are authoritative.
============================================================
```

---

### 3. Reviewing and Curating a Draft

**Manual Process** (Human-only):

1. **Open the draft**:
   ```bash
   # Example path
   code topics/drafts/DRAFT_hsi_pointers_20260121_143052.md
   ```

2. **Review checklist**:
   - [ ] All citations verified against source PDFs
   - [ ] All "NOT SPECIFIED" claims verified (absence confirmed)
   - [ ] No inferences or assumptions present
   - [ ] Related terms cross-referenced
   - [ ] Open questions documented
   - [ ] Definition is complete and accurate
   - [ ] Rules are explicit from source
   - [ ] Procedures are correctly extracted
   - [ ] Edge cases documented if present

3. **Fill in gaps**:
   - Read source documents directly
   - Add missing procedures
   - Clarify ambiguous statements
   - Add human expertise and context

4. **Promote to curated**:
   ```bash
   # Remove DRAFT_ prefix and timestamp
   mv topics/drafts/DRAFT_hsi_pointers_20260121_143052.md topics/hsi_pointers.md
   ```

5. **Update metadata**:
   - Change `Status: DRAFT` → `Status: CURATED`
   - Set `Reviewed By: <Your Name>`
   - Update timestamp

6. **Commit**:
   ```bash
   git add topics/hsi_pointers.md
   git commit -m "Add curated topic: HSI pointers

   - Verified all citations against E550 Operators Guide
   - Completed definition from multiple sources
   - Added operational procedures
   - Human reviewed and validated

   Reviewed-by: <Your Name>"
   ```

---

### 4. Searching Raw Chunks (Non-Authoritative)

**Command**:
```bash
python scripts/search_chunks.py "HSI pointer" --limit 10
```

**Behavior**:

- Searches all chunks for matching text
- Shows raw excerpts with context
- Provides citations (document, section, page)
- **Clearly labeled as NON-AUTHORITATIVE**

**Use Cases**:

- Finding source document references
- Locating specific procedures
- Verifying draft citations
- Exploring undocumented concepts

**WARNING**: Raw search results are NOT authoritative knowledge.
Always create a curated topic for authoritative reference.

---

## Topic File Structure

Every topic file follows the template in `_template.md`:

```markdown
# Topic: <Name>

> **Status**: DRAFT | CURATED
> **Reviewed By**: <Name or NOT REVIEWED>

## Definition
- Primary definition with citation
- Synonyms

## Related Terms
- Cross-references with relationships

## Sources
- Primary source documents
- Coverage assessment

## Rules
- IF/WHEN → THEN rules
- Explicit from source only

## Behavior
- Normal operation
- States/Modes

## Limitations
- Explicit constraints
- Boundary conditions

## Procedures
- Step-by-step procedures
- Preconditions and outcomes

## Edge Cases
- Documented edge cases only

## Open Questions
- Gaps in documentation
- NOT assumptions

## Verification Status
- Review checklist

## Metadata
- Source documents
- Generation info
```

---

## Integration with Existing Pipeline

### Relationship to Synthesis

```
PDF Documents
     ↓
 extract.py  → extracted/
     ↓
 chunk.py    → chunks/
     ↓
 embed.py    → index/ (regenerable, not truth)
     ↓
 synthesize.py → synth/
                  ├── glossary.md      ← Curated (used by topics)
                  ├── rules.md         ← Curated (used by topics)
                  ├── invariants.md    ← Curated (used by topics)
                  └── procedures/      ← Curated (used by topics)
     ↓
 topic_draft.py → topics/drafts/       ← NOT authoritative
     ↓
 [Human Review]
     ↓
 topics/<name>.md  ← AUTHORITATIVE
```

### Truth Hierarchy

1. **Source PDFs** - Ultimate truth
2. **Curated topics/** - Authoritative, human-reviewed
3. **Curated synth/*.md** - Authoritative, human-reviewed
4. **Drafts** - NOT authoritative, require review
5. **Index** - Regenerable tool, NOT truth
6. **Raw chunks** - Mechanical extraction, NOT truth

---

## Examples

### Example 1: Looking Up Existing Topic

```bash
$ python scripts/topic_lookup.py "ADI Display"

============================================================
AUTHORITATIVE TOPIC (CURATED)
============================================================

# Topic: ADI Display

> **Status**: CURATED
> **Reviewed By**: John Smith
> **Last Updated**: 2026-01-20

## Definition
The Attitude Director Indicator (ADI) format provides essential...
[Full curated content]

============================================================
Source: topics/adi_display.md
Status: AUTHORITATIVE (human-reviewed)
============================================================
```

### Example 2: Topic Not Found

```bash
$ python scripts/topic_lookup.py "HSI pointers"

============================================================
TOPIC NOT FOUND: 'HSI pointers'
============================================================

[Options menu shown]
```

### Example 3: Creating Draft

```bash
$ python scripts/topic_draft.py "HSI pointers" --verbose

============================================================
TOPIC DRAFT GENERATION
============================================================

Searching glossary.md...
Found entry: HSI (Horizontal Situation Indicator)
Searching rules.md...
Found 2 rules mentioning HSI
Searching chunks for citations...
Found 15 chunks

============================================================
DRAFT GENERATED
============================================================
Output: topics/drafts/DRAFT_hsi_pointers_20260121_143052.md

[Instructions shown]
```

### Example 4: List All Topics

```bash
$ python scripts/topic_lookup.py --list-topics "dummy"

CURATED TOPICS:
  - ADI Display
  - AFCS Modes
  - Air Data System
  - Autopilot Engagement
  - FMS Navigation
  ...
```

---

## Absolute Prohibitions

### NEVER

- ❌ Auto-generate topics on demand
- ❌ Write to `topics/` directory (only `topics/drafts/`)
- ❌ Treat search results as authoritative
- ❌ Infer undocumented behavior
- ❌ Auto-promote drafts to curated status
- ❌ Claim completeness without curated topic file
- ❌ Use chat history as memory

### ALWAYS

- ✅ Require explicit command to create draft
- ✅ Label drafts clearly as non-authoritative
- ✅ Cite sources for every fact
- ✅ Mark gaps as "NOT SPECIFIED"
- ✅ Require human review before curation
- ✅ Preserve chain of verification

---

## Commands Reference

### Topic Lookup
```bash
python scripts/topic_lookup.py "<topic name>"
python scripts/topic_lookup.py "<topic name>" --show-draft
python scripts/topic_lookup.py --list-topics "dummy"
```

### Draft Generation
```bash
python scripts/topic_draft.py "<topic name>"
python scripts/topic_draft.py "<topic name>" --verbose
```

### Raw Search
```bash
python scripts/search_chunks.py "<query>"
python scripts/search_chunks.py "<query>" --limit 50
python scripts/search_chunks.py "<query>" --context 500
```

---

## Maintenance

### Adding New Topics

1. Generate draft: `python scripts/topic_draft.py "<topic>"`
2. Review draft thoroughly
3. Verify all citations
4. Fill in gaps from source documents
5. Move to `topics/` and rename
6. Update status to CURATED
7. Commit with review notes

### Updating Existing Topics

1. Edit the topic file directly
2. Verify all changes against source
3. Update "Last Updated" timestamp
4. Update "Reviewed By" if different reviewer
5. Commit with change description

### Regenerating Drafts

Drafts can be regenerated as curated knowledge improves:

```bash
python scripts/topic_draft.py "<topic>" --verbose
```

Compare new draft with existing curated topic to identify gaps.

---

## Version History

- **v1.0.0** (2026-01-21) - Initial topic system implementation
  - Topic template created
  - Lookup, draft, and search scripts
  - Workflow documentation

---

**Last Updated**: 2026-01-21
