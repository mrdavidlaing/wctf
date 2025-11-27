#!/usr/bin/env python3
"""
Research and create organizational map.

Usage: uv run python scripts/map_org.py <company>
"""

import sys
from pathlib import Path

# Add parent directory to path to import wctf_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core import WCTFClient


def print_research_guidance(company_name: str):
    """Print structured research guidance."""
    print(f"\n🏔 Organizational Research for {company_name}")
    print("=" * 50)

    print("\n📋 Research Areas to Investigate:")
    print("   1. Leadership Structure")
    print("      • VP-level executives (SVP, VP) and their domains")
    print("      • Reporting relationships and organizational hierarchy")
    print("      • Leadership tenure and recent changes")

    print("\n   2. Team Organization")
    print("      • Director-level teams and their scope")
    print("      • Team sizes and growth patterns")
    print("      • Geographic distribution and remote work")

    print("\n   3. Technical Focus")
    print("      • Primary technology stacks and platforms")
    print("      • Engineering practices and methodologies")
    print("      • Technical debt and modernization efforts")

    print("\n   4. Coordination Patterns")
    print("      • Meeting cadence and decision-making processes")
    print("      • Cross-team collaboration patterns")
    print("      • Response to incidents and opportunities")

    print("\n🔍 Research Sources:")
    print("   1. Company Website (leadership pages, about us)")
    print("   2. LinkedIn (executives, team structures)")
    print("   3. Press Releases (org announcements, leadership changes)")
    print("   4. Industry Reports (company size, growth trends)")
    print("   5. Your Network (former colleagues, insider contacts)")

    print("\n📝 Data to Extract:")
    print("   • Peak IDs (unique identifiers like 'cloud_services')")
    print("   • Team names and missions")
    print("   • Headcount ranges (format: '40-50' or '800-1000')")
    print("   • Growth trends (expanding, stable, contracting)")
    print("   • Coordination style indicators")
    print("   • Insider connections with contact details")


def read_yaml_input():
    """Read YAML input from user."""
    print("\n📋 Paste organizational data as YAML (Ctrl+D when done):")
    print("   Use the format from /map-org documentation")
    print("   Include all peaks and rope teams discovered")
    print("-" * 50)

    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "":  # Empty line might signal end
                break
            lines.append(line)
    except EOFError:
        pass

    yaml_content = "\n".join(lines)
    if not yaml_content.strip():
        return None

    try:
        import yaml

        # Validate YAML syntax
        yaml.safe_load(yaml_content)
        return yaml_content
    except yaml.YAMLError as e:
        print(f"❌ YAML Error: {e}")
        print("Please fix YAML format and try again")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/map_org.py <company>")
        print("Example: uv run python scripts/map_org.py Apple")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    print(f"🚀 Starting organizational research for {company_name}")
    print("=" * 50)

    # Check for existing orgmap
    existing_result = client.get_orgmap(company_name)
    if existing_result["success"]:
        print(f"📊 Found existing orgmap:")
        orgmap = existing_result["orgmap"]
        print(f"   Peaks: {orgmap['total_peaks']}")
        print(f"   Rope teams: {orgmap['total_rope_teams']}")
        print("\n💡 Consider updating existing data rather than creating new map")

    print_research_guidance(company_name)

    # Get orgmap data from user
    yaml_content = read_yaml_input()

    if yaml_content:
        print(f"\n💾 Saving organizational map for {company_name}...")
        result = client.save_orgmap(company_name, yaml_content)

        if result["success"]:
            orgmap = result["orgmap"]
            print(f"✅ Orgmap saved to: {result['path']}")
            print(f"📊 Summary:")
            print(f"   Company: {orgmap['company']}")
            print(f"   Slug: {orgmap['company_slug']}")
            print(f"   Peaks: {orgmap['total_peaks']}")
            print(f"   Rope teams: {orgmap['total_rope_teams']}")

            if orgmap["total_peaks"] > 0:
                print(f"\n🎯 Next steps:")
                print("   1. Use /search-roles to find open positions")
                print("   2. Map roles to discovered organizational structure")
                print("   3. Reach out to insider connections for referrals")
        else:
            print(f"❌ Error saving orgmap: {result['error']}")
    else:
        print("\n❌ No organizational data provided. Research cancelled.")


if __name__ == "__main__":
    main()
