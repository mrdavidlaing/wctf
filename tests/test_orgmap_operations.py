"""Tests for orgmap operations."""

import yaml
from pathlib import Path
import pytest


class TestSaveOrgmap:
    """Tests for save_orgmap operation."""

    def test_save_orgmap_creates_file(self, tmp_path):
        """Test save_orgmap creates orgmap file."""
        from wctf_core.operations.orgmap import save_orgmap

        orgmap_yaml = """
company: Test Company
company_slug: test-company
last_updated: '2025-11-11'
mapping_metadata:
  sources: [LinkedIn]
  confidence: high
peaks:
  - peak_id: test_peak
    peak_name: Test Peak
    leadership:
      vp_name: Test VP
    mission: Test mission
    org_metrics:
      estimated_headcount: 100-200
      growth_trend: stable
    tech_focus:
      primary: [Python]
    coordination_signals:
      style_indicators: alpine
      evidence: [Fast decisions]
"""

        result = save_orgmap("Test Company", orgmap_yaml, base_path=tmp_path)

        assert result['success'] is True
        assert 'path' in result

        orgmap_path = Path(result['path'])
        assert orgmap_path.exists()
        assert orgmap_path.name == "company.orgmap.yaml"

    def test_save_orgmap_validates_data(self, tmp_path):
        """Test save_orgmap validates Pydantic model."""
        from wctf_core.operations.orgmap import save_orgmap

        invalid_yaml = """
company: Test
company_slug: test
last_updated: '2025-11-11'
mapping_metadata: {}
peaks:
  - peak_id: bad_peak
    peak_name: Bad Peak
    leadership:
      vp_name: VP
    mission: Mission
    org_metrics:
      estimated_headcount: '1000'
      growth_trend: stable
    tech_focus:
      primary: [Python]
    coordination_signals:
      style_indicators: alpine
      evidence: [Fast]
"""

        result = save_orgmap("Test", invalid_yaml, base_path=tmp_path)

        assert result['success'] is False
        assert 'error' in result
        assert 'range format' in result['error'].lower()


class TestGetOrgmap:
    """Tests for get_orgmap operation."""

    def test_get_orgmap_reads_existing_file(self, tmp_path):
        """Test get_orgmap reads existing orgmap."""
        from wctf_core.operations.orgmap import save_orgmap, get_orgmap

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
      estimated_headcount: 50-100
      growth_trend: stable
    tech_focus:
      primary: [Python]
    coordination_signals:
      style_indicators: alpine
      evidence: [Fast]
"""

        # Save first
        save_orgmap("Test Company", orgmap_yaml, base_path=tmp_path)

        # Now read
        result = get_orgmap("Test Company", base_path=tmp_path)

        assert result['success'] is True
        assert 'orgmap' in result
        assert result['orgmap']['company'] == "Test Company"
        assert len(result['orgmap']['peaks']) == 1

    def test_get_orgmap_missing_file(self, tmp_path):
        """Test get_orgmap handles missing file."""
        from wctf_core.operations.orgmap import get_orgmap

        result = get_orgmap("Nonexistent", base_path=tmp_path)

        assert result['success'] is False
        assert 'error' in result
        assert 'No orgmap found' in result['error']
