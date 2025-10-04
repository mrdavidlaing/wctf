"""MCP server for WCTF company research data.

This module contains the MCP server implementation with tools for
managing and querying company research data.
"""

import logging

from mcp.server.fastmcp import FastMCP, Context

from wctf_mcp.tools.company import (
    get_company_facts,
    get_company_flags,
    list_companies,
)
from wctf_mcp.tools.research import (
    get_research_prompt,
    save_research_results,
)
from wctf_mcp.tools.flags import (
    extract_flags,
    add_manual_flag,
)
from wctf_mcp.tools.conversation import (
    get_conversation_questions,
)
from wctf_mcp.tools.decision import (
    gut_check,
    save_gut_decision,
    get_evaluation_summary,
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the FastMCP server instance
mcp = FastMCP("wctf-mcp")


@mcp.tool()
async def list_companies_tool(ctx: Context) -> dict:
    """List all companies with research data.

    Returns company names, count, and metadata about available files.
    """
    await ctx.info("Listing all companies in the database")
    logger.info("list_companies_tool called")
    result = list_companies()
    logger.info(f"Found {result.get('count', 0)} companies")
    await ctx.info(f"Found {result.get('count', 0)} companies")
    return result


@mcp.tool()
async def get_company_facts_tool(company_name: str, ctx: Context) -> dict:
    """Get research facts for a specific company.

    Returns detailed factual information from company.facts.yaml including
    financial health, market position, organizational stability, and technical culture.

    Args:
        company_name: Name of the company (e.g., '1Password', 'anthropic')
    """
    await ctx.info(f"Retrieving facts for company: {company_name}")
    logger.info(f"get_company_facts_tool called for: {company_name}")
    result = get_company_facts(company_name=company_name)
    if result.get("success"):
        logger.info(f"Successfully retrieved facts for {company_name}")
        await ctx.info(f"Successfully retrieved facts for {company_name}")
    else:
        logger.warning(f"Failed to retrieve facts for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")
    return result


@mcp.tool()
async def get_company_flags_tool(company_name: str, ctx: Context) -> dict:
    """Get evaluation flags for a specific company.

    Returns evaluation data from company.flags.yaml including
    green flags, red flags, missing critical data, and synthesis.

    Args:
        company_name: Name of the company (e.g., '1Password', 'anthropic')
    """
    await ctx.info(f"Retrieving evaluation flags for company: {company_name}")
    logger.info(f"get_company_flags_tool called for: {company_name}")
    result = get_company_flags(company_name=company_name)
    if result.get("success"):
        logger.info(f"Successfully retrieved flags for {company_name}")
        await ctx.info(f"Successfully retrieved flags for {company_name}")
    else:
        logger.warning(f"Failed to retrieve flags for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")
    return result


@mcp.tool()
async def get_research_prompt_tool(company_name: str, ctx: Context) -> dict:
    """Get the Layer 1 research prompt for a company.

    Returns a structured research prompt that you (the calling agent) should execute
    using your web search capabilities. After completing the research, use
    save_research_results to save the YAML output.

    Research covers: financial health, market position, organizational stability,
    and technical culture.

    Args:
        company_name: Name of the company to research (e.g., 'Stripe', 'Vercel', 'Railway')
    """
    await ctx.info(f"Generating research prompt for company: {company_name}")
    logger.info(f"get_research_prompt_tool called for: {company_name}")
    result = get_research_prompt(company_name=company_name)
    if result.get("success"):
        logger.info(f"Successfully generated research prompt for {company_name}")
        await ctx.info(f"Research prompt generated for {company_name}")
    else:
        logger.warning(f"Failed to generate prompt for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")
    return result


@mcp.tool()
async def save_research_results_tool(company_name: str, yaml_content: str, ctx: Context) -> dict:
    """Save company research results to company.facts.yaml file.

    Takes YAML content (as a string) from completed research and saves it
    to the appropriate company directory. Use this after completing research
    from get_research_prompt.

    Args:
        company_name: Name of the company
        yaml_content: YAML content as a string (the research results)
    """
    await ctx.info(f"Saving research results for company: {company_name}")
    logger.info(f"save_research_results_tool called for: {company_name}")
    logger.debug(f"YAML content length: {len(yaml_content)} characters")

    result = save_research_results(
        company_name=company_name,
        yaml_content=yaml_content
    )

    if result.get("success"):
        facts_count = result.get("facts_generated", 0)
        logger.info(f"Successfully saved {facts_count} facts for {company_name}")
        await ctx.info(f"Saved {facts_count} facts for {company_name}")
    else:
        logger.error(f"Failed to save research for {company_name}: {result.get('error')}")
        await ctx.error(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def extract_flags_tool(
    company_name: str,
    conversation_notes: str,
    extracted_flags_yaml: str = None,
    ctx: Context = None
) -> dict:
    """Extract evaluation flags from conversation notes.

    This tool works in two modes:
    1. If extracted_flags_yaml is None: Returns a prompt for analyzing conversation notes
    2. If extracted_flags_yaml is provided: Processes and saves the extracted flags

    After getting the extraction prompt, use your analysis capabilities to extract flags,
    then call this tool again with the YAML results.

    Args:
        company_name: Name of the company being evaluated
        conversation_notes: Raw conversation notes to analyze
        extracted_flags_yaml: Optional YAML content with extracted flags (from LLM analysis)
    """
    if extracted_flags_yaml is None:
        await ctx.info(f"Generating flag extraction prompt for {company_name}")
        logger.info(f"extract_flags_tool called (prompt mode) for: {company_name}")
    else:
        await ctx.info(f"Processing extracted flags for {company_name}")
        logger.info(f"extract_flags_tool called (save mode) for: {company_name}")

    result = extract_flags(
        company_name=company_name,
        conversation_notes=conversation_notes,
        extracted_flags_yaml=extracted_flags_yaml
    )

    if result.get("success"):
        if extracted_flags_yaml:
            logger.info(f"Successfully saved flags for {company_name}")
            await ctx.info(f"Flags saved for {company_name}")
        else:
            logger.info(f"Extraction prompt generated for {company_name}")
            await ctx.info(f"Prompt ready - analyze notes and call again with YAML results")
    else:
        logger.warning(f"Error in extract_flags for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def add_manual_flag_tool(
    company_name: str,
    flag_type: str,
    mountain_element: str,
    ctx: Context,
    severity: str = None,
    flag: str = None,
    impact: str = None,
    confidence: str = None,
    question: str = None,
    why_important: str = None,
    how_to_find: str = None
) -> dict:
    """Manually add a flag to company evaluation (double hierarchy).

    For green flags: severity = "critical_matches" or "strong_positives"
    For red flags: severity = "dealbreakers" or "concerning"
    For green/red flags, also provide: flag, impact, confidence
    For missing data, provide: question, why_important, how_to_find (no severity needed)

    Args:
        company_name: Name of the company
        flag_type: Type of flag - "green", "red", or "missing"
        mountain_element: Mountain element - "mountain_range", "chosen_peak",
                         "rope_team_confidence", "daily_climb", or "story_worth_telling"
        severity: Severity level (required for green/red flags)
        flag: Flag text (for green/red flags)
        impact: Impact description (for green/red flags)
        confidence: Confidence level (for green/red flags)
        question: Question text (for missing data)
        why_important: Why it matters (for missing data)
        how_to_find: How to find the answer (for missing data)
    """
    await ctx.info(f"Adding {flag_type} flag for {company_name}")
    logger.info(f"add_manual_flag_tool called: {company_name} ({flag_type})")

    result = add_manual_flag(
        company_name=company_name,
        flag_type=flag_type,
        mountain_element=mountain_element,
        severity=severity,
        flag=flag,
        impact=impact,
        confidence=confidence,
        question=question,
        why_important=why_important,
        how_to_find=how_to_find
    )

    if result.get("success"):
        logger.info(f"Successfully added {flag_type} flag for {company_name}")
        await ctx.info(f"Flag added successfully")
    else:
        logger.warning(f"Failed to add flag for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def get_conversation_questions_tool(
    company_name: str,
    ctx: Context,
    stage: str = "opening",
    max_questions: int = 8
) -> dict:
    """Get conversation guidance questions based on existing company data.

    Returns relevant questions from a pre-built question bank, prioritizing
    areas where information is missing.

    Args:
        company_name: Name of the company
        stage: Conversation stage - "opening", "follow_up", or "deep_dive" (default: "opening")
        max_questions: Maximum number of questions to return (default: 8)
    """
    await ctx.info(f"Getting {stage} questions for {company_name}")
    logger.info(f"get_conversation_questions_tool called: {company_name} ({stage})")

    result = get_conversation_questions(
        company_name=company_name,
        stage=stage,
        max_questions=max_questions
    )

    if result.get("success"):
        question_count = len(result.get("questions", []))
        logger.info(f"Returned {question_count} questions for {company_name}")
        await ctx.info(f"Generated {question_count} questions")
    else:
        logger.warning(f"Failed to get questions for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def gut_check_tool(company_name: str, ctx: Context) -> dict:
    """Present a gut-check summary for decision making.

    Reads facts and flags, then formats an organized summary to help with
    decision making. Does not make any decisions - just presents the data.

    Args:
        company_name: Name of the company
    """
    await ctx.info(f"Generating gut check summary for {company_name}")
    logger.info(f"gut_check_tool called for: {company_name}")

    result = gut_check(company_name=company_name)

    if result.get("success"):
        logger.info(f"Gut check summary generated for {company_name}")
        await ctx.info(f"Summary generated")
    else:
        logger.warning(f"Failed to generate gut check for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def save_gut_decision_tool(
    company_name: str,
    mountain_worth_climbing: str,
    confidence: str,
    ctx: Context,
    reasoning: str = None
) -> dict:
    """Save a gut decision to the company's flags file.

    Records the decision with a timestamp. This is a data operation only -
    the decision itself must be made by the user.

    Args:
        company_name: Name of the company
        mountain_worth_climbing: "YES", "NO", or "MAYBE"
        confidence: "HIGH", "MEDIUM", or "LOW"
        reasoning: Optional reasoning text explaining the decision
    """
    await ctx.info(f"Saving gut decision for {company_name}: {mountain_worth_climbing}")
    logger.info(f"save_gut_decision_tool called: {company_name} = {mountain_worth_climbing}")

    result = save_gut_decision(
        company_name=company_name,
        mountain_worth_climbing=mountain_worth_climbing,
        confidence=confidence,
        reasoning=reasoning
    )

    if result.get("success"):
        logger.info(f"Decision saved for {company_name}")
        await ctx.info(f"Decision saved successfully")
    else:
        logger.warning(f"Failed to save decision for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def get_evaluation_summary_tool(ctx: Context) -> dict:
    """Generate a summary table of all company evaluations.

    Returns a formatted table showing all companies with their evaluation
    status, decisions, and confidence levels.
    """
    await ctx.info("Generating evaluation summary for all companies")
    logger.info("get_evaluation_summary_tool called")

    result = get_evaluation_summary()

    if result.get("success"):
        company_count = result.get("company_count", 0)
        logger.info(f"Summary generated for {company_count} companies")
        await ctx.info(f"Summary generated for {company_count} companies")
    else:
        logger.warning(f"Failed to generate summary: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
