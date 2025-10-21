#!/usr/bin/env python3
"""
Migrate existing company directories to stage-based structure.

This script moves all existing companies from data/* to data/stage-1/*.
It also creates empty stage-2 and stage-3 directories for future use.

Run this script once to migrate from the old flat structure to the new
stage-based structure.
"""

import sys
from pathlib import Path

# Add parent directory to path to import wctf_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core.utils.paths import get_data_dir, get_stage_dir


def migrate_to_stages(base_path: Path = None, dry_run: bool = False) -> None:
    """Migrate companies from flat structure to stage-based structure.

    Args:
        base_path: Optional base path. If not provided, uses project root.
        dry_run: If True, show what would be done without actually doing it.
    """
    data_dir = get_data_dir(base_path)

    if not data_dir.exists():
        print(f"Data directory {data_dir} does not exist. Nothing to migrate.")
        return

    # Check if already migrated
    existing_stages = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith("stage-")]
    if existing_stages:
        print(f"Found existing stage directories: {[d.name for d in existing_stages]}")
        response = input("Migration may have already been run. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return

    # Find all company directories (non-stage directories)
    company_dirs = [
        d for d in data_dir.iterdir()
        if d.is_dir() and not d.name.startswith("stage-")
    ]

    if not company_dirs:
        print("No company directories found to migrate.")
    else:
        print(f"Found {len(company_dirs)} companies to migrate:")
        for d in sorted(company_dirs):
            print(f"  - {d.name}")

    # Create stage directories
    print("\nCreating stage directories...")
    for stage_num in [1, 2, 3]:
        stage_dir = get_stage_dir(stage_num, base_path)
        if dry_run:
            print(f"  [DRY RUN] Would create {stage_dir}")
        else:
            stage_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Created {stage_dir}")

    # Move companies to stage-1
    if company_dirs:
        print(f"\nMoving {len(company_dirs)} companies to stage-1...")
        stage_1_dir = get_stage_dir(1, base_path)

        for company_dir in sorted(company_dirs):
            target_dir = stage_1_dir / company_dir.name

            if dry_run:
                print(f"  [DRY RUN] Would move {company_dir} -> {target_dir}")
            else:
                try:
                    company_dir.rename(target_dir)
                    print(f"  Moved {company_dir.name}")
                except Exception as e:
                    print(f"  ERROR moving {company_dir.name}: {e}")

    print("\nMigration complete!")
    if dry_run:
        print("\nThis was a DRY RUN. No changes were made.")
        print("Run without --dry-run to perform the actual migration.")


def main():
    """Main entry point for the migration script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate company directories to stage-based structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        help="Optional base path (defaults to project root)",
    )

    args = parser.parse_args()

    migrate_to_stages(base_path=args.base_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
