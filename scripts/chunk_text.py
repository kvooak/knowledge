#!/usr/bin/env python3
"""
chunk_text.py - Semantic chunking of extracted text

CONTRACT:
    Input:  knowledge/extracted/<doc_name>/<page>.md
    Output: knowledge/chunks/<doc_name>/*.json

GUARANTEES:
    - Each JSON file represents ONE semantic idea
    - Includes: id, source_document, section, page_range, raw_text
    - Chunk size target: 300-800 tokens
    - NO embeddings
    - NO LLM usage
    - Deterministic output

CHUNK SCHEMA:
{
    "id": "doc_name_chunk_0001",
    "source_document": "document_name",
    "section": "Heading text or null",
    "page_start": 1,
    "page_end": 1,
    "raw_text": "The actual text content",
    "token_count_estimate": 350,
    "chunk_index": 1,
    "total_chunks": 100,
    "created_at": "ISO timestamp"
}
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
EXTRACTED_DIR = PROJECT_ROOT / "extracted"
CHUNKS_DIR = PROJECT_ROOT / "chunks"

# Chunking parameters
MIN_CHUNK_TOKENS = 300
MAX_CHUNK_TOKENS = 800
TARGET_CHUNK_TOKENS = 500


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using simple word-based heuristic.

    This is a mechanical estimation, not exact tokenization.
    Assumes ~1.3 tokens per word on average for English text.
    """
    words = len(text.split())
    return int(words * 1.3)


def generate_chunk_id(doc_name: str, chunk_index: int) -> str:
    """Generate deterministic chunk ID."""
    return f"{doc_name}_chunk_{chunk_index:04d}"


def extract_page_number(filename: str) -> Optional[int]:
    """Extract page number from filename like 'page_0001.md'."""
    match = re.search(r"page_(\d+)", filename)
    if match:
        return int(match.group(1))
    return None


def extract_sections_from_page(content: str) -> list[dict]:
    """
    Parse markdown content into sections based on headings.

    Returns list of {heading, text, level} dicts.
    """
    lines = content.split("\n")
    sections = []
    current_section = {"heading": None, "text": [], "level": 0}

    for line in lines:
        # Skip metadata block at top
        if line.startswith(">") or line.startswith("---") or line.startswith("# "):
            if line.startswith("# ") and " - Page " in line:
                continue  # Skip page header
            continue

        # Check for headings
        heading_match = re.match(r"^(#{2,4})\s+(.+)$", line)
        if heading_match:
            # Save previous section if it has content
            if current_section["text"]:
                current_section["text"] = "\n".join(current_section["text"]).strip()
                if current_section["text"]:
                    sections.append(current_section)

            # Start new section
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            current_section = {"heading": heading, "text": [], "level": level}
        else:
            current_section["text"].append(line)

    # Don't forget last section
    if current_section["text"]:
        current_section["text"] = "\n".join(current_section["text"]).strip()
        if current_section["text"]:
            sections.append(current_section)

    return sections


def chunk_sections(
    sections: list[dict], doc_name: str, page_num: int
) -> list[dict]:
    """
    Split sections into chunks of appropriate size.

    Respects section boundaries when possible.
    """
    chunks = []

    for section in sections:
        text = section["text"]
        heading = section["heading"]
        tokens = estimate_tokens(text)

        if tokens <= MAX_CHUNK_TOKENS:
            # Section fits in one chunk
            chunks.append({
                "section": heading,
                "text": text,
                "page_start": page_num,
                "page_end": page_num,
                "token_estimate": tokens,
            })
        else:
            # Need to split section into multiple chunks
            # Split on paragraph boundaries (double newline)
            paragraphs = re.split(r"\n\s*\n", text)

            current_chunk_text = []
            current_tokens = 0

            for para in paragraphs:
                para_tokens = estimate_tokens(para)

                if current_tokens + para_tokens > MAX_CHUNK_TOKENS and current_chunk_text:
                    # Save current chunk
                    chunk_text = "\n\n".join(current_chunk_text)
                    chunks.append({
                        "section": heading,
                        "text": chunk_text,
                        "page_start": page_num,
                        "page_end": page_num,
                        "token_estimate": current_tokens,
                    })
                    current_chunk_text = [para]
                    current_tokens = para_tokens
                else:
                    current_chunk_text.append(para)
                    current_tokens += para_tokens

            # Don't forget remaining text
            if current_chunk_text:
                chunk_text = "\n\n".join(current_chunk_text)
                chunks.append({
                    "section": heading,
                    "text": chunk_text,
                    "page_start": page_num,
                    "page_end": page_num,
                    "token_estimate": estimate_tokens(chunk_text),
                })

    return chunks


