# Energy Matrix Integration for WCTF v4.0

**Date:** 2025-01-08
**Status:** Design Complete - Ready for Implementation
**Author:** David Laing with Claude Code

## Executive Summary

This design integrates Scott Muc's Energy Matrix into WCTF to evaluate whether daily work will energize or drain you. The framework currently answers "Is this mountain worth climbing?" This addition answers "Will I have the energy TO climb?"

The Energy Matrix classifies work into four quadrants based on two dimensions:
- **Vertical axis:** Does this work energize or drain me?
- **Horizontal axis:** Am I good at this work?

The integration stores your personal profile (energy drains, generators, strengths) in `data/profile.yaml`, captures task implications during flag extraction, auto-calculates which quadrant each task falls into, and synthesizes the distribution to determine if the role is energetically sustainable.

**Key insight:** A role with 70% draining tasks (even with great compensation and mission) leads to burnout. Accept only roles with ≥60% energizing work that leverages your strengths.

## Background

### The Problem

Career decisions based solely on mission, compensation, and team quality miss a critical factor: daily energy sustainability. You discovered this through experience:

- **Current role (MO):** Decent comp, interesting mission, good colleagues (Zell, Toby, Porter)
- **But:** 20-30% of time spent in energy-draining work (Roberto meetings, organizational conflict)
- **Result:** Each draining interaction requires 2-3x recovery time, costing 25-30% of weekly progress capacity

Traditional WCTF evaluation captured this as red flags but couldn't quantify the energy impact or predict sustainability.

### Scott Muc's Energy Matrix

The Energy Matrix classifies daily tasks into four quadrants:

```
                           Good at
        ┌──────────────────┬──────────────────┐
        │                  │                  │
        │   SPARINGLY      │     MUTUAL       │
Drains  │   (Top Left)     │   (Top Right)    │
Energy  │                  │                  │
        │  Skilled but     │  SWEET SPOT:     │
        │  draining work   │  Energizing AND  │
        │  (limit this)    │  leveraging      │
        │                  │  strengths       │
        ├──────────────────┼──────────────────┤
        │                  │                  │
        │   BURNOUT        │  HELP/MENTORING  │
Brings  │   (Bottom Left)  │  (Bottom Right)  │
Energy  │                  │                  │
        │  Weak AND        │  Energizing but  │
        │  draining        │  still learning  │
        │  (eliminate)     │  (growth area)   │
        │                  │                  │
        └──────────────────┴──────────────────┘
                          Bad at
```

**Sustainable role requirements:**
- ≥60% Mutual (green flags)
- ≤20% Burnout (red flags)
- ≤30% Sparingly + Help/Mentoring combined (yellow flags)

### Your Core Value: Progress

Through reflection on experiences with Zell (energizing), Roberto (draining), and building Pensive (pure flow), you identified your fundamental value: **the ability to make progress**.

Everything else serves this:
- **Rope Team (energy source):** Groups amplify progress IF they generate more energy than they drain
- **Aligned Direction:** Misalignment blocks progress through circular motion
- **Financial Stability:** Money anxiety drains energy from progress work
- **Mission:** Adds meaning but doesn't enable progress

**Key insight:** "I'd rather climb to the top of the wrong peak than circle at the bottom of the right one."

Progress requires energy. Energy comes from work that fits the Mutual quadrant.

## Design Goals

1. **Quantify energy sustainability** - Convert subjective "this feels draining" into objective % distribution
2. **Predict burnout risk** - Identify roles that will deplete you before accepting them
3. **Reusable profile** - Store your characteristics once, evaluate many companies against it
4. **Evolving self-knowledge** - Update profile as you learn, re-evaluate companies with new insights
5. **Integration with existing WCTF** - Enhance flag extraction, don't replace it

## Architecture

### Data Structure

```
wctf/
├── data/
│   ├── profile.yaml              # NEW: Your personal profile (versioned)
│   └── <company>/
│       ├── company.facts.yaml    # Existing
│       ├── company.insider.yaml  # Existing
│       └── company.flags.yaml    # ENHANCED: Now includes task implications
```

### Profile Storage (`data/profile.yaml`)

Git tracks version history. The `profile_version` field enables compatibility checking.

