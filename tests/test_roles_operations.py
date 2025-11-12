"""Tests for roles operations."""

import yaml
from pathlib import Path
import pytest


class TestSaveRoles:
    """Tests for save_roles operation."""

    def test_save_roles_creates_file(self, tmp_path):
        """Test save_roles creates roles file."""
        from wctf_core.operations.roles import save_roles

        roles_yaml = """
company: Test Company
company_slug: test-company
last_updated: '2025-11-11'
search_metadata:
  sources: [careers_page]
  last_search_date: '2025-11-11'
peaks:
  - peak_id: test_peak
    peak_name: Test Peak
    roles:
      - role_id: test_role_1
        title: Senior SWE
        url: https://jobs.test.com/1
        posted_date: '2025-11-01'
        location: Remote
        seniority: senior_ic
        description: Build stuff
unmapped_roles: []
"""

        result = save_roles("Test Company", roles_yaml, base_path=tmp_path)

        assert result['success'] is True
        assert 'path' in result

        roles_path = Path(result['path'])
        assert roles_path.exists()
        assert roles_path.name == "company.roles.yaml"

    def test_save_roles_validates_data(self, tmp_path):
        """Test save_roles validates Pydantic model."""
        from wctf_core.operations.roles import save_roles

        invalid_yaml = """
company: Test
company_slug: test
last_updated: '2025-11-11'
search_metadata: {}
peaks:
  - peak_id: peak1
    peak_name: Peak 1
    roles:
      - role_id: role1
        title: Engineer
        url: https://jobs.com/1
        posted_date: '2025-11-01'
        location: Remote
        seniority: invalid_seniority
        description: Work
"""

        result = save_roles("Test", invalid_yaml, base_path=tmp_path)

        assert result['success'] is False
        assert 'error' in result


class TestGetRoles:
    """Tests for get_roles operation."""

    def test_get_roles_reads_existing_file(self, tmp_path):
        """Test get_roles reads existing roles."""
        from wctf_core.operations.roles import save_roles, get_roles

        roles_yaml = """
company: Test Company
company_slug: test-company
last_updated: '2025-11-11'
search_metadata:
  sources: [careers_page]
peaks:
  - peak_id: peak1
    peak_name: Peak 1
    roles:
      - role_id: role1
        title: Senior SWE
        url: https://jobs.com/1
        posted_date: '2025-11-01'
        location: Remote
        seniority: senior_ic
        description: Work
unmapped_roles: []
"""

        # Save first
        save_roles("Test Company", roles_yaml, base_path=tmp_path)

        # Now read
        result = get_roles("Test Company", base_path=tmp_path)

        assert result['success'] is True
        assert 'roles' in result
        assert result['roles']['company'] == "Test Company"
        assert result['roles']['total_roles'] == 1

    def test_get_roles_missing_file(self, tmp_path):
        """Test get_roles handles missing file."""
        from wctf_core.operations.roles import get_roles

        result = get_roles("Nonexistent", base_path=tmp_path)

        assert result['success'] is False
        assert 'error' in result
        assert 'No roles found' in result['error']
