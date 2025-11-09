# Tuned WCTF Flag Extraction Workflow

**Date**: 2025-11-09
**Status**: Quality-controlled and ready for batch application
**Tested on**: Stripe (complex), CircleCI (simpler with red flags)

## Overview

This workflow uses the WCTF SDK to extract company flags with proper `task_implications` that auto-calculate Energy Matrix quadrants. This approach was tested and validated on 2 companies with excellent results.

## Quality Control Results

### Test Company 1: Stripe (Dublin)

**Energy Matrix:**
- MOARE (green): 83.3%
- SPARINGLY (yellow): 16.7%
- BURNOUT (red): 0.0%
- **Energy Sustainability: HIGH**

**Flags Created:**
- 6 green flags with detailed task_implications
- 3 red flags with detailed task_implications
- All characteristics properly set based on company facts
- Time estimates realistic (totaling ~100%)

### Test Company 2: CircleCI

**Energy Matrix:**
- MOARE (green): 66.7%
- SPARINGLY (yellow): 29.2%
- BURNOUT (red): 4.2%
- **Energy Sustainability: HIGH** (but with more overhead)

**Flags Created:**
- 6 green critical matches + 4 strong positives
- 6 red concerning flags
- Demonstrates how organizational chaos affects energy distribution
- Proper differentiation from Stripe (less stable = more draining)

## Validated Workflow

### Step 1: Setup

```python
import sys
from pathlib import Path
sys.path.insert(0, "/home/mrdavidlaing/workspace/pensive/active/projects/wctf")

from wctf_core.operations.flags import save_flags_op
import yaml
```

### Step 2: Read Inputs

```python
# Read company facts
with open("data/stage-1/{company}/company.facts.yaml") as f:
    facts = yaml.safe_load(f)

# Read profile for reference
with open("data/profile.yaml") as f:
    profile = yaml.safe_load(f)
```

### Step 3: Extract Flags with task_implications

For each flag, create `task_implications` with:

**Required structure:**
```yaml
task_implications:
  - task: "Concrete daily task description"
    time_estimate_pct: "25%"
    characteristics:
      # Conflict & alignment (3 fields)
      conflict_exposure: "low" | "moderate" | "high"
      alignment_clarity: "high" | "moderate" | "low"
      authority_ambiguity: "low" | "moderate" | "high"

      # Progress & autonomy (3 fields)
      progress_visibility: "high" | "moderate" | "low"
      autonomy_level: "high" | "moderate" | "low"
      decision_speed: "fast" | "moderate" | "slow"

      # Skill alignment (6 fields)
      learning_required: "none" | "low" | "moderate" | "high"
      uses_systems_thinking: true | false
      uses_tool_building: true | false
      uses_glue_work: true | false
      uses_infrastructure_automation: true | false
      uses_decision_frameworks: true | false

      # Work context (4 fields)
      collaboration_type: "solo" | "paired" | "team" | "cross_team"
      meeting_intensity: "low" | "moderate" | "high"
      requires_sync_communication: true | false
      timezone_spread: "co_located" | "narrow" | "moderate" | "wide"
    notes: "Optional context explaining quadrant classification"
```

**Total: 16 required characteristics per task_implication**

### Step 4: Build Flags Structure

