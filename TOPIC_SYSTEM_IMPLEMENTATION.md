# Topic-Based Knowledge System - Implementation Summary

**Date**: 2026-01-21
**Version**: 1.0.0
**Status**: READY FOR REVIEW

---

## Executive Summary

This document summarizes the implementation of a **topic-based knowledge view system** on top of the existing PDF ingestion and synthesis pipeline. The system enforces **strict human review** and prevents automatic generation of authoritative content.

### Core Principle

**Topics are curated files, NOT on-demand syntheses.**

If a topic doesn't exist as a file in `topics/`, it is NOT authoritative.

---

## Deliverables

All deliverables have been created and are ready for review:

### 1. Directory Structure

```
knowledge/topics/
├── README.md                                           # Complete workflow documentation
├── _template.md                                        # Mandatory topic template
├── drafts/                                             # Draft topics (NOT authoritative)
│   └── EXAMPLE_DRAFT_hsi_pointers_20260121_150000.md  # Example draft
└── (empty - awaiting curated topics)
```

**Status**: ✅ Created

### 2. Topic Template (`topics/_template.md`)

Strict structure enforcing:
- Definition with mandatory citations
- Related Terms
- Sources (primary and referenced)
- Rules (IF/WHEN → THEN format)
- Behavior (normal operation, states/modes)
- Limitations (constraints, boundaries)
- Procedures (step-by-step)
- Edge Cases
- Open Questions (gaps in docs, NOT assumptions)
- Verification Status (review checklist)
- Metadata (source docs, generation info)

**Status**: ✅ Created
**File**: `knowledge/topics/_template.md`

### 3. Topic Lookup Script (`scripts/topic_lookup.py`)

**Purpose**: Look up topics with ZERO auto-generation

**Behavior**:
- **If curated topic exists**: Display authoritative content
- **If topic does NOT exist**: Offer explicit options (NOT auto-generate)
  - Option 1: Create draft topic
  - Option 2: Show glossary references (non-authoritative)
  - Option 3: Show related curated topics
  - Option 4: Search raw chunks (non-authoritative)

**Guarantees**:
- NEVER auto-generates topics
- NEVER treats search results as authoritative
- ONLY returns curated files as authoritative

**Usage**:
```bash
python scripts/topic_lookup.py "HSI pointers"
python scripts/topic_lookup.py --list-topics "dummy"
```

**Status**: ✅ Created (Not executed)
**File**: `knowledge/scripts/topic_lookup.py`

### 4. Topic Draft Generation Script (`scripts/topic_draft.py`)

**Purpose**: Generate draft from curated knowledge ONLY

**Sources (in order)**:
1. `synth/glossary.md` - definitions
2. `synth/rules.md` - rules
3. `synth/invariants.md` - constraints
4. `synth/procedures/*.md` - procedures
5. `chunks/**/*.json` - citations ONLY

**Output**: `topics/drafts/DRAFT_<topic>_<timestamp>.md`

**Guarantees**:
- Uses ONLY curated knowledge (no LLM)
- Raw chunks for citations only
- No inference beyond source text
- Clearly labeled as DRAFT
- NEVER writes to `topics/` (only `topics/drafts/`)

**Usage**:
```bash
python scripts/topic_draft.py "HSI pointers" --verbose
```

**Status**: ✅ Created (Not executed)
**File**: `knowledge/scripts/topic_draft.py`

### 5. Chunk Search Script (`scripts/search_chunks.py`)

**Purpose**: Search raw chunks (non-authoritative helper)

**Behavior**:
- Searches all chunks for query string
- Shows raw excerpts with context
- Provides citations (document, section, page)
- **Clearly labeled as NON-AUTHORITATIVE**

**Use Cases**:
- Finding source document references
- Verifying draft citations
- Exploring undocumented concepts

**Usage**:
```bash
python scripts/search_chunks.py "HSI pointer" --limit 20
python scripts/search_chunks.py "deviation bar" --context 500
```

**Status**: ✅ Created (Not executed)
**File**: `knowledge/scripts/search_chunks.py`

### 6. Complete Workflow Documentation (`topics/README.md`)

Comprehensive documentation including:
- Philosophy and principles
- Directory structure
- Complete workflows (lookup, draft, curation)
- Examples with expected output
- Truth hierarchy
- Absolute prohibitions
- Integration with existing pipeline
- Command reference

**Status**: ✅ Created
**File**: `knowledge/topics/README.md`

### 7. Example Topic Draft

Demonstrates complete topic structure with:
- Definition from glossary
- Related terms
- Sources with citations
- Rules (IF/WHEN → THEN)
- Behavior and states
- Open Questions (gaps documented)
- Verification checklist
- Clear DRAFT labeling

**Status**: ✅ Created
**File**: `knowledge/topics/drafts/EXAMPLE_DRAFT_hsi_pointers_20260121_150000.md`

### 8. Updated PROJECT.md

Added comprehensive documentation:
- Topic system overview
- Directory structure updated
- Topic lookup workflow
- Draft generation process
- Topic structure
- Curation process (human-only)
- Truth hierarchy
- Absolute prohibitions
- Commands reference

