# SYNTHESIS CONTRACT: Rules Extraction

## BINDING CONSTRAINTS

You are bound by the following constraints. Violation invalidates your output.

### CONSTRAINT 1: NO INFERENCE
You MUST NOT infer rules that are not explicitly stated.
Implicit rules do not exist for this extraction.

### CONSTRAINT 2: NO GAP FILLING
You MUST NOT create rules from partial information.
If conditions or actions are unclear, state: "INCOMPLETE - REQUIRES SOURCE CLARIFICATION"

### CONSTRAINT 3: MANDATORY CITATION
Every rule MUST include:
- Chunk ID (e.g., "doc_name_chunk_0042")
- Source document name
- Page number(s)

Format: `[Source: {chunk_id}, {document}, p.{page}]`

### CONSTRAINT 4: STRUCTURE REQUIREMENT
Rules follow the pattern: IF/WHEN → THEN

You MUST identify:
- The condition (IF/WHEN)
- The action or requirement (THEN)
- Any exceptions mentioned

### CONSTRAINT 5: OUTPUT FORMAT
Every rule MUST follow this exact format:

```markdown
### Rule: {Short Descriptive Name}

**Condition**: IF {condition} / WHEN {trigger}

**Action**: THEN {required action or outcome}

**Exceptions**: {Any exceptions stated, or "NONE SPECIFIED"}

**Source**: [{chunk_id}, {document}, p.{page}]

**Status**: DRAFT - REQUIRES HUMAN REVIEW

**Confidence**: {HIGH if explicit, MEDIUM if clear but implicit structure, LOW if reconstructed}
```

## TASK

Extract rules from the provided source chunks.

A rule exists when the source text specifies:
- A condition and a resulting requirement
- A trigger and a mandated action
- A situation and its required handling

For each potential rule:
1. Identify the condition/trigger
2. Identify the action/requirement
3. Note any exceptions
4. Cite the exact source
5. Assess confidence level

## OUTPUT REQUIREMENTS

- Output ONLY rules explicitly stated or clearly structured in source
- Every rule has a citation
- No rules synthesized from fragments without clear connection
- No assumed business logic
- Mark anything uncertain as LOW confidence
