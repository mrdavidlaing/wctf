# Organizational Cartography Design (Layer 1.5)

**Date:** 2025-11-11
**Epic:** wctf-gbt
**Status:** Design Complete, Ready for Implementation

## Executive Summary

Add "Organizational Cartography" (Layer 1.5) to WCTF framework, enabling discovery of VP-level organizations ("peaks") and Director-level teams ("rope teams"), plus role search that maps to org structure. Implements iterative discovery where roles and org mapping inform each other.

## Motivation

When evaluating companies, we need to answer:
1. **What peaks exist?** - Which VP orgs are climbing which mountains?
2. **Which rope teams are hiring?** - Where are the actual openings?
3. **Do I have insider connections?** - Who can provide ground truth?

Currently, we jump from company-level evaluation (Layer 1) directly to insider conversations (Layer 2) without systematically mapping the organizational landscape. This creates gaps in understanding where opportunities exist and which teams to target.

## Core Concepts

### WCTF Terminology

- **Peak** - VP-level organization with unified mission (e.g., "Cloud Services & Infrastructure")
- **Rope Team** - Director-level team cluster (e.g., "Kubernetes Platform Team")
- **Organizational Cartography** - Systematic mapping of peaks and rope teams

### Design Principles

1. **Stage-agnostic** - Commands work at any stage, typical usage: orgmap at stage-2, roles at stage-3
2. **Separate concerns** - Org structure (slow-changing) vs open roles (fast-changing) in separate files
3. **Iterative discovery** - Roles inform orgmap, orgmap enriches role understanding
4. **LLM-driven** - Use WebSearch/WebFetch for research, SDK enforces structure
5. **Rich validation** - Pydantic models with validators, helpers, computed properties

## Architecture

### Component Overview

```
wctf_core/
├── operations/
│   ├── orgmap.py          # NEW - Org mapping operations
│   └── roles.py           # NEW - Role search with orgmap integration
├── models.py              # EXTENDED - Add orgmap and role models
└── client.py              # EXTENDED - Add orgmap and role methods

.claude/commands/
├── map-org.md             # NEW - /map-org slash command
└── search-roles.md        # NEW - /search-roles slash command

data/
├── stage-1/               # Initial research
├── stage-2/               # Worth investigating
│   └── {company}/
│       ├── company.facts.yaml
│       ├── company.flags.yaml
│       ├── company.insider.yaml
│       └── company.orgmap.yaml    # NEW
└── stage-3/               # Active applications
    └── {company}/
        ├── company.orgmap.yaml    # NEW
        └── company.roles.yaml     # NEW
```

### Data Flow

```
User: /map-org chronosphere
  ↓
Slash command instructs LLM
  ↓
LLM: WebSearch + WebFetch → extract org structure
  ↓
LLM: client.save_orgmap('chronosphere', yaml)
  ↓
SDK: Validate with Pydantic → Save to company.orgmap.yaml

---

User: /search-roles apple
  ↓
Slash command instructs LLM
  ↓
LLM: WebSearch + WebFetch → find roles
  ↓
LLM: Load orgmap, match roles to peaks/teams
  ↓
LLM: Prompt for orgmap updates if needed
  ↓
LLM: client.save_roles('apple', yaml)
  ↓
SDK: Validate, deduplicate → Save to company.roles.yaml
```

## Data Schemas

### company.orgmap.yaml

Maps VP-level orgs (peaks) and Director-level teams (rope teams).

