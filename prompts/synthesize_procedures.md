# SYNTHESIS CONTRACT: Procedures Extraction

## BINDING CONSTRAINTS

You are bound by the following constraints. Violation invalidates your output.

### CONSTRAINT 1: NO INFERENCE
You MUST NOT infer steps that are not explicitly stated.
If a step is unclear, mark it: "STEP UNCLEAR - SEE SOURCE"

### CONSTRAINT 2: NO GAP FILLING
You MUST NOT add steps to make a procedure "complete."
Missing steps remain missing. State: "POSSIBLE MISSING STEP"

### CONSTRAINT 3: MANDATORY CITATION
Every procedure and each step MUST include:
- Chunk ID (e.g., "doc_name_chunk_0042")
- Source document name
- Page number(s)

Format: `[Source: {chunk_id}, {document}, p.{page}]`

### CONSTRAINT 4: ORDER PRESERVATION
You MUST preserve the exact order stated in the source.
If order is ambiguous, mark: "ORDER UNCERTAIN"

### CONSTRAINT 5: OUTPUT FORMAT
Every procedure MUST follow this exact format:

```markdown
### Procedure: {Procedure Name}

**Purpose**: {What this procedure accomplishes, as stated in source}

**Prerequisites**: {Required conditions before starting, or "NOT SPECIFIED"}

**Steps**:
1. {Step 1 description}
   - Source: [{chunk_id}, {document}, p.{page}]

2. {Step 2 description}
   - Source: [{chunk_id}, {document}, p.{page}]

[Continue for all steps]

**Expected Outcome**: {Result when completed correctly, or "NOT SPECIFIED"}

**Warnings/Notes**: {Any cautions mentioned, or "NONE"}

**Status**: DRAFT - REQUIRES HUMAN REVIEW

**Completeness**: {COMPLETE if all steps present, PARTIAL if gaps exist}
```

## TASK

Extract procedures from the provided source chunks.

A procedure exists when the source text specifies:
- A sequence of steps to accomplish a task
- An ordered list of actions
- A workflow or process description

For each procedure:
1. Identify all explicitly stated steps
2. Preserve the original order
3. Note any prerequisites or conditions
4. Note expected outcomes if stated
5. Cite each step to its source
6. Identify any apparent gaps

## OUTPUT REQUIREMENTS

- Output ONLY steps explicitly stated in source
- Every step has a citation
- No steps added for "completeness"
- No assumed prerequisite steps
- Mark gaps as "POSSIBLE MISSING STEP BETWEEN X AND Y"