```yaml
profile_version: "1.0"
last_updated: "2025-01-08"

# Energy drains (things that deplete your reserves)
energy_drains:
  interpersonal_conflict:
    severity: "severe"  # severe/moderate/mild
    trigger: "childhood_trauma"
    description: "Conflicts in close working relationships cause severe energy drain"

  misalignment:
    severity: "severe"
    trigger: "blocks_progress"
    description: "Team moving in different directions, circular motion instead of forward progress"

  authority_ambiguity:
    severity: "moderate"
    trigger: "creates_latent_conflict"
    description: "Unclear ownership/authority creates hidden conflicts that drain energy"

  financial_anxiety:
    severity: "moderate"
    trigger: "survival_concerns"
    description: "Worrying about money leaks energy from progress work"

# Energy generators (things that restore/amplify your reserves)
energy_generators:
  visible_progress:
    strength: "core_need"  # core_need/strong/moderate
    description: "Building things, shipping features, seeing forward momentum"

  aligned_collaboration:
    strength: "strong"
    description: "Team moving together toward shared goal with clear direction"

  tool_building:
    strength: "core_need"
    description: "Creating systems and tools, flow state work"

  structured_processes:
    strength: "moderate"
    description: "Clear decision frameworks that prevent conflict"

# Core strengths (established expertise)
core_strengths:
  - name: "systems_thinking"
    level: "expert"
    description: "Designing and building complex interconnected systems"

  - name: "tool_building"
    level: "expert"
    description: "Creating automation, CLIs, infrastructure tooling"

  - name: "glue_work"
    level: "expert"
    description: "Bridging between teams, enabling others' progress"

  - name: "infrastructure_automation"
    level: "expert"
    description: "Platform engineering, SRE practices, release engineering"

  - name: "decision_frameworks"
    level: "proficient"
    description: "Building frameworks that prevent misalignment conflicts"

# Growth areas (actively learning)
growth_areas:
  - name: "multi_agent_orchestration"
    current_level: "learning"
    energizing: true
    description: "Coordinating multiple AI agents for complex workflows"

  - name: "ai_augmented_workflows"
    current_level: "proficient"
    energizing: true
    description: "Building human+AI collaboration systems"

# Communication & decision-making preferences
communication_preferences:
  async_work_capability:
    preference: "strong"
    description: "Can make progress through async communication effectively"

  timezone_flexibility:
    max_spread: "6_hours"  # co_located/6_hours/12_hours/global
    notes: "Can handle EU-US East Coast (6hr), struggle beyond that"

  decision_making_speed_needs:
    when_uncertain: "fast_alignment"
    when_clear: "autonomous"
    description: "In uncertain problems, need fast decision cycles to prevent circular motion"

  meeting_intensity_tolerance:
    max_pct: 30
    ideal_pct: 20
    notes: "High meeting load drains energy, especially if unproductive"

# Organizational coherence requirements
organizational_coherence_needs:
  - pattern: "uncertain_problem_space"
    requires_one_of:
      - "async_first_culture"
      - "co_located_team"
      - "fast_sync_decision_cadence"
    incompatible_with:
      - "wide_timezone_spread + sync_heavy_culture"
    impact_if_violated: "severe_drain"
    description: "Uncertain problems need tight feedback loops - either async-friendly OR co-located"
```

### Task Implications in Flags (`company.flags.yaml`)

Each flag now includes task implications that describe what you'll actually DO day-to-day.