```yaml
company: "Apple"
company_slug: "apple"
last_updated: "2025-11-11"
mapping_metadata:
  sources: ["LinkedIn profiles", "Engineering blog", "Conference talks"]
  confidence: "high"  # high/medium/low
  notes: "Pre-annual reorg structure"

peaks:  # VP-level organizations
  - peak_id: "apple_cloud_services"
    peak_name: "Cloud Services & Infrastructure"

    leadership:
      vp_name: "Jane Smith"
      vp_linkedin: "https://linkedin.com/in/janesmith"
      vp_tenure: "3 years"
      reports_to: "SVP Engineering"

    mission: "Build and operate Apple's global cloud infrastructure supporting iCloud, App Store, and internal services"

    org_metrics:
      estimated_headcount: "800-1000"
      growth_trend: "expanding"  # expanding/stable/contracting
      recent_changes:
        - date: "2024-08"
          change: "Merged with Platform Engineering org"
          impact: "Reorganization, some team movements"

    tech_focus:
      primary: ["Kubernetes", "distributed systems", "reliability"]
      secondary: ["security", "observability"]

    coordination_signals:
      style_indicators: "expedition"  # alpine/expedition/established/orienteering/trail_crew
      evidence:
        - "Multiple teams (8+) coordinating on shared platform"
        - "Quarterly planning cycles mentioned in blog posts"
        - "Clear architecture review process"
      realignment_signals:
        - "Team successfully pivoted from VMs to containers (2023)"
        - "Monthly all-hands for strategy updates"

    insider_connections:
      - name: "Bob Jones"
        relationship: "Former colleague at Google"
        role: "Senior Staff Engineer"
        team: "Kubernetes Platform"
        last_contact: "2025-09"
        willing_to_intro: true

    rope_teams:  # Director-level team clusters
      - team_id: "apple_k8s_platform"
        team_name: "Kubernetes Platform"

        leadership:
          director_name: "Alex Chen"
          director_linkedin: "https://linkedin.com/in/alexchen"
          director_tenure: "2 years"

        mission: "Build and evolve Apple's internal Kubernetes platform"
        estimated_size: "40-50 engineers"
        tech_focus: ["Kubernetes", "control plane", "automation"]

        public_presence:
          - "KubeCon talk 2024: 'Operating K8s at Apple Scale'"
          - "Engineering blog posts about multi-cluster management"

        insider_info:
          contact: "Bob Jones"
          notes: "Team is well-regarded, good work-life balance, challenging scale problems"
```

### company.roles.yaml

Open roles mapped to org structure.

```yaml
company: "Apple"
company_slug: "apple"
last_updated: "2025-11-11"
search_metadata:
  sources: ["careers_page", "websearch"]
  last_search_date: "2025-11-11"

peaks:  # Group roles by VP org
  - peak_id: "apple_cloud_services"  # References company.orgmap.yaml
    peak_name: "Cloud Services & Infrastructure"

    roles:
      - role_id: "apple_202511_senior_swe_k8s"
        title: "Senior Software Engineer - Kubernetes Platform"
        url: "https://jobs.apple.com/..."
        posted_date: "2025-11-01"
        location: "Cupertino, CA / Remote"

        # Link to orgmap
        rope_team_id: "apple_k8s_platform"  # References company.orgmap.yaml
        rope_team_name: "Kubernetes Platform"

        # Role details
        seniority: "senior_ic"  # senior_ic/staff_plus/management
        description: "Build scalable Kubernetes control plane..."
        requirements:
          - "8+ years distributed systems experience"
          - "Deep Kubernetes expertise"
        salary_range: "$180k-$250k"

        # WCTF Analysis (filled by separate /analyze-role command)
        wctf_analysis:
          analyzed_date: null
          coordination_style: null  # alpine/expedition/established/orienteering/trail_crew
          terrain_match: null       # good_fit/workable/mismatched
          mountain_clarity: null    # clear/unclear/conflicting

          energy_matrix:
            predicted_quadrant: null  # moare/sparingly/help_mentoring/burnout
            percentage_estimate: null
            key_tasks: []

          alignment_signals:
            green_flags: []
            red_flags: []
            missing_data: []

unmapped_roles:  # Couldn't match to orgmap
  - role_id: "apple_202511_mystery"
    title: "Senior Engineer - Special Projects"
    url: "https://jobs.apple.com/..."
    posted_date: "2025-11-05"
    location: "Cupertino, CA"

    # No peak_id or rope_team_id
    seniority: "senior_ic"
    description: "Work on confidential next-generation projects..."
    requirements: []

    wctf_analysis:
      analyzed_date: null
      # ... same structure

    orgmap_notes: "No matching peak found - update orgmap or insufficient info in posting?"
```

## SDK Implementation

### operations/orgmap.py

Core org mapping operations.

