"""MCP server for WCTF company research data.

This module contains the MCP server implementation with tools for
managing and querying company research data.
"""

from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

from wctf_mcp.tools.company import (
    get_company_facts,
    get_company_flags,
    list_companies,
)

# Create the MCP server instance
app = Server("wctf-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="list_companies",
            description=(
                "List all companies with research data. "
                "Returns company names, count, and metadata about available files."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_company_facts",
            description=(
                "Get research facts for a specific company. "
                "Returns detailed factual information from company.facts.yaml including "
                "financial health, market position, organizational stability, and technical culture."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Name of the company (e.g., '1Password', 'anthropic')",
                    },
                },
                "required": ["company_name"],
            },
        ),
        Tool(
            name="get_company_flags",
            description=(
                "Get evaluation flags for a specific company. "
                "Returns evaluation data from company.flags.yaml including "
                "green flags, red flags, missing critical data, and synthesis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Name of the company (e.g., '1Password', 'anthropic')",
                    },
                },
                "required": ["company_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution requests."""

    if name == "list_companies":
        result = list_companies()

        # Format the response nicely
        if "error" in result:
            return [TextContent(type="text", text=f"Error: {result['error']}")]

        companies = result.get("companies", [])
        count = result.get("count", 0)

        if count == 0:
            return [TextContent(
                type="text",
                text="No companies found in the data directory."
            )]

        # Build a formatted response
        response_lines = [f"Found {count} companies:\n"]

        for detail in result.get("company_details", []):
            name_str = detail["name"]
            facts_str = "✓" if detail["has_facts"] else "✗"
            flags_str = "✓" if detail["has_flags"] else "✗"
            response_lines.append(f"  - {name_str} (facts: {facts_str}, flags: {flags_str})")

        return [TextContent(type="text", text="\n".join(response_lines))]

    elif name == "get_company_facts":
        company_name = arguments.get("company_name")

        if not company_name:
            return [TextContent(
                type="text",
                text="Error: company_name is required"
            )]

        result = get_company_facts(company_name=company_name)

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            suggestion = result.get("suggestion", "")
            response = f"Error: {error_msg}"
            if suggestion:
                response += f"\n\nSuggestion: {suggestion}"
            return [TextContent(type="text", text=response)]

        # Format facts data nicely
        facts = result["facts"]
        response_lines = [
            f"# Facts for {facts.get('company', company_name)}",
            f"Research Date: {facts.get('research_date', 'Unknown')}",
            "",
        ]

        # Add summary first
        if "summary" in facts:
            summary = facts["summary"]
            response_lines.extend([
                "## Summary",
                f"- Total Facts: {summary.get('total_facts_found', 0)}",
                f"- Completeness: {summary.get('information_completeness', 'unknown')}",
                f"- Verdict: {summary.get('verdict', 'N/A')}",
                "",
            ])

        # Add categories
        for category in ["financial_health", "market_position", "organizational_stability", "technical_culture"]:
            if category in facts:
                cat_data = facts[category]
                cat_name = category.replace("_", " ").title()
                response_lines.append(f"## {cat_name}")

                facts_found = cat_data.get("facts_found", [])
                if facts_found:
                    response_lines.append(f"Found {len(facts_found)} facts")

                missing = cat_data.get("missing_information", [])
                if missing:
                    response_lines.append(f"Missing {len(missing)} items")

                response_lines.append("")

        return [TextContent(type="text", text="\n".join(response_lines))]

    elif name == "get_company_flags":
        company_name = arguments.get("company_name")

        if not company_name:
            return [TextContent(
                type="text",
                text="Error: company_name is required"
            )]

        result = get_company_flags(company_name=company_name)

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            suggestion = result.get("suggestion", "")
            response = f"Error: {error_msg}"
            if suggestion:
                response += f"\n\nSuggestion: {suggestion}"
            return [TextContent(type="text", text=response)]

        # Format flags data nicely
        flags = result["flags"]
        response_lines = [
            f"# Evaluation Flags for {flags.get('company', company_name)}",
            f"Evaluation Date: {flags.get('evaluation_date', 'Unknown')}",
            f"Context: {flags.get('evaluator_context', 'N/A')}",
            "",
        ]

        # Add synthesis first (most important)
        if "synthesis" in flags:
            synthesis = flags["synthesis"]
            response_lines.extend([
                "## Synthesis",
                f"- Worth Climbing: {synthesis.get('mountain_worth_climbing', 'UNKNOWN')}",
                f"- Sustainability: {synthesis.get('sustainability_confidence', 'UNKNOWN')}",
                f"- Confidence: {synthesis.get('confidence_level', 'UNKNOWN')}",
                "",
            ])

            if "primary_strengths" in synthesis:
                response_lines.append("Primary Strengths:")
                for strength in synthesis["primary_strengths"]:
                    response_lines.append(f"  - {strength}")
                response_lines.append("")

            if "primary_risks" in synthesis:
                response_lines.append("Primary Risks:")
                for risk in synthesis["primary_risks"]:
                    response_lines.append(f"  - {risk}")
                response_lines.append("")

        # Add alignment
        if "senior_engineer_alignment" in flags:
            alignment = flags["senior_engineer_alignment"]
            response_lines.extend([
                "## Senior Engineer Alignment",
            ])
            for key, value in alignment.items():
                key_name = key.replace("_", " ").title()
                response_lines.append(f"- {key_name}: {value}")
            response_lines.append("")

        # Add green flags summary
        if "green_flags" in flags:
            green = flags["green_flags"]
            critical = len(green.get("critical_matches", []))
            strong = len(green.get("strong_positives", []))
            response_lines.append(f"## Green Flags: {critical} critical, {strong} strong")
            response_lines.append("")

        # Add red flags summary
        if "red_flags" in flags:
            red = flags["red_flags"]
            dealbreakers = len(red.get("dealbreakers", []))
            concerning = len(red.get("concerning", []))
            response_lines.append(f"## Red Flags: {dealbreakers} dealbreakers, {concerning} concerning")
            response_lines.append("")

        # Add missing data count
        if "missing_critical_data" in flags:
            missing_count = len(flags["missing_critical_data"])
            response_lines.append(f"## Missing Critical Data: {missing_count} items")
            response_lines.append("")

        return [TextContent(type="text", text="\n".join(response_lines))]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


def main():
    """Main entry point for the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
