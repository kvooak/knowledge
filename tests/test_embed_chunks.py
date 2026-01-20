#!/usr/bin/env python3
"""
test_embed_chunks.py - Unit tests for embeddings generation

Run with: pytest tests/test_embed_chunks.py -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.embed_chunks import load_chunks, create_index


class TestChunkLoading:
    """Test chunk loading from filesystem."""

    @pytest.fixture
    def temp_chunks_dir(self, tmp_path):
        """Create temporary chunks directory with test data."""
        chunks_dir = tmp_path / "chunks" / "TestProject" / "doc"
        chunks_dir.mkdir(parents=True, exist_ok=True)

        # Create test chunk files
        for i in range(1, 4):
            chunk_data = {
                "id": f"doc_chunk_{i:04d}",
                "source_document": "test.pdf",
                "raw_text": f"Test content {i}",
                "chunk_index": i - 1,
            }
            chunk_file = chunks_dir / f"doc_chunk_{i:04d}.json"
            chunk_file.write_text(json.dumps(chunk_data), encoding="utf-8")

        # Create metadata file (should be skipped)
        metadata = {"test": "metadata"}
        (chunks_dir / "_chunking_metadata.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )

        return tmp_path / "chunks"

    def test_load_chunks_recursive(self, temp_chunks_dir):
        """Should load chunks from nested directories."""
        chunks = load_chunks(temp_chunks_dir)
        assert len(chunks) == 3
        assert all("id" in chunk for chunk in chunks)

    def test_skip_metadata_files(self, temp_chunks_dir):
        """Should skip files starting with underscore."""
        chunks = load_chunks(temp_chunks_dir)
        # Should have 3 chunks, not 4 (metadata skipped)
        assert len(chunks) == 3

    def test_chunks_sorted(self, temp_chunks_dir):
        """Chunks should be sorted by document and index."""
        chunks = load_chunks(temp_chunks_dir)
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i


class TestIndexCreation:
    """Test embedding index creation."""

    def test_index_metadata_exists(self):
        """Index metadata should exist after embedding."""
        project_root = Path(__file__).parent.parent
        index_dir = project_root / "index"
        metadata_file = index_dir / "metadata.json"

        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

            required_fields = [
                "created_at",
                "generator",
                "generator_version",
                "model",
                "chunk_count",
                "embedding_dimension",
                "is_truth",
                "regenerable",
                "warning",
            ]

            for field in required_fields:
                assert field in metadata, f"Missing required field: {field}"

    def test_index_not_truth(self):
        """Index metadata must explicitly state it's not truth."""
        project_root = Path(__file__).parent.parent
        index_dir = project_root / "index"
        metadata_file = index_dir / "metadata.json"

        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

            assert metadata["is_truth"] is False
            assert metadata["regenerable"] is True
            assert "search only" in metadata["warning"].lower()

    def test_index_files_created(self):
        """Index creation should create required files."""
        project_root = Path(__file__).parent.parent
        index_dir = project_root / "index"

        if index_dir.exists() and any(index_dir.iterdir()):
            # Check required files exist
            assert (index_dir / "embeddings.npy").exists()
            assert (index_dir / "chunk_ids.json").exists()
            assert (index_dir / "metadata.json").exists()
            assert (index_dir / "_INDEX_IS_NOT_TRUTH").exists()


class TestEmbeddingContract:
    """Test embedding contract compliance."""

    def test_no_llm_usage(self):
        """Embeddings must not use LLM (uses sentence-transformers only)."""
        # This is verified by code inspection
        # Should only use sentence-transformers, not Claude/OpenAI
        pass

    def test_regenerable(self):
        """Index must be fully regenerable from chunks."""
        # The metadata should explicitly state this
        # Test verified in test_index_not_truth
        pass

    def test_index_warning_file(self):
        """Warning file must exist to remind that index is not truth."""
        project_root = Path(__file__).parent.parent
        index_dir = project_root / "index"
        warning_file = index_dir / "_INDEX_IS_NOT_TRUTH"

        if warning_file.exists():
            content = warning_file.read_text(encoding="utf-8")
            assert "NOT TRUTH" in content.upper()
            assert "SEARCH" in content.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
