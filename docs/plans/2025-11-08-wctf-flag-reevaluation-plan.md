# WCTF 4.0 Flag Reevaluation Plan - Parallel Subagent Approach

> **Goal:** Reevaluate all 39 companies' flags using WCTF 4.0 / Energy Matrix evaluation criteria with parallel subagent execution for maximum efficiency.

## Current State

- **Companies with flags:** 39 (4 in stage-2, 35 in stage-1)
- **Current framework version:** WCTF 3.1 (alpine/expedition/established route archetypes)
- **Target framework version:** WCTF 4.0 (Energy Matrix integration)
- **Profile available:** Yes (`data/profile.yaml`)

## Energy Matrix Framework

The Energy Matrix adds personal energy evaluation to WCTF's "worth climbing" assessment:

**Four Quadrants:**
1. **Mutual (60%+ target)** - Uses strengths + energizing
2. **Sparingly (flexible)** - Uses strengths + draining
3. **Burnout (≤20% target)** - Requires learning + draining
4. **Help/Mentoring (flexible)** - Requires learning + energizing

**Key Profile Elements:**
- **Energy drains:** interpersonal_conflict (severe), misalignment (severe), authority_ambiguity (moderate)
- **Energy generators:** visible_progress (core_need), tool_building (core_need), aligned_collaboration (strong)
- **Core strengths:** systems_thinking, tool_building, glue_work, infrastructure_automation
- **Growth areas:** multi_agent_orchestration (learning, energizing), ai_augmented_workflows (proficient, energizing)

## Reevaluation Approach

### Phase 1: Infrastructure Setup (Single-Threaded)

**Objective:** Create the tooling and templates needed for parallel reevaluation.

#### Task 1.1: Create Reevaluation Template
**What:** Write a standardized prompt template for reevaluating a single company's flags.

**Details:**
- Input: company name, existing flags YAML, facts YAML, profile YAML
- Output: Updated flags YAML with Energy Matrix annotations
- Template sections:
  1. Context loading (profile + existing evaluation)
  2. Energy Matrix quadrant mapping instructions
  3. Flag annotation guidance (add task characteristics)
  4. Synthesis update requirements (add energy distribution)
  5. Output format specification

**Location:** `active/projects/wctf/docs/reevaluation-template.md`

**Acceptance criteria:**
- Template includes all four Energy Matrix quadrants
- Maps task characteristics to energy profile
- Specifies threshold checking (≥60% mutual, ≤20% burnout)
- Includes example of annotated flag

**Estimated effort:** 30 minutes

---

#### Task 1.2: Create Company Batch Script
**What:** Write a Python script to divide 39 companies into N batches for parallel processing.

**Details:**
```python
# scripts/batch_companies.py
from pathlib import Path
import json
import math

def get_companies_with_flags(data_dir: Path) -> list[dict]:
    """Find all companies with flags files."""
    companies = []
    for stage_dir in sorted(data_dir.glob("stage-*")):
        for company_dir in sorted(stage_dir.iterdir()):
            flags_path = company_dir / "company.flags.yaml"
            if flags_path.exists():
                companies.append({
                    "name": company_dir.name,
                    "stage": stage_dir.name,
                    "path": str(company_dir),
                    "flags_path": str(flags_path),
                })
    return companies

def create_batches(companies: list[dict], num_batches: int) -> list[list[dict]]:
    """Divide companies into roughly equal batches."""
    batch_size = math.ceil(len(companies) / num_batches)
    return [companies[i:i+batch_size] for i in range(0, len(companies), batch_size)]

if __name__ == "__main__":
    import sys
    num_batches = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    data_dir = Path("data")
    companies = get_companies_with_flags(data_dir)
    batches = create_batches(companies, num_batches)

    print(f"Found {len(companies)} companies")
    print(f"Creating {len(batches)} batches")

    for i, batch in enumerate(batches):
        output_file = Path(f"batches/batch-{i+1}.json")
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(json.dumps(batch, indent=2))
        print(f"Batch {i+1}: {len(batch)} companies -> {output_file}")
```

**Location:** `active/projects/wctf/scripts/batch_companies.py`

**Acceptance criteria:**
- Finds all 39 companies with flags
- Creates N batches with roughly equal distribution
- Outputs batch JSON files to `batches/` directory
- Each batch file contains company metadata (name, stage, paths)

**Estimated effort:** 20 minutes

---

#### Task 1.3: Create Reevaluation Agent Prompt
**What:** Write the agent prompt that processes a single batch of companies.

