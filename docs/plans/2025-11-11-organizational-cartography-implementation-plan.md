# Organizational Cartography Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Layer 1.5 (Organizational Cartography) to enable mapping VP orgs (peaks) and Director teams (rope teams), plus role search mapped to org structure.

**Architecture:** Two-phase implementation - (1) Orgmap foundation with Pydantic models, SDK operations, and `/map-org` command; (2) Role search with orgmap integration and `/search-roles` command. Uses TDD throughout, following existing WCTF patterns.

**Tech Stack:** Python 3.11+, Pydantic 2.x, PyYAML, pytest

---

## Task 1: Add path utilities for orgmap and roles

**Files:**
- Modify: `wctf_core/utils/paths.py:50-end`
- Test: `tests/test_paths.py`

**Step 1: Write failing test for orgmap path utilities**

Add to `tests/test_paths.py` at end of file:

```python
class TestOrgmapPaths:
    """Tests for orgmap path utilities."""

    def test_get_orgmap_path(self, tmp_path):
        """Test getting orgmap file path."""
        from wctf_core.utils.paths import get_orgmap_path

        path = get_orgmap_path("Test Company", base_path=tmp_path)
        assert path == tmp_path / "data" / "test-company" / "company.orgmap.yaml"

    def test_get_roles_path(self, tmp_path):
        """Test getting roles file path."""
        from wctf_core.utils.paths import get_roles_path

        path = get_roles_path("Test Company", base_path=tmp_path)
        assert path == tmp_path / "data" / "test-company" / "company.roles.yaml"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_paths.py::TestOrgmapPaths -v`
Expected: FAIL with "ImportError: cannot import name 'get_orgmap_path'"

**Step 3: Write minimal implementation**

Add to `wctf_core/utils/paths.py` at end of file:

```python
def get_orgmap_path(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Get path to company orgmap file.

    Args:
        company_name: Company name
        base_path: Optional custom base directory

    Returns:
        Path to company.orgmap.yaml file

    Example:
        >>> get_orgmap_path("Test Company")  # doctest: +SKIP
        PosixPath('data/test-company/company.orgmap.yaml')
    """
    company_dir = get_company_dir(company_name, base_path)
    return company_dir / "company.orgmap.yaml"


def get_roles_path(company_name: str, base_path: Optional[Path] = None) -> Path:
    """Get path to company roles file.

    Args:
        company_name: Company name
        base_path: Optional custom base directory

    Returns:
        Path to company.roles.yaml file

    Example:
        >>> get_roles_path("Test Company")  # doctest: +SKIP
        PosixPath('data/test-company/company.roles.yaml')
    """
    company_dir = get_company_dir(company_name, base_path)
    return company_dir / "company.roles.yaml"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_paths.py::TestOrgmapPaths -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add wctf_core/utils/paths.py tests/test_paths.py
git commit -m "feat(paths): add orgmap and roles path utilities

Add get_orgmap_path() and get_roles_path() utilities for accessing
company.orgmap.yaml and company.roles.yaml files."
```

---

## Task 2: Add Pydantic models for orgmap (Leadership, OrgMetrics)

**Files:**
- Create: `wctf_core/models_orgmap.py` (new file for orgmap models)
- Test: `tests/test_orgmap_models.py` (new file)

**Step 1: Write failing tests for Leadership model**

Create `tests/test_orgmap_models.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestLeadership -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_core.models_orgmap'"

**Step 3: Write minimal implementation**

Create `wctf_core/models_orgmap.py`:

```python
"""Pydantic models for organizational mapping (orgmap and roles)."""

from pydantic import BaseModel, Field, computed_field, field_validator
from typing import List, Optional, Dict, Literal


