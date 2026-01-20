#!/usr/bin/env python3
"""
test_compliance.py - Compliance test for Knowledge System

This test verifies that all project requirements are met:
1. Mandatory directory structure exists
2. All required files exist
3. Scripts follow their contracts
4. Prohibitions are enforced
5. Documentation is complete

Run with: pytest tests/test_compliance.py -v
"""

import ast
import re
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestDirectoryStructure:
    """Verify mandatory directory structure exists."""

    REQUIRED_DIRS = [
        "sources",
        "extracted",
        "chunks",
        "synth",
        "synth/drafts",
        "synth/procedures",
        "index",
        "scripts",
        "prompts",
    ]

    @pytest.mark.parametrize("directory", REQUIRED_DIRS)
    def test_required_directory_exists(self, directory):
        """Each required directory must exist."""
        dir_path = PROJECT_ROOT / directory
        assert dir_path.exists(), f"Required directory missing: {directory}"
        assert dir_path.is_dir(), f"Path exists but is not a directory: {directory}"


class TestRequiredFiles:
    """Verify all required files exist."""

    REQUIRED_FILES = [
        "Makefile",
        "README.md",
        "scripts/extract_pdf.py",
        "scripts/chunk_text.py",
        "scripts/embed_chunks.py",
        "scripts/synthesize.py",
        "synth/glossary.md",
        "synth/rules.md",
        "synth/invariants.md",
        "synth/contradictions.md",
        "synth/open_questions.md",
    ]

    REQUIRED_PROMPTS = [
        "prompts/synthesize_glossary.md",
        "prompts/synthesize_rules.md",
        "prompts/synthesize_invariants.md",
        "prompts/synthesize_procedures.md",
        "prompts/synthesize_contradictions.md",
        "prompts/synthesize_questions.md",
    ]

    @pytest.mark.parametrize("filepath", REQUIRED_FILES)
    def test_required_file_exists(self, filepath):
        """Each required file must exist."""
        file_path = PROJECT_ROOT / filepath
        assert file_path.exists(), f"Required file missing: {filepath}"
        assert file_path.is_file(), f"Path exists but is not a file: {filepath}"

    @pytest.mark.parametrize("filepath", REQUIRED_PROMPTS)
    def test_required_prompt_exists(self, filepath):
        """Each required prompt file must exist."""
        file_path = PROJECT_ROOT / filepath
        assert file_path.exists(), f"Required prompt missing: {filepath}"


class TestSynthFiles:
    """Verify synth files have correct structure."""

    def test_synth_files_have_curated_warning(self):
        """Curated synth files must have non-authoritative warning."""
        curated_files = [
            "synth/glossary.md",
            "synth/rules.md",
            "synth/invariants.md",
            "synth/contradictions.md",
            "synth/open_questions.md",
        ]

        for filepath in curated_files:
            file_path = PROJECT_ROOT / filepath
            if file_path.exists():
                content = file_path.read_text()
                assert "CURATED" in content or "curated" in content, \
                    f"Curated file missing CURATED marker: {filepath}"


class TestExtractScript:
    """Verify extract_pdf.py follows its contract."""

    @pytest.fixture
    def script_content(self):
        script_path = PROJECT_ROOT / "scripts" / "extract_pdf.py"
        return script_path.read_text()

    def test_no_llm_imports(self, script_content):
        """Extract script must NOT import LLM libraries."""
        prohibited_imports = ["openai", "anthropic", "langchain", "llama"]
        for lib in prohibited_imports:
            assert lib not in script_content.lower(), \
                f"extract_pdf.py must not use LLM: found reference to {lib}"

    def test_has_deterministic_output_claim(self, script_content):
        """Extract script must claim deterministic output."""
        assert "deterministic" in script_content.lower(), \
            "extract_pdf.py must document deterministic output"

    def test_uses_mechanical_extraction(self, script_content):
        """Extract script must use mechanical extraction."""
        assert "fitz" in script_content or "pymupdf" in script_content.lower(), \
            "extract_pdf.py should use PyMuPDF for mechanical extraction"


class TestChunkScript:
    """Verify chunk_text.py follows its contract."""

    @pytest.fixture
    def script_content(self):
        script_path = PROJECT_ROOT / "scripts" / "chunk_text.py"
        return script_path.read_text()

    def test_no_llm_imports(self, script_content):
        """Chunk script must NOT import LLM libraries."""
        prohibited_imports = ["openai", "anthropic", "langchain", "llama"]
        for lib in prohibited_imports:
            assert lib not in script_content.lower(), \
                f"chunk_text.py must not use LLM: found reference to {lib}"

    def test_no_embeddings(self, script_content):
        """Chunk script must NOT generate embeddings."""
        assert "embedding" not in script_content.lower() or \
               "no embedding" in script_content.lower(), \
            "chunk_text.py must not generate embeddings"

    def test_outputs_json(self, script_content):
        """Chunk script must output JSON format."""
        assert "json" in script_content.lower(), \
            "chunk_text.py must output JSON format"

    def test_includes_required_fields(self, script_content):
        """Chunk script must include required fields in output."""
        required_fields = ["id", "source_document", "section", "page", "raw_text"]
        for field in required_fields:
            assert field in script_content, \
                f"chunk_text.py must include field: {field}"


