"""Tests for organizational mapping Pydantic models."""

import pytest
from pydantic import ValidationError


class TestLeadership:
    """Tests for Leadership model."""

    def test_leadership_vp_valid(self):
        """Test creating Leadership with VP info."""
        from wctf_core.models.orgmap import Leadership

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
        from wctf_core.models.orgmap import Leadership

        leader = Leadership(
            director_name="Alex Chen",
            linkedin="https://linkedin.com/in/alexchen",
            tenure="2 years"
        )

        assert leader.director_name == "Alex Chen"
        assert leader.vp_name is None

    def test_leadership_minimal(self):
        """Test creating Leadership with minimal fields."""
        from wctf_core.models.orgmap import Leadership

        leader = Leadership()

        assert leader.vp_name is None
        assert leader.director_name is None


class TestOrgMetrics:
    """Tests for OrgMetrics model."""

    def test_orgmetrics_valid_headcount(self):
        """Test OrgMetrics with valid headcount format."""
        from wctf_core.models.orgmap import OrgMetrics

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
        from wctf_core.models.orgmap import OrgMetrics

        with pytest.raises(ValidationError) as exc_info:
            OrgMetrics(
                estimated_headcount="1000",  # Missing range format
                growth_trend="stable"
            )

        assert "range format" in str(exc_info.value).lower()

    def test_orgmetrics_minimal(self):
        """Test OrgMetrics with minimal fields."""
        from wctf_core.models.orgmap import OrgMetrics

        metrics = OrgMetrics(
            estimated_headcount="40-50",
            growth_trend="stable"
        )

        assert metrics.recent_changes == []


class TestCoordinationSignals:
    """Tests for CoordinationSignals model."""

    def test_coordination_signals_valid(self):
        """Test CoordinationSignals with valid style."""
        from wctf_core.models.orgmap import CoordinationSignals

        signals = CoordinationSignals(
            style_indicators="expedition",
            evidence=["8+ teams coordinating", "Quarterly planning"],
            realignment_signals=["Pivoted VMs to containers"]
        )

        assert signals.style_indicators == "expedition"
        assert len(signals.evidence) == 2
        assert len(signals.realignment_signals) == 1

    def test_coordination_signals_minimal(self):
        """Test CoordinationSignals with minimal fields."""
        from wctf_core.models.orgmap import CoordinationSignals

        signals = CoordinationSignals(
            style_indicators="alpine",
            evidence=["Fast autonomous decisions"]
        )

        assert signals.realignment_signals == []


class TestInsiderConnection:
    """Tests for InsiderConnection model."""

    def test_insider_connection_valid(self):
        """Test InsiderConnection with valid data."""
        from wctf_core.models.orgmap import InsiderConnection

        connection = InsiderConnection(
            name="Bob Jones",
            relationship="Former Google colleague",
            role="Senior Staff Engineer",
            team="Kubernetes Platform",
            last_contact="2025-09",
            willing_to_intro=True
        )

        assert connection.name == "Bob Jones"
        assert connection.willing_to_intro is True

    def test_insider_connection_default_willing_to_intro(self):
        """Test InsiderConnection defaults willing_to_intro to False."""
        from wctf_core.models.orgmap import InsiderConnection

        connection = InsiderConnection(
            name="Jane Doe",
            relationship="Met at conference",
            role="Staff Engineer",
            team="Observability",
            last_contact="2025-10"
        )

        assert connection.willing_to_intro is False


class TestRopeTeam:
    """Tests for RopeTeam model."""

    def test_rope_team_valid(self):
        """Test RopeTeam with valid data."""
        from wctf_core.models.orgmap import RopeTeam, Leadership

        team = RopeTeam(
            team_id="apple_k8s_platform",
            team_name="Kubernetes Platform",
            leadership=Leadership(director_name="Alex Chen"),
            mission="Build internal K8s platform",
            estimated_size="40-50 engineers",
            tech_focus=["Kubernetes", "control plane"],
            public_presence=["KubeCon 2024 talk"],
            insider_info={"contact": "Bob Jones", "notes": "Good WLB"}
        )

        assert team.team_id == "apple_k8s_platform"
        assert len(team.tech_focus) == 2
        assert team.has_insider_connection is True

    def test_rope_team_no_insider_connection(self):
        """Test RopeTeam without insider connection."""
        from wctf_core.models.orgmap import RopeTeam, Leadership

        team = RopeTeam(
            team_id="apple_observability",
            team_name="Observability",
            leadership=Leadership(director_name="Sam Lee"),
            mission="Build observability platform",
            estimated_size="30-40 engineers",
            tech_focus=["Prometheus", "Grafana"]
        )

        assert team.has_insider_connection is False


