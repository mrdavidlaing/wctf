"""Tests for organizational mapping Pydantic models."""

import pytest
from pydantic import ValidationError


class TestLeadership:
    """Tests for Leadership model."""

    def test_leadership_vp_valid(self):
        """Test creating Leadership with VP info."""
        from wctf_core.models_orgmap import Leadership

        leader = Leadership(
            vp_name="Jane Smith",
            linkedin="https://linkedin.com/in/janesmith",
            tenure="3 years",
            reports_to="SVP Engineering"
        )

        assert leader.vp_name == "Jane Smith"
        assert leader.director_name is None
        assert leader.linkedin == "https://linkedin.com/in/janesmith"
        assert leader.tenure == "3 years"

    def test_leadership_director_valid(self):
        """Test creating Leadership with Director info."""
        from wctf_core.models_orgmap import Leadership

        leader = Leadership(
            director_name="Alex Chen",
            linkedin="https://linkedin.com/in/alexchen",
            tenure="2 years"
        )

        assert leader.director_name == "Alex Chen"
        assert leader.vp_name is None

    def test_leadership_minimal(self):
        """Test creating Leadership with minimal fields."""
        from wctf_core.models_orgmap import Leadership

        leader = Leadership()

        assert leader.vp_name is None
        assert leader.director_name is None


class TestOrgMetrics:
    """Tests for OrgMetrics model."""

    def test_orgmetrics_valid_headcount(self):
        """Test OrgMetrics with valid headcount format."""
        from wctf_core.models_orgmap import OrgMetrics

        metrics = OrgMetrics(
            estimated_headcount="800-1000",
            growth_trend="expanding",
            recent_changes=[
                {"date": "2024-08", "change": "Merged with Platform", "impact": "Reorg"}
            ]
        )

        assert metrics.estimated_headcount == "800-1000"
        assert metrics.growth_trend == "expanding"
        assert len(metrics.recent_changes) == 1

    def test_orgmetrics_invalid_headcount_format(self):
        """Test OrgMetrics rejects invalid headcount format."""
        from wctf_core.models_orgmap import OrgMetrics

        with pytest.raises(ValidationError) as exc_info:
            OrgMetrics(
                estimated_headcount="1000",  # Missing range format
                growth_trend="stable"
            )

        assert "range format" in str(exc_info.value).lower()

    def test_orgmetrics_minimal(self):
        """Test OrgMetrics with minimal fields."""
        from wctf_core.models_orgmap import OrgMetrics

        metrics = OrgMetrics(
            estimated_headcount="40-50",
            growth_trend="stable"
        )

        assert metrics.recent_changes == []
