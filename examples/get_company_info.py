#!/usr/bin/env python3
"""Get detailed information about a company.

This script retrieves and displays both facts and flags for a company.

Usage:
    uv run python examples/get_company_info.py "Company Name"
"""

import sys
import json
from wctf_core import WCTFClient


def main():
    """Get and display company information."""
    if len(sys.argv) < 2:
        print("Usage: uv run python examples/get_company_info.py \"Company Name\"")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    # Check if company exists
    if not client.company_exists(company_name):
        print(f"Error: Company '{company_name}' not found.")
        print("\nAvailable companies:")
        for company in client.list_companies():
            print(f"  - {company['name']}")
        sys.exit(1)

    # Get facts
    print("=" * 80)
    print(f"FACTS FOR: {company_name}")
    print("=" * 80)
    facts_result = client.get_facts(company_name)

    if facts_result.get("success"):
        facts = facts_result["facts"]
        print(f"\nCompany: {facts.get('company')}")
        print(f"Research Date: {facts.get('research_date')}")

        # Print summary
        summary = facts.get("summary", {})
        print(f"\nTotal Facts: {summary.get('total_facts_found', 0)}")
        print(f"Completeness: {summary.get('information_completeness', 'unknown')}")

        # Print fact counts by category
        for category in ["financial_health", "market_position", "organizational_stability", "technical_culture"]:
            if category in facts:
                facts_found = facts[category].get("facts_found", [])
                print(f"  {category.replace('_', ' ').title()}: {len(facts_found)} facts")
    else:
        print(f"No facts available: {facts_result.get('error')}")

    # Get flags
    print("\n" + "=" * 80)
    print(f"FLAGS FOR: {company_name}")
    print("=" * 80)
    flags_result = client.get_flags(company_name)

    if flags_result.get("success"):
        flags = flags_result["flags"]
        print(f"\nEvaluation Date: {flags.get('evaluation_date')}")

        # Print green flags count
        green_flags = flags.get("green_flags", {})
        total_green = sum(
            len(element.get("critical_matches", [])) + len(element.get("strong_positives", []))
            for element in green_flags.values()
        )
        print(f"Green Flags: {total_green}")

        # Print red flags count
        red_flags = flags.get("red_flags", {})
        total_red = sum(
            len(element.get("dealbreakers", [])) + len(element.get("concerning", []))
            for element in red_flags.values()
        )
        print(f"Red Flags: {total_red}")

        # Print synthesis
        synthesis = flags.get("synthesis", {})
        if synthesis:
            print(f"\nDecision: {synthesis.get('mountain_worth_climbing', 'Not set')}")
            print(f"Confidence: {synthesis.get('sustainability_confidence', 'Not set')}")
    else:
        print(f"No flags available: {flags_result.get('error')}")


if __name__ == "__main__":
    main()
