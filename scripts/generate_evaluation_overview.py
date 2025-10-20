#!/usr/bin/env python3
"""Generate evaluation overview to share with insider interview contacts.

Usage:
    uv run python scripts/generate_evaluation_overview.py <company-slug>

Example:
    uv run python scripts/generate_evaluation_overview.py workday
"""

import sys
from datetime import datetime
from pathlib import Path
import yaml


def load_company_data(company_slug: str) -> tuple[dict, dict]:
    """Load facts and flags for a company."""
    data_dir = Path("data") / company_slug

    facts_path = data_dir / "company.facts.yaml"
    flags_path = data_dir / "company.flags.yaml"

    if not facts_path.exists():
        raise FileNotFoundError(f"Facts file not found: {facts_path}")
    if not flags_path.exists():
        raise FileNotFoundError(f"Flags file not found: {flags_path}")

    with open(facts_path) as f:
        facts = yaml.safe_load(f)

    with open(flags_path) as f:
        flags = yaml.safe_load(f)

    return facts, flags


def build_dimension_summary(dimension_name: str, facts_section: dict, flags_section: dict, missing_data: list) -> dict:
    """Build summary for one WCTF dimension."""
    facts_found = facts_section.get("facts_found", [])[:5]  # Top 5 facts
    green_flags = []
    red_flags = []

    if flags_section:
        green_flags = (flags_section.get("critical_matches", []) +
                      flags_section.get("strong_positives", []))[:4]
        red_flags = (flags_section.get("dealbreakers", []) +
                    flags_section.get("concerning", []))[:4]

    # Find missing data for this dimension
    dimension_gaps = [item for item in missing_data
                     if item.get("mountain_element", "").replace("_", " ") in dimension_name.lower()]

    return {
        "facts": facts_found,
        "green_flags": green_flags,
        "red_flags": red_flags,
        "gaps": dimension_gaps[:3]  # Top 3 gaps
    }