def merge_small_chunks(chunks: list[dict]) -> list[dict]:
    """
    Merge consecutive small chunks from same section.

    Maintains page range tracking.
    """
    if not chunks:
        return []

    merged = []
    current = dict(chunks[0])

    for chunk in chunks[1:]:
        combined_tokens = current["token_estimate"] + chunk["token_estimate"]

        # Merge if same section and combined size is acceptable
        if (
            chunk["section"] == current["section"]
            and combined_tokens <= MAX_CHUNK_TOKENS
            and current["token_estimate"] < MIN_CHUNK_TOKENS
        ):
            current["text"] = current["text"] + "\n\n" + chunk["text"]
            current["page_end"] = chunk["page_end"]
            current["token_estimate"] = combined_tokens
        else:
            merged.append(current)
            current = dict(chunk)

    merged.append(current)
    return merged


def process_document(doc_dir: Path, output_dir: Path, verbose: bool = False) -> dict:
    """
    Process all pages of a document into chunks.

    Returns processing metadata.
    """
    doc_name = doc_dir.name
    doc_output_dir = output_dir / doc_name
    doc_output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "source_document": doc_name,
        "input_directory": str(doc_dir),
        "output_directory": str(doc_output_dir),
        "processing_time": datetime.now(timezone.utc).isoformat(),
        "processor": "chunk_text.py",
        "processor_version": "1.0.0",
        "pages_processed": 0,
        "chunks_created": 0,
        "token_range": {"min": MAX_CHUNK_TOKENS, "max": 0},
    }

    # Collect all pages
    page_files = sorted(doc_dir.glob("page_*.md"))

    if not page_files:
        metadata["error"] = "No page files found"
        return metadata

    all_chunks = []

    for page_file in page_files:
        page_num = extract_page_number(page_file.name)
        if page_num is None:
            continue

        content = page_file.read_text(encoding="utf-8")
        sections = extract_sections_from_page(content)
        page_chunks = chunk_sections(sections, doc_name, page_num)
        all_chunks.extend(page_chunks)
        metadata["pages_processed"] += 1

    # Merge small chunks
    all_chunks = merge_small_chunks(all_chunks)

    # Finalize and write chunks
    total_chunks = len(all_chunks)

    for idx, chunk in enumerate(all_chunks, start=1):
        chunk_id = generate_chunk_id(doc_name, idx)

        chunk_data = {
            "id": chunk_id,
            "source_document": doc_name,
            "section": chunk["section"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "raw_text": chunk["text"],
            "token_count_estimate": chunk["token_estimate"],
            "chunk_index": idx,
            "total_chunks": total_chunks,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Update token range stats
        metadata["token_range"]["min"] = min(
            metadata["token_range"]["min"], chunk["token_estimate"]
        )
        metadata["token_range"]["max"] = max(
            metadata["token_range"]["max"], chunk["token_estimate"]
        )

        # Write chunk file
        chunk_file = doc_output_dir / f"{chunk_id}.json"
        chunk_file.write_text(json.dumps(chunk_data, indent=2), encoding="utf-8")

        if verbose:
            print(f"  Created: {chunk_file.name} ({chunk['token_estimate']} tokens)")

        metadata["chunks_created"] += 1

    # Write processing metadata
    metadata_file = doc_output_dir / "_chunking_metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return metadata


def find_extracted_docs(extracted_dir: Path) -> list[Path]:
    """Find all extracted document directories."""
    docs = []
    for item in extracted_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            docs.append(item)
    return sorted(docs)


def main():
    parser = argparse.ArgumentParser(
        description="Chunk extracted text into semantic units (no LLM)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=EXTRACTED_DIR,
        help=f"Input directory with extracted text (default: {EXTRACTED_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=CHUNKS_DIR,
        help=f"Output directory for chunks (default: {CHUNKS_DIR})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )
    parser.add_argument(
        "--doc",
        type=str,
        help="Process only a specific document by name",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    if args.doc:
        doc_dirs = [args.input / args.doc]
        if not doc_dirs[0].exists():
            print(f"ERROR: Document not found: {doc_dirs[0]}", file=sys.stderr)
            sys.exit(1)
    else:
        doc_dirs = find_extracted_docs(args.input)

    if not doc_dirs:
        print(f"No extracted documents found in {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(doc_dirs)} document(s) to chunk")
    print(f"Output directory: {args.output}")
    print(f"Target chunk size: {MIN_CHUNK_TOKENS}-{MAX_CHUNK_TOKENS} tokens")
    print()

    total_chunks = 0
    for doc_dir in doc_dirs:
        print(f"Chunking: {doc_dir.name}")
        metadata = process_document(doc_dir, args.output, verbose=args.verbose)

        if "error" in metadata:
            print(f"  ERROR: {metadata['error']}", file=sys.stderr)
        else:
            chunks = metadata["chunks_created"]
            total_chunks += chunks
            token_min = metadata["token_range"]["min"]
            token_max = metadata["token_range"]["max"]
            print(f"  Chunks: {chunks} (tokens: {token_min}-{token_max})")

    print()
    print(f"Total chunks created: {total_chunks}")
    print("Chunking complete. No LLM was used. Output is deterministic.")


if __name__ == "__main__":
    main()