```python
flags_data = {
    "company": "{company_slug}",
    "evaluation_date": "2025-11-09",
    "evaluator_context": "Extracted from company facts using WCTF tools workflow",
    "profile_version_used": "1.0",
    "green_flags": {
        "mountain_range": {
            "critical_matches": [
                {
                    "flag": "Profitable with $6.1B ARR, 10.6% net margin",
                    "impact": "Zero financial risk, sustainable business model",
                    "confidence": "High - Financial filings",
                    "task_implications": [
                        {
                            "task": "Build payment infrastructure at $1.4T scale",
                            "time_estimate_pct": "35%",
                            "characteristics": {
                                "conflict_exposure": "low",
                                "alignment_clarity": "high",
                                "authority_ambiguity": "low",
                                "progress_visibility": "high",
                                "autonomy_level": "high",
                                "decision_speed": "fast",
                                "learning_required": "low",
                                "uses_systems_thinking": True,
                                "uses_tool_building": True,
                                "uses_glue_work": False,
                                "uses_infrastructure_automation": True,
                                "uses_decision_frameworks": True,
                                "collaboration_type": "team",
                                "meeting_intensity": "low",
                                "requires_sync_communication": False,
                                "timezone_spread": "moderate"
                            },
                            "notes": "Profitability eliminates financial_anxiety drain"
                        }
                    ]
                }
            ],
            "strong_positives": []
        },
        # Focus on mountain_range, leave others empty to avoid auto-distribution
        "chosen_peak": {"critical_matches": [], "strong_positives": []},
        "rope_team_confidence": {"critical_matches": [], "strong_positives": []},
        "daily_climb": {"critical_matches": [], "strong_positives": []},
        "story_worth_telling": {"critical_matches": [], "strong_positives": []}
    },
    "red_flags": {
        "mountain_range": {
            "dealbreakers": [],
            "concerning": [
                # Red flags with task_implications
            ]
        },
        "chosen_peak": {"dealbreakers": [], "concerning": []},
        "rope_team_confidence": {"dealbreakers": [], "concerning": []},
        "daily_climb": {"dealbreakers": [], "concerning": []},
        "story_worth_telling": {"dealbreakers": [], "concerning": []}
    },
    "missing_critical_data": []
}
```

### Step 5: Save Using SDK

```python
# Convert to YAML
flags_yaml = yaml.dump(flags_data, default_flow_style=False, sort_keys=False)

# Save - SDK will auto-calculate quadrants
result = save_flags_op(
    "{company_slug}",
    flags_yaml,
    base_path=Path("/home/mrdavidlaing/workspace/pensive/active/projects/wctf")
)

print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
```

## Quality Guidelines (Validated)

### ✅ DO - These Practices Worked Well

1. **Create concrete task descriptions**
   - ✓ "Build payment infrastructure handling $1.4T annual volume"
   - ✗ "Work on infrastructure"

2. **Vary characteristics based on company facts**
   - Profitable company → conflict_exposure: "low"
   - Layoffs/reorgs → conflict_exposure: "moderate" or "high"
   - API-first culture → autonomy_level: "high", decision_speed: "fast"
   - Organizational chaos → authority_ambiguity: "high", alignment_clarity: "low"

3. **Set uses_* flags based on actual work**
   - Infrastructure work → uses_systems_thinking: true, uses_infrastructure_automation: true
   - API development → uses_tool_building: true
   - Cross-team coordination → uses_glue_work: true

4. **Make time estimates realistic**
   - Green flags should total 60-80%
   - Red flags should total 20-40%
   - Individual tasks typically 5-35%

5. **Reference profile drains and generators**
   - Profitable company → eliminates financial_anxiety
   - Clear product vision → provides aligned_collaboration generator
   - Frequent reorgs → triggers misalignment severe drain

### ❌ DON'T - Issues to Avoid

1. **Don't use generic "medium" for everything**
   - Bad: All flags have conflict_exposure: "medium"
   - Good: Vary based on company context (low/moderate/high)

2. **Don't skip required characteristics**
   - All 16 fields must be present
   - SDK validation will fail if missing fields

3. **Don't manually set energy_quadrant**
   - The SDK calculates this automatically
   - Manual values will be overwritten

4. **Don't create abstract tasks**
   - Bad: "Support business objectives"
   - Good: "Design K8s operators for CI/CD pipeline"

5. **Don't use wrong base_path**
   - Issue found: Using `base_path=Path.cwd() / "data"` creates nested `data/data/`
   - Fix: Use `base_path=Path.cwd()` when working in wctf root

## Characteristics Decision Guide (Field-Tested)

### conflict_exposure

Based on actual company indicators:

- **high**: Layoffs + culture problems + leadership departures
  - Example: CircleCI (3 layoffs in 18 months, "disconnected executives")

- **moderate**: Rapid growth with some instability
  - Example: Stripe Jan 2025 (300 layoffs despite growth)

- **low**: Stable, profitable, good employee sentiment
  - Example: Stripe overall (3.9/5 Glassdoor, founder-led)

