# SYNTHESIS CONTRACT: Glossary Extraction

## BINDING CONSTRAINTS

You are bound by the following constraints. Violation invalidates your output.

### CONSTRAINT 1: NO INFERENCE
You MUST NOT infer, deduce, or extrapolate beyond the explicit text.
If the source does not state something explicitly, you do not know it.

### CONSTRAINT 2: NO GAP FILLING
You MUST NOT fill gaps with assumed knowledge, common sense, or prior training.
Gaps remain gaps. State: "NOT SPECIFIED IN SOURCE"

### CONSTRAINT 3: MANDATORY CITATION
Every factual statement MUST include:
- Chunk ID (e.g., "doc_name_chunk_0042")
- Source document name
- Page number(s)

Format: `[Source: {chunk_id}, {document}, p.{page}]`

### CONSTRAINT 4: AMBIGUITY DECLARATION
If a term has multiple possible meanings in the source, you MUST:
- List all meanings found
- Mark as "AMBIGUOUS - REQUIRES HUMAN RESOLUTION"

### CONSTRAINT 5: OUTPUT FORMAT
Every definition MUST follow this exact format:

```markdown
### {Term}

**Definition**: {Exact definition from source, quoted or closely paraphrased}

**Source**: [{chunk_id}, {document}, p.{page}]

**Status**: DRAFT - REQUIRES HUMAN REVIEW

**Notes**: {Any ambiguity, uncertainty, or related terms found}
```

## TASK

Extract definitions/terms from the provided source chunks.

For each term:
1. Extract the definition as stated in the source
2. Cite the exact source location
3. Note any ambiguity or multiple definitions
4. Mark status as DRAFT

If a term is used but not defined:
- Include it with: "Definition: NOT PROVIDED IN SOURCE"
- Mark for human follow-up

## OUTPUT REQUIREMENTS

- Output ONLY definitions found in the source text
- Every definition has a citation
- No definitions without source support
- No assumed definitions
- No external knowledge
