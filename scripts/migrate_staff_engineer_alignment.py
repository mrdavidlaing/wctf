#!/usr/bin/env python3
"""Migrate company.flags.yaml files from senior_engineer_alignment to staff_engineer_alignment.

This script updates the field name in all company.flags.yaml files to reflect
the terminology change from "senior engineer" to "staff engineer".

Usage:
    uv run python scripts/migrate_staff_engineer_alignment.py [--dry-run] [--data-dir PATH]

Options:
    --dry-run    Show what would be changed without making modifications
    --data-dir   Specify data directory (defaults to ./data)
"""

import argparse
import sys
from pathlib import Path

import yaml


def find_flags_files(data_dir: Path) -> list[Path]:
    """Find all company.flags.yaml files in the data directory."""
    return list(data_dir.glob("*/company.flags.yaml"))


def migrate_file(file_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Migrate a single flags file.

    Returns:
        (changed, message) tuple where changed is True if file needed migration
    """
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if migration is needed
        if 'senior_engineer_alignment' not in content:
            return False, f"Skipped (already migrated or field not present)"

        # Perform the replacement
        new_content = content.replace(
            'senior_engineer_alignment',
            'staff_engineer_alignment'
        )

        if dry_run:
            return True, "Would migrate (dry-run)"

        # Validate YAML structure before writing
        try:
            yaml.safe_load(new_content)
        except yaml.YAMLError as e:
            return False, f"Error: Invalid YAML after migration: {e}"

        # Write the migrated content
        with open(file_path, 'w') as f:
            f.write(new_content)

        return True, "Migrated successfully"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Run the migration."""
    parser = argparse.ArgumentParser(
        description="Migrate company.flags.yaml files to use staff_engineer_alignment"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making modifications'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path('./data'),
        help='Data directory containing company folders (default: ./data)'
    )

    args = parser.parse_args()

    # Validate data directory
    if not args.data_dir.exists():
        print(f"Error: Data directory not found: {args.data_dir}")
        sys.exit(1)

    # Find all flags files
    flags_files = find_flags_files(args.data_dir)

    if not flags_files:
        print(f"No company.flags.yaml files found in {args.data_dir}")
        sys.exit(0)

    print(f"Found {len(flags_files)} flags files")
    if args.dry_run:
        print("Running in DRY-RUN mode - no files will be modified\n")
    else:
        print()

    # Migrate each file
    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in sorted(flags_files):
        company_dir = file_path.parent.name
        changed, message = migrate_file(file_path, dry_run=args.dry_run)

        status_symbol = "✓" if changed else "○"
        if "Error" in message:
            status_symbol = "✗"
            error_count += 1
        elif changed:
            migrated_count += 1
        else:
            skipped_count += 1

        print(f"{status_symbol} {company_dir:30s} {message}")

    # Summary
    print("\n" + "="*60)
    print(f"Summary:")
    print(f"  Migrated: {migrated_count}")
    print(f"  Skipped:  {skipped_count}")
    print(f"  Errors:   {error_count}")

    if args.dry_run and migrated_count > 0:
        print(f"\nRun without --dry-run to apply changes")
    elif not args.dry_run and migrated_count > 0:
        print(f"\n✓ Migration completed successfully")

    sys.exit(0 if error_count == 0 else 1)


if __name__ == "__main__":
    main()
