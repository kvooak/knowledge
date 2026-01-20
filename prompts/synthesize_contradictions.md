# SYNTHESIS CONTRACT: Contradictions Detection

## BINDING CONSTRAINTS

You are bound by the following constraints. Violation invalidates your output.

### CONSTRAINT 1: NO INFERENCE
You MUST NOT infer contradictions from interpretation differences.
Only flag contradictions where statements directly conflict.

### CONSTRAINT 2: NO GAP FILLING
You MUST NOT assume intent to resolve apparent contradictions.
Present both statements as found.

### CONSTRAINT 3: MANDATORY CITATION
Every contradiction MUST include full citations for BOTH conflicting statements:
- Chunk ID (e.g., "doc_name_chunk_0042")
- Source document name
- Page number(s)

Format: `[Source: {chunk_id}, {document}, p.{page}]`

### CONSTRAINT 4: DIRECT CONFLICT ONLY
A contradiction exists ONLY when:
- Statement A asserts X
- Statement B asserts NOT X (or incompatible Y)
- Both cannot be simultaneously true

Do NOT flag:
- Different levels of detail
- Different contexts
- Evolving requirements (unless both are current)

### CONSTRAINT 5: OUTPUT FORMAT
Every contradiction MUST follow this exact format:

```markdown
### Contradiction: {Short Descriptive Name}

**Statement A**:
> {Exact quote or close paraphrase}

Source: [{chunk_id}, {document}, p.{page}]

**Statement B**:
> {Exact quote or close paraphrase}

Source: [{chunk_id}, {document}, p.{page}]

**Nature of Conflict**: {Explain why these cannot both be true}

**Possible Explanations**:
- {If different contexts might apply, note them}
- {If temporal difference (old vs new), note it}
- {If genuinely irreconcilable, state so}

**Resolution**: UNRESOLVED - REQUIRES HUMAN REVIEW

**Status**: DRAFT
```

## TASK

Identify contradictions in the provided source chunks.

Scan for:
- Directly conflicting statements
- Incompatible requirements
- Mutually exclusive conditions
- Numerical discrepancies

For each contradiction:
1. Quote both conflicting statements exactly
2. Cite both sources fully
3. Explain the nature of the conflict
4. Note possible explanations (without resolving)
5. Leave resolution to human review

## OUTPUT REQUIREMENTS

- Output ONLY clear, direct contradictions
- Every statement has a citation
- No interpretation-based conflicts
- No resolution attempts (humans resolve)
- If no contradictions found, state: "NO CONTRADICTIONS DETECTED IN PROVIDED CHUNKS"
