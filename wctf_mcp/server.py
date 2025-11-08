"""MCP server for WCTF company research data.

This module contains the MCP server implementation with tools for
managing and querying company research data.
"""

import logging

from mcp.server.fastmcp import FastMCP, Context

from wctf_core.operations.company import (
    get_company_facts,
    get_company_flags,
    list_companies,
)
from wctf_core.operations.research import (
    get_research_prompt,
    save_research_results,
)
from wctf_core.operations.flags import (
    get_flags_extraction_prompt_op,
    save_flags_op,
    add_manual_flag,
)
from wctf_core.operations.insider import (
    get_insider_extraction_prompt,
    save_insider_facts,
)
from wctf_core.operations.conversation import (
    get_conversation_questions,
)
from wctf_core.operations.decision import (
    gut_check,
    save_gut_decision,
    get_evaluation_summary,
)
from wctf_mcp.tools.profile_tools import get_profile_tool, update_profile_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set FastMCP and uvicorn to ERROR level to see our logs better
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

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
    """Start Layer 1 research for a company using Research mode.

    IMPORTANT TWO-STEP WORKFLOW:
    1. Call this tool to get the research prompt
    2. STOP and tell the user: "Please enable Research mode (toggle in Claude Desktop UI), then say 'ready' to proceed"
    3. Wait for user confirmation
    4. ONLY THEN execute the research using Research mode
    5. Format findings as YAML and save with save_research_results_tool

    Research mode provides deep, multi-source investigation with citations.
    Do NOT proceed with basic web search.

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

    IMPORTANT - DEDUPLICATION WORKFLOW:
    Before calling this tool, you MUST follow this workflow to avoid duplicates:

    1. Call get_company_facts_tool(company_name) to retrieve existing facts
    2. Compare your new research against the existing facts semantically
    3. For duplicate facts (same information, even if worded differently):
       - Combine sources: "Source A; Source B"
       - Use the most recent date
       - Keep the clearest wording
    4. Only include in yaml_content:
       - Genuinely new facts not present in existing data
       - Enhanced facts (same info but better source/date)

    Example: If existing has "Revenue of $5B (TechCrunch, 2024-01-15)" and you
    found "Company revenue is $5 billion (10-K filing, 2024-03-01)", merge them as:
    "Revenue of $5B (TechCrunch; 10-K filing, 2024-03-01)"

    This tool will merge your new facts with existing ones, so proper deduplication
    before saving keeps the data clean.

    IMPORTANT: yaml_content must be a complete YAML string following this exact structure:

    ```yaml
    company: "CompanyName"
    research_date: "YYYY-MM-DD"

    financial_health:
      facts_found:
        - fact: "Descriptive statement"
          source: "Source citation"
          date: "YYYY-MM-DD"
          confidence: "explicit_statement"
      missing_information:
        - "What's missing"

    market_position:
      facts_found: [...]
      missing_information: [...]

    organizational_stability:
      facts_found: [...]
      missing_information: [...]

    technical_culture:
      facts_found: [...]
      missing_information: [...]

    summary:
      total_facts_found: 42
      information_completeness: "high"
      most_recent_data_point: "YYYY-MM-DD"
      oldest_data_point: "YYYY-MM-DD"
    ```

    All four categories (financial_health, market_position, organizational_stability,
    technical_culture) and the summary section are REQUIRED.

    SIZE LIMITS - IMPORTANT:
    YAML content must be under ~50KB to avoid truncation. If research is extensive:
    - Consolidate related facts (e.g., combine multiple funding rounds into one fact)
    - Keep 20-30 most important facts per category, not 50+
    - Use concise sources: "Company announcements" not "Press Release, PR Newswire, Wikipedia"
    - Shorten context fields to essential information only
    Quality over quantity - focused facts are better than truncated comprehensive research.

    Args:
        company_name: Name of the company
        yaml_content: Complete YAML content as a string (the research results)
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
async def get_flags_extraction_prompt_tool(
    company_name: str,
    evaluator_context: str,
    ctx: Context = None
) -> dict:
    """Get prompt for extracting evaluation flags from research.

    Returns a detailed prompt to guide analysis of company research facts
    and extraction of green flags, red flags, and missing critical data.

    Args:
        company_name: Name of the company being evaluated
        evaluator_context: Your evaluation criteria and context
            (e.g., "Senior engineer seeking strong technical culture and work-life balance")
    """
    await ctx.info(f"Generating flag extraction prompt for {company_name}")
    logger.info(f"get_flags_extraction_prompt_tool called for: {company_name}")

    result = get_flags_extraction_prompt_op(
        company_name=company_name,
        evaluator_context=evaluator_context
    )

    if result.get("success"):
        logger.info(f"Extraction prompt generated for {company_name}")
        await ctx.info(f"Prompt ready - analyze research and extract flags")
    else:
        logger.warning(f"Error generating extraction prompt for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def save_flags_tool(
    company_name: str,
    flags_yaml: str,
    ctx: Context = None
) -> dict:
    """Save extracted evaluation flags to company.flags.yaml.

    Takes YAML content with extracted flags (green flags, red flags, missing data)
    and saves to the company's flags file. Merges with existing flags if present.

    Args:
        company_name: Name of the company
        flags_yaml: Complete YAML content with extracted flags
    """
    await ctx.info(f"Saving evaluation flags for {company_name}")
    logger.info(f"save_flags_tool called for: {company_name}")

    result = save_flags_op(
        company_name=company_name,
        flags_yaml=flags_yaml
    )

    if result.get("success"):
        logger.info(f"Successfully saved flags for {company_name}")
        await ctx.info(f"Flags saved for {company_name}")
    else:
        logger.warning(f"Error saving flags for {company_name}: {result.get('error')}")
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
async def get_insider_extraction_prompt_tool(
    company_name: str,
    interview_date: str,
    interviewee_name: str,
    ctx: Context,
    interviewee_role: str = None
) -> dict:
    """Extract facts from an INSIDER INTERVIEW transcript (employees/ex-employees only).

    IMPORTANT: Use this tool ONLY for interviews with current or former employees who
    have firsthand knowledge of working at the company. For general conversation notes,
    research discussions, or non-employee conversations, DO NOT use this tool - instead
    manually format facts as YAML and save with save_research_results_tool.

    Returns a formatted prompt that guides extraction of structured facts from
    the insider interview transcript (which should already be in your conversation context).
    Classifies facts as objective or subjective. Saves to company.insider.yaml (separate
    from public research facts).

    After receiving this prompt, analyze the transcript in your conversation context
    and extract facts, then call save_insider_facts_tool to save the extracted YAML.

    Args:
        company_name: Name of the company
        interview_date: Date of interview in YYYY-MM-DD format
        interviewee_name: Name of person interviewed (e.g., "Ahmad A")
        interviewee_role: Optional role/title (e.g., "Senior Engineer, Observability")
    """
    await ctx.info(f"Generating insider fact extraction prompt for {company_name}")
    logger.info(f"get_insider_extraction_prompt_tool called for: {company_name}")

    result = get_insider_extraction_prompt(
        company_name=company_name,
        interview_date=interview_date,
        interviewee_name=interviewee_name,
        interviewee_role=interviewee_role
    )

    if result.get("success"):
        logger.info(f"Extraction prompt generated for {company_name}")
        await ctx.info(f"Prompt ready - analyze transcript and extract facts")
    else:
        logger.warning(f"Error generating prompt for {company_name}: {result.get('error')}")
        await ctx.warning(f"Error: {result.get('error')}")

    return result


@mcp.tool()
async def save_insider_facts_tool(
    company_name: str,
    interview_date: str,
    interviewee_name: str,
    extracted_facts_yaml: str,
    ctx: Context,
    interviewee_role: str = None
) -> dict:
    """Save extracted INSIDER INTERVIEW facts to company.insider.yaml.

    IMPORTANT: Use this tool ONLY for saving facts extracted from interviews with
    current or former employees. For general research facts, use save_research_results_tool
    instead (which saves to company.facts.yaml).

    Takes YAML content with extracted facts and saves them to the appropriate
    company directory. Merges with existing insider facts if the file already exists.

    Use this after get_insider_extraction_prompt_tool has been used to analyze
    the insider interview transcript and extract structured facts.

    Args:
        company_name: Name of the company
        interview_date: Date of interview in YYYY-MM-DD format
        interviewee_name: Name of person interviewed (e.g., "Ahmad A")
        extracted_facts_yaml: YAML content with extracted facts (from analysis)
        interviewee_role: Optional role/title (e.g., "Senior Engineer, Observability")
    """
    await ctx.info(f"Saving extracted insider facts for {company_name}")
    logger.info(f"save_insider_facts_tool called for: {company_name}")

    result = save_insider_facts(
        company_name=company_name,
        interview_date=interview_date,
        interviewee_name=interviewee_name,
        extracted_facts_yaml=extracted_facts_yaml,
        interviewee_role=interviewee_role
    )

    if result.get("success"):
        facts_count = result.get("facts_count", 0)
        logger.info(f"Successfully saved {facts_count} insider facts for {company_name}")
        await ctx.info(f"Saved {facts_count} insider facts for {company_name}")
    else:
        logger.warning(f"Error saving insider facts for {company_name}: {result.get('error')}")
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


@mcp.tool()
async def get_profile(ctx: Context) -> str:
    """Get current profile.yaml for reference during flag extraction.

    Returns the full profile including energy drains, generators, strengths,
    and organizational coherence needs.
    """
    await ctx.info("Retrieving profile")
    logger.info("get_profile tool called")

    result = await get_profile_tool()

    # Return the text content directly
    return result[0].text


@mcp.tool()
async def update_profile(updated_profile_yaml: str, ctx: Context) -> str:
    """Update profile.yaml with new self-knowledge.

    Args:
        updated_profile_yaml: Complete profile YAML content

    Actions:
        - Increments profile_version (e.g., "1.0" -> "1.1")
        - Updates last_updated timestamp
        - Writes to data/profile.yaml
    """
    await ctx.info("Updating profile")
    logger.info("update_profile tool called")

    result = await update_profile_tool(updated_profile_yaml)

    # Return the text content directly
    return result[0].text


def main():
    """Main entry point for the MCP server.

    Transport can be controlled via WCTF_TRANSPORT environment variable:
    - "stdio" (default): For Claude Desktop config, provides "hot reload" (code changes picked up on next call)
    - "streamable-http": For HTTP-based connections, faster but requires restart for code changes
    """
    import os
    import signal
    import sys

    # Get transport from environment, default to stdio for easier development
    transport = os.getenv("WCTF_TRANSPORT", "stdio")

    if transport not in ["stdio", "streamable-http", "sse"]:
        logger.error(f"Invalid transport: {transport}. Use 'stdio' or 'streamable-http'")
        sys.exit(1)

    logger.info(f"Starting WCTF MCP server with {transport} transport")

    def signal_handler(sig, frame):
        """Handle Ctrl+C gracefully."""
        logger.info("Received shutdown signal, stopping server...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        mcp.run(transport=transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
