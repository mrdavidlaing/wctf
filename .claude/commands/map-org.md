# Map Organization Structure

Generate organizational map (company.orgmap.yaml) by researching VP organizations (peaks) and Director teams (rope teams).

## What It Does

Creates a structured organizational map showing:
- **Peaks**: VP-level organizations with leadership, mission, size, and coordination style
- **Rope Teams**: Director-level teams within peaks with technical focus and insider connections
- **Coordination Signals**: Team coordination style indicators (alpine, expedition, established, etc.)
- **Insider Network**: Known contacts within each organization

## Steps

### 1. Get Research Prompt

Run the map-org command to get a structured research prompt:

```bash
/map-org {{company}}
```

This provides a detailed prompt for researching:
- **VP-level leadership**: Names, tenure, reporting structure
- **Organization metrics**: Headcount ranges, growth trends, recent changes
- **Technical focus**: Primary and secondary technology areas
- **Coordination patterns**: Meeting cadence, decision-making style, adaptation signals
- **Insider connections**: People you know who can provide context

### 2. Conduct Research

Use the prompt to research the company through:
- **LinkedIn**: Search for VP and Director titles
- **Company website**: Leadership pages and org charts
- **Press releases**: Recent organizational changes
- **Industry reports**: Company size and growth information
- **Your network**: Reach out to known contacts

### 3. Extract Organizational Data

Structure your findings as YAML:

```yaml
company: "Company Name"
last_updated: "YYYY-MM-DD"
mapping_metadata:
  sources: ["LinkedIn", "company website", "press releases"]
  confidence: "high"  # high, medium, low
  notes: "Additional context about research quality"

peaks:
  - peak_id: "unique_id_like_cloud_services"
    peak_name: "Cloud Services"
    leadership:
      vp_name: "VP Name"
      linkedin: "https://linkedin.com/in/vp-name"
      tenure: "2 years"
      reports_to: "SVP Name"
    mission: "Build and operate cloud infrastructure services"
    org_metrics:
      estimated_headcount: "800-1000"
      growth_trend: "expanding"  # expanding, stable, contracting
      recent_changes:
        - "Hired 50 engineers in Q3"
        - "Launched new product line"
    tech_focus:
      primary: ["kubernetes", "go", "aws"]
      secondary: ["python", "terraform"]
    coordination_signals:
      style_indicators: "established"  # alpine, expedition, established, orienteering, trail_crew
      evidence:
        - "Weekly leadership sync meetings"
        - "Quarterly planning cycles"
        - "Formal architecture review process"
      realignment_signals:
        - "Rapid response to production incidents"
        - "Cross-team initiatives for cloud migration"
    insider_connections:
      - name: "Contact Name"
        relationship: "Former colleague"
        role: "Senior Engineer"
        team: "Platform Infrastructure"
        last_contact: "2025-10"
        willing_to_intro: true
    rope_teams:
      - team_id: "platform_infrastructure"
        team_name: "Platform Infrastructure"
        leadership:
          director_name: "Director Name"
          linkedin: "https://linkedin.com/in/director-name"
        mission: "Maintain core platform services"
        estimated_size: "40-50 engineers"
        tech_focus: ["kubernetes", "go", "monitoring"]
        public_presence:
          - "KubeCon 2024 talk on observability"
          - "Company blog post on reliability"
        insider_info:
          name: "Contact Name"
          relationship: "Current teammate"
          role: "Staff Engineer"
          team: "Platform Infrastructure"
          last_contact: "2025-11"
          willing_to_intro: true
```

### 4. Save Organizational Map

Use the WCTF SDK to save your research:

```python
from wctf_core import WCTFClient

client = WCTFClient()
result = client.save_orgmap("Company Name", orgmap_yaml_string)

if result['success']:
    print(f"Orgmap saved to: {result['path']}")
    print(f"Found {result['orgmap']['total_peaks']} peaks")
    print(f"Found {result['orgmap']['total_rope_teams']} rope teams")
else:
    print(f"Error: {result['error']}")
```

## Key Concepts

### **Peaks (VP Organizations)**
- VP-level business units with P&L responsibility
- Typically 50-1000+ engineers
- Multiple director teams reporting up
- Strategic importance to company

### **Rope Teams (Director Teams)**
- Director-level engineering teams
- Typically 5-50 engineers
- Clear technical focus area
- More stable than project teams

### **Coordination Styles**
- **Alpine**: Fast, lightweight, autonomous teams
- **Expedition**: Goal-oriented, temporary teams for specific objectives
- **Established**: Formal processes, clear hierarchies
- **Orienteering**: Navigation-focused, exploring new territory
- **Trail Crew**: Support-focused, enabling other teams

### **Insider Connections**
- **Warm intros**: People who know you and will vouch for you
- **Cold contacts**: People you can reach out to directly
- **Network value**: Each connection provides unique organizational context

## Validation

The SDK automatically validates:
- **Required fields**: All mandatory data present
- **Slug generation**: Company names converted to filesystem-safe identifiers
- **Headcount format**: Must be range like "40-50" or "800-1000"
- **Enum values**: Coordination styles, growth trends must match allowed values
- **URL formats**: LinkedIn URLs must be valid

## Integration with Role Search

Organizational maps inform role search by:
- **Targeting**: Focus search on known peaks/rope teams
- **Context**: Understand team culture and coordination style
- **Network**: Leverage insider connections for referrals
- **Validation**: Cross-check role postings against known org structure

## Tips

### **Research Strategy**
1. **Start broad**: Get overall company structure first
2. **Go deep**: Research specific peaks and teams
3. **Validate**: Cross-reference multiple sources
4. **Network**: Use insider connections for ground truth

### **Data Quality**
- **Multiple sources**: Don't rely on single source
- **Recent data**: Prioritize information from last 6 months
- **Specific numbers**: Avoid vague descriptions like "large team"
- **Context**: Note why information matters for career decisions

### **Common Challenges**
- **Private companies**: Less public information available
- **Recent reorgs**: Org structure may be in flux
- **Multiple names**: Same role might have different titles internally
- **Geographic distribution**: Teams may be split across locations

## File Location

Organizational maps are saved to:
```
data/{company-slug}/company.orgmap.yaml
```

This integrates with the existing WCTF data structure and can be referenced by role search operations.