```python
"""Organizational mapping operations."""
from typing import Dict, Optional
from ..models import CompanyOrgMap
from ..utils.yaml_handler import read_yaml, write_yaml
from ..utils.paths import get_orgmap_path, ensure_company_dir

def save_orgmap(company_name: str, orgmap_yaml: str, base_path: Optional[str] = None) -> Dict:
    """
    Validate and save organizational map.

    Args:
        company_name: Company name
        orgmap_yaml: YAML string with org structure
        base_path: Optional custom data directory

    Returns:
        Dict with success status and saved orgmap

    Example:
        >>> result = save_orgmap("Chronosphere", orgmap_yaml)
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

def get_orgmap(company_name: str, base_path: Optional[str] = None) -> Dict:
    """
    Read existing organizational map.

    Args:
        company_name: Company name
        base_path: Optional custom data directory

    Returns:
        Dict with orgmap data or error

    Example:
        >>> result = get_orgmap("Chronosphere")
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

def update_peak(company_name: str, peak_id: str, peak_data: dict, base_path: Optional[str] = None) -> Dict:
    """
    Update single VP org in orgmap.

    Args:
        company_name: Company name
        peak_id: Peak identifier
        peak_data: Updated peak data
        base_path: Optional custom data directory

    Returns:
        Dict with success status
    """
    # Implementation: Load orgmap, find peak by id, update, save
    pass

def add_rope_team(company_name: str, peak_id: str, team_data: dict, base_path: Optional[str] = None) -> Dict:
    """
    Add director team to a peak.

    Args:
        company_name: Company name
        peak_id: Peak identifier
        team_data: Rope team data
        base_path: Optional custom data directory

    Returns:
        Dict with success status
    """
    # Implementation: Load orgmap, find peak, append rope_team, save
    pass
```

### operations/roles.py

Role search operations with orgmap integration.

```python
"""Role search operations."""
from typing import Dict, List, Optional
from ..models import CompanyRoles, Role
from ..utils.yaml_handler import read_yaml, write_yaml
from ..utils.paths import get_roles_path, ensure_company_dir
from .orgmap import get_orgmap

def save_roles(company_name: str, roles_yaml: str, base_path: Optional[str] = None) -> Dict:
    """
    Validate and save role search results.

    Args:
        company_name: Company name
        roles_yaml: YAML string with roles
        base_path: Optional custom data directory

    Returns:
        Dict with success status and saved roles

    Example:
        >>> result = save_roles("Apple", roles_yaml)
        >>> result['success']
        True
    """
    try:
        # Parse and validate
        roles_data = yaml.safe_load(roles_yaml)
        roles = CompanyRoles(**roles_data)

        # Deduplicate roles
        roles = _deduplicate_roles(roles)

        # Save to file
        ensure_company_dir(company_name, base_path)
        roles_path = get_roles_path(company_name, base_path)
        write_yaml(roles_path, roles.model_dump())

        return {
            'success': True,
            'roles': roles.model_dump(),
            'path': str(roles_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_roles(company_name: str, base_path: Optional[str] = None) -> Dict:
    """
    Read existing roles.

    Args:
        company_name: Company name
        base_path: Optional custom data directory

    Returns:
        Dict with roles data or error

    Example:
        >>> result = get_roles("Apple")
        >>> result['roles']['total_roles']
        15
    """
    try:
        roles_path = get_roles_path(company_name, base_path)
        if not roles_path.exists():
            return {
                'success': False,
                'error': f'No roles found for {company_name}'
            }

        roles_data = read_yaml(roles_path)
        roles = CompanyRoles(**roles_data)

        return {
            'success': True,
            'roles': roles.model_dump()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def add_role(company_name: str, role_data: dict, base_path: Optional[str] = None) -> Dict:
    """
    Add single role with deduplication.

    Args:
        company_name: Company name
        role_data: Role data dict
        base_path: Optional custom data directory

    Returns:
        Dict with success status
    """
    # Implementation: Load roles, check for duplicate, add if unique, save
    pass

def match_role_to_orgmap(company_name: str, role_data: dict, base_path: Optional[str] = None) -> Optional[Dict]:
    """
    Try to link role to peak/rope_team in orgmap.

    Args:
        company_name: Company name
        role_data: Role data with team/org info
        base_path: Optional custom data directory

    Returns:
        Dict with peak_id and rope_team_id if matched, None otherwise
    """
    # Implementation: Load orgmap, fuzzy match role's team name to rope_teams
    pass

def extract_org_signals(role_data: dict) -> Dict:
    """
    Pull team/director/VP info from role posting.

    Args:
        role_data: Role data dict

    Returns:
        Dict with extracted org signals (team_name, director_name, vp_org)
    """
    # Implementation: Parse description/title for org indicators
    pass

def update_orgmap_from_roles(company_name: str, unmatched_roles: List[dict], base_path: Optional[str] = None) -> Dict:
    """
    Create/update orgmap entries from role metadata.

    Args:
        company_name: Company name
        unmatched_roles: List of roles that didn't match orgmap
        base_path: Optional custom data directory

    Returns:
        Dict with updated orgmap
    """
    # Implementation: Extract org signals, create skeleton peaks/teams, merge with existing orgmap
    pass

def _deduplicate_roles(roles: CompanyRoles) -> CompanyRoles:
    """Remove duplicate roles (same title + URL)."""
    # Implementation: Use set of (title, url) tuples to dedupe
    pass
```

