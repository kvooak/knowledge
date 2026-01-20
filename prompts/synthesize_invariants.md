# SYNTHESIS CONTRACT: Invariants Extraction

## BINDING CONSTRAINTS

You are bound by the following constraints. Violation invalidates your output.

### CONSTRAINT 1: NO INFERENCE
You MUST NOT infer invariants from examples or patterns.
Only extract invariants explicitly stated as always-true conditions.

### CONSTRAINT 2: NO GAP FILLING
You MUST NOT assume invariants based on common sense or domain knowledge.
If not explicitly stated as an invariant, it is not one.

### CONSTRAINT 3: MANDATORY CITATION
Every invariant MUST include:
- Chunk ID (e.g., "doc_name_chunk_0042")
- Source document name
- Page number(s)

Format: `[Source: {chunk_id}, {document}, p.{page}]`

### CONSTRAINT 4: INVARIANT IDENTIFICATION
An invariant is identified by language such as:
- "must always"
- "shall never"
- "at all times"
- "invariably"
- "without exception"

Do NOT elevate guidelines or recommendations to invariants.

### CONSTRAINT 5: OUTPUT FORMAT
Every invariant MUST follow this exact format:

```markdown
### Invariant: {Short Descriptive Name}

**Statement**: {The condition that must always hold}

**Rationale**: {Why this must be true, if stated in source, or "NOT STATED"}

**Violation Consequence**: {What happens if violated, if stated, or "NOT SPECIFIED"}

**Source**: [{chunk_id}, {document}, p.{page}]

**Status**: DRAFT - REQUIRES HUMAN REVIEW

**Strength**: {EXPLICIT if directly stated, IMPLIED if strongly suggested}
```

## TASK

Extract invariants from the provided source chunks.

An invariant exists when the source text specifies:
- A condition that must ALWAYS be true
- A state that must NEVER occur
- A property that must be maintained without exception

For each invariant:
1. Extract the exact statement
2. Identify any stated rationale
3. Note consequences of violation if mentioned
4. Cite the exact source
5. Assess strength (explicit vs implied)

## OUTPUT REQUIREMENTS

- Output ONLY invariants with explicit "always/never" language
- Every invariant has a citation
- No invariants derived from patterns or examples
- No assumed system constraints
- Mark anything not using explicit invariant language as IMPLIED
