# WCTF Scripts

Tools for managing company research data and generating insider interview materials.

## Insider Interview Workflow

Scripts for generating interview guides, evaluation overviews, and analytical rubrics.

**Framework Context:** All workflow tools reference `WCTF_FRAMEWORK.md` which explains the evaluation philosophy, mountain metaphor, and flag-based approach. This context helps Claude Code generate better content and helps readers understand the analytical lens.

### generate_interview_guide.py

Generate a conversation flowchart interview guide for validating facts and flags with insider contacts.

**Usage:**
```bash
# Via slash command (recommended)
/interview-guide <company-slug>

# Direct invocation
uv run python scripts/generate_interview_guide.py <company-slug>

# Example
uv run python scripts/generate_interview_guide.py workday
```

**What it creates:**
- Timestamped HTML file: `data/{company-slug}/YYYYMMDD-insider-interview-guide.html`
- Conversation flowchart with starter questions and conditional branches
- Critical data checklist from `missing_critical_data`
- Interview phases organized by WCTF dimensions
- Print-ready for A4 paper

**Use when:**
- Preparing for an insider interview
- Need structured questions to validate facts and flags
- Want a conversation guide with follow-up branches

---

### generate_evaluation_overview.py

Generate a brief (3-4 page) evaluation overview to share with insider interview contacts.

**Usage:**
```bash
# Via slash command (recommended)
/evaluation-overview <company-slug>

# Direct invocation
uv run python scripts/generate_evaluation_overview.py <company-slug>

# Example
uv run python scripts/generate_evaluation_overview.py workday
```

**What it creates:**
- Timestamped HTML file: `data/{company-slug}/YYYYMMDD-evaluation-overview.html`
- WCTF framework explanation
- Facts organized by dimension and confidence level
- Green flags, red flags, and knowledge gaps per dimension
- Prioritized validation targets
- Print-ready for A4 paper

**Use when:**
- Sharing context with insider contacts before/during interview
- Explaining your evaluation approach
- Showing what you've researched and what needs validation

---

### generate_evaluation_rubric.py

Generate a comprehensive WCTF evaluation rubric with analytical synthesis.

**Usage:**
```bash
# Via slash command (recommended)
/evaluation-rubric <company-slug>

# Direct invocation
uv run python scripts/generate_evaluation_rubric.py <company-slug>

# Example
uv run python scripts/generate_evaluation_rubric.py workday
```

**What it creates:**
- Timestamped HTML file: `data/{company-slug}/YYYYMMDD-evaluation-rubric.html`
- Complete analytical rubric (~6-7 pages) with:
  - Structured fact sections for each WCTF dimension
  - Placeholders for AI-synthesized analysis paragraphs
  - Green flags, red flags, and knowledge gaps
  - Comprehensive references section with footnotes
- Print-ready for A4 paper

**Post-generation step:**
After generating, ask Claude Code to "synthesize the analysis paragraphs" to replace placeholders with narrative synthesis.

**Use when:**
- Creating comprehensive evaluation documentation
- Need analytical synthesis of all research findings
- Want objective presentation without prescriptive recommendations

---

## Insider Interview Slash Commands

Located in `.claude/commands/`, these provide guided workflows:

- `/interview-guide <company-slug>` - Generate interview guide
- `/evaluation-overview <company-slug>` - Generate evaluation overview
- `/evaluation-rubric <company-slug>` - Generate evaluation rubric

The slash commands:
1. Read company facts and flags
2. Invoke the appropriate Python script
3. Open the generated HTML file
4. Summarize what was created
5. Remind about printing options

**Example workflow:**
```bash
# Pre-interview: Generate materials
/interview-guide workday
/evaluation-overview workday

# Post-interview: Generate rubric
/evaluation-rubric workday
# Then ask: "Synthesize the analysis paragraphs in the rubric"
```

---

## Maintenance Scripts

Operational tools for managing and maintaining WCTF company research data.

### Scripts

### check_duplicates.py

Find duplicate and similar facts across all companies.

**Usage:**
```bash
# Check with default 85% similarity threshold
uv run python scripts/check_duplicates.py

# Check with stricter threshold (90% recommended for auto-merge)
uv run python scripts/check_duplicates.py --threshold 90

# Check with looser threshold (more results, more false positives)
uv run python scripts/check_duplicates.py --threshold 80
```

**What it does:**
- Scans all companies for exact duplicate facts (same text, source, date)
- Uses fuzzy string matching to find semantically similar facts
- Reports similarity scores and which companies have issues

**Threshold guidance:**
- **90%+**: Clear duplicates, safe for auto-merge
- **85-89%**: Likely duplicates, review recommended
- **<85%**: Many false positives, manual review required

---

### show_duplicates.py

Display full details of duplicate facts for manual review.

**Usage:**
```bash
# Show duplicates for all companies
uv run python scripts/show_duplicates.py --threshold 90

# Show duplicates for specific company
uv run python scripts/show_duplicates.py Chronosphere --threshold 90
```

**What it does:**
- Shows complete fact details (text, source, date, confidence)
- Displays array indices for locating facts in YAML files
- Provides instructions for manual merging

