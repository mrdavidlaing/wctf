#!/usr/bin/env python3
"""Automatically merge duplicate facts with high similarity.

This script finds facts with similarity >= threshold and keeps the more
complete version (longer text, more sources, etc.).

Usage:
    uv run python merge_duplicates.py [--threshold THRESHOLD] [--dry-run]

Default threshold: 90
Use --dry-run to preview changes without modifying files.
"""

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import re

from rapidfuzz import fuzz
from wctf_core import WCTFClient
from wctf_core.utils.yaml_handler import read_yaml, write_yaml
from wctf_core.utils.paths import get_facts_path


def extract_numbers_and_dates(text: str) -> set:
    """Extract all numbers and dates from text for comparison.

    This helps identify facts that look similar but have different data.
    """
    # Find all numbers (including decimals, percentages, currency)
    numbers = set(re.findall(r'\d+(?:\.\d+)?', text))
    return numbers


def are_different_facts(fact1: dict, fact2: dict) -> bool:
    """Check if two facts are actually different despite high similarity.

    Returns True if they're different facts (e.g., different years, different values).
    """
    fact1_text = fact1.get('fact', '')
    fact2_text = fact2.get('fact', '')

    # Extract numbers from both facts
    nums1 = extract_numbers_and_dates(fact1_text)
    nums2 = extract_numbers_and_dates(fact2_text)

    # If they have different numbers, they might be different facts
    # (e.g., "Revenue in 2023: $10M" vs "Revenue in 2024: $15M")
    if nums1 != nums2:
        # Check if the difference is significant (not just rounding)
        unique_to_1 = nums1 - nums2
        unique_to_2 = nums2 - nums1

        # If there are unique numbers in each, they're likely different facts
        if unique_to_1 and unique_to_2:
            return True

    return False


def choose_better_fact(fact1: dict, fact2: dict) -> Tuple[dict, dict]:
    """Choose the more complete fact from two similar facts.

    Returns (keep, discard) tuple.

    Criteria (in order):
    1. Longer fact text (more detail)
    2. More sources (semicolon-separated count)
    3. Same length -> keep first one (arbitrary but consistent)
    """
    fact1_text = fact1.get('fact', '')
    fact2_text = fact2.get('fact', '')

    # 1. Prefer longer text (more detail)
    if len(fact1_text) != len(fact2_text):
        if len(fact1_text) > len(fact2_text):
            return (fact1, fact2)
        else:
            return (fact2, fact1)

    # 2. Prefer more sources
    fact1_sources = fact1.get('source', '').count(';') + 1
    fact2_sources = fact2.get('source', '').count(';') + 1

    if fact1_sources != fact2_sources:
        if fact1_sources > fact2_sources:
            return (fact1, fact2)
        else:
            return (fact2, fact1)

    # 3. Equal - keep first one
    return (fact1, fact2)