### alignment_clarity

Based on strategic coherence:

- **high**: Clear product vision, profitable, strong PMF
  - Example: Stripe ($1.4T processed, 34% growth, market leader)

- **moderate**: Some uncertainty but decent direction

- **low**: Frequent pivots, unclear priorities, "vision all over the place"
  - Example: CircleCI (reorgs every 6 months, declining market share)

### authority_ambiguity

Based on organizational structure:

- **high**: Matrix org, unclear ownership, manager churn
  - Example: CircleCI (5-6 managers in 2 years)

- **moderate**: Some overlap in decision-making

- **low**: Clear ownership, stable leadership
  - Example: Stripe (founder-led since 2010)

### learning_required

Based on alignment with profile strengths:

- **none/low**: Uses 2+ core expert strengths
  - systems_thinking + infrastructure_automation + tool_building

- **moderate**: Partially uses strengths, some new skills
  - Uses 1 expert strength + learning new domain

- **high**: Outside all core strengths
  - Sales, marketing, pure management (no tool building)

## Energy Matrix Interpretation

### High Sustainability (Both test companies achieved this)

**Stripe: 83.3% MOARE**
- Profitable → no financial_anxiety
- Clear vision → aligned_collaboration
- Infrastructure work → uses expert strengths
- API-first culture → high autonomy, visible progress

**CircleCI: 66.7% MOARE**
- Good tech stack → uses expert strengths
- Remote-first → timezone flexibility
- CI/CD infrastructure → tool building, systems thinking

### Yellow Flags (SPARINGLY quadrant)

**Stripe: 16.7%**
- Minor layoff uncertainty
- Some coordination overhead

**CircleCI: 29.2%**
- Frequent reorgs (15% of time)
- Layoff anxiety (10%)
- Async timezone coordination (10%)

### Red Flags (BURNOUT quadrant)

**Stripe: 0.0%**
- No tasks that drain energy without using strengths

**CircleCI: 4.2%**
- Compensation negotiation during financial stress (5%)
- Combines high learning + energy drains

## Validated Time Estimates

### Typical Distribution

**Green Flags (60-80% total):**
- 1-2 major tasks: 25-35% each
- 2-3 medium tasks: 10-20% each
- 1-2 minor tasks: 5-10% each

**Red Flags (20-40% total):**
- 1-2 major drains: 10-15% each
- 2-3 minor drains: 5-10% each

### Example (Stripe)

Green:
- Build payment infrastructure (35%)
- Design APIs/SDKs (25%)
- AI/ML fraud detection (20%)
- Open source contributions (10%)
- Conference talks (5%)
- Remote collaboration (5%)
Total: 100%

Red:
- Navigate layoff uncertainty (10%)
- Timezone coordination overhead (5%)
- Compensation discussions (5%)
Total: 20%

## Next Steps for Batch Application

1. **Create batch assignments** - Group remaining 37 companies into batches of 8-10
2. **Launch parallel subagents** - Each processes one batch using this workflow
3. **Quality review** - Spot-check 2-3 companies per batch for characteristic quality
4. **Aggregate analysis** - Compare all companies by Energy Matrix sustainability

## Issues Discovered (For Future Improvement)

1. **Flag auto-distribution**: SDK appears to duplicate flags across all 5 mountain elements. Need to investigate if this is intended behavior or bug.

2. **base_path handling**: Using `base_path=Path.cwd() / "data"` creates nested directory. Should use `base_path=Path.cwd()` when already in wctf root.

3. **Merge behavior**: When existing flags present, SDK may duplicate during merge. May want to start fresh for clean results.

## Success Criteria

✅ All 16 characteristics present per task
✅ Percentages sum to 100% (normalized correctly after bug fix)
✅ Characteristics vary based on company context
✅ uses_* flags align with profile strengths
✅ Energy Matrix shows realistic differentiation (Stripe 83.3% vs CircleCI 66.7%)
✅ Synthesis identifies key drains (misalignment, authority_ambiguity, financial_anxiety)

This workflow is ready for batch application across all remaining companies.
