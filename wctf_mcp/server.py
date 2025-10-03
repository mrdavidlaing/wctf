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


def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
