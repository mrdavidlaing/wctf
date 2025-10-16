# Future WCTF Prompt Templates

This directory contains prompt templates that are **not currently implemented** in the MCP server but may be useful for future features.

## Currently Active Prompts

The MCP server uses prompts from `wctf_mcp/prompts/`:
- `layer1_research.md` - Main research prompt (used by research tools)
- `mountain_flags.md` - Flag extraction from conversations (used by flag tools)
- `insider_interview_extraction.md` - Extract facts from insider interviews (used by insider tools)

## Future Implementation Candidates

### Synthesis & Analysis
- **synthesis-prompt.md** - Analyze collected facts to identify information gaps, contradictions, and patterns
  - Potential tool: `synthesize_research_tool(company_name)` that reads existing facts and provides pattern analysis
  - Use case: After initial research, identify what needs deeper investigation

### Specialized Research by Company Stage
- **startup-viability-prompt.md** - Focus on founder backgrounds, investor quality, runway (Seed to Series B)
- **public-company-prompt.md** - Focus on earnings, stock performance, SEC filings, analyst ratings
- **company-in-flux-prompt.md** - Focus on layoffs, leadership changes, pivots, restructuring
  - Potential enhancement: Add `company_stage` parameter to `get_research_prompt_tool()` to return specialized prompts
  - Use case: Tailor research questions based on company maturity

### Focused Follow-up Research
- **financial-health-check.md** - Quick financial viability scan
- **market-position-deep-dive.md** - Deep competitive and product analysis
- **leadership-culture-assessment.md** - Leadership stability and culture focus
  - Potential tools: Category-specific research tools for targeted follow-up investigations
  - Use case: When you need to dig deeper into one specific aspect

## Usage Notes

These prompts were part of the initial design but simplified for the v1 implementation. They represent:
1. Real use cases from company research workflows
2. Natural next features for the MCP server
3. Patterns that emerged during prototype testing

When implementing these, consider:
- Following the existing prompt pattern (markdown with placeholders like `{company_name}`)
- Storing prompts in `wctf_mcp/prompts/` when ready to implement
- Adding corresponding tool functions in `wctf_mcp/tools/`
- Using the two-step pattern: tool returns prompt, agent executes, tool saves results

## Obsolete Prompts (Deleted)

The following prompts were removed as they're superseded by current implementations:
- `master-research-prompt.md` - Replaced by `wctf_mcp/prompts/layer1_research.md`
- `mountain-expedition-flag-extraction.md` - Too personalized; replaced by generic `mountain_flags.md`
- `flag-extraction-*.md` - Component pieces merged into current flag tools
