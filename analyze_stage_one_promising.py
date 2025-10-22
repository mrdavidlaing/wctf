#!/usr/bin/env python3
"""Analyze stage 1 companies to identify most promising candidates for insider interviews."""
import os
from pathlib import Path
from wctf_core import WCTFClient

def count_flags(flags_data, flag_type='green_flags', severity='critical_matches'):
    """Count flags of a specific type across all mountain elements."""
    count = 0
    flag_section = flags_data.get(flag_type, {})
    for element in ['mountain_range', 'chosen_peak', 'rope_team_confidence', 'daily_climb', 'story_worth_telling']:
        element_data = flag_section.get(element, {})
        flags = element_data.get(severity, [])
        count += len(flags) if isinstance(flags, list) else 0
    return count

def main():
    # Create client pointing to data directory (contains all stages)
    client = WCTFClient()  # Uses ./data by default
    stage_1_path = Path("data/stage-1")

    # Get all stage 1 companies
    stage_1_companies = []
    for company_dir in sorted(stage_1_path.iterdir()):
        if company_dir.is_dir():
            stage_1_companies.append(company_dir.name)

    print(f"Found {len(stage_1_companies)} stage 1 companies\n")

    # Categorize companies
    yes_companies = []
    no_companies = []
    not_evaluated = []
    has_insider = []
    evaluated_companies = []

    for company_slug in stage_1_companies:
        # Check for insider interviews
        insider_path = stage_1_path / company_slug / "company.insider.yaml"
        if insider_path.exists():
            has_insider.append(company_slug)

        # Check for flags
        flags_path = stage_1_path / company_slug / "company.flags.yaml"
        if not flags_path.exists():
            not_evaluated.append(company_slug)
            continue

        # Get flags
        result = client.get_flags(company_slug)
        if not result['success'] or not result['flags']:
            not_evaluated.append(company_slug)
            continue

        flags = result['flags']

        # Check synthesis section
        synthesis = flags.get('synthesis', {})
        if synthesis:
            worth_climbing = synthesis.get('mountain_worth_climbing', None)
            if worth_climbing == True or worth_climbing == 'YES':
                yes_companies.append({
                    'name': company_slug,
                    'confidence': synthesis.get('sustainability_confidence', 'UNKNOWN'),
                    'strengths': synthesis.get('primary_strengths', []),
                    'risks': synthesis.get('primary_risks', [])
                })
            elif worth_climbing == False or worth_climbing == 'NO':
                no_companies.append(company_slug)
        else:
            # No synthesis - analyze the flags to estimate promise
            green_critical = count_flags(flags, 'green_flags', 'critical_matches')
            green_strong = count_flags(flags, 'green_flags', 'strong_positives')
            red_dealbreaker = count_flags(flags, 'red_flags', 'dealbreakers')
            red_concerning = count_flags(flags, 'red_flags', 'concerning')

            evaluated_companies.append({
                'name': company_slug,
                'green_critical': green_critical,
                'green_strong': green_strong,
                'red_dealbreaker': red_dealbreaker,
                'red_concerning': red_concerning,
                'has_insider': company_slug in has_insider
            })

    # Sort evaluated companies by promise (more green critical, fewer red dealbreakers)
    evaluated_companies.sort(key=lambda x: (
        -x['red_dealbreaker'],  # Fewer dealbreakers is better (negate for sort)
        -x['green_critical'],   # More critical green flags is better
        -x['green_strong'],     # More strong positives is better
        x['red_concerning']      # Fewer concerning is better
    ))

    # Print results
    print("=" * 80)
    print("DEFINITE YES - Companies with synthesis recommendation")
    print("=" * 80)
    if yes_companies:
        for company in yes_companies:
            has_int = "✓ HAS INSIDER" if company['name'] in has_insider else ""
            print(f"\n{company['name'].upper()} {has_int}")
            print(f"  Confidence: {company['confidence']}")
            if company['strengths']:
                print(f"  Top strengths:")
                for s in company['strengths'][:3]:
                    print(f"    - {s}")
    else:
        print("  None found")

    print("\n" + "=" * 80)
    print("DEFINITE NO - Companies with negative synthesis")
    print("=" * 80)
    if no_companies:
        for company in no_companies:
            has_int = "✓ HAS INSIDER" if company in has_insider else ""
            print(f"  - {company} {has_int}")
    else:
        print("  None found")

    print("\n" + "=" * 80)
    print("EVALUATED BUT NO SYNTHESIS - Ranked by promise")
    print("=" * 80)
    print("(Sorted by: fewest dealbreakers, most critical matches, fewest concerns)")
    print()

    for i, company in enumerate(evaluated_companies[:15], 1):  # Top 15
        has_int = "✓" if company['has_insider'] else " "
        print(f"{i:2}. [{has_int}] {company['name']:30} | "
              f"Green: {company['green_critical']:2}C/{company['green_strong']:2}S | "
              f"Red: {company['red_dealbreaker']:2}D/{company['red_concerning']:2}C")

    print("\n" + "=" * 80)
    print("NOT YET EVALUATED")
    print("=" * 80)
    if not_evaluated:
        for company in not_evaluated[:10]:  # First 10
            has_int = "✓ HAS INSIDER" if company in has_insider else ""
            print(f"  - {company} {has_int}")
        if len(not_evaluated) > 10:
            print(f"  ... and {len(not_evaluated) - 10} more")
    else:
        print("  None")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Definite YES: {len(yes_companies)}")
    print(f"  Definite NO: {len(no_companies)}")
    print(f"  Evaluated (no synthesis): {len(evaluated_companies)}")
    print(f"  Not yet evaluated: {len(not_evaluated)}")
    print(f"  Already have insider data: {len(has_insider)}")

    print("\n" + "=" * 80)
    print("RECOMMENDATION PRIORITY FOR INSIDER INTERVIEWS")
    print("=" * 80)

    print("\n1. DEFINITE YES companies without insider:")
    yes_without_insider = [c['name'] for c in yes_companies if c['name'] not in has_insider]
    if yes_without_insider:
        for company in yes_without_insider:
            print(f"   - {company}")
    else:
        print("   (None)")

    print("\n2. TOP EVALUATED companies without insider (no dealbreakers, most green):")
    top_without_insider = [c for c in evaluated_companies if not c['has_insider'] and c['red_dealbreaker'] == 0][:10]
    if top_without_insider:
        for company in top_without_insider:
            print(f"   - {company['name']:30} (Green: {company['green_critical']}C/{company['green_strong']}S, Red: {company['red_concerning']}C)")
    else:
        print("   (None)")

if __name__ == "__main__":
    main()