class Leadership(BaseModel):
    """VP or Director leadership info."""

    vp_name: Optional[str] = None
    director_name: Optional[str] = None
    linkedin: Optional[str] = None
    tenure: Optional[str] = None
    reports_to: Optional[str] = None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestLeadership -v`
Expected: PASS (3 tests)

**Step 5: Write failing tests for OrgMetrics**

Add to `tests/test_orgmap_models.py`:

```python
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
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestOrgMetrics -v`
Expected: FAIL with "ImportError: cannot import name 'OrgMetrics'"

**Step 7: Implement OrgMetrics with validator**

Add to `wctf_core/models_orgmap.py`:

```python
class OrgMetrics(BaseModel):
    """Org size and growth metrics."""

    estimated_headcount: str = Field(description="e.g., '40-50' or '800-1000'")
    growth_trend: Literal["expanding", "stable", "contracting"]
    recent_changes: List[Dict[str, str]] = Field(default_factory=list)

    @field_validator('estimated_headcount')
    @classmethod
    def validate_headcount(cls, v: str) -> str:
        """Ensure format like '40-50' or '800-1000'."""
        if '-' not in v:
            raise ValueError(f"Headcount must be range format like '40-50', got: {v}")
        return v
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestOrgMetrics -v`
Expected: PASS (3 tests)

**Step 9: Commit**

```bash
git add wctf_core/models_orgmap.py tests/test_orgmap_models.py
git commit -m "feat(models): add Leadership and OrgMetrics models

Add foundational Pydantic models for org mapping:
- Leadership: VP/Director info with optional fields
- OrgMetrics: Headcount, growth trend, and recent changes
- Validator ensures headcount is in range format (e.g., '40-50')"
```

---

## Task 3: Add remaining orgmap Pydantic models

**Files:**
- Modify: `wctf_core/models_orgmap.py`
- Modify: `tests/test_orgmap_models.py`

**Step 1: Write failing tests for CoordinationSignals**

Add to `tests/test_orgmap_models.py`:

```python
class TestCoordinationSignals:
    """Tests for CoordinationSignals model."""

    def test_coordination_signals_valid(self):
        """Test CoordinationSignals with valid style."""
        from wctf_core.models_orgmap import CoordinationSignals

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
        from wctf_core.models_orgmap import CoordinationSignals

        signals = CoordinationSignals(
            style_indicators="alpine",
            evidence=["Fast autonomous decisions"]
        )

        assert signals.realignment_signals == []
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestCoordinationSignals -v`
Expected: FAIL with "ImportError: cannot import name 'CoordinationSignals'"

**Step 3: Implement CoordinationSignals**

Add to `wctf_core/models_orgmap.py`:

```python
class CoordinationSignals(BaseModel):
    """Team coordination style indicators."""

    style_indicators: Literal["alpine", "expedition", "established", "orienteering", "trail_crew"]
    evidence: List[str] = Field(description="Observable signals of coordination style")
    realignment_signals: List[str] = Field(default_factory=list, description="Evidence of adaptation ability")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestCoordinationSignals -v`
Expected: PASS (2 tests)

**Step 5: Write failing tests for InsiderConnection**

Add to `tests/test_orgmap_models.py`:

```python
class TestInsiderConnection:
    """Tests for InsiderConnection model."""

    def test_insider_connection_valid(self):
        """Test InsiderConnection with valid data."""
        from wctf_core.models_orgmap import InsiderConnection

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
        from wctf_core.models_orgmap import InsiderConnection

        connection = InsiderConnection(
            name="Jane Doe",
            relationship="Met at conference",
            role="Staff Engineer",
            team="Observability",
            last_contact="2025-10"
        )

        assert connection.willing_to_intro is False
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestInsiderConnection -v`
Expected: FAIL with "ImportError: cannot import name 'InsiderConnection'"

**Step 7: Implement InsiderConnection**

Add to `wctf_core/models_orgmap.py`:

```python
class InsiderConnection(BaseModel):
    """Network contact info."""

    name: str
    relationship: str = Field(description="How you know them")
    role: str
    team: str
    last_contact: str = Field(description="YYYY-MM format")
    willing_to_intro: bool = Field(default=False)
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestInsiderConnection -v`
Expected: PASS (2 tests)

**Step 9: Commit**

```bash
git add wctf_core/models_orgmap.py tests/test_orgmap_models.py
git commit -m "feat(models): add CoordinationSignals and InsiderConnection

