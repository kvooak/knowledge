#!/usr/bin/env python3
"""
search_chunks.py - Search raw chunks (non-authoritative)

CONTRACT:
    Input:  Search term (string)
    Output: Matching chunks with citations

GUARANTEES:
    - Clearly labeled as NON-AUTHORITATIVE
    - Shows raw document excerpts only
    - Provides citations for manual verification
    - Does NOT interpret or synthesize

WARNINGS:
    - This is RAW search, not authoritative knowledge
    - Always verify against source documents
    - Chunks may be out of context
    - Use curated topics when available

VERSION: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CHUNKS_DIR = PROJECT_ROOT / "chunks"


def search_chunks(query: str, limit: int = 20, context_chars: int = 300) -> list[dict]:
    """
    Search chunks for query string.

    Returns list of matching chunks with metadata.
    """
    matches = []

    for chunk_file in CHUNKS_DIR.rglob("*.json"):
        if chunk_file.name.startswith("_"):
            continue  # Skip metadata files

        try:
            chunk = json.loads(chunk_file.read_text(encoding="utf-8"))
            raw_text = chunk.get("raw_text", "")

            if query.lower() in raw_text.lower():
                # Find query position for context
                pos = raw_text.lower().find(query.lower())
                start = max(0, pos - context_chars // 2)
                end = min(len(raw_text), pos + len(query) + context_chars // 2)

                context = raw_text[start:end]
                if start > 0:
                    context = "..." + context
                if end < len(raw_text):
                    context = context + "..."

                matches.append({
                    "id": chunk.get("id", "unknown"),
                    "source_document": chunk.get("source_document", "unknown"),
                    "project_name": chunk.get("project_name", "unknown"),
                    "section": chunk.get("section", "N/A"),
                    "page_start": chunk.get("page_start", "?"),
                    "page_end": chunk.get("page_end", "?"),
                    "context": context,
                    "chunk_index": chunk.get("chunk_index", 0),
                })

                if len(matches) >= limit:
                    return matches

        except (json.JSONDecodeError, IOError):
            continue

    return matches


def display_results(query: str, matches: list[dict]):
    """Display search results with clear warnings."""
    print("=" * 80)
    print("RAW CHUNK SEARCH - NON-AUTHORITATIVE")
    print("=" * 80)
    print()
    print("WARNING: These are raw document excerpts, NOT authoritative knowledge.")
    print("Always verify against source documents.")
    print("Use curated topics when available.")
    print()
    print(f"Query: '{query}'")
    print(f"Matches found: {len(matches)}")
    print()

    if not matches:
        print("No matches found.")
        print()
        print("SUGGESTIONS:")
        print("1. Try different search terms")
        print("2. Check for typos")
        print("3. Search curated glossary: python scripts/topic_lookup.py \"<term>\"")
        print("=" * 80)
        return

    for i, match in enumerate(matches, 1):
        print(f"[{i}] {match['source_document']}")
        print(f"    Section: {match['section']}")
        print(f"    Pages: {match['page_start']}-{match['page_end']}")
        print(f"    Chunk: {match['id']}")
        print()
        print(f"    {match['context']}")
        print()
        print("-" * 80)
        print()

    print("=" * 80)
    print("REMINDER: This is RAW search, not authoritative knowledge.")
    print("Create a curated topic file for authoritative reference.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Search raw chunks (non-authoritative)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "query",
        type=str,
        help="Search query",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of results (default: 20)",
    )

    parser.add_argument(
        "--context",
        type=int,
        default=300,
        help="Context characters around match (default: 300)",
    )

    args = parser.parse_args()

    matches = search_chunks(args.query, limit=args.limit, context_chars=args.context)
    display_results(args.query, matches)


if __name__ == "__main__":
    main()
