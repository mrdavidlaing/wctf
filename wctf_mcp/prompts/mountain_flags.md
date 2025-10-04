# Mountain Flags Extraction Prompt

You are analyzing conversation notes about **{company_name}** to extract evaluation flags for a senior engineer researching potential employers. Your goal is to identify green flags, red flags, and missing critical information from the conversation, and map them to the five mountain elements.

## The Five Mountain Elements

Every observation should be classified into one of these five elements:

### 1. Mountain Range (Financial & Market Foundation)
The overall landscape and sustainability of the business:
- Financial health (revenue, funding, profitability, runway)
- Market position (competition, growth, market size)
- Business model viability
- Customer base and retention
- Economic moat and defensibility

### 2. Chosen Peak (Technical Culture & Work Quality)
The technical environment and engineering excellence:
- Technology stack and technical investments
- Engineering practices (CI/CD, testing, code review)
- Technical debt management
- Innovation vs. maintenance balance
- Open source contributions and technical reputation
- AI/LLM tool policies

### 3. Rope Team Confidence (Leadership & Organization)
Trust in the team and leadership guiding the climb:
- Leadership stability and track record
- Organizational maturity
- Decision-making frameworks
- Manager quality and span of control
- Company culture and values alignment
- Communication patterns

### 4. Daily Climb (Day-to-Day Experience)
The actual experience of working there:
- Meeting load and maker time
- Work-life balance and sustainability
- Compensation and benefits
- Remote/hybrid policies
- Team dynamics and collaboration
- Daily friction points (deployment, tooling, process)
- Geographic considerations

### 5. Story Worth Telling (Growth & Legacy)
Long-term career value and impact:
- Learning opportunities and technical growth
- Impact and scope of work
- Interesting technical challenges
- Career progression paths
- Equity upside potential
- Resume value and industry recognition

## Input: Conversation Notes

{conversation_notes}

## Your Task

Analyze the conversation notes and extract:

1. **Green Flags** - Positive indicators organized by mountain element
2. **Red Flags** - Concerns or negative indicators organized by mountain element
3. **Missing Critical Data** - Important questions raised but not answered

## Output Format

Provide your analysis in the following YAML structure (double hierarchy: mountain element -> severity -> flags):

```yaml
green_flags:
  mountain_range:  # Financial & Market Foundation
    critical_matches:  # Exactly what you're looking for
      - flag: "Specific observation from conversation"
        impact: "Why this matters for a senior engineer"
        confidence: "High/Medium/Low - evidence source"
    strong_positives:  # Generally good signals
      - flag: "Another positive observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"

  chosen_peak:  # Technical Culture & Work Quality
    critical_matches:
      - flag: "Specific observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"
    strong_positives:
      - flag: "Another observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"

  rope_team_confidence:  # Leadership & Organization
    critical_matches: []
    strong_positives:
      - flag: "Observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"

  daily_climb:  # Day-to-Day Experience
    critical_matches:
      - flag: "Observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"
    strong_positives: []

  story_worth_telling:  # Growth & Legacy
    critical_matches: []
    strong_positives:
      - flag: "Observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"

red_flags:
  mountain_range:  # Financial & Market Foundation
    dealbreakers:  # Would eliminate this option
      - flag: "Specific concern from conversation"
        impact: "Why this kills the opportunity"
        confidence: "High/Medium/Low - evidence source"
    concerning:  # Worth investigating further
      - flag: "Another concern"
        impact: "Potential negative impact"
        confidence: "High/Medium/Low - evidence source"

  chosen_peak:  # Technical Culture & Work Quality
    dealbreakers: []
    concerning:
      - flag: "Concern"
        impact: "Why this is concerning"
        confidence: "High/Medium/Low - evidence source"

  rope_team_confidence:  # Leadership & Organization
    dealbreakers: []
    concerning: []

  daily_climb:  # Day-to-Day Experience
    dealbreakers: []
    concerning:
      - flag: "Concern"
        impact: "Why this is concerning"
        confidence: "High/Medium/Low - evidence source"

  story_worth_telling:  # Growth & Legacy
    dealbreakers: []
    concerning: []

missing_critical_data:
  - question: "What specific information is needed?"
    why_important: "Why this matters for the evaluation"
    how_to_find: "How to get this information (interview questions, research sources)"
    mountain_element: "mountain_range/chosen_peak/rope_team_confidence/daily_climb/story_worth_telling"
```

## Important Guidelines

- **Be specific**: Extract actual observations from the conversation, not generic statements
- **Quote context**: Reference what was actually discussed, not assumptions
- **Classify carefully**: Each flag should fit one primary mountain element
- **Severity classification**:
  - **Critical Matches** (green): Exactly what you're looking for - standout positives that strongly favor this opportunity
  - **Strong Positives** (green): Generally good signals that indicate health and fit
  - **Dealbreakers** (red): Would eliminate this option - serious concerns that can't be overlooked
  - **Concerning** (red): Worth investigating further - potential issues that need clarification
- **Empty sections OK**: If no flags found for a severity level, use empty list `[]`
- **Confidence levels**:
  - High: Directly stated in conversation with clear evidence
  - Medium: Implied or inferred from discussion
  - Low: Speculative or based on limited information
- **Missing data**: Track questions raised but not answered, or critical topics not discussed
- **Impact matters**: Every flag should explain WHY it matters for a senior engineer

## Context

- Evaluation date: {evaluation_date}
- Evaluator context: Senior engineer (25yr experience) focused on sustainable excellence
- Decision framework: Five mountain elements for career decisions
