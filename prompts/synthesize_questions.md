# SYNTHESIS CONTRACT: Open Questions Identification

## BINDING CONSTRAINTS

You are bound by the following constraints. Violation invalidates your output.

### CONSTRAINT 1: NO INFERENCE
You MUST NOT answer questions using external knowledge.
If the source doesn't answer, the question remains open.

### CONSTRAINT 2: NO GAP FILLING
You MUST NOT assume answers based on context or common sense.
Unanswered questions remain unanswered.

### CONSTRAINT 3: MANDATORY CITATION
Every question MUST cite the context that raised it:
- Chunk ID (e.g., "doc_name_chunk_0042")
- Source document name
- Page number(s)

Format: `[Context: {chunk_id}, {document}, p.{page}]`

### CONSTRAINT 4: QUESTION CRITERIA
Flag as open questions:
- Explicit questions in the source text
- Implied questions (term used but not defined)
- Missing information critical to understanding
- Ambiguous statements requiring clarification

### CONSTRAINT 5: OUTPUT FORMAT
Every open question MUST follow this exact format:

```markdown
### Question: {Short form of question}

**Full Question**: {Complete, specific question}

**Why This Matters**: {Why answering this is important for understanding}

**Context That Raised It**:
> {Quote from source that created this question}

Source: [{chunk_id}, {document}, p.{page}]

**What We Know**: {Any partial information from source, or "NOTHING SPECIFIED"}

**What We Need**: {Specific information required to answer}

**Status**: OPEN - REQUIRES RESEARCH OR SME INPUT
```

## TASK

Identify open questions from the provided source chunks.

Look for:
- Explicit questions in the text
- Terms used without definition
- Processes referenced but not explained
- Dependencies mentioned but not detailed
- Edge cases not addressed
- Exceptions not fully specified

For each question:
1. State the question clearly and specifically
2. Explain why it matters
3. Cite the context that raised it
4. Note any partial information available
5. Specify what information is needed

## OUTPUT REQUIREMENTS

- Output questions that genuinely cannot be answered from source
- Every question has context citation
- No questions answerable from the provided chunks
- No questions based on external expectations
- Questions should be specific enough to research
