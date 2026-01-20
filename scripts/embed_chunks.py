#!/usr/bin/env python3
"""
embed_chunks.py - Generate embeddings index for semantic search

CONTRACT:
    Input:  knowledge/chunks/<doc_name>/*.json
    Output: knowledge/index/

GUARANTEES:
    - Index is fully regenerable from chunks
    - Index is NOT the source of truth
    - Index can be deleted and recreated at any time
    - Embeddings are for retrieval only, not for making decisions

CRITICAL NOTES:
    - The index is a SEARCH TOOL, not a knowledge store
    - Truth lives in synth/*.md (curated by humans)
    - Deleting index/ loses nothing; regenerate with: make embed

DEPENDENCIES:
    - sentence-transformers: pip install sentence-transformers
    - numpy: pip install numpy

INDEX STRUCTURE:
    index/
    ├── embeddings.npy       # Numpy array of embeddings
    ├── chunk_ids.json       # List of chunk IDs in same order
    ├── metadata.json        # Index generation metadata
    └── _INDEX_IS_NOT_TRUTH  # Marker file with warning
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("ERROR: numpy not installed. Run: pip install numpy", file=sys.stderr)
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print(
        "ERROR: sentence-transformers not installed. "
        "Run: pip install sentence-transformers",
        file=sys.stderr,
    )
    sys.exit(1)


# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CHUNKS_DIR = PROJECT_ROOT / "chunks"
INDEX_DIR = PROJECT_ROOT / "index"

# Embedding model - small and fast, good for semantic search
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Warning text for marker file
INDEX_WARNING = """
================================================================================
                        WARNING: INDEX IS NOT TRUTH
================================================================================

This index directory contains SEARCH ARTIFACTS only.

The index:
    - Is fully regenerable from chunks/
    - Can be deleted at any time without data loss
    - Is NOT the source of truth for any knowledge
    - Should NEVER be used to make authoritative claims

Truth lives in:
    - synth/glossary.md (curated definitions)
    - synth/rules.md (curated rules)
    - synth/invariants.md (curated invariants)
    - synth/procedures/ (curated procedures)

These synth files are human-reviewed and authoritative.
The index is just a search tool to find relevant chunks.

To regenerate this index:
    make embed

================================================================================
"""


def load_chunks(chunks_dir: Path) -> list[dict]:
    """Load all chunk JSON files from all documents (recursive)."""
    chunks = []

    # Use recursive glob to find all chunk JSON files
    for chunk_file in chunks_dir.rglob("*.json"):
        if chunk_file.name.startswith("_"):
            continue  # Skip metadata files

        try:
            chunk_data = json.loads(chunk_file.read_text(encoding="utf-8"))
            chunk_data["_file_path"] = str(chunk_file)
            chunks.append(chunk_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {chunk_file}: {e}", file=sys.stderr)

    # Sort by document and chunk index for deterministic ordering
    chunks.sort(key=lambda c: (c.get("source_document", ""), c.get("chunk_index", 0)))

    return chunks


def create_index(
    chunks: list[dict],
    output_dir: Path,
    model_name: str = DEFAULT_MODEL,
    verbose: bool = False,
) -> dict:
    """
    Create embeddings index from chunks.

    Returns generation metadata.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "generator": "embed_chunks.py",
        "generator_version": "1.0.0",
        "model": model_name,
        "chunk_count": len(chunks),
        "embedding_dimension": None,
        "is_truth": False,  # Explicit: this is NOT authoritative
        "regenerable": True,
        "warning": "Index is for search only. Truth lives in synth/*.md",
    }

    if not chunks:
        metadata["error"] = "No chunks to embed"
        return metadata

    # Load embedding model
    if verbose:
        print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)

    # Extract texts for embedding
    texts = [chunk.get("raw_text", "") for chunk in chunks]
    chunk_ids = [chunk.get("id", f"unknown_{i}") for i, chunk in enumerate(chunks)]

    # Generate embeddings
    if verbose:
        print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=verbose,
        convert_to_numpy=True,
    )

    metadata["embedding_dimension"] = embeddings.shape[1]

    # Save embeddings as numpy array
    embeddings_file = output_dir / "embeddings.npy"
    np.save(embeddings_file, embeddings)
    if verbose:
        print(f"Saved embeddings: {embeddings_file}")

    # Save chunk IDs in same order
    chunk_ids_file = output_dir / "chunk_ids.json"
    chunk_ids_file.write_text(json.dumps(chunk_ids, indent=2), encoding="utf-8")
    if verbose:
        print(f"Saved chunk IDs: {chunk_ids_file}")

    # Save metadata
    metadata_file = output_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if verbose:
        print(f"Saved metadata: {metadata_file}")

    # Create warning marker file
    warning_file = output_dir / "_INDEX_IS_NOT_TRUTH"
    warning_file.write_text(INDEX_WARNING, encoding="utf-8")
    if verbose:
        print(f"Created warning marker: {warning_file}")

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Generate embeddings index for semantic search (regenerable, not truth)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=CHUNKS_DIR,
        help=f"Input directory with chunks (default: {CHUNKS_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INDEX_DIR,
        help=f"Output directory for index (default: {INDEX_DIR})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Sentence transformer model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if index exists",
    )

    args = parser.parse_args()

    # Check if index exists
    if (args.output / "embeddings.npy").exists() and not args.force:
        print("Index already exists. Use --force to regenerate.")
        print("Remember: The index is NOT truth and can be safely regenerated.")
        sys.exit(0)

    # Load chunks
    print(f"Loading chunks from: {args.input}")
    chunks = load_chunks(args.input)

    if not chunks:
        print(f"ERROR: No chunks found in {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(chunks)} chunks to embed")
    print(f"Using model: {args.model}")
    print()

    # Create index
    metadata = create_index(chunks, args.output, args.model, verbose=args.verbose)

    if "error" in metadata:
        print(f"ERROR: {metadata['error']}", file=sys.stderr)
        sys.exit(1)

    print()
    print(f"Index created: {args.output}")
    print(f"Chunks indexed: {metadata['chunk_count']}")
    print(f"Embedding dimension: {metadata['embedding_dimension']}")
    print()
    print("=" * 60)
    print("REMINDER: This index is NOT the source of truth.")
    print("Truth lives in synth/*.md (human-curated files).")
    print("This index can be deleted and regenerated at any time.")
    print("=" * 60)


if __name__ == "__main__":
    main()
