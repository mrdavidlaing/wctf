# Generate Evaluation Overview

Generate a brief (3-4 page) evaluation overview to share with insider interview contacts, explaining the WCTF framework and what needs validation.

## Steps

0. **Understand the WCTF framework:**
   - Read `WCTF_FRAMEWORK.md` to understand the evaluation philosophy
   - This provides context on:
     - The mountain metaphor and five dimensions
     - Why these dimensions matter for career decisions
     - The two-layer investigation approach
     - What insider perspective adds beyond public research
     - How to explain the framework to interview contacts

1. **Read the company data files:**
   - Read `data/{{arg}}/company.facts.yaml` to understand current research
   - Read `data/{{arg}}/company.flags.yaml` to identify what needs validation

2. **Generate the overview:**
   - Run: `uv run python scripts/generate_evaluation_overview.py {{arg}}`
   - This creates: `data/{{arg}}/YYYYMMDD-evaluation-overview.html`

3. **Review the output:**
   - Open the generated HTML file
   - Summarize what was created:
     - WCTF framework explanation included
     - Facts organized by dimension and confidence level
     - Priority validation targets identified
     - Estimated page count

4. **Remind the user:**
   - This overview is designed to share with the insider contact
   - It provides context on the WCTF framework and evaluation approach
   - Shows what's already been researched (with confidence levels)
   - Highlights what needs insider validation
   - Can be printed via browser (Ctrl+P → Save as PDF)
   - Print-ready for A4 paper

## Example Usage

```
/evaluation-overview workday
```

This will create a printable overview at:
`data/workday/20251018-evaluation-overview.html`

## Use Case

Share this document with your insider contact before or at the start of the interview so they understand:
- Your evaluation framework
- What you've already researched
- Where you need their insider perspective
- Which facts have low/medium confidence and need validation
