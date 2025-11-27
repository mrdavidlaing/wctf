# Search and Map Roles

Search for open roles and map them to organizational structure (company.roles.yaml).

## What It Does

Finds and categorizes open roles by:
- **Role Details**: Title, seniority, location, requirements
- **Organizational Mapping**: Links roles to known peaks/rope teams
- **WCTF Analysis**: Evaluates role fit against framework dimensions
- **Unmapped Roles**: Identifies roles needing orgmap updates

## Steps

### 1. Get Search Prompt

Run search-roles command to get a structured search prompt:

```bash
/search-roles {{company}}
```

This provides a detailed prompt for searching:
- **Role sources**: Company careers page, LinkedIn, industry job boards
- **Search strategy**: Keywords, filters, targeting approach
- **Mapping criteria**: How to match roles to orgmap structure
- **Analysis framework**: WCTF dimensions to evaluate for each role

### 2. Conduct Role Search

Use the prompt to search for open roles through:
- **Company careers page**: Most direct source of current openings
- **LinkedIn**: Search for company + specific technologies/seniority
- **Industry job boards**: AngelList, Otta, Built In, etc.
- **Technical communities**: HN, Reddit, Discord for specific tech stacks
- **Referrals**: Reach out to insider connections for warm intros

### 3. Extract and Map Role Data

Structure your findings as YAML:

```yaml
company: "Company Name"
last_updated: "YYYY-MM-DD"
search_metadata:
  sources: ["company careers", "LinkedIn", "referrals"]
  last_search_date: "YYYY-MM-DD"
  search_strategy: "Targeted search for senior+staff roles in cloud infrastructure"
  notes: "Focused on roles matching orgmap peaks/rope teams"

peaks:
  - peak_id: "cloud_services"  # Must match existing orgmap peak_id
    peak_name: "Cloud Services"
    roles:
      - role_id: "unique_id_like_202511_senior_swe_k8s"
        title: "Senior Software Engineer, Kubernetes"
        url: "https://company.com/careers/12345"
        posted_date: "2025-11-27"
        location: "Remote / San Francisco, CA"
        rope_team_id: "platform_infrastructure"  # Links to orgmap rope team
        rope_team_name: "Platform Infrastructure"
        seniority: "senior_ic"  # senior_ic, staff_plus, management
        description: "Build and maintain Kubernetes infrastructure for cloud services"
        requirements:
          - "5+ years of production Kubernetes experience"
          - "Go programming proficiency"
          - "Experience with distributed systems"
          - "Understanding of cloud security principles"
        salary_range: "$180,000-$250,000"
        wctf_analysis:
          analyzed_date: "2025-11-27"
          coordination_style: "established"
          terrain_match: "good_fit"
          mountain_clarity: "clear"
          energy_matrix:
            quadrants: ["optimize", "automate"]
            tasks: ["infrastructure_maintenance", "reliability_improvement"]
          alignment_signals:
            green_flags:
              - "Clear technical challenges"
              - "Established team processes"
            red_flags:
              - "High on-call rotation without proper staffing"

unmapped_roles:  # Roles that couldn't be mapped to known org structure
  - role_id: "202511_senior_ml_engineer"
    title: "Senior ML Engineer"
    url: "https://company.com/careers/67890"
    posted_date: "2025-11-27"
    location: "Remote"
    seniority: "senior_ic"
    description: "Build machine learning models for product features"
    requirements: ["ML experience", "Python", "TensorFlow/PyTorch"]
    notes: "New team not yet documented in orgmap - suggests orgmap update needed"
```

### 4. Save Role Data

Use the WCTF SDK script to save your findings:

```bash
uv run python scripts/search_roles.py {{company}}
```

This will:
- Prompt for role data in YAML format
- Validate with WCTF SDK
- Save to `data/{company-slug}/company.roles.yaml`
- Show summary of mapped vs unmapped roles

Or use the SDK directly:

```python
from wctf_core import WCTFClient

client = WCTFClient()
result = client.save_roles("Company Name", roles_yaml_string)

if result['success']:
    print(f"Roles saved to: {result['path']}")
    print(f"Total roles: {result['roles']['total_roles']}")
    print(f"Mapped roles: {result['roles']['mapped_roles']}")
    print(f"Unmapped roles: {result['roles']['unmapped_count']}")
else:
    print(f"Error: {result['error']}")
```