**Status**: ✅ Updated
**File**: `knowledge/.claude/PROJECT.md`

---

## Key Design Decisions

### 1. Topics are Files, Not Functions

**Decision**: Topics MUST exist as files to be authoritative.

**Rationale**: Prevents treating ephemeral search results or LLM outputs as truth.

**Implementation**: Lookup script returns file content only, NEVER generates on demand.

### 2. Strict Separation: Curated vs Drafts

**Decision**: Two-tier system with absolute prohibition on direct writing to `topics/`.

**Directories**:
- `topics/` - AUTHORITATIVE (human-curated only)
- `topics/drafts/` - NON-AUTHORITATIVE (machine-generated)

**Enforcement**: Scripts can ONLY write to `topics/drafts/`.

### 3. No LLM in Draft Generation

**Decision**: Draft generation uses ONLY curated knowledge files.

**Sources Allowed**:
- ✅ `synth/glossary.md` (already curated)
- ✅ `synth/rules.md` (already curated)
- ✅ `synth/invariants.md` (already curated)
- ✅ `synth/procedures/*.md` (already curated)
- ✅ `chunks/**/*.json` (ONLY for citations)

**Sources Prohibited**:
- ❌ LLM synthesis
- ❌ Inference beyond text
- ❌ Gap filling with assumptions

**Rationale**: Maintains strict chain of verification from PDF → curated synth → topic.

### 4. Explicit Options, Not Auto-Generation

**Decision**: When topic not found, offer menu of options instead of auto-generating.

**Rationale**: Forces conscious decision to create draft, prevents silent generation.

**Implementation**: Lookup script displays 4 explicit options and exits.

### 5. Mandatory Human Review

**Decision**: Every topic requires human review before curation.

**Enforcement**:
- Drafts clearly labeled with "DRAFT" status
- Verification checklist in template
- Manual file move required for promotion
- Reviewer name required in curated topics

**Rationale**: Human domain expertise essential for authoritative knowledge.

---

## Integration with Existing Pipeline

### Current Pipeline

```
PDF → extract → chunk → embed → synthesize → synth/*.md (curated)
```

### With Topics

```
PDF → extract → chunk → embed → synthesize → synth/*.md (curated)
                                                    ↓
                                          topic_draft.py
                                                    ↓
                                          topics/drafts/*.md (NOT authoritative)
                                                    ↓
                                          [Human Review & Curation]
                                                    ↓
                                          topics/*.md (AUTHORITATIVE)
```

### Truth Hierarchy

