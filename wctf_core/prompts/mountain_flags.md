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

## Energy Matrix Integration

For each flag, identify **task implications** - what you'll actually DO day-to-day because of this fact.

### Task Implication Structure

For each flag, add `task_implications` with:

```yaml
task_implications:
  - task: "Clear description of what you'll do"
    time_estimate_pct: "15-20%"  # Or single value like "10%"
    characteristics:
      # Conflict & alignment
      conflict_exposure: "high" | "moderate" | "low" | "none"
      alignment_clarity: "high" | "moderate" | "low"
      authority_ambiguity: "high" | "moderate" | "low"

      # Progress & autonomy
      progress_visibility: "high" | "moderate" | "low"
      autonomy_level: "high" | "moderate" | "low"
      decision_speed: "fast" | "moderate" | "slow"

      # Skill alignment (check profile.yaml for your strengths)
      learning_required: "none" | "low" | "moderate" | "high"
      uses_systems_thinking: true | false
      uses_tool_building: true | false
      uses_glue_work: true | false
      uses_infrastructure_automation: true | false
      uses_decision_frameworks: true | false

      # Work context
      collaboration_type: "solo" | "paired" | "team" | "cross_team"
      meeting_intensity: "low" | "moderate" | "high"
      requires_sync_communication: true | false
      timezone_spread: "co_located" | "narrow" | "moderate" | "wide"
    notes: "Optional notes about this task"
```

### Time Estimate Realism - CRITICAL GUIDANCE

**IMPORTANT**: Time estimates must reflect ACTUAL organizational overhead, not wishful thinking. Dysfunction consumes time exponentially, not linearly.

**Organizational Health Levels (use research facts to classify):**

**Level 1 - Exceptional Stability** (profitable, founder-led 10+ years, no layoffs, high sentiment):
- Green (productive work): 70-85%
- Yellow (coordination): 10-20%
- Red (defensive): 0-10%

**Level 2 - Healthy Growth** (growing revenue, stable leadership, good sentiment 3.5-4.0):
- Green (productive work): 60-70%
- Yellow (coordination): 20-30%
- Red (defensive): 5-15%

**Level 3 - Moderate Dysfunction** (1-2 layoffs, occasional reorgs, mixed sentiment 3.0-3.5):
- Green (productive work): 50-60%
- Yellow (coordination): 25-35%
- Red (defensive): 15-25%

**Level 4 - Severe Dysfunction** (3+ layoffs in 18mo, reorgs every 6mo, <3.0 sentiment):
- Green (productive work): 30-45%
- Yellow (coordination): 30-40%
- Red (defensive): 25-40%

**Level 5 - Terminal Decline** (mass layoffs >30%, leadership exodus, bankruptcy risk):
- Green (productive work): 10-25%
- Yellow (keeping lights on): 30-40%
- Red (survival/exit): 40-60%

**Task-Specific Time Guidance:**

*Navigating Reorgs:*
- Every 2-3 years: 5-10%
- Every 12-18 months: 10-15%
- Every 6 months: 20-30% (constant realignment overhead)

*Managing Layoff Anxiety:*
- Single past layoff: 5%
- 2 layoffs in 2 years: 10-15%
- 3+ layoffs in 18 months: 15-25% (ongoing survival stress)

*Below-Market Compensation:*
- Slight gap (<10%): 5%
- Moderate gap (10-20%): 10-15%
- Severe gap (>20%) + layoffs: 15-25% (active job search)

*Manager Churn:*
- Stable (2+ years same manager): 0-5%
- 1 change per year: 10%
- 2-3 changes per year: 15-20%
- 5-6 managers in 2 years: 20-25% (constant re-proving value)

*Unclear Product Vision:*
- Clear vision: 0-5%
- Some uncertainty: 10-15%
- "All over the place": 20-30% (constant reprioritization waste)

**Red Flag Compounding:**
Multiple severe issues create MORE than additive overhead due to interaction effects.

**Validation Check:**
- For "PROCEED WITH EXTREME CAUTION" companies → Energy Sustainability should be MEDIUM or LOW (not HIGH)
- For "CONCERNING STABILITY" companies → Usually MEDIUM
- Total time should sum to ~100% (green + yellow + red)

### Reference Profile

Use the `get_profile` tool to see your personal energy drains, generators, and strengths.
Match task characteristics against your profile to ensure accurate quadrant calculation.

### Example

```yaml
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Modern tech stack: Kubernetes, Python, Go"
        impact: "Matches infrastructure expertise"
        confidence: "High - explicit in job description"
        task_implications:
          - task: "Design K8s operators for platform services"
            time_estimate_pct: "20-30%"
            characteristics:
              conflict_exposure: "low"
              alignment_clarity: "high"
              authority_ambiguity: "low"
              progress_visibility: "high"
              autonomy_level: "high"
              decision_speed: "fast"
              uses_systems_thinking: true
              uses_tool_building: true
              uses_infrastructure_automation: true
              learning_required: "low"
              collaboration_type: "team"
              meeting_intensity: "low"
              requires_sync_communication: false
              timezone_spread: "narrow"
            notes: "Platform work with clear scope, autonomous execution"
```

The system will auto-calculate the Energy Matrix quadrant (moare/sparingly/burnout/help_mentoring)
when you save the flags.

## Evaluator Context

You are evaluating from the perspective of a staff engineer (25+ years experience) focused on sustainable excellence and long-term career growth. Consider the five mountain elements as your decision framework.