### client.py additions

High-level API for orgmap and roles.

```python
class WCTFClient:
    # ... existing methods ...

    # Org mapping methods
    def save_orgmap(self, company_name: str, orgmap_yaml: str) -> Dict:
        """
        Save organizational map.

        Args:
            company_name: Company name
            orgmap_yaml: YAML string with org structure

        Returns:
            Dict with success status and saved orgmap

        Example:
            >>> client = WCTFClient()
            >>> result = client.save_orgmap("Chronosphere", orgmap_yaml)
            >>> result['success']
            True
        """
        from .operations import orgmap
        return orgmap.save_orgmap(company_name, orgmap_yaml, self.base_path)

    def get_orgmap(self, company_name: str) -> Dict:
        """
        Get organizational map.

        Args:
            company_name: Company name

        Returns:
            Dict with orgmap data or error

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_orgmap("Chronosphere")
            >>> len(result['orgmap']['peaks'])
            3
        """
        from .operations import orgmap
        return orgmap.get_orgmap(company_name, self.base_path)

    # Role search methods
    def save_roles(self, company_name: str, roles_yaml: str) -> Dict:
        """
        Save role search results.

        Args:
            company_name: Company name
            roles_yaml: YAML string with roles

        Returns:
            Dict with success status and saved roles

        Example:
            >>> client = WCTFClient()
            >>> result = client.save_roles("Apple", roles_yaml)
            >>> result['success']
            True
        """
        from .operations import roles
        return roles.save_roles(company_name, roles_yaml, self.base_path)

    def get_roles(self, company_name: str) -> Dict:
        """
        Get open roles.

        Args:
            company_name: Company name

        Returns:
            Dict with roles data or error

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_roles("Apple")
            >>> result['roles']['total_roles']
            15
        """
        from .operations import roles
        return roles.get_roles(company_name, self.base_path)

    def match_role_to_org(self, company_name: str, role_data: dict) -> Dict:
        """
        Match role to org structure.

        Args:
            company_name: Company name
            role_data: Role data with team/org info

        Returns:
            Dict with peak_id and rope_team_id if matched

        Example:
            >>> client = WCTFClient()
            >>> role = {"title": "Senior SWE - K8s Platform", ...}
            >>> result = client.match_role_to_org("Apple", role)
            >>> result['peak_id']
            'apple_cloud_services'
        """
        from .operations import roles
        return roles.match_role_to_orgmap(company_name, role_data, self.base_path)
```

## Pydantic Models

### Orgmap Models