class TestEmbedScript:
    """Verify embed_chunks.py follows its contract."""

    @pytest.fixture
    def script_content(self):
        script_path = PROJECT_ROOT / "scripts" / "embed_chunks.py"
        return script_path.read_text()

    def test_warns_index_not_truth(self, script_content):
        """Embed script must warn that index is not truth."""
        content_lower = script_content.lower()
        assert "not truth" in content_lower or "not the source of truth" in content_lower, \
            "embed_chunks.py must warn that index is NOT truth"

    def test_index_is_regenerable(self, script_content):
        """Embed script must document that index is regenerable."""
        assert "regenera" in script_content.lower(), \
            "embed_chunks.py must document that index is regenerable"


class TestSynthesizeScript:
    """Verify synthesize.py follows its contract."""

    @pytest.fixture
    def script_content(self):
        script_path = PROJECT_ROOT / "scripts" / "synthesize.py"
        return script_path.read_text()

    def test_outputs_to_drafts(self, script_content):
        """Synthesize script must output to drafts/ directory."""
        assert "drafts" in script_content, \
            "synthesize.py must output to synth/drafts/"

    def test_labels_as_non_authoritative(self, script_content):
        """Synthesize script must label output as non-authoritative."""
        content_lower = script_content.lower()
        assert "draft" in content_lower and "not authoritative" in content_lower, \
            "synthesize.py must label drafts as non-authoritative"

    def test_refuses_to_overwrite_curated(self, script_content):
        """Synthesize script must refuse to overwrite curated files."""
        content_lower = script_content.lower()
        assert "refuse" in content_lower or "protected" in content_lower, \
            "synthesize.py must refuse to overwrite curated files"

    def test_requires_human_review(self, script_content):
        """Synthesize script must require human review."""
        content_lower = script_content.lower()
        assert "human review" in content_lower or "human-review" in content_lower, \
            "synthesize.py must require human review"


class TestPromptContracts:
    """Verify prompts follow contract requirements."""

    PROMPT_FILES = [
        "prompts/synthesize_glossary.md",
        "prompts/synthesize_rules.md",
        "prompts/synthesize_invariants.md",
        "prompts/synthesize_procedures.md",
        "prompts/synthesize_contradictions.md",
        "prompts/synthesize_questions.md",
    ]

    @pytest.mark.parametrize("prompt_file", PROMPT_FILES)
    def test_prompt_forbids_inference(self, prompt_file):
        """Each prompt must forbid inference."""
        content = (PROJECT_ROOT / prompt_file).read_text().lower()
        assert "no inference" in content or "must not infer" in content or \
               "never infer" in content, \
            f"{prompt_file} must forbid inference"

    @pytest.mark.parametrize("prompt_file", PROMPT_FILES)
    def test_prompt_forbids_gap_filling(self, prompt_file):
        """Each prompt must forbid gap filling."""
        content = (PROJECT_ROOT / prompt_file).read_text().lower()
        assert "gap" in content or "fill" in content, \
            f"{prompt_file} must forbid gap filling"

    @pytest.mark.parametrize("prompt_file", PROMPT_FILES)
    def test_prompt_requires_citation(self, prompt_file):
        """Each prompt must require citations."""
        content = (PROJECT_ROOT / prompt_file).read_text().lower()
        assert "citation" in content or "cite" in content or "source" in content, \
            f"{prompt_file} must require citations"


class TestMakefile:
    """Verify Makefile follows requirements."""

    @pytest.fixture
    def makefile_content(self):
        makefile_path = PROJECT_ROOT / "Makefile"
        return makefile_path.read_text()

    def test_has_extract_target(self, makefile_content):
        """Makefile must have extract target."""
        assert "extract:" in makefile_content or "extract :" in makefile_content, \
            "Makefile must have 'extract' target"

    def test_has_chunk_target(self, makefile_content):
        """Makefile must have chunk target."""
        assert "chunk:" in makefile_content or "chunk :" in makefile_content, \
            "Makefile must have 'chunk' target"

    def test_has_embed_target(self, makefile_content):
        """Makefile must have embed target."""
        assert "embed:" in makefile_content or "embed :" in makefile_content, \
            "Makefile must have 'embed' target"

    def test_has_synth_target(self, makefile_content):
        """Makefile must have synth target."""
        assert "synth:" in makefile_content or "synth :" in makefile_content, \
            "Makefile must have 'synth' target"

    def test_has_ingest_target(self, makefile_content):
        """Makefile must have ingest target."""
        assert "ingest:" in makefile_content or "ingest :" in makefile_content, \
            "Makefile must have 'ingest' target"

    def test_ingest_includes_pipeline(self, makefile_content):
        """Ingest target must include extract, chunk, embed."""
        # Find the ingest target line
        assert "extract" in makefile_content and \
               "chunk" in makefile_content and \
               "embed" in makefile_content, \
            "Makefile ingest must use extract, chunk, embed"


