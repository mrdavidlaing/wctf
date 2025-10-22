#!/usr/bin/env python3
"""Generate comprehensive WCTF evaluation rubric with analysis synthesis.

Usage:
    uv run python scripts/generate_evaluation_rubric.py <company-slug>

Example:
    uv run python scripts/generate_evaluation_rubric.py workday

Note: This script generates the rubric framework. Use Claude Code to synthesize
analysis paragraphs by asking it to "synthesize the analysis sections."
"""

import sys
from datetime import datetime
from pathlib import Path
import yaml

# Add parent directory to path to import wctf_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core.utils.paths import get_facts_path, get_flags_path, find_company
from wctf_core.utils.yaml_handler import read_yaml


def load_company_data(company_slug: str) -> tuple[dict, dict, int, Path]:
    """Load facts and flags for a company.

    Args:
        company_slug: Company name or slug

    Returns:
        Tuple of (facts_dict, flags_dict, stage_number, company_dir_path)

    Raises:
        FileNotFoundError: If company not found or missing required files
    """
    # Find company across all stages
    stage, company_dir = find_company(company_slug)

    if stage is None:
        raise FileNotFoundError(
            f"Company '{company_slug}' not found in any stage. "
            f"Please ensure the company exists in data/stage-N/<company>/"
        )

    facts_path = get_facts_path(company_slug, stage=stage)
    flags_path = get_flags_path(company_slug, stage=stage)

    if not facts_path.exists():
        raise FileNotFoundError(f"Facts file not found: {facts_path}")
    if not flags_path.exists():
        raise FileNotFoundError(f"Flags file not found: {flags_path}")

    facts = read_yaml(facts_path)
    flags = read_yaml(flags_path)

    return facts, flags, stage, company_dir


def build_references(facts: dict) -> list[dict]:
    """Build reference list from all facts."""
    references = []
    ref_num = 1

    for category in ["financial_health", "market_position", "organizational_stability", "technical_culture"]:
        section = facts.get(category, {})
        for fact in section.get("facts_found", []):
            references.append({
                "num": ref_num,
                "fact": fact.get("fact", ""),
                "source": fact.get("source", "Unknown"),
                "date": fact.get("date", "Unknown")
            })
            ref_num += 1

    return references


def generate_dimension_html(dimension_name: str, description: str, facts_data: dict,
                            green_flags: dict, red_flags: dict, gaps: list, references: list) -> str:
    """Generate HTML for one dimension section."""

    # Build facts list with references
    facts_html = ""
    for i, fact in enumerate(facts_data.get("facts_found", [])[:10], 1):
        fact_text = fact.get("fact", "")
        # Find reference number
        ref_num = next((r["num"] for r in references
                       if r["fact"] == fact_text), "?")
        facts_html += f"<li>{fact_text}<sup>{ref_num}</sup></li>\n                "

    # Build green flags
    green_html = ""
    for flag in (green_flags.get("critical_matches", []) + green_flags.get("strong_positives", []))[:8]:
        green_html += f"<li>{flag.get('flag', '')}</li>\n                "

    # Build red flags
    red_html = ""
    for flag in (red_flags.get("dealbreakers", []) + red_flags.get("concerning", []))[:8]:
        red_html += f"<li>{flag.get('flag', '')}</li>\n                "

    # Build knowledge gaps
    gaps_html = ""
    for gap in gaps[:5]:
        gaps_html += f"<li><strong>{gap.get('question', '')}</strong><br><em>{gap.get('why_important', '')}</em></li>\n                "

    html = f"""
        <h2>{dimension_name}: {description}</h2>

        <h3>Analysis</h3>
        <div class="analysis-section">
            <p><em>[AI Synthesis Placeholder: Synthesize the facts below into 2-3 analytical paragraphs with footnotes, highlighting tensions and paradoxes]</em></p>
            <div class="fact-list" style="background-color: #f9f9f9; padding: 0.3cm; margin: 0.3cm 0;">
                <strong>Key Facts:</strong>
                <ul style="margin: 0.2cm 0;">
                {facts_html if facts_html else "<li><em>Limited facts available</em></li>"}
                </ul>
            </div>
        </div>

        <h3>Green Flags</h3>
        <ul>
            {green_html if green_html else "<li><em>None identified</em></li>"}
        </ul>

        <h3>Red Flags</h3>
        <ul>
            {red_html if red_html else "<li><em>None identified</em></li>"}
        </ul>

        <h3>Knowledge Gaps</h3>
        <ul>
            {gaps_html if gaps_html else "<li><em>No specific gaps identified</em></li>"}
        </ul>

        <hr>
"""
    return html


