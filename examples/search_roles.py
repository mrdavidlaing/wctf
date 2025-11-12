#!/usr/bin/env python3
"""Example: Search for open roles at a company.

This shows how to use the roles search workflow:
1. Get the roles extraction prompt (with orgmap integration)
2. Search for roles
3. Save the roles

Usage:
    uv run python examples/search_roles.py "Company Name"
"""

import sys
from wctf_core import WCTFClient


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python examples/search_roles.py 'Company Name'")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    # Get the extraction prompt
    from wctf_core.operations.prompts import get_roles_extraction_prompt

    print(f"=== Roles Extraction Prompt for {company_name} ===\n")
    prompt = get_roles_extraction_prompt(company_name)
    print(prompt)

    print("\n" + "=" * 80)
    print("\nNext steps:")
    print("1. Use the prompt above to search for roles")
    print("2. Extract the YAML with WCTF analysis")
    print("3. Save it with: client.save_roles(company_name, roles_yaml)")

    # Check if roles already exist
    result = client.get_roles(company_name)
    if result['success']:
        print(f"\n✓ Roles already exist for {company_name}")
        print(f"  Total Roles: {result['roles']['total_roles']}")
        print(f"  Mapped: {result['roles']['mapped_roles']}")
        print(f"  Unmapped: {result['roles']['unmapped_count']}")
    else:
        print(f"\n✗ No roles yet for {company_name}")

    # Check if orgmap exists
    orgmap_result = client.get_orgmap(company_name)
    if orgmap_result['success']:
        print(f"\n✓ Orgmap exists - roles can be linked to peaks/teams")
    else:
        print(f"\n⚠ No orgmap - consider running map_organization.py first")


if __name__ == "__main__":
    main()