**Details:**
```markdown
# Batch Reevaluation Agent Instructions

You are a specialized agent for reevaluating WCTF company flags using the Energy Matrix framework.

## Your Task

Process the companies in your assigned batch file, reevaluating each company's flags to add Energy Matrix annotations.

## Input Files

You will receive:
1. `batch-N.json` - Your assigned batch of companies
2. `docs/reevaluation-template.md` - Reevaluation instructions
3. `data/profile.yaml` - Energy profile for evaluation

## For Each Company

1. **Load context:**
   - Read `{company_path}/company.flags.yaml`
   - Read `{company_path}/company.facts.yaml`
   - Read `data/profile.yaml`

2. **Reevaluate flags:**
   - Follow reevaluation template instructions
   - Add task characteristics to each flag (conflict_exposure, progress_visibility, etc.)
   - Map flags to Energy Matrix quadrants (mutual/sparingly/burnout/help_mentoring)
   - Calculate daily energy distribution percentages

3. **Update synthesis:**
   - Add `energy_matrix` section to synthesis:
     ```yaml
     energy_matrix:
       mutual_percentage: 65
       sparingly_percentage: 20
       burnout_percentage: 10
       help_mentoring_percentage: 5
       meets_thresholds: true  # ≥60% mutual AND ≤20% burnout
       energy_sustainability: "HIGH"  # HIGH/MEDIUM/LOW
     ```

4. **Save updated flags:**
   - Write to `{company_path}/company.flags.yaml`
   - Preserve all existing flag content
   - Add Energy Matrix annotations

5. **Log progress:**
   - Create `batches/batch-N-progress.log`
   - Log each company completion
   - Note any errors or skipped companies

## Output

When complete, write a summary to `batches/batch-N-summary.json`:
```json
{
  "batch_number": 1,
  "total_companies": 10,
  "completed": 9,
  "errors": 1,
  "error_details": [
    {"company": "example-co", "error": "Missing facts file"}
  ],
  "energy_distribution_stats": {
    "avg_mutual_pct": 62,
    "avg_burnout_pct": 15,
    "companies_meeting_thresholds": 8
  }
}
```

## Critical Requirements

- **DO NOT** change existing flag content, only add Energy Matrix annotations
- **DO** preserve YAML formatting and structure
- **DO** validate threshold compliance (≥60% mutual, ≤20% burnout)
- **DO** provide detailed task characteristics for each flag

## Tools Available

You have access to:
- `Read` - Read company flags, facts, profile
- `Edit` - Update company flags YAML files
- `Write` - Write progress logs and summaries
- `Bash` - Run validation scripts if needed
```

**Location:** `active/projects/wctf/docs/batch-reevaluation-agent.md`

**Acceptance criteria:**
- Clear instructions for batch processing
- Specifies input/output files
- Defines Energy Matrix annotation format
- Includes progress logging requirements
- Provides summary JSON format

**Estimated effort:** 30 minutes

---

#### Task 1.4: Create Validation Script
**What:** Write a script to validate reevaluated flags meet Energy Matrix requirements.

**Details:**
```python
# scripts/validate_reevaluation.py
import yaml
from pathlib import Path

def validate_energy_matrix(flags_data: dict) -> list[str]:
    """Validate Energy Matrix annotations in flags."""
    errors = []

    # Check for energy_matrix in synthesis
    synthesis = flags_data.get("synthesis", {})
    em = synthesis.get("energy_matrix", {})

    if not em:
        errors.append("Missing energy_matrix section in synthesis")
        return errors

    # Validate required fields
    required = ["mutual_percentage", "sparingly_percentage",
                "burnout_percentage", "help_mentoring_percentage",
                "meets_thresholds", "energy_sustainability"]
    for field in required:
        if field not in em:
            errors.append(f"Missing {field} in energy_matrix")

    # Validate percentages sum to ~100
    total = (em.get("mutual_percentage", 0) +
             em.get("sparingly_percentage", 0) +
             em.get("burnout_percentage", 0) +
             em.get("help_mentoring_percentage", 0))
    if abs(total - 100) > 5:
        errors.append(f"Percentages sum to {total}, should be ~100")

    # Validate thresholds
    mutual = em.get("mutual_percentage", 0)
    burnout = em.get("burnout_percentage", 0)

    if mutual < 60:
        errors.append(f"Mutual percentage {mutual}% below 60% threshold")
    if burnout > 20:
        errors.append(f"Burnout percentage {burnout}% above 20% threshold")

    return errors

def validate_company(company_path: Path) -> dict:
    """Validate a single company's reevaluation."""
    flags_path = company_path / "company.flags.yaml"

    if not flags_path.exists():
        return {"status": "error", "message": "Flags file not found"}

    try:
        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        errors = validate_energy_matrix(flags_data)

        if errors:
            return {"status": "invalid", "errors": errors}
        else:
            return {"status": "valid"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    data_dir = Path("data")
    results = {}

    for stage_dir in sorted(data_dir.glob("stage-*")):
        for company_dir in sorted(stage_dir.iterdir()):
            result = validate_company(company_dir)
            results[company_dir.name] = result

    # Print summary
    valid = sum(1 for r in results.values() if r["status"] == "valid")
    invalid = sum(1 for r in results.values() if r["status"] == "invalid")
    errors = sum(1 for r in results.values() if r["status"] == "error")

    print(f"\nValidation Summary:")
    print(f"  Valid: {valid}")
    print(f"  Invalid: {invalid}")
    print(f"  Errors: {errors}")

    if invalid > 0 or errors > 0:
        print("\nDetails:")
        for company, result in results.items():
            if result["status"] != "valid":
                print(f"\n{company}: {result['status']}")
                if "errors" in result:
                    for error in result["errors"]:
                        print(f"  - {error}")
                if "message" in result:
                    print(f"  - {result['message']}")
```