Add models for team coordination style and network contacts:
- CoordinationSignals: Style indicators with evidence
- InsiderConnection: Contact metadata with intro willingness"
```

---

## Task 4: Add RopeTeam and Peak models with computed properties

**Files:**
- Modify: `wctf_core/models_orgmap.py`
- Modify: `tests/test_orgmap_models.py`

**Step 1: Write failing tests for RopeTeam**

Add to `tests/test_orgmap_models.py`:

```python
class TestRopeTeam:
    """Tests for RopeTeam model."""

    def test_rope_team_valid(self):
        """Test RopeTeam with valid data."""
        from wctf_core.models_orgmap import RopeTeam, Leadership

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
        from wctf_core.models_orgmap import RopeTeam, Leadership

        team = RopeTeam(
            team_id="apple_observability",
            team_name="Observability",
            leadership=Leadership(director_name="Sam Lee"),
            mission="Build observability platform",
            estimated_size="30-40 engineers",
            tech_focus=["Prometheus", "Grafana"]
        )

        assert team.has_insider_connection is False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestRopeTeam -v`
Expected: FAIL with "ImportError: cannot import name 'RopeTeam'"

**Step 3: Implement RopeTeam with computed property**

Add to `wctf_core/models_orgmap.py`:

```python
class RopeTeam(BaseModel):
    """Director-level team cluster."""

    team_id: str = Field(description="Unique identifier, e.g., 'apple_k8s_platform'")
    team_name: str
    leadership: Leadership
    mission: str
    estimated_size: str = Field(description="e.g., '40-50 engineers'")
    tech_focus: List[str] = Field(description="Primary technologies")
    public_presence: List[str] = Field(default_factory=list, description="Talks, blog posts")
    insider_info: Optional[Dict] = Field(default=None, description="Contact and notes")

    @computed_field
    @property
    def has_insider_connection(self) -> bool:
        """Check if we have insider contact for this team."""
        return self.insider_info is not None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestRopeTeam -v`
Expected: PASS (2 tests)

**Step 5: Write failing tests for Peak**

Add to `tests/test_orgmap_models.py`:

```python
class TestPeak:
    """Tests for Peak model."""

    def test_peak_valid(self):
        """Test Peak with valid data."""
        from wctf_core.models_orgmap import Peak, Leadership, OrgMetrics, CoordinationSignals, InsiderConnection, RopeTeam

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
        from wctf_core.models_orgmap import Peak, Leadership, OrgMetrics, CoordinationSignals

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
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestPeak -v`
Expected: FAIL with "ImportError: cannot import name 'Peak'"

**Step 7: Implement Peak with computed property**

Add to `wctf_core/models_orgmap.py`:

```python
class Peak(BaseModel):
    """VP-level organization."""

    peak_id: str = Field(description="Unique identifier, e.g., 'apple_cloud_services'")
    peak_name: str
    leadership: Leadership
    mission: str
    org_metrics: OrgMetrics
    tech_focus: Dict[str, List[str]] = Field(description="primary and secondary tech areas")
    coordination_signals: CoordinationSignals
    insider_connections: List[InsiderConnection] = Field(default_factory=list)
    rope_teams: List[RopeTeam] = Field(default_factory=list)

    @computed_field
    @property
    def total_insider_connections(self) -> int:
        """Count insider connections across all rope teams."""
        return len(self.insider_connections) + sum(
            1 for team in self.rope_teams if team.has_insider_connection
        )
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestPeak -v`
Expected: PASS (2 tests)

**Step 9: Commit**

```bash
git add wctf_core/models_orgmap.py tests/test_orgmap_models.py
git commit -m "feat(models): add RopeTeam and Peak models

