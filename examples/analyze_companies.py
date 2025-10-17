#!/usr/bin/env python3
"""Analyze companies that need evaluation.

This script finds companies that have facts but no flags,
suggesting they need evaluation.

Usage:
    uv run python examples/analyze_companies.py
"""

from wctf_core import WCTFClient


def main():
    """Find and analyze companies needing evaluation."""
    client = WCTFClient()

    # Get all companies
    companies = client.list_companies()

    # Filter for those needing evaluation
    needs_facts = []
    needs_flags = []
    complete = []

    for company in companies:
        name = company["name"]
        has_facts = company.get("has_facts", False)
        has_flags = company.get("has_flags", False)

        if not has_facts and not has_flags:
            needs_facts.append(name)
        elif has_facts and not has_flags:
            needs_flags.append(name)
        elif has_facts and has_flags:
            complete.append(name)

    # Print summary
    print("=" * 80)
    print("COMPANY EVALUATION STATUS")
    print("=" * 80)
    print()

    print(f"✓ Complete (facts + flags): {len(complete)}")
    if complete:
        for name in complete:
            print(f"    - {name}")
    print()

    print(f"⚠ Needs Evaluation (has facts, no flags): {len(needs_flags)}")
    if needs_flags:
        for name in needs_flags:
            print(f"    - {name}")
    print()

    print(f"✗ Needs Research (no facts): {len(needs_facts)}")
    if needs_facts:
        for name in needs_facts:
            print(f"    - {name}")
    print()

    # Get evaluation summary if there are any complete evaluations
    if complete:
        print("=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        result = client.get_evaluation_summary()
        if result.get("success"):
            print(result["summary_table"])


if __name__ == "__main__":
    main()
