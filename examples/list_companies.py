#!/usr/bin/env python3
"""List all companies in the WCTF database.

Usage:
    uv run python examples/list_companies.py
"""

from wctf_core import WCTFClient


def main():
    """List all companies with their data availability status."""
    client = WCTFClient()

    companies = client.list_companies()

    if not companies:
        print("No companies found in the database.")
        return

    print(f"Found {len(companies)} companies:\n")

    for company in companies:
        name = company["name"]
        has_facts = "✓" if company.get("has_facts") else "✗"
        has_flags = "✓" if company.get("has_flags") else "✗"

        print(f"  {name}")
        print(f"    Facts: {has_facts}  Flags: {has_flags}")


if __name__ == "__main__":
    main()
