# Generate Evaluation Rubric

Generate a comprehensive WCTF evaluation rubric with analytical synthesis of facts and flags across all 5 dimensions.

## Steps

0. **Understand the WCTF framework deeply:**
   - Read `WCTF_FRAMEWORK.md` to understand the evaluation philosophy
   - This is CRITICAL for synthesis - you need to understand:
     - The mountain metaphor and what each dimension truly evaluates
     - Why "no mechanical scoring" - you're surfacing tensions, not calculating scores
     - What trade-offs and paradoxes matter (e.g., "profitable but laying off")
     - How context changes flag interpretation
     - What makes analysis meaningful vs just listing facts
     - The evaluator values (autonomy, excellence, sustainability, impact, narrative)

1. **Read the company data files:**
   - Read `data/{{arg}}/company.facts.yaml` to get all research facts
   - Read `data/{{arg}}/company.flags.yaml` to get green/red flags and gaps

2. **Generate the rubric framework:**
   - Run: `uv run python scripts/generate_evaluation_rubric.py {{arg}}`
   - This creates: `data/{{arg}}/YYYYMMDD-evaluation-rubric.html`
   - The rubric includes:
     - WCTF framework explanation
     - Structured fact sections for each dimension
     - Placeholders for analysis paragraph synthesis
     - Green flags, red flags, and knowledge gaps
     - Complete references section with footnotes

3. **Synthesize analysis paragraphs (IMPORTANT):**
   - Open the generated HTML file
   - Find sections marked with `[AI Synthesis Placeholder]`
   - For each dimension, synthesize the listed facts into 2-3 analytical paragraphs that:
     - Create narrative flow from the facts
     - Use superscript footnotes (e.g., ¹, ²) referencing the fact numbers
     - Highlight tensions and paradoxes in the data
     - Use hedging language based on confidence ("appears," "suggests," "unclear")
     - Maintain analytical tone without prescribing recommendations
   - Replace the placeholder text with your synthesized paragraphs
   - Keep the fact list boxes for reference

4. **Review the output:**
   - Verify all 5 dimensions have analysis paragraphs
   - Check that footnotes reference the correct facts
   - Confirm green/red flags are properly listed
   - Ensure knowledge gaps are documented
   - Verify references section is complete

5. **Remind the user:**
   - The rubric is ~6-7 pages when printed
   - It presents research objectively without recommendations
   - Can be printed via browser (Ctrl+P → Save as PDF)
   - Print-ready for A4 paper

## Example Usage

```
/evaluation-rubric workday
```

This will create a rubric framework at:
`data/workday/20251018-evaluation-rubric.html`

Then ask me to "synthesize the analysis paragraphs in the rubric" to complete it.

## Use Case

This comprehensive rubric:
- Documents all research findings objectively
- Synthesizes facts into analytical narratives
- Identifies tensions and knowledge gaps
- Serves as reference material for decision-making
- Avoids prescribing "yes/no" recommendations
- Enables informed personal decision-making based on individual priorities
