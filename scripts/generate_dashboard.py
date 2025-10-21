#!/usr/bin/env python3
"""
Generate an HTML dashboard showing job search pipeline progress.

This script creates a static HTML page (data/dashboard.html) that shows:
- Pipeline progress counts (Stage 1, 2, 3)
- Per-stage tables with company metrics
- Fact counts, flag counts, insider interview counts
- Sorted by evaluation date (most recent first)
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path to import wctf_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core.utils.paths import (
    get_data_dir,
    get_stage_dir,
    list_all_companies_by_stage,
    get_facts_path,
    get_flags_path,
    get_insider_facts_path,
)
from wctf_core.utils.yaml_handler import read_yaml


def get_company_metrics(company_slug: str, stage: int, base_path: Optional[Path] = None) -> Dict[str, Any]:
    """Extract metrics for a single company.

    Args:
        company_slug: Slugified company name (directory name)
        stage: Stage number where company is located
        base_path: Optional base path

    Returns:
        Dictionary with company metrics
    """
    metrics = {
        "company_slug": company_slug,
        "company_name": company_slug,  # Will be replaced if we can read the YAML
        "stage": stage,
        "evaluation_date": None,
        "fact_count": 0,
        "green_flags": 0,
        "red_flags": 0,
        "insider_interviews": 0,
        "mountain_worth_climbing": "N/A",
    }

    try:
        # Try to read facts
        facts_path = get_facts_path(company_slug, stage=stage, base_path=base_path)
        if facts_path.exists():
            facts_data = read_yaml(facts_path)
            metrics["company_name"] = facts_data.get("company", company_slug)
            summary = facts_data.get("summary", {})
            metrics["fact_count"] = summary.get("total_facts_found", 0)
    except Exception as e:
        print(f"Warning: Could not read facts for {company_slug}: {e}")

    try:
        # Try to read flags
        flags_path = get_flags_path(company_slug, stage=stage, base_path=base_path)
        if flags_path.exists():
            flags_data = read_yaml(flags_path)

            # Get evaluation date
            eval_date = flags_data.get("evaluation_date")
            if eval_date:
                metrics["evaluation_date"] = eval_date

            # Count green flags
            green_flags = flags_data.get("green_flags", {})
            critical_matches = green_flags.get("critical_matches", [])
            strong_positives = green_flags.get("strong_positives", [])
            metrics["green_flags"] = len(critical_matches) + len(strong_positives)

            # Count red flags
            red_flags = flags_data.get("red_flags", {})
            dealbreakers = red_flags.get("dealbreakers", [])
            concerning = red_flags.get("concerning", [])
            metrics["red_flags"] = len(dealbreakers) + len(concerning)

            # Get mountain worth climbing
            synthesis = flags_data.get("synthesis", {})
            metrics["mountain_worth_climbing"] = synthesis.get("mountain_worth_climbing", "N/A")
    except Exception as e:
        print(f"Warning: Could not read flags for {company_slug}: {e}")

    try:
        # Try to read insider facts
        insider_path = get_insider_facts_path(company_slug, stage=stage, base_path=base_path)
        if insider_path.exists():
            insider_data = read_yaml(insider_path)
            summary = insider_data.get("summary", {})
            metrics["insider_interviews"] = summary.get("total_interviews", 0)
    except Exception as e:
        print(f"Warning: Could not read insider facts for {company_slug}: {e}")

    return metrics


def generate_html_dashboard(base_path: Optional[Path] = None) -> str:
    """Generate HTML dashboard content.

    Args:
        base_path: Optional base path

    Returns:
        HTML content as string
    """
    # Get all companies by stage
    companies_by_stage = list_all_companies_by_stage(base_path=base_path)

    # Organize companies by stage
    stage_data: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: []}

    for stage, company_slug in companies_by_stage:
        if stage in stage_data:
            metrics = get_company_metrics(company_slug, stage, base_path=base_path)
            stage_data[stage].append(metrics)

    # Sort each stage by evaluation date (most recent first)
    for stage in stage_data:
        stage_data[stage].sort(
            key=lambda x: str(x["evaluation_date"]) if x["evaluation_date"] else "0000-00-00",
            reverse=True
        )

    # Calculate pipeline progress
    stage_1_count = len(stage_data[1])
    stage_2_count = len(stage_data[2])
    stage_3_count = len(stage_data[3])

    stage_1_target = 100
    stage_2_target = 25
    stage_3_target = 5

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WCTF Job Search Pipeline Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .pipeline-progress {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .stage-card {{
            flex: 1;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stage-card h3 {{
            margin-top: 0;
            color: #007bff;
        }}
        .stage-card .count {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .stage-card .target {{
            color: #666;
            font-size: 0.9em;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #28a745;
            transition: width 0.3s ease;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        th {{
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-yes {{
            background-color: #d4edda;
            color: #155724;
        }}
        .badge-maybe {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .badge-no {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .badge-na {{
            background-color: #e9ecef;
            color: #6c757d;
        }}
        .metric {{
            text-align: center;
            font-weight: 600;
        }}
        .generated-date {{
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            text-align: right;
        }}
        .empty-stage {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}
        th.sortable {{
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        th.sortable:hover {{
            background-color: #0056b3;
        }}
        th.sortable::after {{
            content: ' ↕';
            opacity: 0.5;
            font-size: 0.8em;
        }}
        th.sorted-asc::after {{
            content: ' ↑';
            opacity: 1;
        }}
        th.sorted-desc::after {{
            content: ' ↓';
            opacity: 1;
        }}
    </style>
</head>
<body>
    <h1>WCTF Job Search Pipeline Dashboard</h1>

    <div class="pipeline-progress">
        <div class="stage-card">
            <h3>Stage 1: Researched & Evaluated</h3>
            <div class="count">{stage_1_count} / {stage_1_target}</div>
            <div class="target">Target: {stage_1_target} companies</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(100, (stage_1_count / stage_1_target) * 100)}%"></div>
            </div>
        </div>

        <div class="stage-card">
            <h3>Stage 2: Insider Interviews</h3>
            <div class="count">{stage_2_count} / {stage_2_target}</div>
            <div class="target">Target: {stage_2_target} companies</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(100, (stage_2_count / stage_2_target) * 100) if stage_2_target > 0 else 0}%"></div>
            </div>
        </div>

        <div class="stage-card">
            <h3>Stage 3: Applications</h3>
            <div class="count">{stage_3_count} / {stage_3_target}</div>
            <div class="target">Target: {stage_3_target} companies</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(100, (stage_3_count / stage_3_target) * 100) if stage_3_target > 0 else 0}%"></div>
            </div>
        </div>
    </div>
"""

    # Generate tables for each stage
    for stage_num in [1, 2, 3]:
        stage_name = {
            1: "Stage 1: Researched & Evaluated",
            2: "Stage 2: Insider Interviews",
            3: "Stage 3: Applications"
        }[stage_num]

        html += f"\n    <h2>{stage_name}</h2>\n"

        companies = stage_data[stage_num]

        if not companies:
            html += '    <div class="empty-stage">No companies in this stage yet</div>\n'
            continue

        html += f"""    <table class="sortable-table" id="stage-{stage_num}-table">
        <thead>
            <tr>
                <th class="sortable" data-column="company" data-type="text">Company</th>
                <th class="sortable sorted-desc" data-column="eval_date" data-type="date">Evaluation Date</th>
                <th class="sortable metric" data-column="facts" data-type="number">Facts</th>
                <th class="sortable metric" data-column="green_flags" data-type="number">Green Flags</th>
                <th class="sortable metric" data-column="red_flags" data-type="number">Red Flags</th>
                <th class="sortable metric" data-column="interviews" data-type="number">Insider Interviews</th>
                <th class="sortable" data-column="worth_climbing" data-type="text">Worth Climbing?</th>
            </tr>
        </thead>
        <tbody>
"""

        for company in companies:
            # Determine badge class for mountain_worth_climbing
            mwc = company["mountain_worth_climbing"]
            badge_class = {
                "YES": "badge-yes",
                "MAYBE": "badge-maybe",
                "NO": "badge-no",
            }.get(mwc, "badge-na")

            eval_date = company["evaluation_date"] or "N/A"

            html += f"""            <tr>
                <td><strong>{company["company_name"]}</strong></td>
                <td>{eval_date}</td>
                <td class="metric">{company["fact_count"]}</td>
                <td class="metric">{company["green_flags"]}</td>
                <td class="metric">{company["red_flags"]}</td>
                <td class="metric">{company["insider_interviews"]}</td>
                <td><span class="badge {badge_class}">{mwc}</span></td>
            </tr>
"""

        html += """        </tbody>
    </table>
"""

    # Add generation timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html += f"""
    <div class="generated-date">
        Generated: {now}
    </div>

    <script>
    // Table sorting functionality
    document.querySelectorAll('.sortable').forEach(header => {{
        header.addEventListener('click', function() {{
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentElement.children).indexOf(this);
            const columnType = this.dataset.type;
            const currentSort = this.classList.contains('sorted-asc') ? 'asc' :
                               this.classList.contains('sorted-desc') ? 'desc' : 'none';

            // Remove sorting indicators from all headers in this table
            table.querySelectorAll('th').forEach(th => {{
                th.classList.remove('sorted-asc', 'sorted-desc');
            }});

            // Determine new sort direction
            const newSort = currentSort === 'none' ? 'asc' :
                           currentSort === 'asc' ? 'desc' : 'asc';

            // Add sorting indicator to clicked header
            this.classList.add(newSort === 'asc' ? 'sorted-asc' : 'sorted-desc');

            // Sort rows
            rows.sort((a, b) => {{
                const aCell = a.children[columnIndex];
                const bCell = b.children[columnIndex];
                let aValue = aCell.textContent.trim();
                let bValue = bCell.textContent.trim();

                // Handle different data types
                if (columnType === 'number') {{
                    aValue = parseInt(aValue) || 0;
                    bValue = parseInt(bValue) || 0;
                }} else if (columnType === 'date') {{
                    aValue = aValue === 'N/A' ? '0000-00-00' : aValue;
                    bValue = bValue === 'N/A' ? '0000-00-00' : bValue;
                }}

                // Compare values
                if (aValue < bValue) return newSort === 'asc' ? -1 : 1;
                if (aValue > bValue) return newSort === 'asc' ? 1 : -1;
                return 0;
            }});

            // Reorder table rows
            rows.forEach(row => tbody.appendChild(row));
        }});
    }});
    </script>
</body>
</html>
"""

    return html


def main():
    """Main entry point for dashboard generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate HTML dashboard for job search pipeline"
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        help="Optional base path (defaults to project root)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (defaults to data/dashboard.html)",
    )

    args = parser.parse_args()

    # Generate HTML
    print("Generating dashboard...")
    html_content = generate_html_dashboard(base_path=args.base_path)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        data_dir = get_data_dir(base_path=args.base_path)
        output_path = data_dir / "dashboard.html"

    # Write HTML file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")

    print(f"Dashboard generated: {output_path}")
    print(f"Open in browser: file://{output_path.absolute()}")


if __name__ == "__main__":
    main()
