#!/usr/bin/env python3
"""
topic_draft.py - Generate topic draft from curated knowledge

CONTRACT:
    Input:  Topic name (string)
    Output: Draft topic file in topics/drafts/

SOURCES (in priority order):
    1. synth/glossary.md (for definitions)
    2. synth/rules.md (for rules)
    3. synth/invariants.md (for constraints)
    4. synth/procedures/*.md (for procedures)
    5. chunks/**/*.json (for citations ONLY)

GUARANTEES:
    - Uses ONLY curated knowledge (synth/ files)
    - Raw chunks used ONLY for citation lookup
    - No LLM synthesis
    - No inference beyond source text
    - Output clearly labeled as DRAFT
    - NEVER writes to topics/ (only topics/drafts/)

ABSOLUTE PROHIBITIONS:
    - Do NOT write to topics/ directory
    - Do NOT treat this as authoritative
    - Do NOT auto-promote to curated status
    - Do NOT infer undocumented behavior

VERSION: 1.0.0
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TOPICS_DIR = PROJECT_ROOT / "topics"
DRAFTS_DIR = TOPICS_DIR / "drafts"
SYNTH_DIR = PROJECT_ROOT / "synth"
CHUNKS_DIR = PROJECT_ROOT / "chunks"
TEMPLATE_FILE = TOPICS_DIR / "_template.md"

# Curated knowledge files
GLOSSARY_FILE = SYNTH_DIR / "glossary.md"
RULES_FILE = SYNTH_DIR / "rules.md"
INVARIANTS_FILE = SYNTH_DIR / "invariants.md"
PROCEDURES_DIR = SYNTH_DIR / "procedures"


def normalize_topic_name(topic: str) -> str:
    """Normalize topic name to filename format."""
    return topic.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def extract_glossary_entry(topic: str, glossary_content: str) -> Optional[dict]:
    """
    Extract definition from glossary.md for the given topic.

    Returns dict with definition, sources, notes or None if not found.
    """
    # Search for topic as header (case-insensitive)
    pattern = rf"###\s+{re.escape(topic)}\s*\n(.*?)(?=\n###|\Z)"
    match = re.search(pattern, glossary_content, re.IGNORECASE | re.DOTALL)

    if not match:
        # Try searching with common abbreviations
        pattern = rf"###\s+.*{re.escape(topic)}.*\n(.*?)(?=\n###|\Z)"
        match = re.search(pattern, glossary_content, re.IGNORECASE | re.DOTALL)

    if not match:
        return None

    entry_text = match.group(1).strip()

    # Extract components
    definition = None
    sources = []
    notes = None

    # Look for **Definition**: pattern
    def_match = re.search(r"\*\*Definition\*\*:\s*(.*?)(?=\n\*\*|$)", entry_text, re.DOTALL)
    if def_match:
        definition = def_match.group(1).strip()

    # Look for **Source**: pattern
    source_matches = re.findall(r"\*\*Source\*\*:\s*\[(.*?)\]", entry_text)
    sources = source_matches

    # Look for **Notes**: pattern
    notes_match = re.search(r"\*\*Notes\*\*:\s*(.*?)(?=\n\*\*|$)", entry_text, re.DOTALL)
    if notes_match:
        notes = notes_match.group(1).strip()

    return {
        "definition": definition,
        "sources": sources,
        "notes": notes,
        "raw_entry": entry_text,
    }


def extract_related_terms(topic: str, glossary_content: str) -> list[tuple[str, str]]:
    """
    Find related terms by searching for topic mentions in glossary.

    Returns list of (term_name, relationship_hint) tuples.
    """
    related = []

    # Search all glossary entries for mentions of the topic
    for match in re.finditer(r"###\s+(.*?)\n(.*?)(?=\n###|\Z)", glossary_content, re.DOTALL):
        term_name = match.group(1).strip()
        entry_text = match.group(2).strip()

        if topic.lower() in entry_text.lower() and topic.lower() not in term_name.lower():
            # This term mentions our topic
            related.append((term_name, "mentions"))

    return related[:10]  # Limit to 10


def extract_rules(topic: str, rules_content: str) -> list[dict]:
    """
    Extract rules from rules.md that mention the topic.

    Returns list of dicts with condition, consequence, source.
    """
    rules = []

    # Search for rules mentioning the topic
    for match in re.finditer(
        r"(IF|WHEN)\s+(.*?)\s+THEN\s+(.*?)(?=\n(?:IF|WHEN|$))",
        rules_content,
        re.IGNORECASE | re.DOTALL
    ):
        rule_text = match.group(0)

        if topic.lower() in rule_text.lower():
            condition = match.group(2).strip()
            consequence = match.group(3).strip()

            # Try to find source citation
            source_match = re.search(r"\[(.*?),\s*p\.(\d+)\]", rule_text)
            source = source_match.group(0) if source_match else "Source not found"

            rules.append({
                "condition": condition,
                "consequence": consequence,
                "source": source,
                "raw": rule_text,
            })

    return rules


def extract_procedures(topic: str) -> list[dict]:
    """
    Search procedures/ directory for procedures mentioning the topic.

    Returns list of dicts with procedure info.
    """
    procedures = []

    if not PROCEDURES_DIR.exists():
        return procedures

    for proc_file in PROCEDURES_DIR.glob("*.md"):
        if proc_file.name.startswith("DRAFT_"):
            continue  # Skip drafts

        content = proc_file.read_text(encoding="utf-8")

        if topic.lower() in content.lower():
            procedures.append({
                "name": proc_file.stem.replace("_", " ").title(),
                "file": proc_file.name,
                "excerpt": content[:500],  # First 500 chars
            })

    return procedures


def search_chunks_for_citations(topic: str, limit: int = 20) -> list[dict]:
    """
    Search raw chunks for topic mentions to extract citations.

    Returns list of chunk dicts with source info.
    """
    citations = []

    for chunk_file in CHUNKS_DIR.rglob("*.json"):
        if chunk_file.name.startswith("_"):
            continue

        try:
            chunk = json.loads(chunk_file.read_text(encoding="utf-8"))

            if topic.lower() in chunk.get("raw_text", "").lower():
                citations.append({
                    "id": chunk.get("id", "unknown"),
                    "source_document": chunk.get("source_document", "unknown"),
                    "section": chunk.get("section", "N/A"),
                    "page_start": chunk.get("page_start", "?"),
                    "page_end": chunk.get("page_end", "?"),
                    "text_excerpt": chunk.get("raw_text", "")[:200],
                })

                if len(citations) >= limit:
                    return citations

        except (json.JSONDecodeError, IOError):
            continue

    return citations


def generate_draft(topic: str, verbose: bool = False) -> Path:
    """
    Generate topic draft from curated knowledge.

    Returns path to generated draft file.
    """
    normalized = normalize_topic_name(topic)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    draft_filename = f"DRAFT_{normalized}_{timestamp}.md"
    output_path = DRAFTS_DIR / draft_filename

    # Ensure drafts directory exists
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Generating draft for topic: {topic}")
        print(f"Output: {output_path}")
        print()

    # Extract information from curated sources
    glossary_entry = None
    if GLOSSARY_FILE.exists():
        if verbose:
            print("Searching glossary.md...")
        glossary_content = GLOSSARY_FILE.read_text(encoding="utf-8")
        glossary_entry = extract_glossary_entry(topic, glossary_content)
        related_terms = extract_related_terms(topic, glossary_content)
    else:
        related_terms = []

    rules = []
    if RULES_FILE.exists():
        if verbose:
            print("Searching rules.md...")
        rules_content = RULES_FILE.read_text(encoding="utf-8")
        rules = extract_rules(topic, rules_content)

    procedures = extract_procedures(topic)
    if verbose and procedures:
        print(f"Found {len(procedures)} related procedures")

    # Get citations from raw chunks
    if verbose:
        print("Searching chunks for citations...")
    citations = search_chunks_for_citations(topic, limit=20)

    # Build draft content
    content = f"""# Topic: {topic}