```yaml
profile_version_used: "1.0"  # Links to profile.yaml version

green_flags:
  critical_matches:
    - flag: "Modern tech stack: Kubernetes, Python, Go"
      impact: "Matches infrastructure expertise"
      confidence: "High - explicit in job description"
      task_implications:
        - task: "Design K8s operators for platform services"
          time_estimate_pct: "20-30%"
          energy_matrix_quadrant: "mutual"  # AUTO-CALCULATED

          characteristics:
            # Conflict & alignment
            conflict_exposure: "low"          # high/moderate/low/none
            alignment_clarity: "high"         # high/moderate/low
            authority_ambiguity: "low"        # high/moderate/low

            # Progress & autonomy
            progress_visibility: "high"       # high/moderate/low
            autonomy_level: "high"            # high/moderate/low
            decision_speed: "fast"            # fast/moderate/slow

            # Skill alignment (matched against profile.core_strengths)
            uses_systems_thinking: true
            uses_tool_building: true
            uses_glue_work: false
            uses_infrastructure_automation: true
            learning_required: "low"          # none/low/moderate/high

            # Work context
            collaboration_type: "team"        # solo/paired/team/cross_team
            meeting_intensity: "low"          # low/moderate/high
            requires_sync_communication: false
            timezone_spread: "narrow"         # co_located/narrow/moderate/wide

          notes: "Platform work with clear scope, autonomous execution"

red_flags:
  dealbreakers:
    - flag: "Highly siloed teams with chaotic cross-team coordination"
      impact: "Creates constant territorial conflicts and ambiguity"
      confidence: "High - insider validation"
      task_implications:
        - task: "Navigate cross-silo coordination for infrastructure changes"
          time_estimate_pct: "15-20%"
          energy_matrix_quadrant: "burnout"  # AUTO-CALCULATED

          characteristics:
            conflict_exposure: "high"
            alignment_clarity: "low"
            authority_ambiguity: "high"
            progress_visibility: "low"
            autonomy_level: "low"
            decision_speed: "slow"
            uses_systems_thinking: false
            uses_tool_building: false
            uses_glue_work: true              # Strength but hostile context
            learning_required: "moderate"
            collaboration_type: "cross_team"
            meeting_intensity: "high"
            requires_sync_communication: true
            timezone_spread: "moderate"

          notes: "Silo boundaries create constant negotiation conflicts"
```

### Energy Distribution Synthesis

After calculating quadrants for all tasks, aggregate them in the synthesis section:

```yaml
synthesis:
  # Existing WCTF fields
  mountain_worth_climbing: "NO"
  sustainability_confidence: "LOW"
  overall_assessment: "Energy matrix predicts burnout within 12-18 months"

  # NEW: Energy matrix analysis
  energy_matrix_analysis:
    profile_version_used: "1.0"

    predicted_daily_distribution:
      mutual_green_flags:
        percentage: 20
        tasks_count: 3
      sparingly_yellow_flags:
        percentage: 30
        tasks_count: 5
      burnout_red_flags:
        percentage: 40
        tasks_count: 6
      help_mentoring_yellow_flags:
        percentage: 10
        tasks_count: 2

    threshold_analysis:
      meets_green_minimum: false     # ≥60% mutual required
      exceeds_red_maximum: true      # ≤20% burnout allowed
      exceeds_yellow_maximum: true   # ≤30% combined yellow allowed

    organizational_coherence:
      status: "MISMATCH"
      issues:
        - pattern: "uncertain_problem_space"
          observed: "sync_heavy_culture + wide_timezone_spread"
          required: "async_first_culture OR co_located_team"
          impact: "Adds 10-15% ambient energy drain to all tasks"

    energy_sustainability: "LOW"  # HIGH/MEDIUM/LOW

    key_insights:
      - "70% of work in draining quadrants (sparingly + burnout)"
      - "Silos create 40% burnout quadrant work"
      - "Organizational coherence mismatch amplifies conflict drain"

    decision_factors:
      - "REJECT: 40% burnout quadrant exceeds 20% threshold"
      - "RED: Insufficient mutual quadrant work (20% vs 60% needed)"
      - "RED: Organizational mismatch adds ambient drain"
```

## Quadrant Calculation Algorithm

The system auto-calculates `energy_matrix_quadrant` by evaluating task characteristics against your profile.

### Algorithm Logic

