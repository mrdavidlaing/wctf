#!/usr/bin/env python3
"""Show full details of duplicate facts for manual review.

This script displays duplicate facts with complete information so you can
manually review and edit the YAML files.

Usage:
    uv run python show_duplicates.py [COMPANY_NAME] [--threshold THRESHOLD]

If no company specified, shows all companies with duplicates.
"""

import argparse
from typing import Optional

from rapidfuzz import fuzz
from wctf_core import WCTFClient


def show_company_duplicates(company_name: str, threshold: int, show_all: bool = False):
    """Show similar facts for a specific company with full details."""
    client = WCTFClient()

    # Get facts
    facts_result = client.get_facts(company_name)
    if not facts_result.get('success'):
        return False

    facts_data = facts_result['facts']
    categories = ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']

    found_any = False

    for category in categories:
        if category not in facts_data:
            continue

        category_data = facts_data[category]
        if 'facts_found' not in category_data:
            continue

        facts_list = category_data['facts_found']

        # Find similar pairs
        for i, fact1 in enumerate(facts_list):
            fact1_text = fact1.get('fact', '')
            if not fact1_text:
                continue

            for j, fact2 in enumerate(facts_list[i+1:], start=i+1):
                fact2_text = fact2.get('fact', '')
                if not fact2_text:
                    continue

                similarity = fuzz.token_sort_ratio(fact1_text, fact2_text)

                if similarity >= threshold:
                    if not found_any:
                        print("\n" + "=" * 80)
                        print(f"COMPANY: {company_name}")
                        print("=" * 80)
                        found_any = True

                    print(f"\n📍 Category: {category} (indices: {i}, {j})")
                    print(f"   Similarity: {similarity:.1f}%")
                    print("-" * 80)
                    print(f"\n   [1] Fact:")
                    print(f"       Text: {fact1.get('fact', 'N/A')}")
                    print(f"       Source: {fact1.get('source', 'N/A')}")
                    print(f"       Date: {fact1.get('date', 'N/A')}")
                    print(f"       Confidence: {fact1.get('confidence', 'N/A')}")

                    print(f"\n   [2] Fact:")
                    print(f"       Text: {fact2.get('fact', 'N/A')}")
                    print(f"       Source: {fact2.get('source', 'N/A')}")
                    print(f"       Date: {fact2.get('date', 'N/A')}")
                    print(f"       Confidence: {fact2.get('confidence', 'N/A')}")

    return found_any


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Show full details of duplicate facts for manual review"
    )
    parser.add_argument(
        'company_name',
        nargs='?',
        help='Name of specific company to review (optional)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=90,
        help='Similarity threshold (0-100, default: 90)'
    )
    args = parser.parse_args()

    client = WCTFClient()

    print("=" * 80)
    print("DUPLICATE FACTS - DETAILED VIEW")
    print("=" * 80)
    print(f"Threshold: {args.threshold}%")

    if args.company_name:
        # Show specific company
        found = show_company_duplicates(args.company_name, args.threshold)
        if not found:
            print(f"\n✨ No duplicates found for {args.company_name}")
    else:
        # Show all companies
        companies = client.list_companies()
        total_companies = 0

        for company in companies:
            if company.get('has_facts'):
                found = show_company_duplicates(company['name'], args.threshold)
                if found:
                    total_companies += 1

        if total_companies == 0:
            print("\n✨ No duplicates found across all companies")
        else:
            print("\n" + "=" * 80)
            print(f"Found duplicates in {total_companies} companies")
            print("=" * 80)

    print("\n💡 To merge duplicates:")
    print("   1. Open the company's data/COMPANY_NAME/company.facts.yaml file")
    print("   2. Find the facts listed above (use the indices if needed)")
    print("   3. Merge the information, keeping the most complete version")
    print("   4. Delete the duplicate entry")
    print("   5. Save and re-run check_duplicates.py to verify")


if __name__ == "__main__":
    main()
