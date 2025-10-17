#!/usr/bin/env python3
"""Get research prompt for a company.

This script demonstrates the research workflow:
1. Get a research prompt for a company
2. Display the prompt (you would then conduct research)
3. Save the research results (after conducting research)

Usage:
    uv run python examples/research_company.py "Company Name"
"""

import sys
from wctf_core import WCTFClient


def main():
    """Get research prompt for a company."""
    if len(sys.argv) < 2:
        print("Usage: uv run python examples/research_company.py \"Company Name\"")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    # Step 1: Get the research prompt
    result = client.get_research_prompt(company_name)

    if not result.get("success"):
        print(f"Error: {result.get('error')}")
        sys.exit(1)

    print("=" * 80)
    print(f"RESEARCH PROMPT FOR: {company_name}")
    print("=" * 80)
    print()
    print(result["research_prompt"])
    print()
    print("=" * 80)
    print("INSTRUCTIONS")
    print("=" * 80)
    print()
    print(result["instructions"])
    print()
    print("After conducting research, format your findings as YAML and save with:")
    print(f"  client.save_facts('{company_name}', yaml_content)")


if __name__ == "__main__":
    main()