## Key Concepts

### **Role Seniority Levels**
- **senior_ic**: Senior individual contributor (typically 5+ years experience)
- **staff_plus**: Staff+ levels (Staff, Senior Staff, Principal)
- **management**: People management roles (Manager, Director, VP)

### **WCTF Analysis Dimensions**
- **Coordination Style**: How the team works (alpine, expedition, established, etc.)
- **Terrain Match**: How well role fits your skills/experience
- **Mountain Clarity**: How clear the role's responsibilities and impact are
- **Energy Matrix**: Which quadrants and tasks the role involves

### **Mapping Strategy**
1. **Exact matches**: Role clearly maps to known rope team
2. **Close matches**: Role similar to known team focus area
3. **New teams**: Roles suggesting undocumented org structure
4. **Cross-functional**: Roles spanning multiple peaks/rope teams

## Integration with OrgMap

Role search builds on organizational maps by:

### **Using OrgMap for Targeting**
- **Focus search**: Look for roles in known peaks/rope teams
- **Keyword optimization**: Use tech focus from orgmap in search queries
- **Insider targeting**: Reach out to contacts in relevant teams
- **Culture matching**: Evaluate coordination style fit

### **Identifying OrgMap Gaps**
- **Unmapped roles**: May indicate new teams or reorgs
- **New tech areas**: Suggest expanding orgmap tech focus
- **Growth indicators**: Multiple roles in new area = expanding team
- **Skill gaps**: Roles requiring skills not in current orgmap

### **Validation Cross-Check**
- **Team size consistency**: Role volume should match orgmap team sizes
- **Seniority distribution**: Check if role levels make sense for org structure
- **Tech alignment**: Required skills should match known tech focus
- **Location patterns**: Remote vs office distribution

## Search Sources and Strategies

### **Primary Sources**
1. **Company Careers Page**: Most accurate and up-to-date
2. **LinkedIn**: Advanced search with company + technology filters
3. **Employee Referrals**: Highest conversion rate through insider connections
4. **Technical Job Boards**: Industry-specific boards (HackerX, Otta, etc.)

### **Search Optimization**
- **Technology keywords**: Use orgmap tech_focus for search terms
- **Seniority filters**: Target appropriate experience levels
- **Location filters**: Consider remote vs office preferences
- **Company size filters**: Adjust search strategy based on orgmap metrics

### **Engagement Strategy**
1. **Warm intros**: Contact insider connections first
2. **Direct applications**: Apply through company careers page
3. **Recruiter outreach**: Engage specialized tech recruiters
4. **Community presence**: Participate in relevant technical communities

## Quality Assessment

### **Role Quality Indicators**
- **Clear requirements**: Specific skills and experience levels
- **Impact description**: Role shows clear business impact
- **Growth potential**: Career progression opportunities
- **Team context**: How role fits into broader organization
- **Technical depth**: Challenging problems to solve

### **Red Flags to Watch**
- **Vague descriptions**: Unclear responsibilities or requirements
- **Unrealistic expectations**: Too many requirements for role level
- **High turnover**: Same role posted frequently
- **No clear manager**: Unclear reporting structure
- **Budget constraints**: Low salary ranges for required experience

## File Location

Role data is saved to:
```
data/{company-slug}/company.roles.yaml
```

This integrates with organizational maps and provides:
- **Role-to-org mapping**: Clear link between roles and teams
- **WCTF analysis**: Framework-based evaluation of each role
- **Search tracking**: Metadata about sources and strategies used
- **Gap identification**: Unmapped roles suggest orgmap updates

## Iterative Process

Role search and org mapping is iterative:

1. **Initial orgmap**: Create basic organizational structure
2. **Role search**: Find and map current openings
3. **Gap analysis**: Identify unmapped roles and new teams
4. **Orgmap update**: Refine organizational structure
5. **Repeat**: Continue cycle as new roles are posted

This ensures your organizational knowledge stays current and role search becomes more targeted over time.