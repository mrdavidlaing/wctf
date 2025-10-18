# Generate Insider Interview Guide

Generate a conversation flowchart interview guide for validating company facts and flags with an insider contact.

## Steps

0. **Understand the WCTF framework:**
   - Read `WCTF_FRAMEWORK.md` to understand the evaluation philosophy
   - This provides context on:
     - The mountain metaphor and five dimensions
     - Why these dimensions matter
     - The two-layer investigation approach
     - Flag-based evaluation philosophy (no mechanical scoring)
     - What tensions and trade-offs to surface

1. **Read the company data files:**
   - Read `data/{{arg}}/company.facts.yaml` to understand current research
   - Read `data/{{arg}}/company.flags.yaml` to identify validation needs

2. **Generate the interview guide:**
   - Run: `uv run python scripts/generate_interview_guide.py {{arg}}`
   - This creates: `data/{{arg}}/YYYYMMDD-insider-interview-guide.html`

3. **Review the output:**
   - Open the generated HTML file
   - Summarize what was created:
     - Number of critical questions extracted
     - Interview phases included
     - Estimated interview duration

4. **Remind the user:**
   - This guide can be printed via browser (Ctrl+P → Save as PDF)
   - It's designed for A4 paper, print-ready
   - The guide includes conversation starters with conditional branches
   - There's a critical data checklist at the top to ensure key questions are answered

## Example Usage

```
/interview-guide workday
```

This will create a printable interview guide at:
`data/workday/20251018-insider-interview-guide.html`
