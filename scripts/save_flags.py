#!/usr/bin/env python3
"""Save extracted flags for a company.

Reads flags YAML from stdin and saves to company.flags.yaml.

Usage:
    # From file
    uv run python scripts/save_flags.py "Company Name" < flags.yaml

    # From heredoc
    uv run python scripts/save_flags.py "Company Name" << 'EOF'
    company: "Company Name"
    evaluation_date: "2025-10-18"
    ...
    EOF
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core import WCTFClient


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/save_flags.py \"Company Name\" < flags.yaml")
        print("\nReads flags YAML from stdin and saves to company.flags.yaml")
        print("\nExample:")
        print("  uv run python scripts/save_flags.py \"Stripe\" << 'EOF'")
        print("  company: \"Stripe\"")
        print("  evaluation_date: \"2025-10-18\"")
        print("  ...")
        print("  EOF")
        sys.exit(1)

    company_name = sys.argv[1]
    client = WCTFClient()

    # Check if company exists
    if not client.company_exists(company_name):
        print(f"ERROR: Company '{company_name}' not found.", file=sys.stderr)
        sys.exit(1)

    # Read YAML from stdin
    print(f"Reading flags YAML from stdin for '{company_name}'...", file=sys.stderr)
    print("(Paste YAML and press Ctrl+D when done, or pipe from file/heredoc)", file=sys.stderr)

    yaml_content = sys.stdin.read()

    if not yaml_content.strip():
        print("ERROR: No YAML content provided.", file=sys.stderr)
        sys.exit(1)

    # Save flags
    result = client.save_flags(company_name, yaml_content)

    if result['success']:
        print(f"\n✓ Successfully saved flags for {company_name}", file=sys.stderr)
        if 'file_path' in result:
            print(f"  File: {result['file_path']}", file=sys.stderr)
    else:
        print(f"\nERROR: Failed to save flags: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
