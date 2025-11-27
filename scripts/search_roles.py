#!/usr/bin/env python3
"""
Search for open roles and map to organizational structure.

Usage: uv run python scripts/search_roles.py <company>
"""

import sys
import yaml
from pathlib import Path

# Add parent directory to path to import wctf_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core import WCTFClient
from wctf_core.utils.paths import get_orgmap_path


def print_search_guidance(company_name: str, orgmap_result: dict):
    """Print structured search guidance based on existing orgmap."""
    print(f"\n🔍 Search Strategy for {company_name}")
    print("=" * 50)

    if orgmap_result["success"]:
        orgmap = orgmap_result["orgmap"]
        print(
            f"📊 Found existing orgmap with {orgmap['total_peaks']} peaks and {orgmap['total_rope_teams']} rope teams"
        )

        print("\n🎯 Targeted Search Approach:")
        for peak in orgmap["peaks"]:
            print(f"\n  🏔 {peak['peak_name']}:")
            print(
                f"     Tech Focus: {', '.join(peak['tech_focus'].get('primary', []))}"
            )
            if peak.get("rope_teams"):
                for team in peak["rope_teams"]:
                    print(
                        f"     👥 {team['team_name']}: {team.get('estimated_size', 'Unknown size')}"
                    )
                    print(f"        Tech: {', '.join(team.get('tech_focus', []))}")

        print("\n💡 Search Keywords by Team:")
        print("   Use team-specific technologies in your searches")
        print("   Target leadership team members on LinkedIn for referrals")

    else:
        print("🗺️ No existing orgmap found - using broad search strategy")
        print("\n🌐 General Search Approach:")
        print("   Search company careers page for all engineering roles")
        print("   Use LinkedIn with company + technology filters")
        print("   Look for patterns in team sizes and tech stacks")

    print("\n📝 Search Sources to Check:")
    print("   1. Company Careers Page (most current)")
    print("   2. LinkedIn (advanced search with filters)")
    print("   3. Employee Referrals (highest conversion)")
    print("   4. Industry Job Boards (AngelList, Otta, etc.)")
    print("   5. Technical Communities (HN, Reddit, Discord)")

    print("\n🔑 Search Optimization Tips:")
    print("   • Use specific technology keywords from orgmap")
    print("   • Filter by appropriate seniority level")
    print("   • Include location preferences (remote/hybrid)")
    print("   • Set up job alerts for targeted roles")
    print("   • Research recent company news for context")


def read_yaml_input():
    """Read YAML input from user."""
    print("\n📋 Paste role data as YAML (Ctrl+D when done):")
    print("   Use the format from /search-roles documentation")
    print("   Include all roles found, mapped or unmapped")
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
        # Validate YAML syntax
        yaml.safe_load(yaml_content)
        return yaml_content
    except yaml.YAMLError as e:
        print(f"❌ YAML Error: {e}")
        print("Please fix YAML format and try again")
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/search_roles.py <company>")
        print("Example: uv run python scripts/search_roles.py Apple")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    print(f"🚀 Starting role search for {company_name}")
    print("=" * 50)

    # Check for existing orgmap
    orgmap_result = client.get_orgmap(company_name)
    print_search_guidance(company_name, orgmap_result)

    # Get role data from user
    yaml_content = read_yaml_input()

    if yaml_content:
        print(f"\n💾 Saving role data for {company_name}...")
        result = client.save_roles(company_name, yaml_content)

        if result["success"]:
            roles = result["roles"]
            print(f"✅ Roles saved to: {result['path']}")
            print(f"📊 Summary:")
            print(f"   Total roles: {roles['total_roles']}")
            print(f"   Mapped roles: {roles['mapped_roles']}")
            print(f"   Unmapped roles: {roles['unmapped_count']}")

            if roles["unmapped_count"] > 0:
                print(f"\n⚠️  Found {roles['unmapped_count']} unmapped roles")
                print("   Consider updating orgmap with: /map-org command")
                print("   New teams may indicate organizational changes")

            if roles["mapped_roles"] > 0:
                print(
                    f"\n🎯 Successfully mapped {roles['mapped_roles']} roles to existing org structure"
                )

        else:
            print(f"❌ Error saving roles: {result['error']}")
    else:
        print("\n❌ No role data provided. Search cancelled.")


if __name__ == "__main__":
    main()