```python
def calculate_quadrant(task_characteristics, profile):
    """
    Calculate energy matrix quadrant from task characteristics and profile.

    Returns: "mutual" | "sparingly" | "burnout" | "help_mentoring"
    """

    # Step 1: Calculate "good_at" (strength alignment)
    strength_score = 0

    # Check core strengths usage
    for strength in profile.core_strengths:
        if getattr(task_characteristics, f"uses_{strength.name}", False):
            if strength.level == "expert":
                strength_score += 2
            elif strength.level == "proficient":
                strength_score += 1

    # Check learning requirement (penalty for high learning needs)
    if task_characteristics.learning_required == "high":
        strength_score -= 2
    elif task_characteristics.learning_required == "moderate":
        strength_score -= 1

    # Check if it's a growth area (energizing learning gets bonus)
    for growth_area in profile.growth_areas:
        if matches_growth_area(task_characteristics, growth_area) and growth_area.energizing:
            strength_score += 1

    good_at = strength_score >= 2  # Threshold (tunable)


    # Step 2: Calculate "energizes" (energy impact)
    energy_score = 0

    # Check energy drains
    for drain_name, drain in profile.energy_drains.items():
        if matches_drain(task_characteristics, drain_name):
            if drain.severity == "severe":
                energy_score -= 3
            elif drain.severity == "moderate":
                energy_score -= 2
            elif drain.severity == "mild":
                energy_score -= 1

    # Check energy generators
    for gen_name, generator in profile.energy_generators.items():
        if matches_generator(task_characteristics, gen_name):
            if generator.strength == "core_need":
                energy_score += 3
            elif generator.strength == "strong":
                energy_score += 2
            elif generator.strength == "moderate":
                energy_score += 1

    # Check organizational coherence mismatches (ambient drain)
    for coherence_need in profile.organizational_coherence_needs:
        if violates_coherence(task_characteristics, coherence_need):
            if coherence_need.impact_if_violated == "severe_drain":
                energy_score -= 2

    energizes = energy_score > 0  # Threshold (tunable)


    # Step 3: Map to quadrant
    if good_at and energizes:
        return "mutual"
    elif good_at and not energizes:
        return "sparingly"
    elif not good_at and energizes:
        return "help_mentoring"
    else:
        return "burnout"


def matches_drain(task_characteristics, drain_name):
    """Check if task characteristics trigger a specific energy drain."""
    if drain_name == "interpersonal_conflict":
        return task_characteristics.conflict_exposure == "high"
    elif drain_name == "misalignment":
        return task_characteristics.alignment_clarity == "low"
    elif drain_name == "authority_ambiguity":
        return task_characteristics.authority_ambiguity == "high"
    # ... etc

def matches_generator(task_characteristics, gen_name):
    """Check if task characteristics activate an energy generator."""
    if gen_name == "visible_progress":
        return task_characteristics.progress_visibility == "high"
    elif gen_name == "aligned_collaboration":
        return (task_characteristics.alignment_clarity == "high" and
                task_characteristics.collaboration_type in ["team", "paired"])
    elif gen_name == "tool_building":
        return task_characteristics.uses_tool_building
    # ... etc
```

### Tunable Parameters

The algorithm has several thresholds that can be adjusted based on experience:

- **Strength threshold:** `good_at = strength_score >= 2`
- **Energy threshold:** `energizes = energy_score > 0`
- **Drain severity weights:** severe=-3, moderate=-2, mild=-1
- **Generator strength weights:** core_need=+3, strong=+2, moderate=+1

These can be tuned empirically as you use the tool with real evaluations.

## Workflow Integration

### Enhanced Flag Extraction Workflow

The existing WCTF workflow is enhanced, not replaced:

**1. Get flags extraction prompt** (enhanced existing tool)
```
get_flags_extraction_prompt_tool(company_name)
```

Now includes Energy Matrix guidance:
```
For each flag, identify task implications:
- What will you actually DO day-to-day because of this fact?
- Estimate % of time (ranges okay: "15-20%")
- Characterize each task:
  * Conflict exposure (high/moderate/low/none)
  * Progress visibility (high/moderate/low)
  * Uses your strengths? (systems_thinking, tool_building, etc.)
  * Autonomy level, decision speed, collaboration type
  * Meeting intensity, timezone spread
  * ... [full characteristic list]

Reference profile.yaml for your strengths/drains/generators.
```

**2. Extract flags with task implications** (evaluator work)

Human extracts flags from facts, now including detailed task implications for each flag.

**3. Save flags** (enhanced existing tool)
```
save_flags_tool(company_name, flags_yaml)
```

Enhanced behavior:
- Validates task_implications structure
- Auto-calculates `energy_matrix_quadrant` for each task
- Generates `energy_matrix_analysis` in synthesis section
- Checks thresholds and sets `energy_sustainability`

**4. Review synthesis** (existing)

Synthesis now includes:
- Energy distribution (% per quadrant)
- Threshold violations
- Organizational coherence issues
- Clear accept/reject signal

### New MCP Tools

Three new tools support profile management and energy analysis:

