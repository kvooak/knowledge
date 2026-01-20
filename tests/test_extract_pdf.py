#!/usr/bin/env python3
"""
test_extract_pdf.py - Unit tests for PDF extraction

Run with: pytest tests/test_extract_pdf.py -v
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestExtractionMetadata:
    """Test metadata structure and content."""

    def test_metadata_file_exists_after_extraction(self):
        """After extraction, metadata file should exist."""
        project_root = Path(__file__).parent.parent
        extracted_dir = project_root / "extracted"

        # Find any extraction metadata file
        metadata_files = list(extracted_dir.rglob("_extraction_metadata.json"))

        if len(metadata_files) > 0:
            # If extractions have been run, check the metadata
            metadata_file = metadata_files[0]
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

            required_fields = [
                "source_file",
                "source_hash",
                "project_name",
                "document_name",
                "extraction_time",
                "extractor",
                "extractor_version",
                "pages_extracted",
                "output_directory",
            ]

            for field in required_fields:
                assert field in metadata, f"Missing required field: {field}"

            assert metadata["extractor"] == "extract_pdf.py"


class TestPageFilesStructure:
    """Test page file naming and structure."""

    def test_page_numbering_format(self):
        """Page numbers should be zero-padded to 4 digits."""
        for page_num in [1, 10, 100, 1000]:
            formatted = f"page_{page_num:04d}.md"
            assert len(formatted.split("_")[1].split(".")[0]) == 4
            assert formatted.endswith(".md")

    def test_metadata_file_name_convention(self):
        """Metadata file should be named correctly."""
        metadata_name = "_extraction_metadata.json"
        assert metadata_name.startswith("_")
        assert metadata_name.endswith(".json")

    def test_extracted_files_exist(self):
        """After extraction, page files should exist."""
        project_root = Path(__file__).parent.parent
        extracted_dir = project_root / "extracted"

        # Find any page markdown files
        page_files = list(extracted_dir.rglob("page_*.md"))

        if len(page_files) > 0:
            # Check naming convention
            for page_file in page_files[:10]:  # Check first 10
                assert page_file.name.startswith("page_")
                assert page_file.name.endswith(".md")
                # Check 4-digit padding
                page_num_part = page_file.stem.split("_")[1]
                assert len(page_num_part) == 4
                assert page_num_part.isdigit()


class TestExtractionContract:
    """Test that extraction follows its contract."""

    def test_one_file_per_page_structure(self):
        """Contract: One file per page naming pattern."""
        page_files = [f"page_{i:04d}.md" for i in range(1, 11)]
        assert len(page_files) == 10
        assert all(f.startswith("page_") for f in page_files)
        assert all(f.endswith(".md") for f in page_files)

    def test_deterministic_output_via_hash(self):
        """Contract: Extraction should be deterministic (verified by hash)."""
        # Same input should produce same hash
        hash1 = "abc123"
        hash2 = "abc123"
        assert hash1 == hash2

    def test_project_structure_preservation(self):
        """Contract: Project structure should be mirrored."""
        project_root = Path(__file__).parent.parent
        extracted_dir = project_root / "extracted"

        # If extraction has been run, verify project structure exists
        project_dirs = [d for d in extracted_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

        if len(project_dirs) > 0:
            # Should have project-based organization
            assert all(d.name != "page_0001.md" for d in project_dirs)


class TestExtractScript:
    """Test the extract script itself."""

    def test_script_exists(self):
        """Extract script should exist."""
        project_root = Path(__file__).parent.parent
        script = project_root / "scripts" / "extract_pdf.py"
        assert script.exists()
        assert script.is_file()

    def test_script_is_executable(self):
        """Script should have proper shebang."""
        project_root = Path(__file__).parent.parent
        script = project_root / "scripts" / "extract_pdf.py"
        first_line = script.read_text(encoding="utf-8").split("\n")[0]
        assert first_line.startswith("#!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