> **Status**: DRAFT
> **Created**: {datetime.now(timezone.utc).isoformat()}
> **Last Updated**: {datetime.now(timezone.utc).isoformat()}
> **Reviewed By**: NOT REVIEWED

---

## Definition

"""

    if glossary_entry and glossary_entry["definition"]:
        content += f"""**Primary Definition**:
{glossary_entry["definition"]}

"""
        if glossary_entry["sources"]:
            content += f"""**Source**: {", ".join(glossary_entry["sources"])}

"""
    else:
        content += """**Primary Definition**:
NOT FOUND IN GLOSSARY

**Action Required**: Search source documents manually or mark as not defined.

"""

    content += """**Synonym(s)**: NOT SPECIFIED

---

## Related Terms

"""

    if related_terms:
        content += """| Term | Relationship | Source |
|------|--------------|--------|
"""
        for term, rel in related_terms:
            content += f"| {term} | {rel} | [glossary.md] |\n"
    else:
        content += """NOT SPECIFIED IN SOURCE

"""

    content += """
---

## Sources

### Primary Sources
"""

    if citations:
        seen_sources = set()
        for cite in citations:
            source_key = f"{cite['source_document']}, p.{cite['page_start']}"
            if source_key not in seen_sources:
                content += f"- {cite['source_document']}, Section: {cite['section']}, p.{cite['page_start']}-{cite['page_end']}\n"
                seen_sources.add(source_key)
    else:
        content += "NO SOURCES FOUND\n"

    content += """