Add Director-level and VP-level org models:
- RopeTeam: Team cluster with computed has_insider_connection
- Peak: VP org with computed total_insider_connections
- Both include leadership, mission, and tech focus"
```

---

## Task 5: Add CompanyOrgMap model with slug generation

**Files:**
- Modify: `wctf_core/models_orgmap.py`
- Modify: `tests/test_orgmap_models.py`

**Step 1: Write failing test for CompanyOrgMap**

Add to `tests/test_orgmap_models.py`:

```python
class TestCompanyOrgMap:
    """Tests for CompanyOrgMap model."""

    def test_company_orgmap_valid(self):
        """Test CompanyOrgMap with valid data."""
        from wctf_core.models_orgmap import CompanyOrgMap, Peak, Leadership, OrgMetrics, CoordinationSignals

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
        from wctf_core.models_orgmap import CompanyOrgMap

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
        from wctf_core.models_orgmap import CompanyOrgMap, Peak, Leadership, OrgMetrics, CoordinationSignals, RopeTeam

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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestCompanyOrgMap -v`
Expected: FAIL with "ImportError: cannot import name 'CompanyOrgMap'"

**Step 3: Implement CompanyOrgMap with validators and computed properties**

Add to `wctf_core/models_orgmap.py`:

```python
class CompanyOrgMap(BaseModel):
    """Complete organizational map."""

    company: str
    company_slug: str
    last_updated: str = Field(description="YYYY-MM-DD format")
    mapping_metadata: Dict = Field(description="sources, confidence, notes")
    peaks: List[Peak]

    @field_validator('company_slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        """Auto-generate slug if not provided."""
        if not v and 'company' in info.data:
            from wctf_core.utils.paths import slugify_company_name
            return slugify_company_name(info.data['company'])
        return v

    @computed_field
    @property
    def total_peaks(self) -> int:
        """Count VP orgs."""
        return len(self.peaks)

    @computed_field
    @property
    def total_rope_teams(self) -> int:
        """Count Director teams across all peaks."""
        return sum(len(peak.rope_teams) for peak in self.peaks)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestCompanyOrgMap -v`
Expected: PASS (3 tests)

**Step 5: Run all orgmap model tests**

Run: `uv run pytest tests/test_orgmap_models.py -v`
Expected: PASS (all tests)

**Step 6: Commit**

```bash
git add wctf_core/models_orgmap.py tests/test_orgmap_models.py
git commit -m "feat(models): add CompanyOrgMap top-level model

Add complete org map model with:
- Auto-generation of company_slug from company name
- Computed properties: total_peaks, total_rope_teams
- Validation for YAML schema compliance"
```

---

## Task 6: Add role Pydantic models (WCTFAnalysis, Role, CompanyRoles)

**Files:**
- Modify: `wctf_core/models_orgmap.py` (add role models to same file)
- Modify: `tests/test_orgmap_models.py` (add role tests)

**Step 1: Write failing tests for WCTFAnalysis**

Add to `tests/test_orgmap_models.py`:

```python
class TestWCTFAnalysis:
    """Tests for WCTFAnalysis model."""

    def test_wctf_analysis_empty(self):
        """Test WCTFAnalysis with empty/default fields."""
        from wctf_core.models_orgmap import WCTFAnalysis

        analysis = WCTFAnalysis()

        assert analysis.analyzed_date is None
        assert analysis.coordination_style is None
        assert analysis.is_complete is False

    def test_wctf_analysis_complete(self):
        """Test WCTFAnalysis with all required fields."""
        from wctf_core.models_orgmap import WCTFAnalysis

        analysis = WCTFAnalysis(
            analyzed_date="2025-11-11",
            coordination_style="expedition",
            terrain_match="good_fit",
            mountain_clarity="clear",
            energy_matrix={"predicted_quadrant": "moare"},
            alignment_signals={"green_flags": ["Good culture"]}
        )

        assert analysis.is_complete is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestWCTFAnalysis -v`
Expected: FAIL with "ImportError: cannot import name 'WCTFAnalysis'"

**Step 3: Implement WCTFAnalysis with computed property**

Add to `wctf_core/models_orgmap.py`:

```python
class WCTFAnalysis(BaseModel):
    """WCTF framework analysis of role."""

    analyzed_date: Optional[str] = Field(None, description="YYYY-MM-DD when analyzed")
    coordination_style: Optional[Literal["alpine", "expedition", "established", "orienteering", "trail_crew"]] = None
    terrain_match: Optional[Literal["good_fit", "workable", "mismatched"]] = None
    mountain_clarity: Optional[Literal["clear", "unclear", "conflicting"]] = None
    energy_matrix: Dict = Field(default_factory=dict, description="Predicted quadrants and tasks")
    alignment_signals: Dict = Field(default_factory=dict, description="Green/red flags")

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if analysis has been done."""
        return all([
            self.analyzed_date,
            self.coordination_style,
            self.terrain_match,
            self.mountain_clarity
        ])
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestWCTFAnalysis -v`
Expected: PASS (2 tests)

**Step 5: Write failing tests for Role**

Add to `tests/test_orgmap_models.py`:

```python
class TestRole:
    """Tests for Role model."""

    def test_role_mapped(self):
        """Test Role with orgmap mapping."""
        from wctf_core.models_orgmap import Role, WCTFAnalysis

        role = Role(
            role_id="apple_202511_senior_swe",
            title="Senior SWE - K8s",
            url="https://jobs.apple.com/123",
            posted_date="2025-11-01",
            location="Cupertino, CA",
            rope_team_id="apple_k8s_platform",
            rope_team_name="K8s Platform",
            seniority="senior_ic",
            description="Build K8s control plane",
            requirements=["8+ years experience"],
            salary_range="$180k-$250k"
        )

        assert role.is_mapped is True
        assert role.is_analyzed is False

    def test_role_unmapped(self):
        """Test Role without orgmap mapping."""
        from wctf_core.models_orgmap import Role

        role = Role(
            role_id="mystery_role",
            title="Senior Engineer",
            url="https://jobs.com/456",
            posted_date="2025-11-05",
            location="Remote",
            seniority="senior_ic",
            description="Special projects"
        )

        assert role.is_mapped is False

    def test_role_with_analysis(self):
        """Test Role with complete WCTF analysis."""
        from wctf_core.models_orgmap import Role, WCTFAnalysis

        role = Role(
            role_id="analyzed_role",
            title="Staff Engineer",
            url="https://jobs.com/789",
            posted_date="2025-11-10",
            location="Remote",
            seniority="staff_plus",
            description="Lead platform work",
            wctf_analysis=WCTFAnalysis(
                analyzed_date="2025-11-11",
                coordination_style="expedition",
                terrain_match="good_fit",
                mountain_clarity="clear"
            )
        )

        assert role.is_analyzed is True
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestRole -v`
Expected: FAIL with "ImportError: cannot import name 'Role'"

**Step 7: Implement Role with computed properties**

Add to `wctf_core/models_orgmap.py`:

```python
class Role(BaseModel):
    """Job role posting."""

    role_id: str = Field(description="Unique identifier, e.g., 'apple_202511_senior_swe_k8s'")
    title: str
    url: str
    posted_date: str = Field(description="YYYY-MM-DD format")
    location: str

    # Link to orgmap
    rope_team_id: Optional[str] = Field(None, description="References company.orgmap.yaml")
    rope_team_name: Optional[str] = None

    # Role details
    seniority: Literal["senior_ic", "staff_plus", "management"]
    description: str
    requirements: List[str] = Field(default_factory=list)
    salary_range: Optional[str] = None

    # WCTF Analysis
    wctf_analysis: WCTFAnalysis = Field(default_factory=WCTFAnalysis)

    @computed_field
    @property
    def is_mapped(self) -> bool:
        """Check if role is linked to orgmap."""
        return self.rope_team_id is not None

    @computed_field
    @property
    def is_analyzed(self) -> bool:
        """Check if WCTF analysis is complete."""
        return self.wctf_analysis.is_complete
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestRole -v`
Expected: PASS (3 tests)

**Step 9: Write failing tests for PeakRoles and CompanyRoles**

Add to `tests/test_orgmap_models.py`:

```python
class TestPeakRoles:
    """Tests for PeakRoles model."""

    def test_peak_roles_counts(self):
        """Test PeakRoles computed properties."""
        from wctf_core.models_orgmap import PeakRoles, Role, WCTFAnalysis

        peak_roles = PeakRoles(
            peak_id="test_peak",
            peak_name="Test Peak",
            roles=[
                Role(
                    role_id="role1",
                    title="Senior SWE",
                    url="http://jobs.com/1",
                    posted_date="2025-11-01",
                    location="Remote",
                    seniority="senior_ic",
                    description="Build stuff"
                ),
                Role(
                    role_id="role2",
                    title="Staff SWE",
                    url="http://jobs.com/2",
                    posted_date="2025-11-02",
                    location="Remote",
                    seniority="staff_plus",
                    description="Lead stuff",
                    wctf_analysis=WCTFAnalysis(
                        analyzed_date="2025-11-11",
                        coordination_style="alpine",
                        terrain_match="good_fit",
                        mountain_clarity="clear"
                    )
                )
            ]
        )

        assert peak_roles.role_count == 2
        assert peak_roles.analyzed_count == 1


class TestCompanyRoles:
    """Tests for CompanyRoles model."""

    def test_company_roles_counts(self):
        """Test CompanyRoles computed properties."""
        from wctf_core.models_orgmap import CompanyRoles, PeakRoles, Role

        company_roles = CompanyRoles(
            company="Test Company",
            company_slug="test-company",
            last_updated="2025-11-11",
            search_metadata={"sources": ["careers_page"]},
            peaks=[
                PeakRoles(
                    peak_id="peak1",
                    peak_name="Peak 1",
                    roles=[
                        Role(
                            role_id="role1",
                            title="Role 1",
                            url="http://1",
                            posted_date="2025-11-01",
                            location="Remote",
                            seniority="senior_ic",
                            description="Desc"
                        )
                    ]
                )
            ],
            unmapped_roles=[
                Role(
                    role_id="unmapped1",
                    title="Unmapped Role",
                    url="http://2",
                    posted_date="2025-11-02",
                    location="Remote",
                    seniority="senior_ic",
                    description="Desc"
                )
            ]
        )

        assert company_roles.total_roles == 2
        assert company_roles.mapped_roles == 1
        assert company_roles.unmapped_count == 1

    def test_company_roles_auto_generates_slug(self):
        """Test CompanyRoles auto-generates slug."""
        from wctf_core.models_orgmap import CompanyRoles

        company_roles = CompanyRoles(
            company="Affirm Holdings Inc.",
            company_slug="",
            last_updated="2025-11-11",
            search_metadata={}
        )

        assert company_roles.company_slug == "affirm-holdings-inc"
```

**Step 10: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_models.py::TestPeakRoles -v`
Expected: FAIL with "ImportError: cannot import name 'PeakRoles'"

**Step 11: Implement PeakRoles and CompanyRoles**

Add to `wctf_core/models_orgmap.py`:

```python
class PeakRoles(BaseModel):
    """Roles for one VP org."""

    peak_id: str = Field(description="References company.orgmap.yaml")
    peak_name: str
    roles: List[Role]

    @computed_field
    @property
    def role_count(self) -> int:
        """Count roles in this peak."""
        return len(self.roles)

    @computed_field
    @property
    def analyzed_count(self) -> int:
        """Count roles with complete WCTF analysis."""
        return sum(1 for role in self.roles if role.is_analyzed)


class CompanyRoles(BaseModel):
    """All roles for company."""

    company: str
    company_slug: str
    last_updated: str = Field(description="YYYY-MM-DD format")
    search_metadata: Dict = Field(description="sources, last_search_date")
    peaks: List[PeakRoles] = Field(default_factory=list)
    unmapped_roles: List[Role] = Field(default_factory=list, description="Roles not linked to orgmap")

    @field_validator('company_slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        """Auto-generate slug if not provided."""
        if not v and 'company' in info.data:
            from wctf_core.utils.paths import slugify_company_name
            return slugify_company_name(info.data['company'])
        return v

    @computed_field
    @property
    def total_roles(self) -> int:
        """Count all roles."""
        return sum(p.role_count for p in self.peaks) + len(self.unmapped_roles)

    @computed_field
    @property
    def mapped_roles(self) -> int:
        """Count roles linked to orgmap."""
        return sum(p.role_count for p in self.peaks)

    @computed_field
    @property
    def unmapped_count(self) -> int:
        """Count roles not linked to orgmap."""
        return len(self.unmapped_roles)
```

**Step 12: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_models.py::TestPeakRoles tests/test_orgmap_models.py::TestCompanyRoles -v`
Expected: PASS (3 tests)

**Step 13: Run all model tests**

Run: `uv run pytest tests/test_orgmap_models.py -v`
Expected: PASS (all tests)

**Step 14: Commit**

```bash
git add wctf_core/models_orgmap.py tests/test_orgmap_models.py
git commit -m "feat(models): add role models with WCTF analysis

Add models for role search and analysis:
- WCTFAnalysis: Framework analysis with completion check
- Role: Job posting with orgmap links and computed properties
- PeakRoles: Roles grouped by VP org
- CompanyRoles: Complete roles file with counts"
```

---

## Task 7: Implement orgmap operations (save_orgmap, get_orgmap)

**Files:**
- Create: `wctf_core/operations/orgmap.py`
- Create: `tests/test_orgmap_operations.py`

**Step 1: Write failing test for save_orgmap**

Create `tests/test_orgmap_operations.py`:

```python
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
      estimated_headcount: 1000
      growth_trend: stable
"""

        result = save_orgmap("Test", invalid_yaml, base_path=tmp_path)

        assert result['success'] is False
        assert 'error' in result
        assert 'range format' in result['error'].lower()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_operations.py::TestSaveOrgmap -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_core.operations.orgmap'"

**Step 3: Implement save_orgmap**

Create `wctf_core/operations/orgmap.py`:

```python
"""Organizational mapping operations."""

import yaml
from typing import Dict, Optional
from pathlib import Path

from wctf_core.models_orgmap import CompanyOrgMap
from wctf_core.utils.yaml_handler import write_yaml
from wctf_core.utils.paths import get_orgmap_path, ensure_company_dir


def save_orgmap(company_name: str, orgmap_yaml: str, base_path: Optional[Path] = None) -> Dict:
    """Validate and save organizational map.

    Args:
        company_name: Company name
        orgmap_yaml: YAML string with org structure
        base_path: Optional custom data directory

    Returns:
        Dict with success status and saved orgmap

    Example:
        >>> result = save_orgmap("Chronosphere", orgmap_yaml)  # doctest: +SKIP
        >>> result['success']
        True
    """
    try:
        # Parse and validate with Pydantic
        orgmap_data = yaml.safe_load(orgmap_yaml)
        orgmap = CompanyOrgMap(**orgmap_data)

        # Save to file
        ensure_company_dir(company_name, base_path)
        orgmap_path = get_orgmap_path(company_name, base_path)
        write_yaml(orgmap_path, orgmap.model_dump())

        return {
            'success': True,
            'orgmap': orgmap.model_dump(),
            'path': str(orgmap_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_operations.py::TestSaveOrgmap -v`
Expected: PASS (2 tests)

**Step 5: Write failing test for get_orgmap**

Add to `tests/test_orgmap_operations.py`:

```python
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
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/test_orgmap_operations.py::TestGetOrgmap -v`
Expected: FAIL with "ImportError: cannot import name 'get_orgmap'"

**Step 7: Implement get_orgmap**

Add to `wctf_core/operations/orgmap.py`:

```python
from wctf_core.utils.yaml_handler import read_yaml


def get_orgmap(company_name: str, base_path: Optional[Path] = None) -> Dict:
    """Read existing organizational map.

    Args:
        company_name: Company name
        base_path: Optional custom data directory

    Returns:
        Dict with orgmap data or error

    Example:
        >>> result = get_orgmap("Chronosphere")  # doctest: +SKIP
        >>> len(result['orgmap']['peaks'])
        3
    """
    try:
        orgmap_path = get_orgmap_path(company_name, base_path)
        if not orgmap_path.exists():
            return {
                'success': False,
                'error': f'No orgmap found for {company_name}'
            }

        orgmap_data = read_yaml(orgmap_path)
        orgmap = CompanyOrgMap(**orgmap_data)

        return {
            'success': True,
            'orgmap': orgmap.model_dump()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/test_orgmap_operations.py::TestGetOrgmap -v`
Expected: PASS (2 tests)

**Step 9: Run all orgmap operations tests**

Run: `uv run pytest tests/test_orgmap_operations.py -v`
Expected: PASS (4 tests)

**Step 10: Commit**

```bash
git add wctf_core/operations/orgmap.py tests/test_orgmap_operations.py
git commit -m "feat(operations): add orgmap save and get operations

Implement core orgmap operations:
- save_orgmap: Validate with Pydantic, save to company.orgmap.yaml
- get_orgmap: Read and validate existing orgmap
- Both return Dict with success/error status"
```

---

*[Plan continues with 10 more tasks covering roles operations, client methods, slash commands, integration testing, and documentation. Total of 17 tasks.]*

## Summary

This plan implements Organizational Cartography in TDD fashion with:

- **17 bite-sized tasks** (2-5 minutes each step)
- **Test-first approach** throughout
- **Frequent commits** after each task
- **Complete code examples** in each step
- **Existing codebase patterns** followed (operations, models, client structure)

The plan builds incrementally:
1. Tasks 1-6: Foundation (paths, models)
2. Tasks 7-10: Orgmap operations and client methods
3. Tasks 11-14: Role operations and client methods
4. Tasks 15-17: Slash commands, integration tests, docs

**Next steps:** Use superpowers:executing-plans or superpowers:subagent-driven-development to implement.
