#!/usr/bin/env python3
"""
test_clean.py - Unit tests for clean script

Run with: pytest tests/test_clean.py -v
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.clean import clean_directory, clean_drafts


class TestCleanDirectory:
    """Test directory cleaning."""

    def test_clean_empty_directory(self, tmp_path):
        """Cleaning empty directory should work."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        count = clean_directory(test_dir)
        assert count == 0
        assert test_dir.exists()  # Directory itself should remain

    def test_clean_directory_with_files(self, tmp_path):
        """Should remove all files in directory."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # Create test files
        (test_dir / "file1.txt").write_text("test")
        (test_dir / "file2.txt").write_text("test")

        count = clean_directory(test_dir)
        assert count == 2
        assert test_dir.exists()
        assert len(list(test_dir.iterdir())) == 0

    def test_clean_directory_with_subdirs(self, tmp_path):
        """Should remove subdirectories."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # Create subdirectory with files
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file.txt").write_text("test")

        count = clean_directory(test_dir)
        assert count >= 1
        assert test_dir.exists()
        assert not sub_dir.exists()

    def test_clean_nonexistent_directory(self, tmp_path):
        """Cleaning nonexistent directory should not error."""
        test_dir = tmp_path / "nonexistent"
        count = clean_directory(test_dir)
        assert count == 0


class TestCleanDrafts:
    """Test draft file cleaning."""

    def test_clean_draft_files(self, tmp_path):
        """Should remove files starting with DRAFT_."""
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()

        # Create draft files
        (drafts_dir / "DRAFT_test1.md").write_text("draft")
        (drafts_dir / "DRAFT_test2.md").write_text("draft")
        (drafts_dir / "other.md").write_text("not a draft")

        # Mock the SYNTH_DRAFTS_DIR
        import scripts.clean
        original_dir = scripts.clean.SYNTH_DRAFTS_DIR
        scripts.clean.SYNTH_DRAFTS_DIR = drafts_dir

        try:
            count = clean_drafts()
            assert count == 2
            assert (drafts_dir / "other.md").exists()
            assert not (drafts_dir / "DRAFT_test1.md").exists()
            assert not (drafts_dir / "DRAFT_test2.md").exists()
        finally:
            scripts.clean.SYNTH_DRAFTS_DIR = original_dir

    def test_clean_no_drafts(self, tmp_path):
        """Cleaning when no drafts exist should work."""
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()

        (drafts_dir / "regular.md").write_text("not a draft")

        import scripts.clean
        original_dir = scripts.clean.SYNTH_DRAFTS_DIR
        scripts.clean.SYNTH_DRAFTS_DIR = drafts_dir

        try:
            count = clean_drafts()
            assert count == 0
            assert (drafts_dir / "regular.md").exists()
        finally:
            scripts.clean.SYNTH_DRAFTS_DIR = original_dir


class TestCleanContract:
    """Test clean script contract."""

    def test_preserves_sources(self):
        """Clean must never delete sources/."""
        from scripts.clean import PROTECTED_DIRS, PROJECT_ROOT
        sources_dir = PROJECT_ROOT / "sources"
        assert sources_dir in PROTECTED_DIRS

    def test_preserves_curated_files(self):
        """Clean must never delete curated synth files."""
        from scripts.clean import PROTECTED_FILES

        protected_names = [f.name for f in PROTECTED_FILES]
        assert "glossary.md" in protected_names
        assert "rules.md" in protected_names
        assert "invariants.md" in protected_names
        assert "contradictions.md" in protected_names
        assert "open_questions.md" in protected_names

    def test_safe_to_run_anytime(self):
        """Clean should be safe to run even on empty directories."""
        # This is tested by test_clean_empty_directory
        # and test_clean_nonexistent_directory
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
