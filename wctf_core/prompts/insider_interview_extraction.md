# Insider Interview Fact Extraction: {company_name}

Extract factual information from an insider interview transcript about **{company_name}**. Convert the conversational content into structured, categorized facts suitable for employer evaluation.

## Interview Context

- **Interviewee**: {interviewee_name}
- **Role**: {interviewee_role}
- **Interview Date**: {interview_date}
- **Company**: {company_name}

## Extraction Guidelines

### Fact Classification

**Objective Facts**: Statements that can be verified or represent concrete data
- Examples: "$400M ARR", "Team of 3 people", "600 employees", "No layoffs in 2024"
- Should be things that could theoretically be fact-checked against company records

**Subjective Facts**: Personal observations, opinions, or cultural assessments
- Examples: "Culture is lighter than HubSpot", "People are more relaxed", "Manager is supportive"
- Represent the interviewee's personal experience or perception
- Still valuable for understanding insider perspective

### Source Attribution

Format source as: `{interviewee_name} ({interviewee_role})`

Example: `Ahmad A (Senior Engineer, Observability Department)`

If role has multiple components, include the most relevant details. If role is unknown, use just the name.

### Confidence Level

Use `firsthand_account` for all facts from insider interviews, since the interviewee has direct experience with the company.

### Context Field

Use the optional `context` field to provide additional nuance:
- For subjective facts: comparison points, timeframe of experience
- For objective facts: clarification, scope, or caveats
- Example: "After 5 weeks at company" or "Compared to HubSpot's mandatory PR metrics"

## Categories

Extract facts into these four categories:

### 1. Financial Health
- Revenue figures (ARR, MRR, team-specific attribution)
- Profitability status
- Funding status
- Customer counts
- Layoffs or hiring plans
- Growth rates
- Team economics

### 2. Market Position
- Product offerings and value proposition
- Customer base and notable clients
- Competitive positioning
- Market strategy
- Geographic presence
- Technology differentiators

### 3. Organizational Stability
- Company culture and working environment
- Work-life balance policies
- Management style and quality
- Team structure and sizes
- Remote/hybrid/office policies
- Career development opportunities
- Performance management
- Company stability signals
- **Team coordination style and decision-making** (NEW in v3.1)
- **Realignment ability when direction changes** (NEW in v3.1)

**Coordination & Realignment Facts to Extract:**
- Team coordination archetype (alpine/expedition/established route/orienteering/trail crew)
- Communication bandwidth (calendar overlap, sync meeting time)
- Decision authority (what team can decide vs must escalate)
- Psychological safety (can people challenge direction?)
- Information transparency (does everyone see the full picture?)
- Shared context (team tenure, shared vocabulary)
- Pivot practice (how team handles direction changes)
- Timezone distribution and impact on coordination
- Cross-team decision-making patterns

**Examples:**
- *Objective*: "Team has 4 hours of calendar overlap per week" or "All architecture decisions must be approved by central committee"
- *Subjective*: "Team pivots feel chaotic" or "People are afraid to question leadership decisions"

### 4. Technical Culture
- Technology stack and tools
- Development practices
- AI/ML tool usage policies
- Code review practices
- Meeting load and maker time
- Open source involvement
- Technical decision-making autonomy
- Engineering standards

## Output Format

Structure your output as valid YAML with this exact format:

```yaml
company: "{company_name}"
last_updated: "{interview_date}"

financial_health:
  facts_found:
    - fact: "Descriptive statement"
      source: "{interviewee_name} ({interviewee_role})"
      date: "{interview_date}"
      confidence: "firsthand_account"
      fact_type: "objective" | "subjective"
      context: "Optional additional context"
  missing_information:
    - "Information not discussed in interview"

market_position:
  facts_found: [...]
  missing_information: [...]

organizational_stability:
  facts_found: [...]
  missing_information: [...]

technical_culture:
  facts_found: [...]
  missing_information: [...]

summary:
  total_facts_found: <number>
  information_completeness: "high" | "medium" | "low"
  most_recent_interview: "{interview_date}"
  oldest_interview: "{interview_date}"
  total_interviews: 1
  interviewees:
    - name: "{interviewee_name}"
      role: "{interviewee_role}"
      interview_date: "{interview_date}"
```

