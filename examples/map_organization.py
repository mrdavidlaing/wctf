#!/usr/bin/env python3
"""Example: Map organization structure for a company.

This shows how to use the orgmap extraction workflow:
1. Get the extraction prompt
2. Research the company
3. Save the orgmap

Usage:
    uv run python examples/map_organization.py "Company Name"
"""

import sys
from wctf_core import WCTFClient


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python examples/map_organization.py 'Company Name'")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    # Get the extraction prompt
    from wctf_core.operations.prompts import get_orgmap_extraction_prompt

    print(f"=== Orgmap Extraction Prompt for {company_name} ===\n")
    prompt = get_orgmap_extraction_prompt(company_name)
    print(prompt)

    print("\n" + "=" * 80)
    print("\nNext steps:")
    print("1. Use the prompt above to research the company")
    print("2. Extract the YAML from your research")
    print("3. Save it with: client.save_orgmap(company_name, orgmap_yaml)")

    # Check if orgmap already exists
    result = client.get_orgmap(company_name)
    if result['success']:
        print(f"\n✓ Orgmap already exists for {company_name}")
        print(f"  Peaks: {result['orgmap']['total_peaks']}")
        print(f"  Rope Teams: {result['orgmap']['total_rope_teams']}")
    else:
        print(f"\n✗ No orgmap yet for {company_name}")


if __name__ == "__main__":
    main()
