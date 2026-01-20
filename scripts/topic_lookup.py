#!/usr/bin/env python3
"""
topic_lookup.py - Topic-based knowledge lookup

CONTRACT:
    Input:  Topic name (string)
    Output: Authoritative topic file OR menu of options

GUARANTEES:
    - NEVER auto-generates topics
    - NEVER treats search results as authoritative
    - ONLY returns curated topic files as authoritative
    - Offers explicit options when topic not found
    - No inference, no gap filling

ABSOLUTE PROHIBITIONS:
    - Do NOT synthesize topics on demand
    - Do NOT treat vector search as authoritative
    - Do NOT auto-promote drafts
    - Do NOT claim completeness without curated topic file

VERSION: 1.0.0
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TOPICS_DIR = PROJECT_ROOT / "topics"
DRAFTS_DIR = TOPICS_DIR / "drafts"
SYNTH_DIR = PROJECT_ROOT / "synth"

# Curated knowledge files
GLOSSARY_FILE = SYNTH_DIR / "glossary.md"
RULES_FILE = SYNTH_DIR / "rules.md"
INVARIANTS_FILE = SYNTH_DIR / "invariants.md"
PROCEDURES_DIR = SYNTH_DIR / "procedures"


def normalize_topic_name(topic: str) -> str:
    """
    Normalize topic name to filename format.

    Example: "HSI pointers" -> "hsi_pointers"
    """
    return topic.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def find_topic_file(topic: str) -> Optional[Path]:
    """
    Look for curated topic file.

    Returns Path if curated file exists, None otherwise.
    """
    normalized = normalize_topic_name(topic)
    topic_file = TOPICS_DIR / f"{normalized}.md"

    if topic_file.exists() and topic_file.is_file():
        return topic_file

    return None


def find_draft_file(topic: str) -> Optional[Path]:
    """
    Look for draft topic file.

    Returns Path if draft exists, None otherwise.
    """
    normalized = normalize_topic_name(topic)

    # Look for exact match draft
    draft_file = DRAFTS_DIR / f"DRAFT_{normalized}.md"
    if draft_file.exists():
        return draft_file

    # Look for timestamped drafts
    pattern = f"DRAFT_{normalized}_*.md"
    matches = list(DRAFTS_DIR.glob(pattern))

    if matches:
        # Return most recent
        return sorted(matches, reverse=True)[0]

    return None


def search_glossary(topic: str) -> list[str]:
    """
    Search glossary for topic mentions (non-authoritative).

    Returns list of matching section headers.
    """
    if not GLOSSARY_FILE.exists():
        return []

    matches = []
    content = GLOSSARY_FILE.read_text(encoding="utf-8")

    # Simple search for topic in headers
    for line in content.split("\n"):
        if line.startswith("###") and topic.lower() in line.lower():
            matches.append(line.strip("# ").strip())

    return matches


def search_related_topics() -> list[str]:
    """
    List all curated topic files.

    Returns list of topic names.
    """
    if not TOPICS_DIR.exists():
        return []

    topics = []
    for topic_file in TOPICS_DIR.glob("*.md"):
        if topic_file.name.startswith("_"):
            continue  # Skip template and meta files

        # Convert filename back to readable name
        name = topic_file.stem.replace("_", " ").title()
        topics.append(name)

    return sorted(topics)


def display_topic(topic_file: Path):
    """Display curated topic file content."""
    print("=" * 80)
    print("AUTHORITATIVE TOPIC (CURATED)")
    print("=" * 80)
    print()
    print(topic_file.read_text(encoding="utf-8"))
    print()
    print("=" * 80)
    print(f"Source: {topic_file}")
    print("Status: AUTHORITATIVE (human-reviewed)")
    print("=" * 80)


def display_draft(draft_file: Path):
    """Display draft topic file with clear warning."""
    print("=" * 80)
    print("DRAFT TOPIC - NOT AUTHORITATIVE")
    print("=" * 80)
    print()
    print("WARNING: This is a DRAFT that has NOT been human-reviewed.")
    print("Do NOT treat this as authoritative knowledge.")
    print()
    print(draft_file.read_text(encoding="utf-8"))
    print()
    print("=" * 80)
    print(f"Source: {draft_file}")
    print("Status: DRAFT (requires human review)")
    print("=" * 80)


def offer_options(topic: str, glossary_matches: list[str], related_topics: list[str]):
    """
    Offer explicit options when topic not found.

    Does NOT auto-generate anything.
    """
    print("=" * 80)
    print(f"TOPIC NOT FOUND: '{topic}'")
    print("=" * 80)
    print()
    print("This topic does not exist as a curated knowledge file.")
    print("Vector search results are NOT authoritative.")
    print()
    print("OPTIONS:")
    print()
    print("1. CREATE DRAFT TOPIC")
    print("   Generate a draft topic file for human review.")
    print("   Command:")
    print(f"   python scripts/topic_draft.py \"{topic}\"")
    print()

    if glossary_matches:
        print("2. GLOSSARY REFERENCES (non-authoritative)")
        print("   The following terms were found in glossary.md:")
        for match in glossary_matches[:5]:  # Limit to 5
            print(f"   - {match}")
        if len(glossary_matches) > 5:
            print(f"   ... and {len(glossary_matches) - 5} more")
        print()

    if related_topics:
        print("3. RELATED CURATED TOPICS (authoritative)")
        print("   The following topics have been curated:")
        for rt in related_topics[:10]:  # Limit to 10
            print(f"   - {rt}")
        if len(related_topics) > 10:
            print(f"   ... and {len(related_topics) - 10} more")
        print()
        print("   Use: python scripts/topic_lookup.py \"<topic name>\"")
        print()

    print("4. SEARCH RAW CHUNKS (non-authoritative)")
    print("   Search original document chunks directly.")
    print("   Command:")
    print(f"   python scripts/search_chunks.py \"{topic}\"")
    print()
    print("=" * 80)
    print("REMINDER: Only curated topic files are authoritative.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Look up topic in knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "topic",
        type=str,
        help="Topic name to look up (e.g., 'HSI pointers')",
    )

    parser.add_argument(
        "--show-draft",
        action="store_true",
        help="Show draft if no curated topic exists",
    )

    parser.add_argument(
        "--list-topics",
        action="store_true",
        help="List all curated topics",
    )

    args = parser.parse_args()

    # List topics mode
    if args.list_topics:
        topics = search_related_topics()
        if topics:
            print("CURATED TOPICS:")
            for topic in topics:
                print(f"  - {topic}")
        else:
            print("No curated topics found.")
        sys.exit(0)

    # Look up topic
    print(f"Looking up topic: {args.topic}")
    print()

    # Check for curated topic file (AUTHORITATIVE)
    topic_file = find_topic_file(args.topic)
    if topic_file:
        display_topic(topic_file)
        sys.exit(0)

    # Check for draft (NOT AUTHORITATIVE)
    if args.show_draft:
        draft_file = find_draft_file(args.topic)
        if draft_file:
            display_draft(draft_file)
            sys.exit(0)

    # Topic not found - offer options
    glossary_matches = search_glossary(args.topic)
    related_topics = search_related_topics()

    offer_options(args.topic, glossary_matches, related_topics)
    sys.exit(1)


if __name__ == "__main__":
    main()
