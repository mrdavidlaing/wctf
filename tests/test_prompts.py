"""Tests for prompt generation operations."""


class TestOrgmapPrompts:
    """Tests for orgmap prompt generation."""

    def test_get_orgmap_extraction_prompt(self):
        """Test orgmap extraction prompt generation."""
        from wctf_core.operations.prompts import get_orgmap_extraction_prompt

        prompt = get_orgmap_extraction_prompt("Chronosphere")

        assert "Chronosphere" in prompt
        assert "VP-level" in prompt or "Peak" in prompt
        assert "Director-level" in prompt or "Rope Team" in prompt
        assert "coordination style" in prompt.lower()
        assert "yaml" in prompt.lower()
