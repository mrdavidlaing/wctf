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


class TestRolesPrompts:
    """Tests for roles prompt generation."""

    def test_get_roles_extraction_prompt(self, tmp_path):
        """Test roles extraction prompt with orgmap reference."""
        from wctf_core.operations.prompts import get_roles_extraction_prompt
        from wctf_core.operations.orgmap import save_orgmap

        # Create an orgmap first
        orgmap_yaml = """
company: Test Company
company_slug: test-company
last_updated: '2025-11-11'
mapping_metadata:
  sources: [LinkedIn]
peaks:
  - peak_id: test_peak
    peak_name: Test Peak
    leadership:
      vp_name: VP
    mission: Mission
    org_metrics:
      estimated_headcount: 100-200
      growth_trend: stable
    tech_focus:
      primary: [Python]
    coordination_signals:
      style_indicators: alpine
      evidence: [Fast]
    rope_teams:
      - team_id: test_team
        team_name: Test Team
        leadership:
          director_name: Director
        mission: Team mission
        estimated_size: 30-40
        tech_focus: [Python]
"""

        save_orgmap("Test Company", orgmap_yaml, base_path=tmp_path)

        prompt = get_roles_extraction_prompt("Test Company", base_path=tmp_path)

        assert "Test Company" in prompt
        assert "Test Peak" in prompt
        assert "Test Team" in prompt
        assert "WCTF" in prompt

    def test_get_roles_extraction_prompt_without_orgmap(self, tmp_path):
        """Test roles extraction prompt without orgmap."""
        from wctf_core.operations.prompts import get_roles_extraction_prompt

        prompt = get_roles_extraction_prompt("No Orgmap Company", base_path=tmp_path)

        assert "No Orgmap Company" in prompt
        assert "no orgmap" in prompt.lower() or "without orgmap" in prompt.lower()