**Location:** `active/projects/wctf/scripts/validate_reevaluation.py`

**Acceptance criteria:**
- Validates energy_matrix section exists
- Checks all required fields present
- Validates percentages sum to ~100
- Validates thresholds (≥60% mutual, ≤20% burnout)
- Provides detailed error messages
- Outputs validation summary

**Estimated effort:** 30 minutes

---

### Phase 2: Parallel Batch Processing

**Objective:** Use multiple subagents to reevaluate companies in parallel batches.

#### Task 2.1: Generate Company Batches
**What:** Run the batch script to divide companies into batches.

**Command:**
```bash
cd active/projects/wctf
python scripts/batch_companies.py 4  # Create 4 batches for parallel processing
```

**Acceptance criteria:**
- `batches/` directory created
- 4 batch JSON files created (batch-1.json through batch-4.json)
- Each batch has ~10 companies
- All 39 companies distributed across batches

**Estimated effort:** 2 minutes

---

#### Task 2.2: Launch Parallel Reevaluation Agents
**What:** Launch 4 parallel Task agents, each processing one batch.

**Implementation:**

Send a SINGLE message with FOUR Task tool calls:

```xml
<Task>
  <subagent_type>general-purpose</subagent_type>
  <description>Reevaluate batch 1 companies</description>
  <prompt>
You are reevaluating WCTF company flags for batch 1 using Energy Matrix criteria.

**Your inputs:**
- Batch file: active/projects/wctf/batches/batch-1.json
- Reevaluation template: active/projects/wctf/docs/reevaluation-template.md
- Agent instructions: active/projects/wctf/docs/batch-reevaluation-agent.md
- Energy profile: active/projects/wctf/data/profile.yaml

**Your task:**
Follow the batch-reevaluation-agent.md instructions exactly to:
1. Load batch-1.json to get your assigned companies
2. For each company, reevaluate flags using reevaluation-template.md
3. Add Energy Matrix annotations (task characteristics + quadrant mapping)
4. Update synthesis with energy_matrix section
5. Save updated flags to company.flags.yaml
6. Log progress to batches/batch-1-progress.log
7. Write summary to batches/batch-1-summary.json

**Critical:** DO NOT change existing flag content, only ADD Energy Matrix annotations.

When complete, report:
- Number of companies completed
- Any errors encountered
- Energy distribution statistics from your batch
  </prompt>
</Task>

<Task>
  <subagent_type>general-purpose</subagent_type>
  <description>Reevaluate batch 2 companies</description>
  <prompt>[Same as above but for batch-2.json]</prompt>
</Task>

<Task>
  <subagent_type>general-purpose</subagent_type>
  <description>Reevaluate batch 3 companies</description>
  <prompt>[Same as above but for batch-3.json]</prompt>
</Task>

<Task>
  <subagent_type>general-purpose</subagent_type>
  <description>Reevaluate batch 4 companies</description>
  <prompt>[Same as above but for batch-4.json]</prompt>
</Task>
```

**Acceptance criteria:**
- All 4 agents launched in parallel
- Each agent receives correct batch file
- Each agent has access to reevaluation template and instructions
- Agents work independently without conflicts