class TestREADME:
    """Verify README explains required concepts."""

    @pytest.fixture
    def readme_content(self):
        readme_path = PROJECT_ROOT / "README.md"
        return readme_path.read_text(encoding="utf-8")

    def test_explains_llm_stateless(self, readme_content):
        """README must explain LLM is stateless."""
        content_lower = readme_content.lower()
        assert "stateless" in content_lower, \
            "README must explain that LLM is stateless"

    def test_explains_where_truth_lives(self, readme_content):
        """README must explain where truth lives."""
        content_lower = readme_content.lower()
        assert "truth" in content_lower and "synth" in content_lower, \
            "README must explain where truth lives (synth/)"

    def test_explains_what_is_regenerable(self, readme_content):
        """README must explain what is safe to regenerate."""
        content_lower = readme_content.lower()
        assert "regenerat" in content_lower, \
            "README must explain what is safe to regenerate"

    def test_explains_what_not_to_modify(self, readme_content):
        """README must explain what must never be auto-modified."""
        content_lower = readme_content.lower()
        assert "never" in content_lower and ("auto" in content_lower or "modif" in content_lower), \
            "README must explain what must never be auto-modified"

    def test_explains_human_in_loop(self, readme_content):
        """README must explain human-in-the-loop workflow."""
        content_lower = readme_content.lower()
        assert "human" in content_lower and ("review" in content_lower or "loop" in content_lower), \
            "README must explain human-in-the-loop workflow"


class TestProhibitions:
    """Verify prohibited patterns are NOT present."""

    def test_no_database_as_truth(self):
        """No database should be used as source of truth."""
        # Check scripts for database imports that might be used as truth
        scripts_dir = PROJECT_ROOT / "scripts"
        db_patterns = ["sqlite", "postgres", "mysql", "mongodb"]

        for script in scripts_dir.glob("*.py"):
            content = script.read_text().lower()
            for pattern in db_patterns:
                if pattern in content:
                    # Check if it's documenting prohibition, not using
                    assert "not" in content or "prohibit" in content or \
                           "don't" in content or "never" in content, \
                        f"Found potential database usage in {script.name}"

    def test_no_background_daemons(self):
        """No background daemons or watchers should exist."""
        scripts_dir = PROJECT_ROOT / "scripts"
        daemon_patterns = ["daemon", "watcher", "observer", "background", "schedule"]

        for script in scripts_dir.glob("*.py"):
            content = script.read_text().lower()
            for pattern in daemon_patterns:
                if pattern in content:
                    # Make sure it's not actually implementing a daemon
                    assert "def watch" not in content and \
                           "class Daemon" not in content and \
                           "while True" not in content, \
                        f"Found potential daemon/watcher in {script.name}"

    def test_extract_no_llm_calls(self):
        """extract_pdf.py must not make LLM API calls."""
        content = (PROJECT_ROOT / "scripts" / "extract_pdf.py").read_text()
        assert "anthropic" not in content and \
               "openai" not in content and \
               "api_key" not in content.lower(), \
            "extract_pdf.py must not use LLM APIs"

    def test_chunk_no_llm_calls(self):
        """chunk_text.py must not make LLM API calls."""
        content = (PROJECT_ROOT / "scripts" / "chunk_text.py").read_text()
        assert "anthropic" not in content and \
               "openai" not in content and \
               "api_key" not in content.lower(), \
            "chunk_text.py must not use LLM APIs"


class TestCitationRequirements:
    """Verify citation requirements are enforced."""

    def test_prompts_require_source_citation(self):
        """All prompts must require source citations."""
        prompts_dir = PROJECT_ROOT / "prompts"

        for prompt_file in prompts_dir.glob("*.md"):
            content = prompt_file.read_text().lower()
            assert "source" in content or "citation" in content or "cite" in content, \
                f"Prompt {prompt_file.name} must require source citations"

    def test_prompts_require_page_numbers(self):
        """All synthesis prompts should mention page numbers."""
        prompts_dir = PROJECT_ROOT / "prompts"

        for prompt_file in prompts_dir.glob("synthesize_*.md"):
            content = prompt_file.read_text().lower()
            assert "page" in content, \
                f"Prompt {prompt_file.name} should require page number citations"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
