"""Prompt generation for research and extraction workflows."""


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
