#!/usr/bin/env python3
"""
run.py - Cross-platform build script for knowledge pipeline

This script provides the same functionality as Makefile but works on Windows.
On Linux/Mac, you can still use `make` commands.

USAGE:
    python run.py <target> [options]

TARGETS:
    extract              - Extract text from PDFs
    chunk                - Chunk extracted text
    embed                - Generate embeddings index
    ingest               - Run full pipeline: extract -> chunk -> embed
    synth                - Generate synthesis (requires TYPE and TOPIC)
    synth-test           - Generate synthesis with limit=50
    clean                - Clean generated files
    clean-all            - Clean all including drafts
    clean-index          - Clean index only
    status               - Show pipeline status
    get-chunk-count      - Display total chunk count
    help                 - Show this help

OPTIONS:
    --type TYPE          - Synthesis type (glossary, rules, etc.)
    --topic TOPIC        - Synthesis topic
    --verbose, -v        - Verbose output
    --force              - Force regeneration

EXAMPLES:
    python run.py extract
    python run.py synth --type glossary --topic "flight systems"
    python run.py synth-test --type rules --topic "procedures"
    python run.py clean --verbose
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SOURCES_DIR = PROJECT_ROOT / "sources"
EXTRACTED_DIR = PROJECT_ROOT / "extracted"
CHUNKS_DIR = PROJECT_ROOT / "chunks"
INDEX_DIR = PROJECT_ROOT / "index"
SYNTH_DIR = PROJECT_ROOT / "synth"

# Scripts
EXTRACT_SCRIPT = SCRIPTS_DIR / "extract_pdf.py"
CHUNK_SCRIPT = SCRIPTS_DIR / "chunk_text.py"
EMBED_SCRIPT = SCRIPTS_DIR / "embed_chunks.py"
SYNTH_SCRIPT = SCRIPTS_DIR / "synthesize.py"
CLEAN_SCRIPT = SCRIPTS_DIR / "clean.py"


def run_command(cmd: list[str], description: str = None, verbose: bool = False):
    """Run a subprocess command."""
    if description:
        print(f"\n{'=' * 60}")
        print(description)
        print('=' * 60)

    if verbose:
        print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=not verbose)

    if result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}", file=sys.stderr)
        if not verbose and result.stderr:
            print(result.stderr.decode(), file=sys.stderr)
        sys.exit(result.returncode)

    return result


def get_chunk_count() -> int:
    """Get total chunk count from metadata files."""
    metadata_files = list(CHUNKS_DIR.rglob("_chunking_metadata.json"))
    if not metadata_files:
        return 0

    total = sum(
        json.loads(f.read_text(encoding="utf-8"))["chunks_created"]
        for f in metadata_files
    )
    return total


def target_extract(args):
    """Extract text from PDFs."""
    cmd = [sys.executable, str(EXTRACT_SCRIPT)]
    if args.verbose:
        cmd.append("--verbose")

    run_command(cmd, "EXTRACTING: PDFs -> Markdown", args.verbose)
    print("Extraction complete.")


def target_chunk(args):
    """Chunk extracted text."""
    cmd = [sys.executable, str(CHUNK_SCRIPT)]
    if args.verbose:
        cmd.append("--verbose")

    run_command(cmd, "CHUNKING: Markdown -> JSON", args.verbose)
    print("Chunking complete.")


def target_embed(args):
    """Generate embeddings index."""
    cmd = [sys.executable, str(EMBED_SCRIPT), "--verbose", "--force"]

    run_command(cmd, "EMBEDDING: Chunks -> Index", args.verbose)
    print("Embedding complete.")


def target_ingest(args):
    """Run full pipeline."""
    print("\n" + "=" * 60)
    print("FULL INGESTION PIPELINE")
    print("=" * 60)

    target_extract(args)
    target_chunk(args)
    target_embed(args)

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"- Extracted: {EXTRACTED_DIR}/")
    print(f"- Chunks:    {CHUNKS_DIR}/")
    print(f"- Index:     {INDEX_DIR}/")
    print("\nNext: Run 'python run.py synth --type <type> --topic <topic>'")


def target_synth(args):
    """Generate synthesis with all chunks."""
    if not args.type:
        print("ERROR: --type is required", file=sys.stderr)
        print("Usage: python run.py synth --type glossary --topic 'your topic'")
        print("Types: glossary, rules, invariants, procedures, contradictions, questions")
        sys.exit(1)

    if not args.topic:
        print("ERROR: --topic is required", file=sys.stderr)
        print(f"Usage: python run.py synth --type {args.type} --topic 'your topic'")
        sys.exit(1)

    chunk_count = get_chunk_count()

    print("=" * 60)
    print(f"SYNTHESIS: Generating {args.type} draft")
    print("=" * 60)
    print("WARNING: This uses an LLM. Output requires human review.")
    print(f"Using all {chunk_count} chunks for synthesis...")
    print()

    cmd = [
        sys.executable,
        str(SYNTH_SCRIPT),
        args.type,
        "--topic", args.topic,
        "--limit", str(chunk_count),
        "--full",  # Output as full document, not draft
    ]

    if args.api_key:
        cmd.extend(["--api-key", args.api_key])

    if args.verbose:
        cmd.append("--verbose")

    run_command(cmd, verbose=args.verbose)


def target_synth_test(args):
    """Generate synthesis with limit=50 for testing."""
    if not args.type:
        print("ERROR: --type is required", file=sys.stderr)
        print("Usage: python run.py synth-test --type glossary --topic 'your topic'")
        sys.exit(1)

    if not args.topic:
        print("ERROR: --topic is required", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print(f"SYNTHESIS TEST: Generating {args.type} draft (LIMIT=50)")
    print("=" * 60)
    print("WARNING: This uses an LLM. Output requires human review.")
    print()

    cmd = [
        sys.executable,
        str(SYNTH_SCRIPT),
        args.type,
        "--topic", args.topic,
        "--limit", "50",
    ]

    if args.api_key:
        cmd.extend(["--api-key", args.api_key])

    if args.verbose:
        cmd.append("--verbose")

    run_command(cmd, verbose=args.verbose)


def target_clean(args):
    """Clean generated files."""
    cmd = [sys.executable, str(CLEAN_SCRIPT)]
    if args.verbose:
        cmd.append("--verbose")

    run_command(cmd, verbose=args.verbose)


def target_clean_all(args):
    """Clean all including drafts."""
    cmd = [sys.executable, str(CLEAN_SCRIPT), "--all"]
    if args.verbose:
        cmd.append("--verbose")

    run_command(cmd, verbose=args.verbose)


def target_clean_index(args):
    """Clean index only."""
    print("Removing index/ (safe - fully regenerable)")
    if INDEX_DIR.exists():
        for item in INDEX_DIR.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)
    print("Index cleaned. Run 'python run.py embed' to regenerate.")


def target_status(args):
    """Show pipeline status."""
    print("Knowledge System Status")
    print("=" * 60)
    print()

    print(f"Sources ({SOURCES_DIR}/):")
    pdf_count = len(list(SOURCES_DIR.rglob("*.pdf")))
    print(f"  PDFs: {pdf_count}")
    print()

    print(f"Extracted ({EXTRACTED_DIR}/):")
    if EXTRACTED_DIR.exists():
        page_count = len(list(EXTRACTED_DIR.rglob("page_*.md")))
        print(f"  Pages: {page_count}")
    else:
        print("  Not yet extracted")
    print()

    print(f"Chunks ({CHUNKS_DIR}/):")
    if CHUNKS_DIR.exists():
        chunk_count = len(list(CHUNKS_DIR.rglob("*_chunk_*.json")))
        print(f"  Chunks: {chunk_count}")
    else:
        print("  Not yet chunked")
    print()

    print(f"Index ({INDEX_DIR}/):")
    if (INDEX_DIR / "embeddings.npy").exists():
        print("  Exists (regenerable)")
    else:
        print("  Not yet created")
    print()

    print(f"Synth ({SYNTH_DIR}/):")
    draft_count = len(list((SYNTH_DIR / "drafts").glob("DRAFT_*.md"))) if (SYNTH_DIR / "drafts").exists() else 0
    print(f"  Drafts: {draft_count}")
    print(f"  Curated files: {SYNTH_DIR}/*.md")


def target_get_chunk_count(args):
    """Display total chunk count."""
    count = get_chunk_count()
    print(f"Total chunks: {count}")


def target_help(args):
    """Show help."""
    print(__doc__)


def main():
    parser = argparse.ArgumentParser(
        description="Knowledge pipeline build script (cross-platform)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "target",
        choices=[
            "extract", "chunk", "embed", "ingest",
            "synth", "synth-test",
            "clean", "clean-all", "clean-index",
            "status", "get-chunk-count", "help"
        ],
        help="Build target to execute"
    )

    parser.add_argument("--type", help="Synthesis type")
    parser.add_argument("--topic", help="Synthesis topic")
    parser.add_argument("--api-key", help="Anthropic API key for synthesis")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--force", action="store_true", help="Force regeneration")

    args = parser.parse_args()

    # Map targets to functions
    targets = {
        "extract": target_extract,
        "chunk": target_chunk,
        "embed": target_embed,
        "ingest": target_ingest,
        "synth": target_synth,
        "synth-test": target_synth_test,
        "clean": target_clean,
        "clean-all": target_clean_all,
        "clean-index": target_clean_index,
        "status": target_status,
        "get-chunk-count": target_get_chunk_count,
        "help": target_help,
    }

    # Execute target
    target_func = targets[args.target]
    target_func(args)


if __name__ == "__main__":
    main()