**Coverage Assessment**: UNKNOWN (draft)
**Confidence**: LOW (draft)

---

## Rules

### Conditional Behaviors (IF/WHEN -> THEN)

"""

    if rules:
        for i, rule in enumerate(rules, 1):
            content += f"""#### Rule {i}: (From curated rules.md)
**Condition**: {rule['condition']}
**Consequence**: {rule['consequence']}
**Source**: {rule['source']}
**Certainty**: EXPLICIT

"""
    else:
        content += """NO RULES SPECIFIED IN SOURCE

"""

    content += """---

## Behavior

### Normal Operation
"""

    if glossary_entry and glossary_entry["notes"]:
        content += f"""{glossary_entry["notes"]}

**Source**: [glossary.md]

"""
    else:
        content += """BEHAVIOR NOT SPECIFIED IN SOURCE

"""

    content += """### States/Modes
| State/Mode | Description | Trigger | Source |
|------------|-------------|---------|--------|
| (none documented) | | | |

---

## Limitations

### Explicit Constraints
NO LIMITATIONS SPECIFIED IN SOURCE

### Boundary Conditions
NO BOUNDARY CONDITIONS SPECIFIED IN SOURCE

---

## Procedures

"""

    if procedures:
        for proc in procedures:
            content += f"""### {proc['name']}

**Purpose**: See {proc['file']}
**Source**: synth/procedures/{proc['file']}

(Refer to procedure file for complete steps)

"""
    else:
        content += """NO PROCEDURES SPECIFIED IN SOURCE

"""

    content += """---

## Edge Cases

### Documented Edge Cases
NO EDGE CASES SPECIFIED IN SOURCE

---

## Open Questions

> These are gaps in documentation, NOT assumptions or inferences.

1. **Complete definition needed**
   **Why this matters**: Draft extracted from glossary only
   **Search attempted**: glossary.md, rules.md, procedures/
   **Result**: Limited information found

2. **Behavior details missing**
   **Why this matters**: Only basic definition available
   **Search attempted**: Curated knowledge files
   **Result**: Insufficient detail

---

## Verification Status

- [ ] All citations verified against source documents
- [ ] All "NOT SPECIFIED" claims verified (absence confirmed)
- [ ] No inferences or assumptions present
- [ ] Related terms cross-referenced
- [ ] Open questions documented
- [ ] Human review completed

**Reviewer Notes**:
(Add human review notes here)

---

## Metadata

**Source Documents Analyzed**:
"""

    if citations:
        seen_docs = set()
        for cite in citations:
            if cite['source_document'] not in seen_docs:
                content += f"- {cite['source_document']}\n"
                seen_docs.add(cite['source_document'])

    content += f"""
**Chunks Analyzed**: {len(citations)} chunks containing topic mention
**Generated By**: topic_draft.py v1.0.0
**Template Version**: 1.0.0

---

**CRITICAL REMINDER**:
This topic file is a DRAFT generated from curated knowledge files.
It requires human review before promotion to authoritative status.
DO NOT treat this as authoritative knowledge.
"""

    # Write draft file
    output_path.write_text(content, encoding="utf-8")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate topic draft from curated knowledge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "topic",
        type=str,
        help="Topic name (e.g., 'HSI pointers')",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("TOPIC DRAFT GENERATION")
    print("=" * 80)
    print()
    print("WARNING: This generates a DRAFT that requires human review.")
    print("Drafts are NOT authoritative.")
    print()

    try:
        output_path = generate_draft(args.topic, verbose=args.verbose)

        print()
        print("=" * 80)
        print("DRAFT GENERATED")
        print("=" * 80)
        print(f"Output: {output_path}")
        print()
        print("NEXT STEPS (REQUIRED):")
        print("1. Review the draft carefully")
        print("2. Verify all citations against source documents")
        print("3. Fill in missing information from source documents")
        print("4. Remove any inferences or assumptions")
        print("5. Complete all 'NOT SPECIFIED' sections")
        print("6. Add human expertise and context")
        print("7. Move to topics/ and remove DRAFT_ prefix when ready")
        print()
        print("REMEMBER: Only files in topics/ (not drafts/) are authoritative.")
        print("=" * 80)

    except Exception as e:
        print(f"ERROR: Failed to generate draft: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
