#!/usr/bin/env python3
"""Get flags extraction prompt for a company.

Displays the company's facts in a structured format and provides
the extraction prompt for evaluating the company.

Usage:
    uv run python scripts/get_flags_prompt.py "Company Name"
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core import WCTFClient


def display_structured_facts(facts: dict) -> None:
    """Display facts in a structured, readable format."""
    print("\n" + "=" * 80)
    print(f"COMPANY: {facts.get('company', 'Unknown')}")
    print(f"Research Date: {facts.get('research_date', 'N/A')}")
    print("=" * 80)

    # Display summary
    summary = facts.get('summary', {})
    print(f"\nSUMMARY:")
    print(f"  Total Facts: {summary.get('total_facts_found', 'N/A')}")
    print(f"  Completeness: {summary.get('information_completeness', 'N/A')}")

    # Categories to display
    categories = [
        ('financial_health', 'FINANCIAL HEALTH'),
        ('market_position', 'MARKET POSITION'),
        ('organizational_stability', 'ORGANIZATIONAL STABILITY'),
        ('technical_culture', 'TECHNICAL CULTURE')
    ]

    for key, title in categories:
        category = facts.get(key, {})
        if not category:
            continue

        print(f"\n{title}:")
        print("-" * 80)

        # Display facts found
        facts_found = category.get('facts_found', [])
        if facts_found:
            print(f"  Facts Found ({len(facts_found)}):")
            for i, fact in enumerate(facts_found, 1):
                print(f"    {i}. {fact.get('fact', 'N/A')}")
                print(f"       Source: {fact.get('source', 'N/A')}")
                print(f"       Date: {fact.get('date', 'N/A')} | Confidence: {fact.get('confidence', 'N/A')}")
                if i < len(facts_found):
                    print()

        # Display missing information
        missing = category.get('missing_information', [])
        if missing:
            print(f"\n  Missing Information ({len(missing)}):")
            for item in missing:
                print(f"    - {item}")

    print("\n" + "=" * 80)


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/get_flags_prompt.py \"Company Name\"")
        print("\nExample:")
        print("  uv run python scripts/get_flags_prompt.py \"Stripe\"")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    # Check if company exists
    if not client.company_exists(company_name):
        print(f"ERROR: Company '{company_name}' not found.")
        print("\nAvailable companies with facts but no flags:")
        companies = client.list_companies()
        need_flags = [c['name'] for c in companies if c['has_facts'] and not c['has_flags']]
        for name in sorted(need_flags):
            print(f"  - {name}")
        sys.exit(1)

    # Get facts
    result = client.get_facts(company_name)
    if not result['success']:
        print(f"ERROR: Could not load facts for {company_name}: {result.get('error')}")
        sys.exit(1)

    # Display facts
    facts = result['facts']
    display_structured_facts(facts)

    # Get and display extraction prompt
    evaluator_context = "Staff software engineer with 25 years experience seeking company where technology is an equal partner to business, with strong engineering practices (high DORA metrics: deployment frequency, lead time, MTTR, change failure rate), access to AI coding tools (GitHub Copilot, Cursor, etc.), and sustainable business model. Remote-first or hybrid in Dublin Ireland is acceptable."
    prompt_result = client.get_flags_extraction_prompt(company_name, evaluator_context)
    if not prompt_result['success']:
        print(f"ERROR: Could not generate extraction prompt: {prompt_result.get('error')}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("FLAGS EXTRACTION PROMPT:")
    print("=" * 80)
    print(prompt_result['extraction_prompt'])
    print("=" * 80)


if __name__ == '__main__':
    main()