def generate_html(company_name: str, facts: dict, flags: dict) -> str:
    """Generate complete HTML evaluation overview."""

    # Reference ID mappings
    dimension_codes = {
        "Mountain Range": "MR",
        "Chosen Peak": "CP",
        "Rope Team Confidence": "RT",
        "Daily Climb": "DC",
        "Story Worth Telling": "ST"
    }

    subsection_codes = {
        "facts": "F",
        "green": "G",
        "red": "R",
        "validate": "V"
    }

    # Extract evaluation context
    evaluator_context = flags.get("evaluator_context", "Senior Engineer evaluating opportunities")
    research_date = facts.get("research_date", "Unknown")
    eval_date = flags.get("evaluation_date", datetime.now().strftime("%Y-%m-%d"))

    # Get missing critical data
    missing_data = flags.get("missing_critical_data", [])

    # Build dimension summaries
    dimensions = {
        "Mountain Range": {
            "description": "Business Viability & Financial Health",
            "facts": facts.get("financial_health", {}),
            "market": facts.get("market_position", {}),
            "flags": flags.get("green_flags", {}).get("mountain_range", {})
        },
        "Chosen Peak": {
            "description": "Strategic Alignment & Coordination Fit",
            "facts": facts.get("technical_culture", {}),
            "flags": flags.get("green_flags", {}).get("chosen_peak", {})
        },
        "Rope Team Confidence": {
            "description": "Leadership & Team Trust",
            "facts": facts.get("organizational_stability", {}),
            "flags": flags.get("green_flags", {}).get("rope_team_confidence", {})
        },
        "Daily Climb": {
            "description": "Day-to-Day Experience",
            "facts": facts.get("organizational_stability", {}),
            "flags": flags.get("green_flags", {}).get("daily_climb", {})
        },
        "Story Worth Telling": {
            "description": "Career Narrative & Impact",
            "facts": facts.get("market_position", {}),
            "flags": flags.get("green_flags", {}).get("story_worth_telling", {})
        }
    }

    # Build dimension HTML sections
    dimension_html = ""
    for dim_name, dim_data in dimensions.items():
        # Get dimension code
        dim_code = dimension_codes.get(dim_name, "XX")

        facts_list = dim_data["facts"].get("facts_found", [])[:3]
        green_flags = (dim_data["flags"].get("critical_matches", []) +
                      dim_data["flags"].get("strong_positives", []))[:3]

        # Get red flags for this dimension
        red_flag_section = flags.get("red_flags", {}).get(
            dim_name.lower().replace(" ", "_").replace("rope_team", "rope_team"), {})
        red_flags = (red_flag_section.get("dealbreakers", []) +
                    red_flag_section.get("concerning", []))[:2]

        # Get gaps for this dimension
        dim_gaps = [item for item in missing_data
                   if dim_name.lower() in item.get("mountain_element", "").lower().replace("_", " ")][:2]

        facts_html = ""
        for i, fact in enumerate(facts_list, 1):
            fact_text = fact.get("fact", "")
            confidence_raw = fact.get("confidence", "unknown")
            # Map fact confidence to HIGH/MEDIUM/LOW
            if confidence_raw == "explicit_statement":
                confidence_level = "HIGH"
                confidence_badge = '<span class="confidence-high">HIGH</span>'
            elif confidence_raw == "implied":
                confidence_level = "MEDIUM"
                confidence_badge = '<span class="confidence-medium">MEDIUM</span>'
            else:
                confidence_level = "MEDIUM"
                confidence_badge = '<span class="confidence-medium">MEDIUM</span>'
            ref_id = f"{dim_code}-{subsection_codes['facts']}{i}"
            facts_html += f"        <li><strong>[{ref_id}]</strong> {fact_text} {confidence_badge}</li>\n"

        green_html = ""
        for i, flag in enumerate(green_flags, 1):
            flag_text = flag.get("flag", "")
            confidence_raw = flag.get("confidence", "")
            # Parse confidence from flags (format: "High - description" or "Medium - description" or "Low - description")
            if confidence_raw.startswith("High"):
                confidence_badge = '<span class="confidence-high">HIGH</span>'
            elif confidence_raw.startswith("Medium"):
                confidence_badge = '<span class="confidence-medium">MEDIUM</span>'
            elif confidence_raw.startswith("Low"):
                confidence_badge = '<span class="confidence-low">LOW</span>'
            else:
                confidence_badge = '<span class="confidence-medium">MEDIUM</span>'
            ref_id = f"{dim_code}-{subsection_codes['green']}{i}"
            green_html += f"        <li><strong>[{ref_id}]</strong> {flag_text} {confidence_badge}</li>\n"

        red_html = ""
        for i, flag in enumerate(red_flags, 1):
            flag_text = flag.get("flag", "")
            confidence_raw = flag.get("confidence", "")
            # Parse confidence from flags (format: "High - description" or "Medium - description" or "Low - description")
            if confidence_raw.startswith("High"):
                confidence_badge = '<span class="confidence-high">HIGH</span>'
            elif confidence_raw.startswith("Medium"):
                confidence_badge = '<span class="confidence-medium">MEDIUM</span>'
            elif confidence_raw.startswith("Low"):
                confidence_badge = '<span class="confidence-low">LOW</span>'
            else:
                confidence_badge = '<span class="confidence-medium">MEDIUM</span>'
            ref_id = f"{dim_code}-{subsection_codes['red']}{i}"
            red_html += f"        <li><strong>[{ref_id}]</strong> {flag_text} {confidence_badge}</li>\n"

        gaps_html = ""
        for i, gap in enumerate(dim_gaps, 1):
            question = gap.get("question", "")
            why = gap.get("why_important", "")
            # Validation items are implicitly LOW confidence (need insider validation)
            confidence_badge = '<span class="confidence-low">LOW</span>'
            ref_id = f"{dim_code}-{subsection_codes['validate']}{i}"
            gaps_html += f"        <li><strong>[{ref_id}]</strong> {question} {confidence_badge}<br><em>{why}</em></li>\n"

        dimension_html += f"""
        <h2>[{dim_code}] {dim_name}: {dim_data['description']}</h2>

        <h3>[{dim_code}-{subsection_codes['facts']}] ✅ What I've Found</h3>
        <ul>
{facts_html if facts_html else "            <li><em>Limited public information available</em></li>\n"}
        </ul>

        <h3>[{dim_code}-{subsection_codes['green']}] 🟢 Green Flags</h3>
        <ul>
{green_html if green_html else "            <li><em>None identified yet</em></li>\n"}
        </ul>

        <h3>[{dim_code}-{subsection_codes['red']}] 🚩 Red Flags</h3>
        <ul>
{red_html if red_html else "            <li><em>None identified yet</em></li>\n"}
        </ul>

        <h3>[{dim_code}-{subsection_codes['validate']}] 🔍 Need to Validate</h3>
        <ul>
{gaps_html if gaps_html else "            <li><em>No specific gaps identified</em></li>\n"}
        </ul>

        <hr>
"""

    # Priority checklist
    priority_html = ""
    for i, item in enumerate(missing_data[:8], 1):
        priority_html += f"""            <li><strong>[P{i}]</strong> {item.get('question', '')}</li>\n"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} Evaluation Overview - WCTF</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 1.5cm 1.2cm;
            }}
            body {{ font-size: 9pt; }}
            h1 {{ font-size: 16pt; }}
            h2 {{ font-size: 11pt; page-break-after: avoid; }}
            h3 {{ font-size: 10pt; page-break-after: avoid; }}
        }}

        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            font-size: 10pt;
            line-height: 1.35;
            color: #333;
            max-width: 21cm;
            margin: 0 auto;
            padding: 1cm;
            background-color: #f5f5f5;
        }}

        .page {{
            background-color: white;
            padding: 1.5cm 1.2cm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}

        h1 {{
            font-size: 18pt;
            font-weight: bold;
            margin-top: 0;
            margin-bottom: 0.2cm;
            border-bottom: 2px solid #333;
            padding-bottom: 0.2cm;
            color: #000;
        }}

        h2 {{
            font-size: 13pt;
            font-weight: bold;
            margin-top: 0.6cm;
            margin-bottom: 0.2cm;
            color: #000;
            page-break-after: avoid;
            background-color: #e8e8e8;
            padding: 0.2cm 0.3cm;
            border-left: 4px solid #333;
        }}

        h3 {{
            font-size: 10pt;
            font-weight: bold;
            margin-top: 0.4cm;
            margin-bottom: 0.15cm;
            color: #222;
            page-break-after: avoid;
        }}

        p {{ margin: 0.15cm 0; }}

        ul, ol {{
            margin: 0.2cm 0;
            padding-left: 1cm;
        }}

        li {{
            margin: 0.08cm 0;
            page-break-inside: avoid;
        }}

        li strong:first-child {{
            color: #0066cc;
            font-size: 9pt;
            margin-right: 0.2cm;
            font-family: 'Courier New', monospace;
        }}

        @media print {{
            li strong:first-child {{
                color: #333;
            }}
        }}

        .confidence-high {{
            background-color: #d4edda;
            color: #155724;
            padding: 0.05cm 0.15cm;
            border-radius: 3px;
            font-size: 8pt;
            font-weight: bold;
            margin-left: 0.2cm;
        }}

        .confidence-medium {{
            background-color: #fff3cd;
            color: #856404;
            padding: 0.05cm 0.15cm;
            border-radius: 3px;
            font-size: 8pt;
            font-weight: bold;
            margin-left: 0.2cm;
        }}

        .confidence-low {{
            background-color: #f8d7da;
            color: #721c24;
            padding: 0.05cm 0.15cm;
            border-radius: 3px;
            font-size: 8pt;
            font-weight: bold;
            margin-left: 0.2cm;
        }}

        @media print {{
            .confidence-high {{
                background-color: #e8e8e8;
                color: #000;
                border: 1px solid #155724;
            }}
            .confidence-medium {{
                background-color: #e8e8e8;
                color: #000;
                border: 1px solid #856404;
            }}
            .confidence-low {{
                background-color: #e8e8e8;
                color: #000;
                border: 1px solid #721c24;
            }}
        }}

        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 0.4cm 0;
        }}

        .framework-box {{
            background-color: #f0f8ff;
            border: 2px solid #4682b4;
            padding: 0.4cm;
            margin: 0.4cm 0;
        }}

        .priority-box {{
            background-color: #fffacd;
            border: 2px solid #ffd700;
            padding: 0.4cm;
            margin: 0.4cm 0;
        }}

        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14pt;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
        }}

        .print-button:hover {{ background-color: #45a049; }}

        @media print {{
            .print-button {{ display: none; }}
            .page {{ box-shadow: none; padding: 0; }}
            body {{ background-color: white; padding: 0; }}
        }}

        .metadata {{
            font-size: 10pt;
            color: #666;
            font-style: italic;
            margin-bottom: 0.5cm;
        }}
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">🖨️ Print to PDF</button>
    <div class="page">
        <h1>{company_name} Evaluation Overview</h1>
        <p class="metadata">
            <strong>Framework:</strong> Worth Climbing Together Framework (WCTF) v3.1<br>
            <strong>Evaluator Context:</strong> {evaluator_context}<br>
            <strong>Research Date:</strong> {research_date} | <strong>Evaluation Date:</strong> {eval_date}
        </p>

        <hr>

        <div class="framework-box">
            <h2 style="margin-top: 0; background: none; padding: 0; border: none;">The WCTF Framework</h2>
            <p><strong>Worth Climbing Together Framework (WCTF)</strong> treats job evaluation like planning a mountain expedition. Every job opportunity is a mountain to climb, and success requires more than just a viable business - you need the right peak, the right team, sustainable conditions, and a story worth telling.</p>

            <p><strong>The Mountain Metaphor - Five Dimensions:</strong></p>
            <ol>
                <li><strong>Mountain Range</strong> - Can <em>any</em> team succeed here? (Business viability, market position, financial health)</li>
                <li><strong>Chosen Peak</strong> - Is everyone climbing the <em>same</em> mountain? (Technical strategy, engineering culture, alignment, <strong>coordination style matches terrain demands</strong> ← NEW v3.1)</li>
                <li><strong>Rope Team Confidence</strong> - Does the team believe they can succeed <em>together</em>? (Leadership trust, team quality, organizational stability)</li>
                <li><strong>Daily Climb</strong> - Will the 99 days be energizing or draining? (Work-life balance, compensation, daily sustainability)</li>
                <li><strong>Story Worth Telling</strong> - Would you be proud to explain this work? (Career narrative, impact, skills growth)</li>
            </ol>

            <p><strong>Two-Layer Investigation:</strong></p>
            <ul style="margin-top: 0.3cm;">
                <li><strong>Layer 1 (Public Research):</strong> Automated research on financials, market position, organizational news, technical culture - creates baseline understanding and surfaces obvious red flags.</li>
                <li><strong>Layer 2 (Insider Conversations):</strong> Conversations with current/former employees to validate Layer 1 findings, understand ground truth vs PR, and surface cultural nuances.</li>
            </ul>

            <p><strong>Flag-Based Philosophy:</strong> WCTF does not produce numerical scores or automated recommendations. Instead, it surfaces <strong>green flags</strong> (positive signals) and <strong>red flags</strong> (concerns) to inform your gut decision. Context matters - the same fact can be different colors depending on your priorities. There are no perfect companies, only trade-offs.</p>
        </div>

        <hr>

{dimension_html}

        <div class="priority-box">
            <h2 style="margin-top: 0; background: none; padding: 0; border: none;">🎯 Priority Validation Targets</h2>
            <p><em>Your insider perspective will be invaluable for validating these items:</em></p>
            <ol>
{priority_html}
            </ol>
        </div>

        <hr>

        <h2>Confidence Levels Explained</h2>
        <ul>
            <li><span class="confidence-high">HIGH</span> Multiple independent sources, recent data, explicit statements</li>
            <li><span class="confidence-medium">MEDIUM</span> Single source, implied information, or dated information</li>
            <li><span class="confidence-low">LOW</span> Absence of data, conflicting signals, or need firsthand validation</li>
        </ul>

        <p style="margin-top: 0.5cm;"><em>Your input as an insider will be invaluable for validating MEDIUM/LOW confidence items and providing ground truth on the priority questions above.</em></p>

    </div>
    <script>
        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {{
                e.preventDefault();
                window.print();
            }}
        }});
    </script>
</body>
</html>
"""
    return html


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/generate_evaluation_overview.py <company-slug>")
        print("Example: uv run python scripts/generate_evaluation_overview.py workday")
        sys.exit(1)

    company_slug = sys.argv[1]

    # Load company data
    try:
        facts, flags = load_company_data(company_slug)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Get company name from facts
    company_name = facts.get("company", company_slug.replace("-", " ").title())

    # Generate HTML
    html = generate_html(company_name, facts, flags)

    # Create output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    output_dir = Path("data") / company_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{timestamp}-evaluation-overview.html"

    # Write file
    with open(output_file, "w") as f:
        f.write(html)

    print(f"✅ Evaluation overview created: {output_file}")
    print(f"📄 Format: A4 paper (~3-4 pages), print-ready")
    print(f"📍 Location: {output_file.absolute()}")
    print(f"\n💡 Share this with your insider contact before/during the interview")
    print(f"🖨️  To print: Open in browser and use Ctrl+P → Save as PDF")


if __name__ == "__main__":
    main()