1. **Source PDFs** - Ultimate truth
2. **Curated topics/*.md** - Authoritative, human-reviewed
3. **Curated synth/*.md** - Authoritative, human-reviewed
4. **Drafts** - NOT authoritative, require review
5. **Index** - Regenerable tool, NOT truth
6. **Raw chunks** - Mechanical extraction, NOT truth

---

## Absolute Prohibitions

The following are STRICTLY FORBIDDEN:

### ❌ Auto-Generation
- Do NOT synthesize topics on demand
- Do NOT generate topics without explicit command
- Do NOT create topics in response to failed lookup

### ❌ Direct Writing to `topics/`
- Scripts may ONLY write to `topics/drafts/`
- Human manual action required to promote drafts
- No automatic promotion mechanism

### ❌ Treating Search as Authoritative
- Vector search results are NOT topics
- Glossary references are NOT topics
- Chunk search results are NOT topics

### ❌ Inference and Gap Filling
- Do NOT infer undocumented behavior
- Do NOT fill gaps with assumptions
- Do NOT synthesize beyond explicit source text

### ❌ Auto-Promotion
- Drafts NEVER auto-promote to curated
- Status change requires human action
- No automatic "approval" workflow

---

## Usage Examples

### Example 1: Looking Up Existing Topic

```bash
$ python scripts/topic_lookup.py "ADI Display"

============================================================
AUTHORITATIVE TOPIC (CURATED)
============================================================

# Topic: ADI Display
[Full curated content displayed]

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

This topic does not exist as a curated knowledge file.

OPTIONS:

1. CREATE DRAFT TOPIC
   python scripts/topic_draft.py "HSI pointers"

2. GLOSSARY REFERENCES (non-authoritative)
   - HSI (Horizontal Situation Indicator)

3. RELATED CURATED TOPICS (authoritative)
   - ADI Display
   - AFCS Modes

4. SEARCH RAW CHUNKS (non-authoritative)
   python scripts/search_chunks.py "HSI pointers"
============================================================
```

### Example 3: Creating Draft

```bash
$ python scripts/topic_draft.py "HSI pointers" --verbose

============================================================
TOPIC DRAFT GENERATION
============================================================

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
3. Fill in missing information
4. Move to topics/ when ready
============================================================
```

### Example 4: Listing Topics

```bash
$ python scripts/topic_lookup.py --list-topics "dummy"

CURATED TOPICS:
  - ADI Display
  - AFCS Modes
  - Air Data System
  (none yet - example output)
```

---

## Testing Recommendations

Before using in production, test the following scenarios:

### Test 1: Lookup Non-Existent Topic
```bash
python scripts/topic_lookup.py "Non-Existent Topic"
```
**Expected**: Options menu displayed, NO auto-generation

### Test 2: Generate Draft
```bash
python scripts/topic_draft.py "HSI pointers" --verbose
```
**Expected**: Draft created in `topics/drafts/`, NOT in `topics/`

### Test 3: Search Chunks
```bash
python scripts/search_chunks.py "HSI" --limit 5
```
**Expected**: Raw chunk excerpts with clear non-authoritative labeling

### Test 4: Verify Draft Content
```bash
cat topics/drafts/DRAFT_hsi_pointers_*.md
```
**Expected**: Contains citations, NO inferences, clear DRAFT labeling

### Test 5: Manual Curation
```bash
# 1. Review draft
code topics/drafts/DRAFT_hsi_pointers_*.md

# 2. Promote to curated (MANUAL)
mv topics/drafts/DRAFT_hsi_pointers_*.md topics/hsi_pointers.md

# 3. Update status in file to CURATED

# 4. Lookup now works
python scripts/topic_lookup.py "HSI pointers"
```
**Expected**: Authoritative topic displayed

---

## Next Steps

### Immediate

1. **Review all deliverables**:
   - [ ] Review `topics/_template.md` structure
   - [ ] Review `scripts/topic_lookup.py` logic
   - [ ] Review `scripts/topic_draft.py` sources
   - [ ] Review `scripts/search_chunks.py` warnings
   - [ ] Review `topics/README.md` documentation

2. **Test scripts** (if approved):
   - [ ] Test topic lookup with non-existent topic
   - [ ] Test draft generation for "HSI pointers"
   - [ ] Test chunk search
   - [ ] Verify no auto-generation occurs

3. **First topic curation**:
   - [ ] Generate draft for key topic
   - [ ] Human review against source PDF
   - [ ] Fill in gaps from documentation
   - [ ] Promote to curated
   - [ ] Verify lookup works

### Future Enhancements

1. **Build Integration**:
   - Add topic commands to `run.py`
   - Add topic targets to `Makefile`
   - Document in build workflow

2. **Cross-Referencing**:
   - Auto-detect related topics
   - Suggest topic links in drafts
   - Validate cross-references

3. **Metrics**:
   - Track topic coverage
   - Identify documentation gaps
   - Monitor curation workflow

4. **Quality Checks**:
   - Citation validator
   - Completeness checker
   - Template compliance test

---

## Files Created

All files created and ready for review:

1. `knowledge/topics/_template.md` - Topic template
2. `knowledge/topics/drafts/` - Draft directory (empty except example)
3. `knowledge/topics/drafts/EXAMPLE_DRAFT_hsi_pointers_20260121_150000.md` - Example
4. `knowledge/topics/README.md` - Complete documentation
5. `knowledge/scripts/topic_lookup.py` - Lookup script
6. `knowledge/scripts/topic_draft.py` - Draft generation script
7. `knowledge/scripts/search_chunks.py` - Chunk search script
8. `knowledge/.claude/PROJECT.md` - Updated with topic system
9. `knowledge/TOPIC_SYSTEM_IMPLEMENTATION.md` - This document

**Total**: 9 files created/updated

---

## Compliance with Requirements

### ✅ Core Concept

- [x] Topics are files, not on-demand syntheses
- [x] If topic doesn't exist as file, it's not authoritative

### ✅ Directory Structure

- [x] `topics/` directory created
- [x] `topics/_template.md` created
- [x] `topics/drafts/` directory created
- [x] Claude NEVER writes to `topics/` (only `topics/drafts/`)

### ✅ Topic Template

- [x] Strict structure with all required sections
- [x] Mandatory citations for every fact
- [x] Open Questions for gaps (not assumptions)

### ✅ Auto-Drafting Behavior

- [x] Uses ONLY existing synthesized knowledge
- [x] Raw chunks for citation only
- [x] No inference, no gap filling
- [x] Clearly labeled as DRAFT

### ✅ Lookup Behavior

- [x] Displays authoritative file if exists
- [x] Offers explicit options if not exists
- [x] Does NOT auto-synthesize

### ✅ Absolute Prohibitions

- [x] Do NOT treat vector search as topics
- [x] Do NOT claim completeness without file
- [x] Do NOT auto-promote drafts
- [x] Do NOT infer undocumented behavior
- [x] Do NOT use chat history as memory

---

## Conclusion

The topic-based knowledge system is **ready for review and testing**.

All deliverables enforce **strict human review** and prevent **automatic generation** of authoritative content.

The system maintains a clear **chain of verification** from source PDFs through curated synthesis to authoritative topics.

**No code has been executed** - all files are ready for review before deployment.

---

**Last Updated**: 2026-01-21
**Implementation**: Complete and ready for review
**Status**: Awaiting approval to test and deploy