**Estimated effort:** 5 minutes setup, ~15-20 minutes agent execution

---

#### Task 2.3: Monitor Agent Progress
**What:** Periodically check agent progress and intervene if needed.

**Monitoring approach:**
```bash
# Watch progress logs
watch -n 5 'for f in batches/batch-*-progress.log; do echo "=== $f ==="; tail -3 $f; done'

# Check for completion
ls batches/batch-*-summary.json | wc -l  # Should reach 4 when all done
```

**Acceptance criteria:**
- Can view progress of all 4 agents
- Can identify stuck or failed agents
- Can intervene if agent needs guidance

**Estimated effort:** Ongoing during Task 2.2

---

#### Task 2.4: Collect Agent Results
**What:** Once all agents complete, collect and review their summaries.

**Command:**
```bash
cd active/projects/wctf
python -c "
import json
from pathlib import Path

for i in range(1, 5):
    summary_file = Path(f'batches/batch-{i}-summary.json')
    if summary_file.exists():
        summary = json.loads(summary_file.read_text())
        print(f\"Batch {i}: {summary['completed']}/{summary['total_companies']} completed\")
        if summary['errors'] > 0:
            print(f\"  Errors: {summary['errors']}\")
            for error in summary['error_details']:
                print(f\"    - {error['company']}: {error['error']}\")
    else:
        print(f\"Batch {i}: No summary file (still running or failed)\")
"
```

**Acceptance criteria:**
- All 4 batch summaries collected
- Total companies processed = 39
- Error count and details captured
- Energy distribution statistics aggregated

**Estimated effort:** 5 minutes

---

### Phase 3: Validation & Cleanup

**Objective:** Validate all reevaluations and handle any failures.

#### Task 3.1: Run Validation Script
**What:** Validate all 39 companies' flags have correct Energy Matrix annotations.

**Command:**
```bash
cd active/projects/wctf
python scripts/validate_reevaluation.py
```

**Expected output:**
```
Validation Summary:
  Valid: 39
  Invalid: 0
  Errors: 0
```

**If validation fails:**
- Review error details
- Manually fix invalid companies
- Re-run validation

**Acceptance criteria:**
- All 39 companies validated successfully
- No missing energy_matrix sections
- All thresholds calculated correctly
- No YAML formatting errors

**Estimated effort:** 5 minutes + fixing time if errors

---

#### Task 3.2: Generate Aggregate Statistics
**What:** Create summary report of reevaluation results across all companies.

**Script:**
```python
# scripts/aggregate_stats.py
import yaml
from pathlib import Path
import statistics

def get_energy_stats(flags_path: Path) -> dict:
    """Extract energy matrix stats from flags file."""
    with open(flags_path) as f:
        flags = yaml.safe_load(f)
    return flags.get("synthesis", {}).get("energy_matrix", {})

if __name__ == "__main__":
    data_dir = Path("data")
    all_stats = []

    for stage_dir in sorted(data_dir.glob("stage-*")):
        for company_dir in sorted(stage_dir.iterdir()):
            flags_path = company_dir / "company.flags.yaml"
            if flags_path.exists():
                stats = get_energy_stats(flags_path)
                if stats:
                    all_stats.append({
                        "company": company_dir.name,
                        "stage": stage_dir.name,
                        **stats
                    })

    # Calculate aggregates
    mutual_pcts = [s["mutual_percentage"] for s in all_stats]
    burnout_pcts = [s["burnout_percentage"] for s in all_stats]
    meets_threshold = sum(1 for s in all_stats if s["meets_thresholds"])

    print(f"\nEnergy Matrix Statistics (n={len(all_stats)}):")
    print(f"\nMutual Percentage:")
    print(f"  Mean: {statistics.mean(mutual_pcts):.1f}%")
    print(f"  Median: {statistics.median(mutual_pcts):.1f}%")
    print(f"  Range: {min(mutual_pcts):.1f}% - {max(mutual_pcts):.1f}%")

    print(f"\nBurnout Percentage:")
    print(f"  Mean: {statistics.mean(burnout_pcts):.1f}%")
    print(f"  Median: {statistics.median(burnout_pcts):.1f}%")
    print(f"  Range: {min(burnout_pcts):.1f}% - {max(burnout_pcts):.1f}%")

    print(f"\nThreshold Compliance:")
    print(f"  Meeting thresholds: {meets_threshold}/{len(all_stats)} ({meets_threshold/len(all_stats)*100:.1f}%)")

    # Companies below threshold
    below = [s for s in all_stats if not s["meets_thresholds"]]
    if below:
        print(f"\nCompanies below threshold:")
        for s in below:
            print(f"  - {s['company']}: {s['mutual_percentage']}% mutual, {s['burnout_percentage']}% burnout")
```

