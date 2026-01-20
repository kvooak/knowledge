# Project TODO: knowledge

> This file tracks project progress, decisions, and tasks.
> Claude will read and update this file throughout the project lifecycle.

## Current Sprint / Focus

- [x] ~~Run compliance test to verify all requirements~~ (75/75 passed)
- [x] ~~Add sample PDF for testing pipeline~~ (Collins/Operators Guide - PL Fusion.pdf)
- [x] ~~Test extraction pipeline~~ (558 pages extracted)
- [x] ~~Test chunking pipeline~~ (783 chunks created)
- [x] ~~Test embeddings pipeline~~ (783 chunks indexed, 384-dim embeddings)
- [x] ~~Test full synthesis pipeline~~ (Generated glossary draft from 50 chunks)

## Backlog

- [ ] Add search functionality for querying chunks
- [ ] Create CLI for interactive querying
- [ ] Add support for other document formats (DOCX, TXT)

## In Progress

<!-- Tasks currently being worked on -->

## Completed

- [x] ~~Create mandatory directory structure~~ (initialization)
- [x] ~~Create scripts/extract_pdf.py~~ (mechanical PDF extraction)
- [x] ~~Create scripts/chunk_text.py~~ (semantic chunking, no LLM)
- [x] ~~Create scripts/embed_chunks.py~~ (embeddings index, regenerable)
- [x] ~~Create scripts/synthesize.py~~ (LLM synthesis with human review)
- [x] ~~Create all prompt contracts~~ (prompts/)
- [x] ~~Create Makefile with required targets~~ (extract, chunk, embed, synth, ingest)
- [x] ~~Create README.md with required explanations~~
- [x] ~~Create synth/ template files~~ (glossary, rules, invariants, etc.)
- [x] ~~Create compliance test~~ (tests/test_compliance.py)
- [x] ~~Add project-based organization~~ (v2.0.0: sources/<project>/ structure)
- [x] ~~Update extract_pdf.py for recursive folders~~ (v2.0.0)
- [x] ~~Update chunk_text.py with project_name in metadata~~ (v2.0.0)
- [x] ~~Test with real PDF~~ (Collins/Operators Guide - PL Fusion.pdf, 558 pages, 783 chunks)
- [x] ~~Fix embed_chunks.py to support recursive directory structure~~ (v1.1.0)
- [x] ~~Fix synthesize.py to support recursive directory structure~~ (v1.1.0)
- [x] ~~Generate embeddings index~~ (783 chunks, all-MiniLM-L6-v2 model)
- [x] ~~Test synthesis pipeline~~ (Generated DRAFT_glossary_flight_systems_and_avionics with 9 terms + 6 terms needing follow-up)

## Decisions Log

- **LLM Isolation**: LLM usage is restricted to synthesize.py only. All other scripts (extract, chunk, embed) are mechanical and deterministic.
- **Truth Location**: Authoritative knowledge lives in synth/*.md curated files. Index is for search only and is NOT truth.
- **Human Review**: All LLM-generated content goes to synth/drafts/ and requires mandatory human review before promotion.
- **No Auto-Overwrite**: synthesize.py refuses to overwrite curated files. This is enforced in code.
- **Prompt Contracts**: All prompts forbid inference, forbid gap-filling, and require citations for every statement.
- **Recursive Directory Support**: Updated embed_chunks.py and synthesize.py to use `rglob()` instead of nested loops to support project-based organization (sources/<project>/subfolders/)

---

*Last updated: Added project-based organization (v2.0.0)*
