#!/usr/bin/env python3
"""Analyze stage 1 companies to identify most promising candidates for insider interviews.

This script provides a comprehensive analysis of companies in stage 1, helping prioritize
which companies to pursue for insider interviews based on their evaluation flags.
"""
from pathlib import Path
from typing import Any, Dict, List

from wctf_core import WCTFClient
from wctf_core.utils.paths import get_stage_dir, list_companies

# Constants for display limits
TOP_EVALUATED_LIMIT = 15
TOP_NOT_EVALUATED_LIMIT = 10
TOP_CANDIDATES_LIMIT = 10

# Mountain elements used in flag categorization
# These correspond to the WCTF Framework's evaluation structure
# See WCTF_FRAMEWORK.md for details
MOUNTAIN_ELEMENTS = [
    'mountain_range',
    'chosen_peak',
    'rope_team_confidence',
    'daily_climb',
    'story_worth_telling'
]


def count_flags(flags_data: Dict[str, Any], flag_type: str = 'green_flags',
                severity: str = 'critical_matches') -> int:
    """Count flags of a specific type across all mountain elements.

    Mountain elements are the five key aspects of company evaluation in the WCTF framework:
    - mountain_range: Industry context and market position
    - chosen_peak: Company mission and strategic direction
    - rope_team_confidence: Team quality and collaboration
    - daily_climb: Day-to-day work and engineering culture
    - story_worth_telling: Impact and career development potential

    Args:
        flags_data: Dictionary containing flag data from company.flags.yaml
        flag_type: Type of flags to count ('green_flags' or 'red_flags')
        severity: Severity level to count ('critical_matches', 'strong_positives',
                 'dealbreakers', or 'concerning')

    Returns:
        Total count of flags matching the specified type and severity
    """
    count = 0
    flag_section = flags_data.get(flag_type, {})
    for element in MOUNTAIN_ELEMENTS:
        element_data = flag_section.get(element, {})
        flags = element_data.get(severity, [])
        count += len(flags) if isinstance(flags, list) else 0
    return count


def main() -> None:
    """Analyze stage 1 companies and identify most promising candidates for insider interviews.

    This function:
    1. Loads all stage 1 companies
    2. Categorizes them by synthesis recommendation (YES/NO/not evaluated)
    3. Ranks evaluated companies by green flags and red flags
    4. Prioritizes companies without existing insider interviews
    5. Displays comprehensive analysis with recommendations
    """
    try:
        # Create client pointing to data directory
        client = WCTFClient()

        # Get stage 1 directory path using SDK utilities
        stage_1_path = get_stage_dir(stage=1)

        if not stage_1_path.exists():
            print(f"Error: Stage 1 directory not found at {stage_1_path}")
            return

        # Get all stage 1 companies using SDK utilities
        stage_1_companies = list_companies(stage=1)

        if not stage_1_companies:
            print("No companies found in stage 1")
            return

        print(f"Found {len(stage_1_companies)} stage 1 companies\n")

    except Exception as e:
        print(f"Error initializing analysis: {e}")
        return

    # Categorize companies
    yes_companies: List[Dict[str, Any]] = []
    no_companies: List[str] = []
    not_evaluated: List[str] = []
    has_insider: List[str] = []
    evaluated_companies: List[Dict[str, Any]] = []

    for company_slug in stage_1_companies:
        try:
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
                # Normalize to uppercase string for consistent comparison
                worth_climbing_str = str(worth_climbing).upper() if worth_climbing is not None else None

                if worth_climbing_str in ('TRUE', 'YES'):
                    yes_companies.append({
                        'name': company_slug,
                        'confidence': synthesis.get('sustainability_confidence', 'UNKNOWN'),
                        'strengths': synthesis.get('primary_strengths', []),
                        'risks': synthesis.get('primary_risks', [])
                    })
                elif worth_climbing_str in ('FALSE', 'NO'):
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
        except Exception as e:
            print(f"Warning: Error processing {company_slug}: {e}")
            continue

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

    for i, company in enumerate(evaluated_companies[:TOP_EVALUATED_LIMIT], 1):
        has_int = "✓" if company['has_insider'] else " "
        print(f"{i:2}. [{has_int}] {company['name']:30} | "
              f"Green: {company['green_critical']:2}C/{company['green_strong']:2}S | "
              f"Red: {company['red_dealbreaker']:2}D/{company['red_concerning']:2}C")

    print("\n" + "=" * 80)
    print("NOT YET EVALUATED")
    print("=" * 80)
    if not_evaluated:
        for company in not_evaluated[:TOP_NOT_EVALUATED_LIMIT]:
            has_int = "✓ HAS INSIDER" if company in has_insider else ""
            print(f"  - {company} {has_int}")
        if len(not_evaluated) > TOP_NOT_EVALUATED_LIMIT:
            print(f"  ... and {len(not_evaluated) - TOP_NOT_EVALUATED_LIMIT} more")
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
    top_without_insider = [c for c in evaluated_companies
                          if not c['has_insider'] and c['red_dealbreaker'] == 0][:TOP_CANDIDATES_LIMIT]
    if top_without_insider:
        for company in top_without_insider:
            print(f"   - {company['name']:30} (Green: {company['green_critical']}C/{company['green_strong']}S, Red: {company['red_concerning']}C)")
    else:
        print("   (None)")


if __name__ == "__main__":
    main()