## Extraction Strategy

1. **Read the entire transcript first**: Understand the full conversation flow
2. **Identify concrete statements**: Numbers, dates, specific policies, team structures
3. **Capture cultural observations**: How the interviewee describes the work environment
4. **Note comparisons**: When interviewee compares to other companies (valuable context)
5. **Extract indirect facts**: Information revealed through stories or examples
6. **Preserve nuance**: Use context field to maintain important qualifications

## Important Guidelines

- **Every statement becomes a separate fact**: Don't combine multiple facts into one
- **Quote accurately**: Keep fact statements close to the original wording
- **Classify carefully**: Be deliberate about objective vs subjective
- **Include context**: Especially for subjective facts and comparisons
- **Skip chitchat**: Focus on substantive information about the company
- **Track gaps**: Note important topics not covered in `missing_information`
- **Completeness**: More facts with proper classification is better than fewer

## Complete YAML Example

```yaml
company: "Grafana Labs"
last_updated: "2025-10-08"

financial_health:
  facts_found:
    - fact: "Company generates $400M ARR as of September 2024"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"

    - fact: "Integration team of 3 engineers generates $40M revenue per year"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Attributed ARR for integrations team"

    - fact: "No economic layoffs have occurred"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Performance-related attrition occurs but no broad layoffs"

  missing_information:
    - "Current profitability margins"
    - "Burn rate and runway"

market_position:
  facts_found:
    - fact: "7,000 paying clients for cloud offering"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"

    - fact: "Building counteroffer to Datadog as primary value proposition"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Department focus is making cloud appealing vs/alongside Datadog"

  missing_information:
    - "Win rate against Datadog"

organizational_stability:
  facts_found:
    - fact: "Culture is lighter and less intense than HubSpot"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "subjective"
      context: "Comparison after 5 weeks at Grafana vs previous HubSpot experience"

    - fact: "No requirement to ship 4-5 PRs per week"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Unlike HubSpot's mandatory PR velocity metrics"

    - fact: "Teams are small, typically 3-4 people"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"

    - fact: "People respect personal boundaries and family responsibilities"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "subjective"
      context: "Interviewee has two small children, mentioned flexibility during interview"

    - fact: "Team coordination is mostly async via Slack, very little real-time overlap"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Team spans multiple timezones globally"

    - fact: "Most technical decisions can be made by team without external approval"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"

    - fact: "Last strategic shift took about 2 weeks for team to fully realign"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Shift from monolith to microservices approach"

  missing_information:
    - "Formal parental leave policies"
    - "Promotion timeline and criteria"
    - "How cross-team conflicts get resolved"

technical_culture:
  facts_found:
    - fact: "Engineers can use any AI tools, company provides licenses"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "No AI mandate like HubSpot/Shopify had"

    - fact: "Tech stack: Go backend, TypeScript/React frontend, LGTM observability stack"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"

    - fact: "Communication is mostly async via Slack"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"

    - fact: "Managers are people-focused, not hands-on technical"
      source: "Ahmad A (Senior Engineer, Observability Department)"
      date: "2025-10-08"
      confidence: "firsthand_account"
      fact_type: "objective"
      context: "Manager manages multiple teams, ~15 reports total"

  missing_information:
    - "On-call rotation frequency"
    - "Code review SLA"

summary:
  total_facts_found: 18
  information_completeness: "high"
  most_recent_interview: "2025-10-08"
  oldest_interview: "2025-10-08"
  total_interviews: 1
  interviewees:
    - name: "Ahmad A"
      role: "Senior Engineer, Observability Department"
      interview_date: "2025-10-08"
```

---

**Begin extraction now.** Analyze the transcript in your conversation context and produce the structured YAML output following the format above.