**Location:** `active/projects/wctf/scripts/aggregate_stats.py`

**Acceptance criteria:**
- Reports mean/median/range for mutual and burnout percentages
- Shows how many companies meet thresholds
- Lists companies that don't meet thresholds
- Identifies patterns in energy distribution

**Estimated effort:** 20 minutes

---

#### Task 3.3: Review High-Risk Companies
**What:** Review companies with <60% mutual or >20% burnout to understand concerns.

**Command:**
```bash
cd active/projects/wctf
python -c "
import yaml
from pathlib import Path

data_dir = Path('data')
high_risk = []

for stage_dir in sorted(data_dir.glob('stage-*')):
    for company_dir in sorted(stage_dir.iterdir()):
        flags_path = company_dir / 'company.flags.yaml'
        if flags_path.exists():
            with open(flags_path) as f:
                flags = yaml.safe_load(f)
            em = flags.get('synthesis', {}).get('energy_matrix', {})
            if not em.get('meets_thresholds', True):
                high_risk.append({
                    'company': company_dir.name,
                    'mutual': em.get('mutual_percentage', 0),
                    'burnout': em.get('burnout_percentage', 0),
                    'sustainability': em.get('energy_sustainability', 'UNKNOWN')
                })

print(f'High-Risk Companies: {len(high_risk)}')
for hr in sorted(high_risk, key=lambda x: x['mutual']):
    print(f\"  {hr['company']}: {hr['mutual']}% mutual, {hr['burnout']}% burnout -> {hr['sustainability']}\")
"
```

**Acceptance criteria:**
- Identifies all companies below energy thresholds
- Highlights specific energy concerns (low mutual, high burnout)
- Provides context for decision-making

**Estimated effort:** 10 minutes

---

#### Task 3.4: Clean Up Temporary Files
**What:** Remove batch processing temporary files.

**Command:**
```bash
cd active/projects/wctf
rm -rf batches/
```

**Acceptance criteria:**
- `batches/` directory removed
- All company flags updated and validated
- No temporary files remain

**Estimated effort:** 1 minute

---

#### Task 3.5: Commit Updated Flags
**What:** Commit all reevaluated flags to git.

**Command:**
```bash
cd active/projects/wctf
git add data/*/company.flags.yaml
git commit -m "feat(wctf): reevaluate all flags with Energy Matrix v4.0

Reevaluated all 39 companies using Energy Matrix framework:
- Added task characteristics to each flag
- Mapped flags to quadrants (mutual/sparingly/burnout/help_mentoring)
- Calculated energy distribution percentages
- Added synthesis energy_matrix section with threshold compliance

Results:
- Companies meeting thresholds (≥60% mutual, ≤20% burnout): [X/39]
- Average mutual percentage: [X]%
- Average burnout percentage: [X]%

Processed in parallel using 4 subagent batches for efficiency.

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

**Acceptance criteria:**
- All updated flags committed
- Commit message includes statistics
- Reevaluation approach documented in commit message

**Estimated effort:** 5 minutes

---

## Summary

**Total Estimated Time:**
- Phase 1 (Infrastructure): ~2 hours
- Phase 2 (Parallel Processing): ~30 minutes
- Phase 3 (Validation): ~45 minutes
- **Total: ~3.25 hours**

**Parallelization Benefit:**
- Sequential processing: ~15 minutes/company × 39 = ~9.75 hours
- Parallel processing (4 batches): ~15 minutes/company × 10 = ~2.5 hours
- **Time saved: ~7.25 hours (74% reduction)**

**Key Success Factors:**
1. Clear reevaluation template ensures consistency
2. Batch processing enables parallelization
3. Validation script catches errors early
4. Progress logging enables monitoring
5. Summary statistics provide oversight

**Risk Mitigation:**
- Validation script catches formatting errors
- Progress logs enable early intervention
- Batch summaries track completion
- Single-file updates prevent merge conflicts
- Git commit enables easy rollback if needed

## Next Steps After Completion

1. Update WCTF framework documentation to v4.0
2. Update MCP tools to use Energy Matrix fields
3. Enhance dashboard to visualize energy distributions
4. Create "energy-first" filtering tools
5. Document learnings from reevaluation process