```python
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import List, Optional, Dict, Literal

class Leadership(BaseModel):
    """VP or Director leadership info."""
    vp_name: Optional[str] = None
    director_name: Optional[str] = None
    linkedin: Optional[str] = None
    tenure: Optional[str] = None
    reports_to: Optional[str] = None

class OrgMetrics(BaseModel):
    """Org size and growth."""
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

class CoordinationSignals(BaseModel):
    """Team coordination style indicators."""
    style_indicators: Literal["alpine", "expedition", "established", "orienteering", "trail_crew"]
    evidence: List[str] = Field(description="Observable signals of coordination style")
    realignment_signals: List[str] = Field(default_factory=list, description="Evidence of adaptation ability")

class InsiderConnection(BaseModel):
    """Network contact info."""
    name: str
    relationship: str = Field(description="How you know them")
    role: str
    team: str
    last_contact: str = Field(description="YYYY-MM format")
    willing_to_intro: bool = Field(default=False)

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
            from ..utils.paths import slugify_company_name
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

### Role Models

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
            from ..utils.paths import slugify_company_name
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

## Workflows

### /map-org Command

**File:** `.claude/commands/map-org.md`

```markdown
# Map Organizational Structure

Map the VP-level orgs (peaks) and Director-level teams (rope teams) for a company.

**Usage:** `/map-org {company_name}`

## Instructions for Claude

When the user runs `/map-org {company_name}`, perform organizational cartography:

1. **Search for VP-level leadership:**
   - Use WebSearch: "{company_name} VP engineering"
   - Use WebSearch: "{company_name} VP infrastructure"
   - Use WebFetch on LinkedIn profiles

2. **Map each VP org (peak):**
   - VP name, tenure, mission
   - Estimated headcount, growth trend
   - Recent changes (reorgs, mergers)
   - Tech focus areas

3. **Identify Director-level teams (rope teams):**
   - Use WebSearch: "{company_name} director platform"
   - Use WebFetch on engineering blog author bios
   - Check conference speaker bios

4. **Extract coordination signals:**
   - Planning cycle (quarterly vs agile)
   - Decision-making style (centralized vs distributed)
   - Recent pivots or adaptations

5. **Check for insider connections:**
   - Cross-reference with known contacts
   - Note relationship, last contact date

6. **Format as company.orgmap.yaml:**
   - Follow schema in design doc
   - Use WCTF terminology (peaks, rope teams)

7. **Save using SDK:**
   ```python
   from wctf_core import WCTFClient
   client = WCTFClient()
   result = client.save_orgmap("{company_name}", orgmap_yaml)
   ```

## Expected Output

- Detailed orgmap with 2-5 peaks (VP orgs)
- 3-8 rope teams per peak
- Coordination style assessment
- Insider connection mapping
- Saved to `data/{stage}/{company}/company.orgmap.yaml`
```

### /search-roles Command

**File:** `.claude/commands/search-roles.md`

```markdown
# Search for Open Roles

Find open positions at a company and map them to organizational structure.

**Usage:** `/search-roles {company_name}`

## Instructions for Claude

When the user runs `/search-roles {company_name}`, search for roles and map to org structure:

1. **Search for open roles:**
   - Use WebSearch: "{company_name} careers senior software engineer"
   - Use WebSearch: "{company_name} jobs staff engineer"
   - Use WebFetch on careers page

2. **Extract role details:**
   - Title, URL, posted date
   - Location, team name
   - Requirements, salary range
   - Seniority level (senior_ic, staff_plus, management)

3. **Extract org signals from each role:**
   - Team name (e.g., "Kubernetes Platform")
   - Director name (if mentioned)
   - VP org (if mentioned)

4. **Load existing orgmap (if exists):**
   ```python
   from wctf_core import WCTFClient
   client = WCTFClient()
   result = client.get_orgmap("{company_name}")
   ```

5. **Match roles to orgmap:**
   - For each role, try to match team name to rope_team_id
   - If matched: Set peak_id and rope_team_id
   - If unmatched: Add to unmapped_roles

6. **Prompt for orgmap updates:**
   - If roles mention teams not in orgmap:
     - "Found role in 'AI Platform' org not in map. Should we add this peak?"
   - If user agrees, extract org signals and update orgmap

7. **Format as company.roles.yaml:**
   - Follow schema in design doc
   - Group by peak, include unmapped_roles section
   - Leave wctf_analysis fields as null (filled by /analyze-role later)

8. **Save using SDK:**
   ```python
   result = client.save_roles("{company_name}", roles_yaml)
   ```