def merge_company_duplicates(company_name: str, threshold: int, dry_run: bool = False) -> Dict[str, int]:
    """Merge duplicate facts for a company.

    Returns dict with statistics about what was merged.
    """
    client = WCTFClient()

    # Get facts
    facts_result = client.get_facts(company_name)
    if not facts_result.get('success'):
        return {'error': True, 'message': facts_result.get('error')}

    facts_data = facts_result['facts']
    categories = ['financial_health', 'market_position', 'organizational_stability', 'technical_culture']

    total_merged = 0
    changes_by_category = {}

    for category in categories:
        if category not in facts_data:
            continue

        category_data = facts_data[category]
        if 'facts_found' not in category_data:
            continue

        facts_list = category_data['facts_found']

        # Track indices to remove (we'll remove from end to preserve indices)
        indices_to_remove = set()
        merged_pairs = []

        # Find and merge similar pairs
        for i, fact1 in enumerate(facts_list):
            if i in indices_to_remove:
                continue

            fact1_text = fact1.get('fact', '')
            if not fact1_text:
                continue

            for j, fact2 in enumerate(facts_list[i+1:], start=i+1):
                if j in indices_to_remove:
                    continue

                fact2_text = fact2.get('fact', '')
                if not fact2_text:
                    continue

                similarity = fuzz.token_sort_ratio(fact1_text, fact2_text)

                if similarity >= threshold:
                    # Check if they're actually different facts (different data)
                    if are_different_facts(fact1, fact2):
                        continue  # Skip - these are different facts

                    # Choose better fact
                    keep, discard = choose_better_fact(fact1, fact2)

                    # Mark for removal
                    if discard == fact1:
                        indices_to_remove.add(i)
                        # Update the kept fact at index j
                        facts_list[j] = keep
                    else:
                        indices_to_remove.add(j)
                        # Keep fact at index i (already there)
                        facts_list[i] = keep

                    merged_pairs.append({
                        'kept': keep.get('fact', '')[:60] + '...',
                        'discarded': discard.get('fact', '')[:60] + '...',
                        'similarity': similarity
                    })

                    total_merged += 1
                    break  # Don't compare fact1 with more facts after merging

        # Remove duplicates (from end to preserve indices)
        if indices_to_remove:
            for idx in sorted(indices_to_remove, reverse=True):
                del facts_list[idx]

            changes_by_category[category] = {
                'removed': len(indices_to_remove),
                'pairs': merged_pairs
            }

    # Save updated facts (if not dry run)
    if not dry_run and total_merged > 0:
        facts_path = get_facts_path(company_name)

        # Update summary count
        if 'summary' in facts_data:
            total_facts = sum(
                len(facts_data.get(cat, {}).get('facts_found', []))
                for cat in categories
            )
            facts_data['summary']['total_facts_found'] = total_facts

        write_yaml(facts_path, facts_data)

    return {
        'error': False,
        'total_merged': total_merged,
        'changes_by_category': changes_by_category
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatically merge duplicate facts with high similarity"
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=90,
        help='Similarity threshold (0-100, default: 90)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    args = parser.parse_args()

    print("=" * 80)
    print("DUPLICATE FACT MERGER")
    print("=" * 80)
    print(f"Threshold: {args.threshold}%")
    print(f"Mode: {'DRY RUN (no changes will be saved)' if args.dry_run else 'LIVE (will modify files)'}")
    print()

    client = WCTFClient()
    companies = client.list_companies()

    total_companies_changed = 0
    total_facts_merged = 0

    for company in companies:
        if not company.get('has_facts'):
            continue

        company_name = company['name']
        result = merge_company_duplicates(company_name, args.threshold, args.dry_run)

        if result.get('error'):
            print(f"❌ {company_name}: {result.get('message')}")
            continue

        merged = result.get('total_merged', 0)
        if merged > 0:
            total_companies_changed += 1
            total_facts_merged += merged

            print(f"\n🔧 {company_name}")
            print("-" * 80)
            print(f"   Merged {merged} duplicate fact(s)")

            for category, changes in result.get('changes_by_category', {}).items():
                print(f"\n   Category: {category}")
                print(f"   Removed {changes['removed']} duplicate(s)")

                for pair in changes['pairs']:
                    print(f"\n     Similarity: {pair['similarity']:.1f}%")
                    print(f"     ✓ Kept:      {pair['kept']}")
                    print(f"     ✗ Discarded: {pair['discarded']}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Companies processed: {len([c for c in companies if c.get('has_facts')])}")
    print(f"Companies with changes: {total_companies_changed}")
    print(f"Total facts merged: {total_facts_merged}")

    if args.dry_run and total_facts_merged > 0:
        print()
        print("💡 This was a dry run. To apply changes, run:")
        print(f"   uv run python merge_duplicates.py --threshold {args.threshold}")
    elif total_facts_merged > 0:
        print()
        print("✅ Changes saved! You can verify with:")
        print(f"   uv run python check_duplicates.py --threshold {args.threshold}")
    else:
        print()
        print("✨ No duplicates found!")


if __name__ == "__main__":
    main()
