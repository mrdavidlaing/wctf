"""Prompt generation for research and extraction workflows."""

from typing import Optional
from pathlib import Path


def get_orgmap_extraction_prompt(company_name: str) -> str:
    """Generate prompt for extracting organizational map from research.

    Args:
        company_name: Company name

    Returns:
        Prompt string for orgmap extraction

    Example:
        >>> prompt = get_orgmap_extraction_prompt("Chronosphere")  # doctest: +SKIP
        >>> "VP-level" in prompt
        True
    """
    return f"""# Organizational Mapping for {company_name}

Your task is to map the organizational structure at VP and Director levels.

## What to Extract

### Peaks (VP-level organizations)
For each VP-level org, identify:
- **Peak ID**: Unique identifier (e.g., "{company_name.lower().replace(' ', '_')}_cloud_services")
- **Peak Name**: Official org name
- **Leadership**: VP name, LinkedIn, tenure, reports to
- **Mission**: What this org builds/owns
- **Org Metrics**: Headcount (range format like "800-1000"), growth trend, recent changes
- **Tech Focus**: Primary and secondary technologies
- **Coordination Signals**: Style indicators (alpine/expedition/established/orienteering/trail_crew)
  - **Evidence**: Observable signals of coordination style
  - **Realignment Signals**: Evidence of adaptation ability

### Rope Teams (Director-level teams)
For each Director-level team within a Peak:
- **Team ID**: Unique identifier (e.g., "{company_name.lower().replace(' ', '_')}_k8s_platform")
- **Team Name**: Official team name
- **Leadership**: Director name, LinkedIn, tenure
- **Mission**: What this team builds
- **Estimated Size**: Team size (e.g., "40-50 engineers")
- **Tech Focus**: Technologies used
- **Public Presence**: Talks, blog posts, open source contributions

### Insider Connections
If you have network contacts at the company:
- **Name**: Contact name
- **Relationship**: How you know them
- **Role**: Their role/title
- **Team**: Which team they're on
- **Last Contact**: YYYY-MM format
- **Willing to Intro**: Boolean

## Output Format

Return YAML in this structure:

```yaml
company: "{company_name}"
company_slug: "{company_name.lower().replace(' ', '-')}"
last_updated: "YYYY-MM-DD"
mapping_metadata:
  sources: ["LinkedIn", "company blog", "conference talks"]
  confidence: "high" # high/medium/low
  notes: "Optional notes about data quality"

peaks:
  - peak_id: "unique_peak_id"
    peak_name: "Peak Name"
    leadership:
      vp_name: "VP Name"
      linkedin: "https://linkedin.com/in/..."
      tenure: "3 years"
      reports_to: "SVP Engineering"
    mission: "What they build"
    org_metrics:
      estimated_headcount: "800-1000"  # Must be range format
      growth_trend: "expanding"  # expanding/stable/contracting
      recent_changes:
        - date: "2024-08"
          change: "Merged with Platform"
          impact: "Reorg"
    tech_focus:
      primary: ["Kubernetes", "Go"]
      secondary: ["Observability", "Security"]
    coordination_signals:
      style_indicators: "expedition"  # alpine/expedition/established/orienteering/trail_crew
      evidence:
        - "8+ teams coordinating"
        - "Quarterly planning cycles"
      realignment_signals:
        - "Pivoted from VMs to containers in 2023"
    insider_connections:
      - name: "Contact Name"
        relationship: "Former Google colleague"
        role: "Staff Engineer"
        team: "K8s Platform"
        last_contact: "2025-09"
        willing_to_intro: true
    rope_teams:
      - team_id: "unique_team_id"
        team_name: "Team Name"
        leadership:
          director_name: "Director Name"
          linkedin: "https://linkedin.com/in/..."
          tenure: "2 years"
        mission: "What they build"
        estimated_size: "40-50 engineers"
        tech_focus: ["Kubernetes", "control plane"]
        public_presence:
          - "KubeCon 2024 talk"
          - "Blog post about K8s at scale"
        insider_info:
          contact: "Contact Name"
          notes: "Good WLB, strong tech culture"
```

## Research Strategy

1. **Start with LinkedIn**: Search for VPs at {company_name}
2. **Company engineering blog**: Look for author bios and org mentions
3. **Conference talks**: Check who's presenting and what orgs they represent
4. **GitHub**: Look for {company_name} org structure in repos
5. **News/press releases**: Look for leadership announcements

## Important Notes

- Use range format for all headcount estimates (e.g., "40-50", "800-1000")
- Coordination style should match WCTF framework archetypes
- Include evidence for coordination style assessment
- Mark confidence level based on data quality
- Leave fields as null/empty if you can't find reliable information

Begin your research and extraction now.
"""