class TestPeak:
    """Tests for Peak model."""

    def test_peak_valid(self):
        """Test Peak with valid data."""
        from wctf_core.models.orgmap import Peak, Leadership, OrgMetrics, CoordinationSignals, InsiderConnection, RopeTeam

        peak = Peak(
            peak_id="apple_cloud_services",
            peak_name="Cloud Services",
            leadership=Leadership(vp_name="Jane Smith"),
            mission="Build cloud infrastructure",
            org_metrics=OrgMetrics(
                estimated_headcount="800-1000",
                growth_trend="expanding"
            ),
            tech_focus={"primary": ["Kubernetes"], "secondary": ["security"]},
            coordination_signals=CoordinationSignals(
                style_indicators="expedition",
                evidence=["Quarterly planning"]
            ),
            insider_connections=[
                InsiderConnection(
                    name="Bob Jones",
                    relationship="Former colleague",
                    role="Staff Engineer",
                    team="K8s Platform",
                    last_contact="2025-09"
                )
            ],
            rope_teams=[
                RopeTeam(
                    team_id="apple_k8s",
                    team_name="K8s Platform",
                    leadership=Leadership(director_name="Alex Chen"),
                    mission="Build K8s",
                    estimated_size="40-50",
                    tech_focus=["Kubernetes"],
                    insider_info={"contact": "Bob"}
                )
            ]
        )

        assert peak.peak_id == "apple_cloud_services"
        assert peak.total_insider_connections == 2  # 1 peak-level + 1 rope team

    def test_peak_no_insider_connections(self):
        """Test Peak without insider connections."""
        from wctf_core.models.orgmap import Peak, Leadership, OrgMetrics, CoordinationSignals

        peak = Peak(
            peak_id="test_peak",
            peak_name="Test Peak",
            leadership=Leadership(vp_name="Test VP"),
            mission="Test mission",
            org_metrics=OrgMetrics(
                estimated_headcount="100-200",
                growth_trend="stable"
            ),
            tech_focus={"primary": ["Python"]},
            coordination_signals=CoordinationSignals(
                style_indicators="alpine",
                evidence=["Fast decisions"]
            )
        )

        assert peak.total_insider_connections == 0


class TestCompanyOrgMap:
    """Tests for CompanyOrgMap model."""

    def test_company_orgmap_valid(self):
        """Test CompanyOrgMap with valid data."""
        from wctf_core.models.orgmap import CompanyOrgMap, Peak, Leadership, OrgMetrics, CoordinationSignals

        orgmap = CompanyOrgMap(
            company="Test Company",
            company_slug="test-company",
            last_updated="2025-11-11",
            mapping_metadata={"sources": ["LinkedIn"], "confidence": "high"},
            peaks=[
                Peak(
                    peak_id="test_peak",
                    peak_name="Test Peak",
                    leadership=Leadership(vp_name="VP Name"),
                    mission="Test mission",
                    org_metrics=OrgMetrics(
                        estimated_headcount="100-200",
                        growth_trend="stable"
                    ),
                    tech_focus={"primary": ["Python"]},
                    coordination_signals=CoordinationSignals(
                        style_indicators="alpine",
                        evidence=["Fast"]
                    )
                )
            ]
        )

        assert orgmap.company == "Test Company"
        assert orgmap.company_slug == "test-company"
        assert orgmap.total_peaks == 1
        assert orgmap.total_rope_teams == 0

    def test_company_orgmap_auto_generates_slug(self):
        """Test CompanyOrgMap auto-generates slug from company name."""
        from wctf_core.models.orgmap import CompanyOrgMap

        orgmap = CompanyOrgMap(
            company="Toast, Inc.",
            company_slug="",  # Empty slug should trigger generation
            last_updated="2025-11-11",
            mapping_metadata={},
            peaks=[]
        )

        assert orgmap.company_slug == "toast-inc"

    def test_company_orgmap_counts_rope_teams(self):
        """Test CompanyOrgMap counts rope teams across peaks."""
        from wctf_core.models.orgmap import CompanyOrgMap, Peak, Leadership, OrgMetrics, CoordinationSignals, RopeTeam

        orgmap = CompanyOrgMap(
            company="Test",
            company_slug="test",
            last_updated="2025-11-11",
            mapping_metadata={},
            peaks=[
                Peak(
                    peak_id="peak1",
                    peak_name="Peak 1",
                    leadership=Leadership(vp_name="VP1"),
                    mission="Mission 1",
                    org_metrics=OrgMetrics(estimated_headcount="50-100", growth_trend="stable"),
                    tech_focus={"primary": ["Python"]},
                    coordination_signals=CoordinationSignals(style_indicators="alpine", evidence=["Fast"]),
                    rope_teams=[
                        RopeTeam(
                            team_id="team1",
                            team_name="Team 1",
                            leadership=Leadership(director_name="Dir1"),
                            mission="Mission",
                            estimated_size="20-30",
                            tech_focus=["Python"]
                        ),
                        RopeTeam(
                            team_id="team2",
                            team_name="Team 2",
                            leadership=Leadership(director_name="Dir2"),
                            mission="Mission",
                            estimated_size="30-40",
                            tech_focus=["Go"]
                        )
                    ]
                )
            ]
        )

        assert orgmap.total_rope_teams == 2