## Expected Output

- 10-30 roles mapped to org structure
- Roles linked to peaks/rope_teams via IDs
- Unmapped roles with notes about why
- Saved to `data/{stage}/{company}/company.roles.yaml`
```

## Iterative Discovery Pattern

### Scenario 1: Roles First, Then Org Map

```
User: /search-roles chronosphere
  ↓
LLM: Searches for roles, extracts org signals
  ↓
LLM: No orgmap exists, creates skeleton from role metadata
  ↓
Result: company.roles.yaml + skeleton company.orgmap.yaml

Later:
User: /map-org chronosphere
  ↓
LLM: Deep research on org structure
  ↓
LLM: Enriches skeleton orgmap with coordination signals, insider connections
  ↓
Result: Enhanced company.orgmap.yaml (role links remain valid)
```

### Scenario 2: Org Map First, Then Roles

```
User: /map-org chronosphere
  ↓
LLM: Research creates detailed orgmap
  ↓
Result: company.orgmap.yaml

Later:
User: /search-roles chronosphere
  ↓
LLM: Searches for roles, loads existing orgmap
  ↓
LLM: Matches most roles to peaks/rope_teams
  ↓
LLM: Discovers "AI Platform" team not in orgmap
  ↓
LLM: Prompts user to update orgmap
  ↓
Result: company.roles.yaml + updated company.orgmap.yaml
```

## Implementation Plan

### Phase 1: Org Mapping Foundation (wctf-mc8, wctf-lzn, wctf-dgt, wctf-rcv)

1. Add Pydantic models for orgmap to `models.py`
2. Implement `operations/orgmap.py` with basic operations
3. Add methods to `client.py`
4. Create `.claude/commands/map-org.md`
5. Test with one stage-2 company (Chronosphere)

**Acceptance Criteria:**
- Can run `/map-org chronosphere`
- Creates valid `company.orgmap.yaml`
- Pydantic validation catches errors
- Computed properties work (total_peaks, has_insider_connection)

### Phase 2: Role Search (wctf-1fn, wctf-hkn, wctf-ojs, wctf-edy)

1. Add Pydantic models for roles to `models.py`
2. Implement `operations/roles.py` with basic operations
3. Add orgmap integration helpers (match, extract, update)
4. Add methods to `client.py`
5. Create `.claude/commands/search-roles.md`
6. Test with one stage-3 company (Apple)

**Acceptance Criteria:**
- Can run `/search-roles apple`
- Creates valid `company.roles.yaml`
- Roles link to existing orgmap
- Deduplication works (same title+URL)
- Computed properties work (is_mapped, total_roles)

### Phase 3: Integration & Refinement (wctf-jfs, wctf-1n7, wctf-bke)

1. Test iterative discovery workflow (both scenarios)
2. Verify cross-references (peak_id, rope_team_id) stay valid
3. Test orgmap updates from unmapped roles
4. Update SDK documentation
5. Write this design doc
6. Test with multiple companies

**Acceptance Criteria:**
- Both discovery scenarios work smoothly
- Orgmap updates don't break role references
- SDK_REFERENCE.md includes new methods
- Design doc committed to docs/plans/

## Success Criteria

- ✅ Can map org structure for any company at any stage
- ✅ Can search roles for any company at any stage
- ✅ Roles automatically link to orgmap peaks/teams
- ✅ Unmapped roles trigger orgmap update suggestions
- ✅ All data validated by Pydantic models
- ✅ SDK methods prevent duplicates
- ✅ Slash commands provide simple user interface
- ✅ Iterative discovery works in both directions

## Future Enhancements

1. **Auto-update**: Periodic role searches (weekly) for stage-3 companies
2. **Role analysis**: Implement `/analyze-role` to fill wctf_analysis fields
3. **Network mapping**: Visualize insider connections across companies
4. **Similarity search**: "Find roles similar to this one"
5. **Application tracking**: Link roles to company.applications.yaml

## References

- Epic: wctf-gbt
- WCTF Framework: WCTF_FRAMEWORK.md
- SDK Documentation: docs/SDK_REFERENCE.md
- Existing operations: wctf_core/operations/
