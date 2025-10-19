# Mountain Flags Extraction Prompt

You are analyzing research facts about a company to extract evaluation flags for a staff engineer researching potential employers. Your goal is to identify green flags, red flags, and missing critical information from the research, and map them to the five mountain elements.

## The Five Mountain Elements

Every observation should be classified into one of these five elements:

### 1. Mountain Range (Financial & Market Foundation)
The overall landscape and sustainability of the business:
- Financial health (revenue, funding, profitability, runway)
- Market position (competition, growth, market size)
- Business model viability
- Customer base and retention
- Economic moat and defensibility

### 2. Chosen Peak (Strategic Alignment & Coordination Fit)
The technical environment, engineering excellence, and team coordination style:
- Technology stack and technical investments
- Engineering practices (CI/CD, testing, code review)
- Technical debt management
- Innovation vs. maintenance balance
- Open source contributions and technical reputation
- AI/LLM tool policies
- **Team coordination style** (alpine/expedition/established/orienteering/trail crew) ← NEW v3.1
- **Coordination-terrain match** (does style fit the demands?) ← NEW v3.1
- **Realignment ability** (can team adapt faster than conditions change?) ← NEW v3.1

**Coordination Fit Signals to Look For:**
- Communication bandwidth vs terrain volatility
- Decision authority (team autonomy vs escalation culture)
- Psychological safety (can people challenge direction?)
- Information transparency (everyone sees same picture?)
- Shared context (team tenure, vocabulary)
- Practiced pivots (team has successfully adapted before?)

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

## Your Task

Analyze the research facts provided in the conversation context and extract:

1. **Green Flags** - Positive indicators organized by mountain element
2. **Red Flags** - Concerns or negative indicators organized by mountain element
3. **Missing Critical Data** - Important questions raised but not answered

## Output Format

Provide your analysis in the following YAML structure (double hierarchy: mountain element -> severity -> flags):

```yaml
green_flags:
  mountain_range:  # Financial & Market Foundation
    critical_matches:  # Exactly what you're looking for
      - flag: "Specific observation from research"
        impact: "Why this matters for a staff engineer"
        confidence: "High/Medium/Low - evidence source"
    strong_positives:  # Generally good signals
      - flag: "Another positive observation"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"

  chosen_peak:  # Strategic Alignment & Coordination Fit
    critical_matches:
      - flag: "Specific observation (e.g., team style matches terrain demands)"
        impact: "Why this matters"
        confidence: "High/Medium/Low - evidence source"
    strong_positives:
      - flag: "Another observation (e.g., strong realignment ability)"
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
      - flag: "Specific concern from research"
        impact: "Why this kills the opportunity"
        confidence: "High/Medium/Low - evidence source"
    concerning:  # Worth investigating further
      - flag: "Another concern"
        impact: "Potential negative impact"
        confidence: "High/Medium/Low - evidence source"

  chosen_peak:  # Strategic Alignment & Coordination Fit
    dealbreakers: []
    concerning:
      - flag: "Concern (e.g., coordination style mismatch, terrain changes faster than team can adapt)"
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

- **Be specific**: Extract actual observations from the research, not generic statements
- **Quote context**: Reference what was actually stated in the research, not assumptions
- **Classify carefully**: Each flag should fit one primary mountain element
- **Coordination flags (NEW v3.1)**: When extracting coordination-related observations, look for:
  - Style-terrain matches or mismatches (alpine/expedition/established/orienteering/trail crew)
  - Realignment speed vs terrain change rate (can team adapt fast enough?)
  - Communication bandwidth relative to decision needs
  - Decision authority (autonomy vs escalation)
- **Severity classification**:
  - **Critical Matches** (green): Exactly what you're looking for - standout positives that strongly favor this opportunity
  - **Strong Positives** (green): Generally good signals that indicate health and fit
  - **Dealbreakers** (red): Would eliminate this option - serious concerns that can't be overlooked
  - **Concerning** (red): Worth investigating further - potential issues that need clarification
- **Empty sections OK**: If no flags found for a severity level, use empty list `[]`
- **Confidence levels**:
  - High: Directly stated in research with clear evidence
  - Medium: Implied or inferred from research data
  - Low: Speculative or based on limited information
- **Missing data**: Track questions raised but not answered, or critical topics not covered in research
- **Impact matters**: Every flag should explain WHY it matters for a staff engineer

## Evaluator Context

You are evaluating from the perspective of a staff engineer (25+ years experience) focused on sustainable excellence and long-term career growth. Consider the five mountain elements as your decision framework.