```python
@server.call_tool()
async def get_profile_tool() -> list[types.TextContent]:
    """
    Get current profile.yaml for reference during flag extraction.

    Returns the full profile including energy drains, generators, strengths,
    and organizational coherence needs.
    """
    # Read and return data/profile.yaml


@server.call_tool()
async def update_profile_tool(updated_profile_yaml: str) -> list[types.TextContent]:
    """
    Update profile.yaml with new self-knowledge.

    Args:
        updated_profile_yaml: Complete profile YAML content

    Actions:
        - Increments profile_version (e.g., "1.0" -> "1.1")
        - Updates last_updated timestamp
        - Writes to data/profile.yaml
        - Optionally: flags companies with outdated profile_version_used
    """
    # Parse, increment version, write


@server.call_tool()
async def get_energy_summary_tool(company_name: str) -> list[types.TextContent]:
    """
    Get just the energy_matrix_analysis from synthesis.

    Quick view of energy distribution without full flags.

    Args:
        company_name: Company to analyze

    Returns:
        energy_matrix_analysis section from synthesis
    """
    # Read flags, return synthesis.energy_matrix_analysis
```

## Example Evaluation: Apple Dublin

Using your actual Apple research, here's how Energy Matrix analysis would appear:

### Task Implications Extracted

**Green Flag:** "Modern tech stack: Kubernetes, Python, Go"
- Task: "Design K8s operators" (20-30%) → **Mutual** quadrant
  - High progress visibility, uses core strengths, low conflict

**Red Flag:** "Highly siloed teams with chaotic cross-team coordination"
- Task: "Navigate cross-silo conflicts" (15-20%) → **Burnout** quadrant
  - High conflict, low progress visibility, authority ambiguity
- Task: "Duplicate work due to poor visibility" (5-10%) → **Burnout** quadrant
  - Low progress, frustration from rework

**Red Flag:** "6-month-old Dublin satellite office"
- Task: "Navigate US/Dublin priority conflicts" (10-15%) → **Sparingly** quadrant
  - Good at organizational navigation, but draining

**Yellow Flag:** "Cross-timezone work 4-5 days/month"
- Task: "Attend late-night US sync meetings" (5%) → **Sparingly** quadrant
  - Can do it, but draining

**Green Flag:** "SRE principles with error budgets"
- Task: "Design SLI/SLO frameworks" (15-20%) → **Mutual** quadrant
  - Core strength, visible progress, energizing

### Synthesis Output

```yaml
energy_matrix_analysis:
  predicted_daily_distribution:
    mutual_green_flags:
      percentage: 20
      tasks_count: 3
    sparingly_yellow_flags:
      percentage: 30
      tasks_count: 5
    burnout_red_flags:
      percentage: 40
      tasks_count: 6
    help_mentoring_yellow_flags:
      percentage: 10
      tasks_count: 2

  threshold_analysis:
    meets_green_minimum: false     # 20% << 60% required
    exceeds_red_maximum: true      # 40% >> 20% allowed
    exceeds_yellow_maximum: true   # 40% >> 30% allowed

  organizational_coherence:
    status: "MISMATCH"
    issues:
      - pattern: "uncertain_problem_space"
        observed: "6-month-old team + wide timezone spread"
        required: "co_located_team OR async_first_culture"
        impact: "Uncertainty requires tight feedback - neither present"

  energy_sustainability: "LOW"

  decision_factors:
    - "REJECT: 40% burnout quadrant (2x threshold)"
    - "REJECT: Only 20% mutual quadrant (1/3 of target)"
    - "RED: Organizational coherence mismatch adds ambient drain"
```

**Verdict:** Hard reject despite exceptional comp ($$$) and interesting mission (PCC). Predicted burnout within 12-18 months.

## Implementation Plan

### Phase 1: Core Data Models
- [ ] Create Pydantic models for `profile.yaml` schema
- [ ] Create Pydantic models for task implications in flags
- [ ] Add validation for energy matrix fields
- [ ] Update existing `CompanyFlags` model with new synthesis fields

### Phase 2: Profile Management
- [ ] Implement `get_profile_tool()`
- [ ] Implement `update_profile_tool()` with version incrementing
- [ ] Create initial `data/profile.yaml` from conversation insights
- [ ] Add profile version compatibility checking

### Phase 3: Quadrant Calculation
- [ ] Implement `calculate_quadrant()` algorithm
- [ ] Implement `matches_drain()` helper functions
- [ ] Implement `matches_generator()` helper functions
- [ ] Implement `violates_coherence()` for org mismatch detection
- [ ] Add tunable threshold configuration

