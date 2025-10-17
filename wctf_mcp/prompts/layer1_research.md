# Layer 1 Research: {company_name}

**Research Mode Required:** Please use Claude Desktop's Research mode (the research toggle/button in the UI) for this investigation. Research mode provides deep, multi-source investigation with citations - much better than basic web search.

Gather factual information about **{company_name}** for a senior engineer evaluating potential employers. Collect structured, verifiable facts across four categories.

## Research Scope

Research the following categories and collect facts with sources, dates, and confidence levels:

### 1. Financial Health
Search for:
- Funding rounds (amounts, dates, lead investors, valuation)
- Revenue figures (annual, growth rates)
- Profitability status
- Burn rate and runway
- Employee count trends
- Layoffs or restructuring events
- Customer metrics (count, notable customers)

### 2. Market Position
Search for:
- Company description and value proposition
- Product/service offerings
- Target market and market size
- Competitors and competitive advantages
- Customer reviews and ratings (G2, Capterra, TrustPilot, etc.)
- Geographic presence and regions
- Certifications and compliance (SOC2, ISO, etc.)
- Pricing model

### 3. Organizational Stability
Search for:
- Leadership team (CEO, CTO, VPs with tenure)
- Board members
- Recent executive changes
- Company location and work model (remote/hybrid/office)
- Glassdoor ratings (overall, culture, work-life balance, compensation)
- Employee reviews and sentiment
- Team structure and size

### 4. Technical Culture
Search for:
- Technology stack and languages used
- Open source projects and contributions
- Engineering blog and publication frequency
- Conference talks and technical presentations
- Notable technical employees and their backgrounds
- Hiring practices and interview process
- Development practices (mentioned in job postings or blog posts)
- AI/ML investments or initiatives

## Output Format

For each fact found, structure it as:

```yaml
- fact: "Descriptive statement of the fact"
  source: "Source name (website, publication, or platform)"
  date: "YYYY-MM-DD (date of publication or when fact was current)"
  confidence: "explicit_statement" or "implied"
```

Use `explicit_statement` when the fact is directly stated. Use `implied` when the fact is reasonably inferred from available information.

For each category, also list `missing_information` - important facts you tried to find but couldn't:

```yaml
missing_information:
  - "Description of missing data point"
```

## Research Strategy

1. **Start broad**: Search "{company_name} funding revenue" to get financial overview
2. **Official sources first**: Check company website, blog, LinkedIn, Crunchbase
3. **News and analysis**: Search "{company_name} news 2024", "{company_name} layoffs", "{company_name} funding"
4. **Reviews and ratings**: Check Glassdoor, G2, Capterra, TrustPilot
5. **Technical presence**: Search "{company_name} github", "{company_name} engineering blog", "{company_name} tech stack"
6. **Community discussion**: Look for Hacker News threads, Reddit discussions

## Important Guidelines

- **Be thorough but focused**: Aim for 30-50 high-quality facts per company (maximum 50)
- **Quality over quantity**: Each fact should be significant and verifiable
- **Cite sources**: Every fact must have a source and date
- **Recent data**: Prioritize information from 2023-2025
- **No speculation**: Only include verifiable facts, mark inferred facts appropriately
- **Track missing data**: Be explicit about what you couldn't find
- **Current date context**: Today is {research_date}

## Summary Requirements

After collecting facts, provide:

```yaml
summary:
  total_facts_found: <number>
  information_completeness: "high" | "medium" | "low"
  most_recent_data_point: "YYYY-MM-DD"
  oldest_data_point: "YYYY-MM-DD"
```

## Time Limit

Complete research within 5 minutes. If interrupted, save partial results with appropriate notes in missing_information sections.

## Complete YAML Example

Here's a complete example showing the exact structure required:

```yaml
company: "{company_name}"
research_date: "{research_date}"

financial_health:
  facts_found:
    - fact: "Series A funding of $10 million raised"
      source: "TechCrunch"
      date: "2024-01-15"
      confidence: "explicit_statement"
    - fact: "Annual revenue of $2M in 2024"
      source: "Company blog"
      date: "2024-12-31"
      confidence: "implied"
  missing_information:
    - "Burn rate not publicly disclosed"
    - "Profitability status unknown"

market_position:
  facts_found:
    - fact: "Provides cloud infrastructure for developers"
      source: "Company website"
      date: "{research_date}"
      confidence: "explicit_statement"
  missing_information:
    - "Market share percentage unknown"

organizational_stability:
  facts_found:
    - fact: "CEO Jane Smith, tenure since 2020"
      source: "LinkedIn"
      date: "{research_date}"
      confidence: "explicit_statement"
  missing_information:
    - "Recent layoffs or restructuring unclear"

technical_culture:
  facts_found:
    - fact: "Primary tech stack is Python and Go"
      source: "Engineering blog"
      date: "2024-08-01"
      confidence: "explicit_statement"
  missing_information: []

summary:
  total_facts_found: 5
  information_completeness: "medium"
  most_recent_data_point: "{research_date}"
  oldest_data_point: "2024-01-15"
```

**IMPORTANT**: All four category sections (financial_health, market_position, organizational_stability, technical_culture) and the summary section are REQUIRED, even if some have empty facts_found arrays.