def get_roles_extraction_prompt(company_name: str, base_path: Optional[Path] = None) -> str:
    """Generate prompt for extracting roles with orgmap integration.

    Args:
        company_name: Company name
        base_path: Optional custom data directory

    Returns:
        Prompt string for roles extraction

    Example:
        >>> prompt = get_roles_extraction_prompt("Apple")  # doctest: +SKIP
        >>> "WCTF" in prompt
        True
    """
    # Try to load orgmap for context
    from wctf_core.operations.orgmap import get_orgmap

    orgmap_result = get_orgmap(company_name, base_path)
    has_orgmap = orgmap_result.get('success', False)

    if has_orgmap:
        orgmap = orgmap_result['orgmap']
        peaks_info = "\n".join([
            f"- **{p['peak_name']}** (ID: {p['peak_id']})"
            for p in orgmap.get('peaks', [])
        ])
        teams_info = "\n".join([
            f"  - {team['team_name']} (ID: {team['team_id']})"
            for peak in orgmap.get('peaks', [])
            for team in peak.get('rope_teams', [])
        ])

        orgmap_section = f"""
## Existing Organizational Map

We already have an orgmap for {company_name}. Try to link roles to these structures:

### Peaks (VP orgs):
{peaks_info}

### Rope Teams (Director teams):
{teams_info}

When you find a role, include `rope_team_id` if you can match it to a team above.
"""
    else:
        orgmap_section = f"""
## No Organizational Map Yet

We don't have an orgmap for {company_name} yet. Extract org signals from role postings:
- Team names mentioned in job descriptions
- Director/VP names
- Org structures referenced

This will help us build the orgmap later.
"""

    return f"""# Role Search for {company_name}

Your task is to find open senior engineering roles and analyze them with the WCTF framework.

{orgmap_section}

## What to Extract

For each role, extract:

### Basic Info
- **Role ID**: Unique identifier (e.g., "{company_name.lower().replace(' ', '_')}_202511_senior_swe_k8s")
- **Title**: Job title
- **URL**: Link to posting
- **Posted Date**: YYYY-MM-DD
- **Location**: Where the role is based
- **Seniority**: senior_ic / staff_plus / management

### Orgmap Linking (if possible)
- **rope_team_id**: Link to rope team from orgmap (if applicable)
- **rope_team_name**: Team name

### Role Details
- **Description**: Brief description of the role
- **Requirements**: List of key requirements
- **Salary Range**: If disclosed (e.g., "$180k-$250k")

### WCTF Analysis
Analyze the role against the WCTF framework:

- **analyzed_date**: YYYY-MM-DD when you analyzed it
- **coordination_style**: alpine / expedition / established / orienteering / trail_crew
- **terrain_match**: good_fit / workable / mismatched
- **mountain_clarity**: clear / unclear / conflicting
- **energy_matrix**: Predicted quadrants and task distribution
- **alignment_signals**: Green flags and red flags

## Output Format

Return YAML in this structure:

```yaml
company: "{company_name}"
company_slug: "{company_name.lower().replace(' ', '-')}"
last_updated: "YYYY-MM-DD"
search_metadata:
  sources: ["careers_page", "LinkedIn"]
  last_search_date: "YYYY-MM-DD"

peaks:
  - peak_id: "peak_id_from_orgmap"
    peak_name: "Peak Name"
    roles:
      - role_id: "unique_role_id"
        title: "Senior SWE - Kubernetes"
        url: "https://jobs.company.com/123"
        posted_date: "2025-11-01"
        location: "Cupertino, CA"
        rope_team_id: "team_id_from_orgmap"
        rope_team_name: "K8s Platform"
        seniority: "senior_ic"
        description: "Build K8s control plane"
        requirements:
          - "8+ years experience"
          - "Deep K8s knowledge"
        salary_range: "$180k-$250k"
        wctf_analysis:
          analyzed_date: "2025-11-11"
          coordination_style: "expedition"
          terrain_match: "good_fit"
          mountain_clarity: "clear"
          energy_matrix:
            predicted_quadrant: "moare"
            reasoning: "High autonomy, clear impact"
          alignment_signals:
            green_flags:
              - "Technical depth valued"
              - "Platform focus aligns"
            red_flags:
              - "Some legacy systems"

unmapped_roles:
  - role_id: "unmapped_role_id"
    title: "Senior Engineer - Special Projects"
    url: "https://jobs.company.com/456"
    posted_date: "2025-11-05"
    location: "Remote"
    seniority: "senior_ic"
    description: "Stealth project"
    wctf_analysis:
      analyzed_date: "2025-11-11"
      coordination_style: "alpine"
      terrain_match: "workable"
      mountain_clarity: "unclear"
```

## Research Strategy

1. **Company careers page**: Primary source for current openings
2. **LinkedIn Jobs**: Additional postings
3. **Greenhouse/Lever**: If company uses these platforms
4. **Filter for senior roles**: Focus on senior_ic and staff_plus

## WCTF Analysis Guidelines

### Coordination Style Signals
- **Alpine**: Small team, fast decisions, high autonomy
- **Expedition**: 8+ teams coordinating, quarterly planning
- **Established**: Clear playbook, proven patterns
- **Orienteering**: Exploring new territory
- **Trail Crew**: Building infrastructure for others

### Terrain Match
- **good_fit**: Role aligns with your strengths and preferences
- **workable**: Some alignment, some stretches
- **mismatched**: Poor fit

### Mountain Clarity
- **clear**: Obvious impact and path forward
- **unclear**: Vague goals or metrics
- **conflicting**: Mixed signals about direction

Begin your research and extraction now.
"""
