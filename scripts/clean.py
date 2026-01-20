#!/usr/bin/env python3
"""
clean.py - Clean generated files from knowledge pipeline

CONTRACT:
    Removes: extracted/, chunks/, index/ contents
    Preserves: synth/ (human-curated knowledge)

USAGE:
    python scripts/clean.py [--all]

OPTIONS:
    --all       Also clean synth/drafts/ (keeps curated synth files)
    --help      Show this help message

GUARANTEES:
    - NEVER deletes synth/*.md curated files
    - NEVER deletes synth/procedures/*.md (non-draft) files
    - NEVER deletes sources/ (original PDFs)
    - Safe to run at any time
"""

import argparse
import shutil
import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
EXTRACTED_DIR = PROJECT_ROOT / "extracted"
CHUNKS_DIR = PROJECT_ROOT / "chunks"
INDEX_DIR = PROJECT_ROOT / "index"
SYNTH_DRAFTS_DIR = PROJECT_ROOT / "synth" / "drafts"

# Protected directories that must NEVER be deleted
PROTECTED_DIRS = [
    PROJECT_ROOT / "sources",
    PROJECT_ROOT / "synth",
]

# Protected files that must NEVER be deleted
PROTECTED_FILES = [
    PROJECT_ROOT / "synth" / "glossary.md",
    PROJECT_ROOT / "synth" / "rules.md",
    PROJECT_ROOT / "synth" / "invariants.md",
    PROJECT_ROOT / "synth" / "contradictions.md",
    PROJECT_ROOT / "synth" / "open_questions.md",
]


def clean_directory(directory: Path, verbose: bool = False) -> int:
    """
    Clean all contents of a directory but keep the directory itself.

    Returns number of items removed.
    """
    if not directory.exists():
        if verbose:
            print(f"  Directory does not exist: {directory}")
        return 0

    count = 0
    for item in directory.iterdir():
        try:
            if item.is_file():
                item.unlink()
                count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                count += 1

            if verbose:
                print(f"  Removed: {item.name}")
        except Exception as e:
            print(f"  Warning: Could not remove {item}: {e}", file=sys.stderr)

    return count


def clean_drafts(verbose: bool = False) -> int:
    """
    Clean only draft files from synth/drafts/.

    Returns number of drafts removed.
    """
    if not SYNTH_DRAFTS_DIR.exists():
        if verbose:
            print(f"  Drafts directory does not exist: {SYNTH_DRAFTS_DIR}")
        return 0

    count = 0
    for draft_file in SYNTH_DRAFTS_DIR.glob("DRAFT_*.md"):
        try:
            draft_file.unlink()
            count += 1
            if verbose:
                print(f"  Removed draft: {draft_file.name}")
        except Exception as e:
            print(f"  Warning: Could not remove {draft_file}: {e}", file=sys.stderr)

    return count


def main():
    parser = argparse.ArgumentParser(
        description="Clean generated files (preserves curated knowledge)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/clean.py              # Clean extracted, chunks, index
  python scripts/clean.py --all        # Also clean drafts
  python scripts/clean.py --verbose    # Show detailed output

Protected (NEVER deleted):
  - sources/               (original PDFs)
  - synth/*.md             (curated knowledge)
  - synth/procedures/*.md  (non-draft procedures)
        """
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Also clean synth/drafts/ (keeps curated files)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CLEANING GENERATED FILES")
    print("=" * 60)
    print()

    if args.verbose:
        print("Protected directories (NEVER deleted):")
        for protected in PROTECTED_DIRS:
            print(f"  - {protected.relative_to(PROJECT_ROOT)}/")
        print()
        print("Protected files (NEVER deleted):")
        for protected in PROTECTED_FILES:
            if protected.exists():
                print(f"  - {protected.relative_to(PROJECT_ROOT)}")
        print()

    total_removed = 0

    # Clean extracted/
    print("Cleaning extracted/ ...")
    count = clean_directory(EXTRACTED_DIR, verbose=args.verbose)
    total_removed += count
    print(f"  Removed {count} items")
    print()

    # Clean chunks/
    print("Cleaning chunks/ ...")
    count = clean_directory(CHUNKS_DIR, verbose=args.verbose)
    total_removed += count
    print(f"  Removed {count} items")
    print()

    # Clean index/
    print("Cleaning index/ ...")
    count = clean_directory(INDEX_DIR, verbose=args.verbose)
    total_removed += count
    print(f"  Removed {count} items")
    print()

    # Clean drafts if --all
    if args.all:
        print("Cleaning synth/drafts/ ...")
        count = clean_drafts(verbose=args.verbose)
        total_removed += count
        print(f"  Removed {count} draft files")
        print()

    print("=" * 60)
    print(f"CLEANING COMPLETE - Removed {total_removed} items")
    print("=" * 60)
    print()
    print("Preserved:")
    print("  - sources/ (original PDFs)")
    print("  - synth/*.md (curated knowledge)")
    if not args.all:
        print("  - synth/drafts/ (use --all to clean)")
    print()
    print("Ready to run pipeline:")
    print("  1. python scripts/extract_pdf.py")
    print("  2. python scripts/chunk_text.py")
    print("  3. python scripts/embed_chunks.py --force")
    print("  4. python scripts/synthesize.py <type> --topic 'topic'")


if __name__ == "__main__":
    main()
