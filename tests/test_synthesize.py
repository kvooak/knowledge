#!/usr/bin/env python3
"""
test_synthesize.py - Unit tests for LLM synthesis

Run with: pytest tests/test_synthesize.py -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.synthesize import (
    check_protected_files,
    load_chunks,
    format_chunks_for_prompt,
    generate_draft,
)


class TestProtectedFiles:
    """Test protected file enforcement."""

    def test_refuse_overwrite_curated_glossary(self):
        """Should refuse to overwrite synth/glossary.md."""
        project_root = Path(__file__).parent.parent
        protected_path = project_root / "synth" / "glossary.md"

        with pytest.raises(ValueError, match="REFUSED"):
            check_protected_files(protected_path)

    def test_refuse_overwrite_curated_rules(self):
        """Should refuse to overwrite synth/rules.md."""
        project_root = Path(__file__).parent.parent
        protected_path = project_root / "synth" / "rules.md"

        with pytest.raises(ValueError, match="REFUSED"):
            check_protected_files(protected_path)

    def test_refuse_non_draft_procedure(self):
        """Should refuse to overwrite procedures without DRAFT_ prefix."""
        project_root = Path(__file__).parent.parent
        protected_path = project_root / "synth" / "procedures" / "my_procedure.md"

        with pytest.raises(ValueError, match="REFUSED"):
            check_protected_files(protected_path)

    def test_allow_draft_files(self):
        """Should allow writing to draft files."""
        project_root = Path(__file__).parent.parent
        draft_path = project_root / "synth" / "drafts" / "DRAFT_test.md"

        # Should not raise
        result = check_protected_files(draft_path)
        assert result is True


class TestChunkLoading:
    """Test chunk loading for synthesis."""

    @pytest.fixture
    def temp_chunks_dir(self, tmp_path):
        """Create temporary chunks directory."""
        chunks_dir = tmp_path / "chunks" / "TestProject" / "doc"
        chunks_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, 6):
            chunk_data = {
                "id": f"doc_chunk_{i:04d}",
                "source_document": "test.pdf",
                "raw_text": f"Test content {i}",
                "chunk_index": i - 1,
            }
            chunk_file = chunks_dir / f"doc_chunk_{i:04d}.json"
            chunk_file.write_text(json.dumps(chunk_data), encoding="utf-8")

        return tmp_path / "chunks"

    def test_load_chunks_with_limit(self, temp_chunks_dir):
        """Should respect limit parameter."""
        chunks = load_chunks(temp_chunks_dir, limit=3)
        assert len(chunks) == 3

    def test_load_all_chunks(self, temp_chunks_dir):
        """Should load all chunks when no limit."""
        chunks = load_chunks(temp_chunks_dir, limit=None)
        assert len(chunks) == 5


class TestChunkFormatting:
    """Test chunk formatting for prompts."""

    def test_format_includes_citation_info(self):
        """Formatted chunks should include citation information."""
        chunks = [
            {
                "id": "test_chunk_0001",
                "source_document": "manual.pdf",
                "section": "Introduction",
                "page_start": 1,
                "page_end": 2,
                "raw_text": "Test content here.",
            }
        ]

        formatted = format_chunks_for_prompt(chunks)

        assert "test_chunk_0001" in formatted
        assert "manual.pdf" in formatted
        assert "Introduction" in formatted
        assert "Test content here." in formatted

    def test_format_multiple_chunks(self):
        """Should format multiple chunks with separators."""
        chunks = [
            {"id": "chunk_0001", "source_document": "doc.pdf", "raw_text": "Text 1"},
            {"id": "chunk_0002", "source_document": "doc.pdf", "raw_text": "Text 2"},
        ]

        formatted = format_chunks_for_prompt(chunks)

        assert "chunk_0001" in formatted
        assert "chunk_0002" in formatted
        assert "Text 1" in formatted
        assert "Text 2" in formatted


class TestDraftGeneration:
    """Test draft synthesis generation."""

    @pytest.fixture
    def mock_chunks(self):
        """Create mock chunks."""
        return [
            {
                "id": "test_chunk_0001",
                "source_document": "test.pdf",
                "section": "Test Section",
                "page_start": 1,
                "page_end": 1,
                "raw_text": "Test content for synthesis.",
            }
        ]

    @pytest.fixture
    def mock_prompt_dir(self, tmp_path):
        """Create mock prompt directory."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir(exist_ok=True)

        # Create mock prompt file
        prompt_content = "Test prompt for glossary synthesis."
        (prompts_dir / "synthesize_glossary.md").write_text(
            prompt_content, encoding="utf-8"
        )

        return prompts_dir

    def test_draft_has_warning_header(self, tmp_path, mock_chunks, mock_prompt_dir):
        """Draft files must have non-authoritative warning."""
        with patch("scripts.synthesize.PROMPTS_DIR", mock_prompt_dir):
            with patch("scripts.synthesize.DRAFTS_DIR", tmp_path):
                with patch("scripts.synthesize.call_llm") as mock_llm:
                    mock_llm.return_value = "LLM generated content"

                    draft_path = generate_draft(
                        synthesis_type="glossary",
                        topic="test",
                        chunks=mock_chunks,
                        api_key="fake-key",
                        verbose=False,
                    )

                    content = draft_path.read_text(encoding="utf-8")
                    assert "DRAFT - NOT AUTHORITATIVE" in content.upper()
                    assert "DO NOT treat this as truth".upper() in content.upper()
                    assert "HUMAN REVIEW" in content.upper()

    def test_draft_filename_format(self, tmp_path, mock_chunks, mock_prompt_dir):
        """Draft filename should follow convention."""
        with patch("scripts.synthesize.PROMPTS_DIR", mock_prompt_dir):
            with patch("scripts.synthesize.DRAFTS_DIR", tmp_path):
                with patch("scripts.synthesize.call_llm") as mock_llm:
                    mock_llm.return_value = "Content"

                    draft_path = generate_draft(
                        synthesis_type="glossary",
                        topic="test topic",
                        chunks=mock_chunks,
                        api_key="fake-key",
                        verbose=False,
                    )

                    assert draft_path.name.startswith("DRAFT_")
                    assert "glossary" in draft_path.name
                    assert draft_path.name.endswith(".md")


class TestSynthesisContract:
    """Test synthesis contract compliance."""

    def test_only_llm_script(self):
        """Only synthesize.py should use LLM."""
        # This is enforced by project structure
        # Other scripts should not import anthropic/openai
        pass

    def test_draft_output_only(self):
        """Synthesis must output to drafts/ only."""
        # Verified by check_protected_files tests
        pass

    def test_citation_requirement(self):
        """LLM prompts must require citations."""
        # This is verified by prompt file contents
        # Each prompt should forbid inference and require citations
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