**Use when:**
- You want to see full context before merging
- You need to manually edit YAML files
- You're investigating borderline duplicates

---

### merge_duplicates.py

Automatically merge duplicate facts, keeping the more complete version.

**Usage:**
```bash
# Dry run (preview changes without modifying files)
uv run python scripts/merge_duplicates.py --threshold 90 --dry-run

# Apply changes (modify YAML files)
uv run python scripts/merge_duplicates.py --threshold 90
```

**What it does:**
- Finds facts with similarity >= threshold
- Intelligently chooses which fact to keep (longer text, more sources)
- Skips facts with different numbers/dates (e.g., "Revenue 2023" vs "Revenue 2024")
- Updates fact counts in summary section
- Saves modified YAML files

**Selection criteria (in order):**
1. Longer fact text (more detail)
2. More sources (semicolon-separated count)
3. If equal, keeps first occurrence

**Safety features:**
- Detects different years/values and skips them
- Dry-run mode for previewing changes
- Updates summary counts automatically

**Recommended workflow:**
1. Run with `--dry-run` to preview
2. Review the changes
3. Run without `--dry-run` to apply
4. Verify with `check_duplicates.py`

---

### get_flags_prompt.py

Display company facts and get the flags extraction prompt.

**Usage:**
```bash
# Get extraction prompt for a specific company
uv run python scripts/get_flags_prompt.py "Company Name"

# Example
uv run python scripts/get_flags_prompt.py "Stripe"
```

**What it does:**
- Displays company facts in structured, readable format
- Shows the flags extraction prompt for evaluation
- Organized by category (Financial Health, Market Position, Org Stability, Technical Culture)
- Each fact shows: text, source, date, confidence level
- Lists missing information per category

**Output format:**
- Company name and research date
- Summary (total facts, completeness)
- Facts grouped by category with sources
- Complete extraction prompt with instructions

**Use when:**
- You want to review a company's facts before evaluation
- You need the extraction prompt to guide your analysis
- Working with Claude Code to extract flags

---

### save_flags.py

Save extracted flags YAML for a company.

**Usage:**
```bash
# From heredoc (recommended for Claude Code)
uv run python scripts/save_flags.py "Company Name" << 'EOF'
company: "Company Name"
evaluation_date: "2025-10-18"
evaluator_context: "..."
...
EOF

# From file
uv run python scripts/save_flags.py "Company Name" < flags.yaml
```

**What it does:**
- Reads flags YAML from stdin
- Validates the YAML structure
- Saves to `data/{company-slug}/company.flags.yaml`
- Reports success with file path

**Use when:**
- You've extracted flags and need to save them
- Working with Claude Code to save evaluation results
- Want to validate YAML before saving

---

## Common Workflows

### Extracting Flags for Companies (with Claude Code)

```bash
# 1. Get the extraction prompt for a company
uv run python scripts/get_flags_prompt.py "Stripe"

# 2. Claude Code reads the facts and extraction prompt
#    and extracts the flags YAML

# 3. Save the extracted flags
uv run python scripts/save_flags.py "Stripe" << 'EOF'
company: "Stripe"
evaluation_date: "2025-10-18"
evaluator_context: "Senior engineer with 15+ years..."
# ... rest of flags YAML ...
EOF

# 4. Repeat for next company
```

**Workflow:**
- Claude Code orchestrates the process for all companies
- Calls `get_flags_prompt.py` to see facts and get the extraction prompt
- Extracts flags based on the facts
- Calls `save_flags.py` with the extracted YAML
- Moves to the next company

**List companies needing flags:**
```bash
uv run python -c "from wctf_core import WCTFClient; client = WCTFClient(); companies = [c['name'] for c in client.list_companies() if c['has_facts'] and not c['has_flags']]; print('\n'.join(sorted(companies)))"
```

### Finding and Fixing Duplicates

```bash
# 1. Check for duplicates at 90% threshold
uv run python scripts/check_duplicates.py --threshold 90

# 2. Preview what would be merged
uv run python scripts/merge_duplicates.py --threshold 90 --dry-run

# 3. If changes look good, apply them
uv run python scripts/merge_duplicates.py --threshold 90

# 4. Verify they're gone
uv run python scripts/check_duplicates.py --threshold 90
```

### Investigating Borderline Cases

```bash
# 1. Find potential duplicates at lower threshold
uv run python scripts/check_duplicates.py --threshold 85

# 2. Get full details for a specific company
uv run python scripts/show_duplicates.py Chronosphere --threshold 85

# 3. Manually edit data/Chronosphere/company.facts.yaml if needed
```

### Regular Maintenance

```bash
# Quick check for any duplicates
uv run python scripts/check_duplicates.py --threshold 90

# If any found, merge them
uv run python scripts/merge_duplicates.py --threshold 90
```

---

## Notes

- These scripts use the WCTF Core SDK (`wctf_core`) for all data access
- They use `rapidfuzz` for fuzzy string matching
- All scripts operate on `./data` by default (current working directory)
- Threshold of 90% is recommended for automated merging
- Always review dry-run output before applying changes

## See Also

- `examples/` - SDK usage examples for learning and reference
- `docs/SDK_REFERENCE.md` - Complete SDK API documentation