### Phase 4: Synthesis Generation
- [ ] Implement energy distribution aggregation
- [ ] Implement threshold checking logic
- [ ] Implement organizational coherence analysis
- [ ] Generate `energy_sustainability` rating
- [ ] Generate `key_insights` and `decision_factors`

### Phase 5: Workflow Integration
- [ ] Enhance `get_flags_extraction_prompt_tool()` with Energy Matrix guidance
- [ ] Enhance `save_flags_tool()` to auto-calculate quadrants
- [ ] Implement `get_energy_summary_tool()`
- [ ] Update flag extraction prompts in `wctf_core/operations/flags.py`

### Phase 6: Testing & Validation
- [ ] Write tests for profile schema validation
- [ ] Write tests for quadrant calculation algorithm
- [ ] Write tests for synthesis generation
- [ ] Test with real company data (Apple Dublin)
- [ ] Tune algorithm thresholds based on results

### Phase 7: Documentation
- [ ] Update `WCTF_FRAMEWORK.md` with Energy Matrix section
- [ ] Update SDK_REFERENCE.md with new tools
- [ ] Create example profile.yaml with annotations
- [ ] Create example company evaluation with Energy Matrix
- [ ] Update README with v4.0 changelog

## Success Criteria

The Energy Matrix integration is successful when:

1. **Predictive accuracy:** Energy analysis correctly predicts your actual experience
   - Test: Evaluate current MO role, should show ~70% mutual + 20-30% sparingly
   - Test: Evaluate Apple Dublin, should show ~40% burnout (matches your rejection)

2. **Decision clarity:** Synthesis provides clear accept/reject signal
   - Threshold violations highlight dealbreakers
   - Organizational coherence issues surfaced explicitly

3. **Reusability:** Profile updates improve all evaluations
   - Update profile with new self-knowledge
   - Re-run synthesis on existing companies
   - See how decisions might change

4. **Practical workflow:** Flag extraction remains manageable
   - Task implications add ~5-10 minutes per flag
   - Characteristics checklist prevents forgetting dimensions
   - Auto-calculation removes manual quadrant assignment burden

## Open Questions

1. **Threshold tuning:** Initial thresholds (≥60% mutual, ≤20% burnout, ≤30% yellow) are estimates. How should we tune these based on experience?

2. **Algorithm weights:** Drain severity weights (severe=-3, moderate=-2, mild=-1) are initial guesses. Should these be configurable per-person?

3. **Growth area bonus:** Should energizing learning areas always bump up strength score, or only when learning_required matches current_level?

4. **Organizational coherence:** We identified one pattern (uncertain_problem_space). What other systemic coherence patterns should we model?

5. **Profile evolution:** When profile version changes, should we auto-flag companies for re-evaluation, or leave that manual?

## Risks & Mitigations

**Risk:** Task time estimates are subjective and might be inaccurate
- **Mitigation:** Use ranges (15-20%) to acknowledge uncertainty
- **Mitigation:** Calibrate by tracking actual time in current role

**Risk:** Too much analysis creates paralysis
- **Mitigation:** Keep flag extraction focused (5-10 min per flag)
- **Mitigation:** Use characteristics checklist to stay structured
- **Mitigation:** Auto-calculation handles complexity

**Risk:** Algorithm thresholds might not match reality
- **Mitigation:** Make thresholds tunable via configuration
- **Mitigation:** Test with known roles (current MO, rejected Apple)
- **Mitigation:** Iterate based on experience

**Risk:** Profile becomes stale if not updated
- **Mitigation:** Include `last_updated` timestamp in profile
- **Mitigation:** Flag companies using old profile versions
- **Mitigation:** Review profile during each major evaluation

## Conclusion

Energy Matrix integration transforms WCTF from "Is this worth climbing?" to "Can I sustain the climb?" By quantifying energy distribution and checking thresholds, it prevents accepting roles that look good on paper but drain you in practice.

The design leverages your deep self-knowledge (profile.yaml), applies it systematically (auto-calculation), and produces clear decisions (threshold checking). It fits naturally into the existing workflow while adding powerful predictive capability.

Most importantly, it codifies your core insight: **progress requires energy, and energy comes from work that energizes you while leveraging your strengths.**

Ready for implementation.
