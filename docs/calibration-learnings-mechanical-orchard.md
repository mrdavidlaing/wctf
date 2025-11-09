# Calibration Learnings: Mechanical Orchard

**Date**: 2025-11-09
**Test Type**: Real-world insider validation
**Purpose**: Calibrate flag extraction workflow against lived experience

## Executive Summary

Mechanical Orchard extraction based on public facts rated the company as **Level 3-4 dysfunction (MEDIUM sustainability)**. Insider knowledge revealed the reality is **Level 4-5 terminal decline (LOW sustainability)**. This represents a **~20% gap in productive work estimates** and **1 full level optimism bias**.

The key missing signal: **Intent to deceive** (vaporware, POC theater, demo ware) creates moral injury that public facts don't capture.

## Test Setup

**Company**: Mechanical Orchard (user currently works there)
**Data Sources**:
- Public: `data/stage-1/mechanical-orchard/company.facts.yaml`
- Insider: `data/stage-1/mechanical-orchard/company.flags.yaml` (existing file with insider knowledge)

**Test**: Extract flags from public facts only, compare to insider reality

## Results Comparison

### Organizational Health Classification

| Dimension | Public Facts Extraction | Insider Reality | Gap |
|-----------|------------------------|-----------------|-----|
| **Level** | 3-4 (Moderate→Severe) | 4-5 (Severe→Terminal) | **-1 level** |
| **Green Work** | 45-55% | 10-30% | **-20%** |
| **Red Overhead** | 20-30% | 40-60% | **-25%** |
| **Sustainability** | MEDIUM | LOW | **-1 level** |
| **Verdict** | MAYBE (proceed with caution) | HARD NO (don't waste time) | **Wrong call** |

### What Public Facts Showed

**Green Flags Identified:**
- ✅ Founder pedigree (Rob Mee → Pivotal Labs success)
- ✅ Strong funding ($53M Series A, Insight Partners)
- ✅ Interesting technical challenge (mainframe modernization)
- ✅ Smart team (Kent Beck involved, pair programming culture)
- ✅ Remote-first culture

**Red Flags Identified:**
- ✅ Customer concentration (1 customer in 2+ years)
- ✅ Sales failure (zero new customers in 2024)
- ✅ Vaporware concerns (product not real)
- ✅ Kent Beck departure (technical leader left)
- ✅ Pivot/desperation (fundamental product change)

**Assessment**: "Exceptional challenge + culture vs existential crisis = MAYBE"

### What Insider Reality Revealed

**Much Worse Than Public Facts:**

1. **Vaporware is INTENTIONAL DECEPTION**, not execution gap
   - "Building demos and lies, not real software"
   - "Potemkin village engineering"
   - This is moral injury (destroys meaning), not just unproductive

2. **POC Theater**, not real business development
   - 5 paid POCs but **ZERO conversions** to date
   - "POC theater not real business"
   - Running POCs with no ability/intent to convert

3. **Scapegoating**, not accountability
   - Sales head "termination" during crisis (not resignation)
   - Blame culture, not fix culture
   - Creates severe interpersonal conflict

4. **Death Spiral Already in Motion**
   - "Classic startup death spiral"
   - Not "pivot or die" - already dying
   - Insider sees inevitable trajectory

5. **Leadership Vacuum**
   - No CTO (technical strategy gap)
   - "Weak leadership" pattern
   - Founder success in past doesn't translate to current execution

**Verdict**: "Don't waste time - this is a clear NO"

## Key Calibration Gaps

### Gap 1: Intent to Deceive (Vaporware)

**Public Signal**: "Product might be vaporware, concerns about real functionality"
**Insider Reality**: "Building demos and lies, not real software"

**Time Impact:**
- Public estimate: 0% (assumed if vaporware, wouldn't work there)
- Insider reality: 20-30% building demos pretending they're real
- **Gap**: Didn't account for moral injury of deception theater

**Learning**: Vaporware creates a special BURNOUT category worse than regular unproductive work.

### Gap 2: POC Theater

**Public Signal**: "5 paid POCs" (sounds like traction)
**Insider Reality**: Zero conversions, "POC theater not real business"

**Time Impact:**
- Public estimate: Assumed POCs were legitimate sales process
- Insider reality: 15-25% performing sales theater with no conversion path
- **Gap**: "X paid POCs" is neutral until conversion rate known

**Learning**: POCs without conversions are red flag, not green flag.

### Gap 3: Scapegoating Culture

**Public Signal**: "Sales head departure" (neutral)
**Insider Reality**: "Sales head termination" during crisis = blame, not accountability

**Time Impact:**
- Public estimate: 0% (didn't detect pattern)
- Insider reality: 10-20% navigating blame dynamics
- **Gap**: Missed interpersonal conflict trigger

**Learning**: Leadership terminations during crisis = scapegoating (red flag).

### Gap 4: Founder Pedigree Over-Weighting

**Public Signal**: "Rob Mee → Pivotal Labs success" (strong green flag)
**Insider Reality**: "Founder pedigree ≠ current execution" (minimal weight)

**Impact:**
- Public estimate: Gave significant credit to past success
- Insider reality: Past success irrelevant when current results failing
- **Gap**: Optimism bias toward "proven leaders"

**Learning**: Founder pedigree only counts if validated by CURRENT results.

### Gap 5: Compounding Dysfunction

**Public Signal**: Multiple severe red flags identified
**Insider Reality**: Multiple severe flags = death spiral (Level 5), not just dysfunction (Level 3-4)

**Impact:**
- Public estimate: Level 3-4 (pivot or die moment)
- Insider reality: Level 4-5 (already dying)
- **Gap**: Didn't compound aggressively enough

**Learning**: Customer loss + sales failure + vaporware + pivot = auto-escalate to Level 5.

## Time Estimate Corrections

### Before Calibration (Public Facts)

**Estimated Time Allocation:**
- Green (productive): 45-55%
  - Build mainframe modernization infrastructure: 30%
  - Design migration tooling: 15-20%

- Yellow (coordination): 25-35%
  - Navigate pivot/product changes: 15-20%
  - Cross-functional collaboration: 10-15%

- Red (defensive): 20-30%
  - Manage financial anxiety (18mo runway): 15%
  - Navigate vaporware misalignment: 10-15%

**Total**: ~100%, MEDIUM sustainability

### After Calibration (Insider Reality)

**Actual Time Allocation:**
- Green (productive): 10-30%
  - Minimal real product work: 10-15%
  - Some infrastructure experimentation: 5-10%
  - Keeping lights on: 5-10%

- Yellow (coordination): 30-40%
  - Navigate constant strategy thrashing: 20-25%
  - Cross-team misalignment: 10-15%

- Red (defensive): 40-60%
  - Building demo ware/vaporware theater: 20-30%
  - POC theater performance: 10-15%
  - Scapegoating navigation: 10-15%
  - Financial anxiety + exit planning: 10-15%
  - Manager/leadership vacuum overhead: 5-10%

**Total**: ~100%, LOW sustainability

### Correction Needed: +30-40% Red Overhead

The missing time went to:
1. **Demo ware construction** (20-30%) - moral injury work
2. **POC theater** (10-15%) - performing sales theater
3. **Scapegoating dynamics** (10-15%) - blame navigation

## Pattern Recognition Successes ✅

Despite optimism bias, the extraction correctly identified:

1. ✅ **Customer concentration as critical risk**
   - Flagged "only 1 customer in 2+ years" as severe
   - Asked about expansion/retention

2. ✅ **Vaporware as dealbreaker**
   - Flagged as "severe misalignment drain"
   - Identified as potential moral injury

3. ✅ **Kent Beck departure as significant signal**
   - Noted "technical thought leader left during crisis"
   - Asked about strategic disagreement vs lost confidence

4. ✅ **Sales failure as existential**
   - "Zero new customers in 2024" flagged as critical
   - Recognized as possibly fatal

5. ✅ **Pivot as desperation**
   - Identified as "panic move" not "calculated"
   - Noted timing (after sales failure)

**What went right**: Pattern recognition, critical thinking, asking right questions

**What went wrong**: Optimism bias in time estimates, giving too much credit to founder pedigree

## Workflow Improvements Implemented

### 1. Theater/Deception Pattern Guidance (Added to Prompt)

```markdown
**Theater/Deception Patterns (Vaporware, POC Theater, Demo Ware):**

*Vaporware (product doesn't exist, only demos):*
- Building demos pretending they're real product: 20-30%
- This is BURNOUT work (moral injury, destroys meaning)
- Triggers: "No real customers," "zero POC conversions," "sales failure"

*POC Theater (running POCs with no conversion intent/ability):*
- Performing sales theater: 15-25%
- Triggers: "X paid POCs" but zero conversions

*Scapegoating Culture (blame vs fix):*
- Navigating blame dynamics: 10-20%
- Triggers: Leadership terminations during crisis, "weak leadership"
```

### 2. Escalation Trigger (Added to Prompt)

```markdown
**When multiple deception patterns present → escalate to Level 5:**
- Customer loss + sales failure + vaporware + pivot = death spiral
- Don't give benefit of doubt - assume Level 5 until insider proves otherwise
```

### 3. Founder Pedigree Discount (Added to Prompt)

```markdown
**Founder Pedigree Discount:**
Past success only counts if validated by CURRENT results.
"Proven leader failing now" is RED flag, not green.
```

### 4. Vaporware Validation Check (Added to Prompt)

```markdown
**Validation Check:**
- For vaporware/POC theater patterns → Usually LOW (10-25% productive work)
```

## Testing Protocol

After implementing improvements, re-extract Mechanical Orchard to verify calibration:

**Expected Results:**
- Organizational Level: 4-5 (Terminal Decline)
- Green Work: 10-30%
- Red Overhead: 40-60%
- Energy Sustainability: LOW
- Verdict: HARD NO

**Success Criteria:**
- Classification matches insider reality (Level 4-5)
- Time estimates within ±10% of insider expectations
- Sustainability rating matches (LOW)
- Verdict matches (HARD NO vs MAYBE)

## Key Lessons for Batch Application

### Critical Patterns to Watch For

1. **Vaporware Indicators:**
   - "No real customers" + "product pivot" + "sales failure"
   - "Demo" or "POC" language without conversions
   - Ask: "Are they building real product or theater?"

2. **POC Theater Indicators:**
   - "X paid POCs" without conversion numbers
   - Customer concentration with no expansion
   - Ask: "What's the POC → customer conversion rate?"

3. **Scapegoating Indicators:**
   - Leadership terminations during crisis
   - "Weak leadership" + "blame culture" in reviews
   - Ask: "Are they fixing problems or finding scapegoats?"

4. **Death Spiral Indicators:**
   - Customer loss + sales failure + pivot + funding concerns
   - Multiple compounding severe issues
   - Ask: "Is this turnaround possible or inevitable decline?"

### When to Escalate to Level 5

**Auto-escalate when ANY of these combinations present:**

1. Customer concentration + sales failure + vaporware
2. Multiple layoffs + pivot + leadership departures
3. Runway < 12mo + sales failure + funding uncertainty
4. "Weak leadership" + "scapegoating" + "strategy thrashing"

**Default assumption**: Level 5 (Terminal Decline) until insider proves otherwise

### Optimism Bias Mitigation

1. **Discount founder pedigree** when contradicted by current results
2. **Assume worst case** when multiple severe signals compound
3. **Treat "X paid POCs"** as neutral until conversion rate known
4. **Flag vaporware early** and add 20-30% theater overhead
5. **Look for intent** behind dysfunction (deception vs execution)

## Validation Metrics

To confirm calibration success, the next batch extraction should:

1. **Classification Accuracy**: Companies with public "CAUTION" verdicts should extract as Level 3-4 or higher
2. **Time Estimate Realism**: Dysfunctional companies should show 40-60% red overhead (not 20-30%)
3. **Sustainability Ratings**: Match expected levels (no "HIGH" for "EXTREME CAUTION" companies)
4. **Insider Validation**: When insider knowledge available, extraction should be within 1 level and ±15% time estimates

## Conclusion

The Mechanical Orchard calibration revealed that **public facts are systematically optimistic** because they miss intentional deception patterns. The workflow improvements add specific guidance for:

1. Detecting theater/deception (vaporware, POC theater, scapegoating)
2. Estimating moral injury overhead (20-40% for deception patterns)
3. Escalating to Level 5 when multiple severe signals compound
4. Discounting founder pedigree when current results fail

**Expected Impact**: Future extractions should be **1 level more realistic** (closer to insider reality) and **20-30% more accurate** on time estimates for dysfunctional organizations.

**Next Test**: Re-extract Mechanical Orchard with updated guidance to verify calibration closes the gap.
