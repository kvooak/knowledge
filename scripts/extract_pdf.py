#!/usr/bin/env python3
"""
extract_pdf.py - Mechanical PDF text extraction

CONTRACT:
    Input:  knowledge/sources/<project>/**/*.pdf (recursive)
    Output: knowledge/extracted/<project>/<relative_path>/<doc_name>/<page>.md

STRUCTURE:
    sources/
    ├── ProjectA/           <- Project name
    │   ├── manual.pdf
    │   └── subfolder/
    │       └── guide.pdf
    └── ProjectB/           <- Another project
        └── docs/
            └── spec.pdf

    Direct subfolders under sources/ are considered "projects".
    Project name is tracked in all metadata.

GUARANTEES:
    - One markdown file per page
    - Page numbers preserved in filename and content
    - Headings preserved when detectable (by font size)
    - Project name stored in metadata
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
from typing import Optional

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


def get_project_name(pdf_path: Path, sources_dir: Path) -> Optional[str]:
    """
    Extract project name from PDF path.

    Project = first-level subfolder under sources/

    Examples:
        sources/ProjectA/manual.pdf -> "ProjectA"
        sources/ProjectA/sub/guide.pdf -> "ProjectA"
        sources/manual.pdf -> None (no project, root level)
    """
    try:
        relative = pdf_path.relative_to(sources_dir)
        parts = relative.parts
        if len(parts) > 1:
            return parts[0]  # First folder is the project
        return None  # File is directly in sources/, no project
    except ValueError:
        return None


def get_relative_path_in_project(pdf_path: Path, sources_dir: Path, project_name: Optional[str]) -> Path:
    """
    Get the relative path within a project (excluding project folder and filename).

    Examples:
        sources/ProjectA/manual.pdf -> Path(".")
        sources/ProjectA/sub/guide.pdf -> Path("sub")
        sources/ProjectA/a/b/c/doc.pdf -> Path("a/b/c")
    """
    try:
        relative = pdf_path.relative_to(sources_dir)
        parts = relative.parts

        if project_name and len(parts) > 2:
            # Skip project name and filename, return middle parts
            return Path(*parts[1:-1])
        return Path(".")
    except ValueError:
        return Path(".")


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


def format_page_markdown(
    page_num: int,
    blocks: list,
    doc_name: str,
    project_name: Optional[str] = None,
    relative_path: Optional[Path] = None
) -> str:
    """
    Format extracted blocks as markdown.

    Preserves:
    - Page number in header
    - Project name in metadata
    - Detected headings as markdown headings
    - Original text structure
    """
    project_line = f"> Project: {project_name}" if project_name else "> Project: (none)"
    path_line = f"> Path: {relative_path}" if relative_path and str(relative_path) != "." else ""

    lines = [
        f"# {doc_name} - Page {page_num}",
        "",
        f"> Extracted from: {doc_name}",
        project_line,
    ]

    if path_line:
        lines.append(path_line)

    lines.extend([
        f"> Page: {page_num}",
        f"> Extraction: Mechanical (no LLM)",
        "",
        "---",
        "",
    ])

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


def extract_pdf(
    pdf_path: Path,
    output_dir: Path,
    sources_dir: Path,
    verbose: bool = False
) -> dict:
    """
    Extract all pages from a PDF to individual markdown files.

    Returns extraction metadata for reproducibility.
    """
    doc_name = pdf_path.stem

    # Determine project name and relative path
    project_name = get_project_name(pdf_path, sources_dir)
    relative_path = get_relative_path_in_project(pdf_path, sources_dir, project_name)

    # Build output path: extracted/<project>/<relative_path>/<doc_name>/
    if project_name:
        if str(relative_path) != ".":
            doc_output_dir = output_dir / project_name / relative_path / doc_name
        else:
            doc_output_dir = output_dir / project_name / doc_name
    else:
        doc_output_dir = output_dir / doc_name

    doc_output_dir.mkdir(parents=True, exist_ok=True)

    # Compute input hash for reproducibility
    input_hash = compute_file_hash(pdf_path)

    metadata = {
        "source_file": str(pdf_path),
        "source_hash": input_hash,
        "project_name": project_name,  # Project tracking
        "relative_path": str(relative_path) if relative_path else None,
        "document_name": doc_name,
        "extraction_time": datetime.now(timezone.utc).isoformat(),
        "extractor": "extract_pdf.py",
        "extractor_version": "2.0.0",  # Version bump for project support
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
                human_page_num,
                annotated_blocks,
                doc_name,
                project_name,
                relative_path
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
    parser.add_argument(
        "--project",
        type=str,
        help="Extract only PDFs from a specific project (subfolder name)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    if args.file:
        pdfs = [args.file]
    elif args.project:
        project_dir = args.sources / args.project
        if not project_dir.exists():
            print(f"Project not found: {project_dir}", file=sys.stderr)
            sys.exit(1)
        pdfs = sorted(project_dir.rglob("*.pdf"))
    else:
        pdfs = find_pdfs(args.sources)

    if not pdfs:
        print(f"No PDF files found in {args.sources}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF file(s) to extract")
    print(f"Output directory: {args.output}")
    print()

    # Group by project for reporting
    projects_found = set()
    total_pages = 0

    for pdf_path in pdfs:
        project = get_project_name(pdf_path, args.sources)
        projects_found.add(project or "(root)")

        project_display = f"[{project}] " if project else ""
        print(f"Extracting: {project_display}{pdf_path.name}")

        metadata = extract_pdf(pdf_path, args.output, args.sources, verbose=args.verbose)

        if "error" in metadata:
            print(f"  ERROR: {metadata['error']}", file=sys.stderr)
        else:
            pages = metadata["pages_extracted"]
            total_pages += pages
            print(f"  Pages: {pages}")

    print()
    print(f"Projects found: {', '.join(sorted(projects_found))}")
    print(f"Total pages extracted: {total_pages}")
    print("Extraction complete. Output is deterministic and reproducible.")


if __name__ == "__main__":
    main()
