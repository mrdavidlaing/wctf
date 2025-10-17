#!/usr/bin/env python3
"""Check for duplicate facts across company data files.

This script uses the WCTF SDK to find both exact and semantically similar
duplicate facts within each company's facts and insider facts files.

Uses rapidfuzz for fuzzy string matching to catch facts that are worded
differently but mean the same thing.

Usage:
    uv run python check_duplicates.py [--threshold SIMILARITY_THRESHOLD]

Default similarity threshold: 85 (out of 100)
"""

import argparse
from collections import defaultdict
from typing import Dict, List, Tuple

from rapidfuzz import fuzz
from wctf_core import WCTFClient


def find_exact_duplicates(facts_data: dict) -> Dict[str, List[Tuple[str, str, str]]]:
    """Find exact duplicate facts in a company's facts data.

    Returns a dict mapping category names to lists of duplicate facts.
    Each duplicate is represented as (fact_text, source, date).
    """
    duplicates = {}

    categories = ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']

    for category in categories:
        if category not in facts_data:
            continue

        category_data = facts_data[category]
        if 'facts_found' not in category_data:
            continue

        facts_list = category_data['facts_found']

        # Track facts by (fact, source, date) tuple
        seen = defaultdict(int)

        for fact_item in facts_list:
            fact_key = (
                fact_item.get('fact', ''),
                fact_item.get('source', ''),
                str(fact_item.get('date', ''))
            )
            seen[fact_key] += 1

        # Find duplicates (count > 1)
        category_dupes = [key for key, count in seen.items() if count > 1]

        if category_dupes:
            duplicates[category] = [(f, s, d) for f, s, d in category_dupes]

    return duplicates


def find_similar_facts(facts_data: dict, threshold: int = 85) -> Dict[str, List[Tuple[str, str, float]]]:
    """Find semantically similar facts using fuzzy string matching.

    Returns a dict mapping category names to lists of similar fact pairs.
    Each pair is (fact1_text, fact2_text, similarity_score).

    Args:
        facts_data: Company facts data
        threshold: Similarity threshold (0-100). Higher = more strict.
                  Default 85 catches most similar facts without too many false positives.
    """
    similar_facts = {}

    categories = ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']

    for category in categories:
        if category not in facts_data:
            continue

        category_data = facts_data[category]
        if 'facts_found' not in category_data:
            continue

        facts_list = category_data['facts_found']

        # Compare each fact to every other fact
        similar_pairs = []
        for i, fact1 in enumerate(facts_list):
            fact1_text = fact1.get('fact', '')
            if not fact1_text:
                continue

            for j, fact2 in enumerate(facts_list[i+1:], start=i+1):
                fact2_text = fact2.get('fact', '')
                if not fact2_text:
                    continue

                # Use token_sort_ratio to handle word order differences
                # e.g., "raised $200M Series C" vs "Series C $200M raised"
                similarity = fuzz.token_sort_ratio(fact1_text, fact2_text)

                if similarity >= threshold:
                    similar_pairs.append((fact1_text, fact2_text, similarity))

        if similar_pairs:
            similar_facts[category] = similar_pairs

    return similar_facts


def main():
    """Check all companies for duplicate facts."""
    parser = argparse.ArgumentParser(
        description="Check for duplicate and similar facts in WCTF company data"
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=85,
        help='Similarity threshold for fuzzy matching (0-100, default: 85)'
    )
    args = parser.parse_args()

    client = WCTFClient()

    print("=" * 80)
    print("DUPLICATE FACT CHECKER")
    print("=" * 80)
    print()
    print("Checking for:")
    print("  1. Exact duplicates (same text, source, and date)")
    print(f"  2. Similar facts (similarity >= {args.threshold}%)")
    print()

    companies = client.list_companies()

    total_exact = 0
    total_similar = 0
    companies_with_exact = []
    companies_with_similar = []

    for company in companies:
        company_name = company['name']
        has_issues = False

        # Check regular facts
        if company.get('has_facts'):
            facts_result = client.get_facts(company_name)
            if facts_result.get('success'):
                facts_data = facts_result['facts']

                # Check for exact duplicates
                exact_dupes = find_exact_duplicates(facts_data)
                if exact_dupes:
                    if not has_issues:
                        print(f"🔍 {company_name}")
                        print("-" * 80)
                        has_issues = True

                    print(f"\n  EXACT DUPLICATES (company.facts.yaml):")
                    for category, dupes in exact_dupes.items():
                        print(f"    {category}:")
                        for fact, source, date in dupes:
                            fact_preview = fact[:60] + "..." if len(fact) > 60 else fact
                            print(f"      - \"{fact_preview}\"")
                            print(f"        ({source}, {date})")
                            total_exact += 1
                    companies_with_exact.append(company_name)

                # Check for similar facts
                similar_facts = find_similar_facts(facts_data, args.threshold)
                if similar_facts:
                    if not has_issues:
                        print(f"🔍 {company_name}")
                        print("-" * 80)
                        has_issues = True

                    print(f"\n  SIMILAR FACTS (company.facts.yaml):")
                    for category, pairs in similar_facts.items():
                        print(f"    {category}:")
                        for fact1, fact2, similarity in pairs:
                            print(f"      Similarity: {similarity:.1f}%")
                            fact1_preview = fact1[:60] + "..." if len(fact1) > 60 else fact1
                            fact2_preview = fact2[:60] + "..." if len(fact2) > 60 else fact2
                            print(f"        1: \"{fact1_preview}\"")
                            print(f"        2: \"{fact2_preview}\"")
                            print()
                            total_similar += 1
                    if company_name not in companies_with_similar:
                        companies_with_similar.append(company_name)

        if has_issues:
            print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Companies checked: {len(companies)}")
    print(f"Companies with exact duplicates: {len(companies_with_exact)}")
    print(f"Companies with similar facts: {len(companies_with_similar)}")
    print(f"Total exact duplicates: {total_exact}")
    print(f"Total similar fact pairs: {total_similar}")

    if companies_with_exact or companies_with_similar:
        print()
        print("💡 Tips:")
        print("   - Exact duplicates: Should be merged (same text, source, date)")
        print("   - Similar facts: Review manually - may be legitimate variations")
        print("   - Adjust threshold with --threshold (higher = more strict)")
        print()
        print(f"   Example: uv run python check_duplicates.py --threshold 90")
    else:
        print()
        print("✨ No duplicates found! Your data is pristine.")


if __name__ == "__main__":
    main()