def generate_html(company_name: str, facts: dict, flags: dict) -> str:
    """Generate complete HTML evaluation rubric."""

    # Extract metadata
    evaluator_context = flags.get("evaluator_context", "Senior Engineer")
    research_date = facts.get("research_date", datetime.now().strftime("%Y-%m-%d"))
    eval_date = flags.get("evaluation_date", datetime.now().strftime("%Y-%m-%d"))

    # Build references
    references = build_references(facts)

    # Get missing data
    missing_data = flags.get("missing_critical_data", [])

    # Build dimensions
    dimensions = [
        {
            "name": "Mountain Range",
            "description": "Business Viability",
            "facts": {**facts.get("financial_health", {}),
                     "facts_found": (facts.get("financial_health", {}).get("facts_found", []) +
                                   facts.get("market_position", {}).get("facts_found", []))},
            "green": flags.get("green_flags", {}).get("mountain_range", {}),
            "red": flags.get("red_flags", {}).get("mountain_range", {}),
            "gaps": [g for g in missing_data if "mountain_range" in g.get("mountain_element", "")]
        },
        {
            "name": "Chosen Peak",
            "description": "Strategic Alignment & Coordination Fit",
            "facts": {**facts.get("technical_culture", {}),
                     "facts_found": (facts.get("technical_culture", {}).get("facts_found", []) +
                                   facts.get("organizational_stability", {}).get("facts_found", []))},
            "green": flags.get("green_flags", {}).get("chosen_peak", {}),
            "red": flags.get("red_flags", {}).get("chosen_peak", {}),
            "gaps": [g for g in missing_data if "chosen_peak" in g.get("mountain_element", "")]
        },
        {
            "name": "Rope Team Confidence",
            "description": "Leadership & Team Trust",
            "facts": facts.get("organizational_stability", {}),
            "green": flags.get("green_flags", {}).get("rope_team_confidence", {}),
            "red": flags.get("red_flags", {}).get("rope_team_confidence", {}),
            "gaps": [g for g in missing_data if "rope_team" in g.get("mountain_element", "")]
        },
        {
            "name": "Daily Climb",
            "description": "Day-to-Day Experience",
            "facts": facts.get("organizational_stability", {}),
            "green": flags.get("green_flags", {}).get("daily_climb", {}),
            "red": flags.get("red_flags", {}).get("daily_climb", {}),
            "gaps": [g for g in missing_data if "daily_climb" in g.get("mountain_element", "")]
        },
        {
            "name": "Story Worth Telling",
            "description": "Career Narrative & Impact",
            "facts": facts.get("market_position", {}),
            "green": flags.get("green_flags", {}).get("story_worth_telling", {}),
            "red": flags.get("red_flags", {}).get("story_worth_telling", {}),
            "gaps": [g for g in missing_data if "story_worth" in g.get("mountain_element", "")]
        }
    ]

    # Generate dimension sections
    dimensions_html = ""
    for dim in dimensions:
        dimensions_html += generate_dimension_html(
            dim["name"], dim["description"], dim["facts"],
            dim["green"], dim["red"], dim["gaps"], references
        )

    # Generate references section
    references_html = ""
    for ref in references:
        references_html += f"""            <li>{ref['fact']} - {ref['source']}, {ref['date']}</li>\n"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WCTF Evaluation Rubric - {company_name}</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2cm 1.5cm;
            }}
            body {{ font-size: 9pt; }}
            h1 {{ font-size: 16pt; }}
            h2 {{ font-size: 12pt; page-break-after: avoid; }}
            h3 {{ font-size: 10pt; page-break-after: avoid; }}
        }}

        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #222;
            max-width: 21cm;
            margin: 0 auto;
            padding: 1cm;
            background-color: #f5f5f5;
        }}

        .page {{
            background-color: white;
            padding: 2cm 1.5cm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}

        h1 {{
            font-size: 20pt;
            font-weight: bold;
            margin-top: 0;
            margin-bottom: 0.3cm;
            border-bottom: 3px solid #333;
            padding-bottom: 0.3cm;
            color: #000;
        }}

        h2 {{
            font-size: 15pt;
            font-weight: bold;
            margin-top: 1cm;
            margin-bottom: 0.4cm;
            color: #000;
            page-break-after: avoid;
            border-left: 5px solid #666;
            padding-left: 0.4cm;
        }}

        h3 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            color: #333;
            page-break-after: avoid;
            font-variant: small-caps;
        }}

        p {{
            margin: 0.3cm 0;
            text-align: justify;
        }}

        ul, ol {{
            margin: 0.3cm 0;
            padding-left: 1.2cm;
        }}

        li {{
            margin: 0.15cm 0;
            page-break-inside: avoid;
        }}

        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 0.6cm 0;
        }}

        sup {{
            font-size: 0.75em;
            vertical-align: super;
        }}

        .framework-box {{
            background-color: #f0f8ff;
            border: 2px solid #4682b4;
            padding: 0.4cm;
            margin: 0.4cm 0;
        }}

        .analysis-section {{
            margin: 0.3cm 0;
        }}

        .fact-list {{
            font-size: 10pt;
            line-height: 1.3;
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
        <h1>WCTF Evaluation Rubric: {company_name}</h1>
        <p class="metadata">
            <strong>Research Date:</strong> {research_date} | <strong>Evaluation Date:</strong> {eval_date}<br>
            <strong>Evaluator Context:</strong> {evaluator_context}
        </p>

        <hr>

        <div class="framework-box">
            <h2 style="margin-top: 0; border: none; padding: 0;">The WCTF Framework</h2>

            <p><strong>Worth Climbing Together Framework (WCTF)</strong> treats job evaluation like planning a mountain expedition. Success in any endeavor requires climbing together as a team. This framework helps you evaluate whether a company represents a mountain worth climbing with that particular team - considering not just business viability, but the right peak, the right teammates, sustainable daily conditions, and a story you'll be proud to tell.</p>

            <h3 style="margin-top: 0.4cm; margin-bottom: 0.2cm; font-size: 11pt;">The Mountain Metaphor - Five Dimensions</h3>

            <ol style="font-size: 10pt; line-height: 1.4;">
                <li><strong>Mountain Range (Macro Environment):</strong> Can <em>any</em> team succeed here? Before evaluating a specific team, ask whether the broader business environment is viable. Are finances sustainable? Is the market position defensible? Can the business model support long-term employment? This isn't about picking winners or predicting IPOs - it's about avoiding mountains that are actively crumbling.</li>

                <li><strong>Chosen Peak (Strategic Alignment & Coordination Fit):</strong> Is everyone climbing the <em>same</em> mountain? Does the organization have clarity about what it's building and why? Are engineering, product, and business aligned on goals? <strong>Does the team's coordination style match what the terrain demands?</strong> (NEW v3.1) Can the team realign faster than conditions change?</li>

                <li><strong>Rope Team Confidence (Mutual Belief):</strong> Does the team believe they can succeed <em>together</em>? Mountaineering requires trust in your rope team - the people literally holding your safety line. Similarly, job success requires believing in your colleagues and leadership. Do you trust the leadership's judgment? Is there psychological safety? Are teammates competent and collaborative? Is the organization stable or constantly churning?</li>

                <li><strong>Daily Climb (Work Reality):</strong> Will the 99 days be energizing or draining? Most of your time won't be at the summit celebrating - it'll be the daily grind of the climb. Is that daily experience sustainable? Can you maintain this pace? Is compensation fair? Are policies reasonable? Will this drain or energize you over months and years?</li>

                <li><strong>Story Worth Telling (The Mom Test):</strong> Would you be proud to explain this work? In five years, when explaining what you did, will you feel proud? Does this build a career narrative you want? This is the "Mom Test" - not whether your mom would understand the technical details, but whether you'd feel good explaining the mission, impact, and what you accomplished.</li>
            </ol>

            <h3 style="margin-top: 0.4cm; margin-bottom: 0.2cm; font-size: 11pt;">Evaluation Philosophy</h3>

            <p style="font-size: 10pt;"><strong>Two-Layer Investigation:</strong> Research happens in two phases. <strong>Layer 1</strong> involves 5-15 minutes of automated public research (financials, market position, organizational news, technical culture) to create baseline understanding and surface obvious red flags. <strong>Layer 2</strong> involves ongoing conversations with current/former employees to validate Layer 1 findings, understand ground truth versus public narrative, and surface cultural nuances.</p>

            <p style="font-size: 10pt;"><strong>Flag-Based Evaluation:</strong> WCTF deliberately avoids mechanical scoring or automated recommendations. Instead, it collects <strong>green flags</strong> (positive signals) and <strong>red flags</strong> (concerning signals) that inform gut decisions. Context matters - the same fact can be different colors depending on your situation and priorities. There are no perfect companies, only trade-offs. After surfacing signals and identifying tensions, trust your intuition.</p>

            <p style="font-size: 10pt;"><strong>Synthesis Over Summation:</strong> This rubric encourages synthesizing tensions rather than tallying flags: "Profitable but laying off" - what does this mean? "Great mission but poor leadership" - can you accept this trade-off? "High compensation but weak culture" - what matters more to you? The analysis presents evidence and tensions objectively, enabling informed personal decision-making based on individual priorities and risk tolerance.</p>

            <p style="font-size: 10pt;"><em><strong>This rubric presents research findings objectively without prescribing a "yes/no" recommendation.</strong> It surfaces what was learned, identifies knowledge gaps, and highlights tensions - but the decision remains yours.</em></p>
        </div>

        <hr>

{dimensions_html}

        <h2>References</h2>
        <ol style="font-size: 9pt; line-height: 1.3;">
{references_html}
        </ol>

        <hr>

        <h2>Research Methodology Note</h2>
        <p>This evaluation rubric synthesizes {len(references)} facts collected from public sources including investor reports, press releases, company websites, analyst coverage, employee review platforms, and technical community sites. Research was conducted {research_date}.</p>

        <p>The analysis identifies knowledge gaps that require insider validation through employee conversations to form a complete picture for decision-making.</p>

        <p><strong>The framework intentionally avoids prescribing a "yes/no" recommendation</strong>, instead presenting evidence and tensions to enable informed personal decision-making based on individual priorities and risk tolerance.</p>

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
        print("Usage: uv run python scripts/generate_evaluation_rubric.py <company-slug>")
        print("Example: uv run python scripts/generate_evaluation_rubric.py workday")
        sys.exit(1)

    company_slug = sys.argv[1]

    # Load company data
    try:
        facts, flags, stage, company_dir = load_company_data(company_slug)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Get company name from facts
    company_name = facts.get("company", company_slug.replace("-", " ").title())

    # Generate HTML
    html = generate_html(company_name, facts, flags)

    # Create output file with timestamp in company directory
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = company_dir / f"{timestamp}-evaluation-rubric.html"

    # Write file
    with open(output_file, "w") as f:
        f.write(html)

    print(f"✅ Evaluation rubric created: {output_file}")
    print(f"📄 Format: A4 paper (~6-7 pages), print-ready")
    print(f"📍 Location: {output_file.absolute()}")
    print(f"🏔️  Stage: {stage}")
    print(f"\n💡 Next step: Ask Claude Code to synthesize the analysis paragraphs")
    print(f"   (The rubric has placeholders for AI-generated narrative synthesis)")
    print(f"\n🖨️  To print: Open in browser and use Ctrl+P → Save as PDF")


if __name__ == "__main__":
    main()
