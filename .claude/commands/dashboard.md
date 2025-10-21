# Generate Pipeline Dashboard

Generate an HTML dashboard showing job search pipeline progress across all stages.

## What It Does

The dashboard provides a visual overview of your job search funnel:
- **Pipeline Progress Cards**: Shows count and progress bars for each stage (Stage 1: 37/100, Stage 2: 4/25, Stage 3: 0/5)
- **Per-Stage Tables**: Lists companies in each stage with sortable columns
- **Company Metrics**: Facts count, green/red flags, insider interviews, evaluation date, worth climbing status

## Steps

1. **Generate the dashboard:**
   - Run: `uv run python scripts/generate_dashboard.py`
   - This creates/updates: `data/dashboard.html`

2. **Open the dashboard:**
   - Open `data/dashboard.html` in your browser
   - Or use: `file:///home/mrdavidlaing/arch-workspace/wctf/data/dashboard.html`

3. **Summarize what was generated:**
   - Report the current pipeline status (how many companies in each stage)
   - Note any key observations (e.g., "38% of target for Stage 1")

## Features

- **Sortable Columns**: Click any column header to sort (company name, date, counts, etc.)
- **Color-Coded Badges**: YES (green), MAYBE (yellow), NO (red) for mountain_worth_climbing
- **Responsive Design**: Clean, professional styling with hover effects
- **Auto-Generated**: Timestamp shows when dashboard was last updated

## Example Usage

```
/dashboard
```

This will regenerate `data/dashboard.html` with current data.

## Pipeline Stages

- **Stage 1**: Researched & Evaluated (has both facts.yaml and flags.yaml)
- **Stage 2**: Insider Interviews (has insider.yaml)
- **Stage 3**: Applications (future - applications submitted)

## Related Operations

To promote a company to the next stage, use the SDK:
```python
from wctf_core import WCTFClient
client = WCTFClient()
client.promote_stage("CompanyName", 2)  # Promote to stage 2
```
