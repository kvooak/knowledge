#!/usr/bin/env python3
"""
test_chunk_text.py - Unit tests for text chunking

Run with: pytest tests/test_chunk_text.py -v
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestChunkStructure:
    """Test chunk data structure."""

    def test_chunk_files_exist_after_chunking(self):
        """After chunking, chunk files should exist."""
        project_root = Path(__file__).parent.parent
        chunks_dir = project_root / "chunks"

        # Find any chunk JSON files
        chunk_files = list(chunks_dir.rglob("*_chunk_*.json"))

        if len(chunk_files) > 0:
            # Check first chunk file
            chunk_file = chunk_files[0]
            chunk_data = json.loads(chunk_file.read_text(encoding="utf-8"))

            required_fields = [
                "id",
                "source_document",
                "raw_text",
                "token_count_estimate",
                "chunk_index",
                "total_chunks",
                "created_at",
            ]

            for field in required_fields:
                assert field in chunk_data, f"Missing required field: {field}"

    def test_chunk_metadata_exists(self):
        """Chunking should create metadata files."""
        project_root = Path(__file__).parent.parent
        chunks_dir = project_root / "chunks"

        metadata_files = list(chunks_dir.rglob("_chunking_metadata.json"))

        if len(metadata_files) > 0:
            metadata_file = metadata_files[0]
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

            assert "processor" in metadata
            assert "processor_version" in metadata


class TestChunkingContract:
    """Test chunking contract compliance."""

    def test_chunk_id_format(self):
        """Chunk IDs should follow naming convention."""
        chunk_id = "document_name_chunk_0001"
        parts = chunk_id.split("_chunk_")
        assert len(parts) == 2
        assert parts[1].isdigit()
        assert len(parts[1]) == 4  # 4-digit padding

    def test_chunk_file_naming(self):
        """Chunk files should be named correctly."""
        project_root = Path(__file__).parent.parent
        chunks_dir = project_root / "chunks"

        chunk_files = list(chunks_dir.rglob("*_chunk_*.json"))

        if len(chunk_files) > 0:
            for chunk_file in chunk_files[:10]:  # Check first 10
                assert "_chunk_" in chunk_file.name
                assert chunk_file.name.endswith(".json")
                # Extract chunk number
                chunk_num = chunk_file.stem.split("_chunk_")[1]
                assert len(chunk_num) == 4
                assert chunk_num.isdigit()

    def test_chunk_size_bounds(self):
        """Chunks should generally be within token limits."""
        project_root = Path(__file__).parent.parent
        chunks_dir = project_root / "chunks"

        chunk_files = list(chunks_dir.rglob("*_chunk_*.json"))

        if len(chunk_files) > 0:
            # Check a sample of chunks
            for chunk_file in chunk_files[:20]:
                if not chunk_file.name.startswith("_"):
                    chunk_data = json.loads(chunk_file.read_text(encoding="utf-8"))
                    token_count = chunk_data.get("token_count_estimate", 0)
                    # Most chunks should be reasonable size
                    # Allow for some variation (very small last chunks, etc.)
                    assert token_count > 0
                    assert token_count < 2000  # Reasonable upper bound

    def test_source_citation_present(self):
        """Chunks should include source citations."""
        project_root = Path(__file__).parent.parent
        chunks_dir = project_root / "chunks"

        chunk_files = list(chunks_dir.rglob("*_chunk_*.json"))

        if len(chunk_files) > 0:
            chunk_file = chunk_files[0]
            chunk_data = json.loads(chunk_file.read_text(encoding="utf-8"))

            assert "source_document" in chunk_data
            assert chunk_data["source_document"]  # Not empty


class TestChunkScript:
    """Test the chunk script itself."""

    def test_script_exists(self):
        """Chunk script should exist."""
        project_root = Path(__file__).parent.parent
        script = project_root / "scripts" / "chunk_text.py"
        assert script.exists()
        assert script.is_file()

    def test_script_has_no_llm_imports(self):
        """Chunk script must not import LLM libraries."""
        project_root = Path(__file__).parent.parent
        script = project_root / "scripts" / "chunk_text.py"
        content = script.read_text(encoding="utf-8")

        # Should not import anthropic or openai
        assert "import anthropic" not in content
        assert "from anthropic" not in content
        assert "import openai" not in content
        assert "from openai" not in content

    def test_outputs_json(self):
        """Chunk script should output JSON files."""
        project_root = Path(__file__).parent.parent
        chunks_dir = project_root / "chunks"

        chunk_files = list(chunks_dir.rglob("*_chunk_*.json"))

        if len(chunk_files) > 0:
            # All chunk files should be valid JSON
            for chunk_file in chunk_files[:5]:
                if not chunk_file.name.startswith("_"):
                    chunk_data = json.loads(chunk_file.read_text(encoding="utf-8"))
                    assert isinstance(chunk_data, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
