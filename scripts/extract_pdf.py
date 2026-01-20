#!/usr/bin/env python3
"""
extract_pdf.py - Mechanical PDF text extraction

CONTRACT:
    Input:  knowledge/sources/**/*.pdf
    Output: knowledge/extracted/<doc_name>/<page>.md

GUARANTEES:
    - One markdown file per page
    - Page numbers preserved in filename and content
    - Headings preserved when detectable (by font size)
    - Deterministic output (same input = same output)
    - NO LLM usage
    - Mechanical extraction ONLY

DEPENDENCIES:
    - PyMuPDF (fitz): pip install pymupdf
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


# Project paths (relative to script location)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SOURCES_DIR = PROJECT_ROOT / "sources"
EXTRACTED_DIR = PROJECT_ROOT / "extracted"


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of file for reproducibility tracking."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def detect_headings(blocks: list, page_height: float) -> list:
    """
    Detect potential headings based on font size.
    Returns blocks with heading level annotations.

    Heuristic: Text with font size > median + threshold is likely a heading.
    This is mechanical detection, not semantic understanding.
    """
    if not blocks:
        return []

    # Collect font sizes from text spans
    font_sizes = []
    for block in blocks:
        if block.get("type") == 0:  # Text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_sizes.append(span.get("size", 12))

    if not font_sizes:
        return blocks

    # Calculate median font size
    sorted_sizes = sorted(font_sizes)
    median_size = sorted_sizes[len(sorted_sizes) // 2]

    # Annotate blocks with heading detection
    annotated = []
    for block in blocks:
        block_copy = dict(block)
        if block.get("type") == 0:
            max_font_size = 0
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    max_font_size = max(max_font_size, span.get("size", 12))

            # Heading level based on font size difference from median
            if max_font_size > median_size * 1.5:
                block_copy["heading_level"] = 1
            elif max_font_size > median_size * 1.25:
                block_copy["heading_level"] = 2
            elif max_font_size > median_size * 1.1:
                block_copy["heading_level"] = 3
            else:
                block_copy["heading_level"] = 0
        annotated.append(block_copy)

    return annotated


def extract_text_from_block(block: dict) -> str:
    """Extract plain text from a block structure."""
    if block.get("type") != 0:  # Not a text block
        return ""

    lines = []
    for line in block.get("lines", []):
        line_text = ""
        for span in line.get("spans", []):
            line_text += span.get("text", "")
        lines.append(line_text)

    return " ".join(lines).strip()


def format_page_markdown(page_num: int, blocks: list, doc_name: str) -> str:
    """
    Format extracted blocks as markdown.

    Preserves:
    - Page number in header
    - Detected headings as markdown headings
    - Original text structure
    """
    lines = [
        f"# {doc_name} - Page {page_num}",
        "",
        f"> Extracted from: {doc_name}",
        f"> Page: {page_num}",
        f"> Extraction: Mechanical (no LLM)",
        "",
        "---",
        "",
    ]

    for block in blocks:
        text = extract_text_from_block(block)
        if not text:
            continue

        heading_level = block.get("heading_level", 0)
        if heading_level == 1:
            lines.append(f"## {text}")
        elif heading_level == 2:
            lines.append(f"### {text}")
        elif heading_level == 3:
            lines.append(f"#### {text}")
        else:
            lines.append(text)
        lines.append("")

    return "\n".join(lines)


def extract_pdf(pdf_path: Path, output_dir: Path, verbose: bool = False) -> dict:
    """
    Extract all pages from a PDF to individual markdown files.

    Returns extraction metadata for reproducibility.
    """
    doc_name = pdf_path.stem
    doc_output_dir = output_dir / doc_name
    doc_output_dir.mkdir(parents=True, exist_ok=True)

    # Compute input hash for reproducibility
    input_hash = compute_file_hash(pdf_path)

    metadata = {
        "source_file": str(pdf_path),
        "source_hash": input_hash,
        "extraction_time": datetime.now(timezone.utc).isoformat(),
        "extractor": "extract_pdf.py",
        "extractor_version": "1.0.0",
        "pages_extracted": 0,
        "output_directory": str(doc_output_dir),
    }

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        metadata["error"] = str(e)
        return metadata

    try:
        for page_num in range(len(doc)):
            page = doc[page_num]

            # Get detailed block information
            blocks = page.get_text("dict")["blocks"]

            # Detect headings mechanically
            annotated_blocks = detect_headings(blocks, page.rect.height)

            # Format as markdown
            # Page numbers are 1-indexed for human readability
            human_page_num = page_num + 1
            markdown_content = format_page_markdown(
                human_page_num, annotated_blocks, doc_name
            )

            # Write page file
            page_file = doc_output_dir / f"page_{human_page_num:04d}.md"
            page_file.write_text(markdown_content, encoding="utf-8")

            if verbose:
                print(f"  Extracted: {page_file.name}")

            metadata["pages_extracted"] += 1
    finally:
        doc.close()

    # Write extraction metadata
    metadata_file = doc_output_dir / "_extraction_metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return metadata


def find_pdfs(sources_dir: Path) -> list[Path]:
    """Find all PDF files in sources directory recursively."""
    return sorted(sources_dir.rglob("*.pdf"))


def main():
    parser = argparse.ArgumentParser(
        description="Extract PDF pages to markdown files (mechanical extraction, no LLM)"
    )
    parser.add_argument(
        "--sources",
        type=Path,
        default=SOURCES_DIR,
        help=f"Source directory containing PDFs (default: {SOURCES_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=EXTRACTED_DIR,
        help=f"Output directory for extracted text (default: {EXTRACTED_DIR})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Extract a single PDF file instead of all in sources",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    if args.file:
        pdfs = [args.file]
    else:
        pdfs = find_pdfs(args.sources)

    if not pdfs:
        print(f"No PDF files found in {args.sources}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF file(s) to extract")
    print(f"Output directory: {args.output}")
    print()

    total_pages = 0
    for pdf_path in pdfs:
        print(f"Extracting: {pdf_path.name}")
        metadata = extract_pdf(pdf_path, args.output, verbose=args.verbose)

        if "error" in metadata:
            print(f"  ERROR: {metadata['error']}", file=sys.stderr)
        else:
            pages = metadata["pages_extracted"]
            total_pages += pages
            print(f"  Pages: {pages}")

    print()
    print(f"Total pages extracted: {total_pages}")
    print("Extraction complete. Output is deterministic and reproducible.")


if __name__ == "__main__":
    main()
