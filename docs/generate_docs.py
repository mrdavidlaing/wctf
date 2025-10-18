#!/usr/bin/env python3
"""Generate comprehensive SDK documentation from docstrings and Pydantic models.

This script introspects wctf_core modules and generates a single SDK_REFERENCE.md
file that agents can read to understand the entire API surface.

Usage:
    uv run python docs/generate_docs.py
"""

import inspect
import re
from datetime import date
from pathlib import Path
from typing import get_type_hints

# Add parent directory to path to import wctf_core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from wctf_core import WCTFClient
from wctf_core import models


def extract_docstring_sections(docstring: str) -> dict:
    """Extract sections from a docstring (Args, Returns, Example, etc.)."""
    if not docstring:
        return {"description": "", "args": {}, "returns": "", "example": ""}

    sections = {
        "description": "",
        "args": {},
        "returns": "",
        "example": "",
        "see_also": ""
    }

    lines = docstring.split("\n")
    current_section = "description"
    current_content = []

    for line in lines:
        line = line.strip()

        # Check for section headers
        if line.startswith("Args:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "args"
            current_content = []
        elif line.startswith("Returns:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "returns"
            current_content = []
        elif line.startswith("Example:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "example"
            current_content = []
        elif line.startswith("See Also:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "see_also"
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def format_method_signature(name: str, method: callable) -> str:
    """Format a method signature for documentation."""
    try:
        sig = inspect.signature(method)
        params = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Get type annotation if available
            if param.annotation != inspect.Parameter.empty:
                type_str = str(param.annotation).replace("typing.", "")
                param_str = f"{param_name}: {type_str}"
            else:
                param_str = param_name

            # Add default value if available
            if param.default != inspect.Parameter.empty:
                if isinstance(param.default, str):
                    param_str += f' = "{param.default}"'
                else:
                    param_str += f" = {param.default}"

            params.append(param_str)

        # Get return type
        return_type = ""
        if sig.return_annotation != inspect.Signature.empty:
            return_type = f" -> {str(sig.return_annotation).replace('typing.', '')}"

        return f"{name}({', '.join(params)}){return_type}"
    except Exception as e:
        return f"{name}(...)"


def generate_client_api_docs() -> str:
    """Generate documentation for WCTFClient class."""
    output = ["## WCTFClient Class", "", "High-level client for all WCTF operations.", ""]

    # Constructor
    init_method = WCTFClient.__init__
    init_doc = extract_docstring_sections(init_method.__doc__)
    output.append("### Constructor")
    output.append("")
    output.append(f"**`{format_method_signature('WCTFClient', init_method)}`**")
    output.append("")
    output.append(init_doc["description"])
    output.append("")

    if init_doc["args"]:
        output.append("**Parameters:**")
        output.append(init_doc["args"])
        output.append("")

    if init_doc["example"]:
        output.append("**Example:**")
        output.append("```python")
        output.append(init_doc["example"])
        output.append("```")
        output.append("")

    output.append("---")
    output.append("")

    # Group methods by category
    categories = {
        "Company Discovery": ["list_companies", "company_exists"],
        "Facts Operations": ["get_facts", "save_facts"],
        "Flags Operations": ["get_flags", "extract_flags", "add_flag"],
        "Research Workflow": ["get_research_prompt"],
        "Insider Interview": ["get_insider_extraction_prompt", "save_insider_facts"],
        "Conversation & Decision": ["get_conversation_questions", "gut_check", "save_decision", "get_evaluation_summary"]
    }

    for category, method_names in categories.items():
        output.append(f"### {category}")
        output.append("")

        for method_name in method_names:
            if not hasattr(WCTFClient, method_name):
                continue

            method = getattr(WCTFClient, method_name)
            doc = extract_docstring_sections(method.__doc__)

            output.append(f"**`{format_method_signature(method_name, method)}`**")
            output.append("")
            output.append(doc["description"])
            output.append("")

            if doc["args"]:
                output.append("**Parameters:**")
                for line in doc["args"].split("\n"):
                    output.append(f"- {line}")
                output.append("")

            if doc["returns"]:
                output.append("**Returns:**")
                output.append(doc["returns"])
                output.append("")

            if doc["example"]:
                output.append("**Example:**")
                output.append("```python")
                output.append(doc["example"])
                output.append("```")
                output.append("")

            if doc["see_also"]:
                output.append("**See Also:**")
                output.append(doc["see_also"])
                output.append("")

            output.append("")

        output.append("---")
        output.append("")

    return "\n".join(output)


def generate_models_docs() -> str:
    """Generate documentation for Pydantic models."""
    output = ["## Data Models", "", "Pydantic models for validating company data structures.", ""]

    # Get all model classes
    model_classes = [
        ("CompanyFacts", models.CompanyFacts, "Public research facts structure"),
        ("CompanyInsiderFacts", models.CompanyInsiderFacts, "Insider interview facts structure"),
        ("CompanyFlags", models.CompanyFlags, "Evaluation flags structure"),
        ("Fact", models.Fact, "Single fact from public research"),
        ("InsiderFact", models.InsiderFact, "Single fact from insider interview"),
        ("FactsCategory", models.FactsCategory, "Category of facts"),
        ("ConfidenceLevel", models.ConfidenceLevel, "Confidence level enum"),
        ("FactType", models.FactType, "Fact type enum (objective/subjective)"),
    ]

    for name, model_class, description in model_classes:
        output.append(f"### {name}")
        output.append("")
        output.append(description)
        output.append("")

        # Get docstring
        if model_class.__doc__:
            doc_sections = extract_docstring_sections(model_class.__doc__)
            output.append(doc_sections["description"])
            output.append("")

            if doc_sections["example"]:
                output.append("**Example:**")
                output.append("```python")
                output.append(doc_sections["example"])
                output.append("```")
                output.append("")

        # For Pydantic models, show fields
        if hasattr(model_class, "model_fields"):
            output.append("**Fields:**")
            output.append("")
            output.append("| Field | Type | Description |")
            output.append("|-------|------|-------------|")

            for field_name, field_info in model_class.model_fields.items():
                field_type = str(field_info.annotation).replace("typing.", "")
                field_desc = field_info.description or ""
                output.append(f"| `{field_name}` | `{field_type}` | {field_desc} |")

            output.append("")

        output.append("---")
        output.append("")

    return "\n".join(output)


def generate_quickstart() -> str:
    """Generate quick start section."""
    return """## Quick Start

### Installation

```bash
# Using uv (recommended)
uv pip install wctf-core

# Or regular pip
pip install wctf-core
```

### Basic Usage

```python
from wctf_core import WCTFClient

# Initialize client
client = WCTFClient()  # Uses ./data by default

# List companies
companies = client.list_companies()
print(f"Found {len(companies)} companies")

# Get company facts
result = client.get_facts("Stripe")
if result['success']:
    facts = result['facts']
    print(f"Company: {facts['company']}")

# Get research prompt
prompt_result = client.get_research_prompt("NewCompany")
print(prompt_result['research_prompt'])

# Save research results (after conducting research)
yaml_content = '''
company: "NewCompany"
research_date: "2025-01-15"
financial_health:
  facts_found: []
  missing_information: []
market_position:
  facts_found: []
  missing_information: []
organizational_stability:
  facts_found: []
  missing_information: []
technical_culture:
  facts_found: []
  missing_information: []
summary:
  total_facts_found: 0
  information_completeness: "low"
'''
client.save_facts("NewCompany", yaml_content)
```

---
"""


def generate_workflows() -> str:
    """Generate common workflows section."""
    return """## Common Workflows

### Research a New Company

```python
from wctf_core import WCTFClient

client = WCTFClient()

# Step 1: Get research prompt
result = client.get_research_prompt("Acme Corp")
print(result['research_prompt'])
print(result['instructions'])

# Step 2: Conduct research using the prompt
# (Use web search, company site, news articles, etc.)

# Step 3: Format findings as YAML and save
yaml_results = '''
company: "Acme Corp"
research_date: "2025-01-15"
# ... rest of YAML structure ...
'''
client.save_facts("Acme Corp", yaml_results)
```

### Extract Facts from Insider Interview

```python
from wctf_core import WCTFClient

client = WCTFClient()

# Step 1: Get extraction prompt
result = client.get_insider_extraction_prompt(
    company_name="Acme Corp",
    interview_date="2025-01-15",
    interviewee_name="Jane Doe",
    interviewee_role="Senior Engineer"
)
print(result['extraction_prompt'])

# Step 2: Analyze interview transcript using the prompt
# (Extract facts from your transcript)

# Step 3: Save extracted facts
yaml_facts = '''
financial_health:
  facts_found:
    - fact: "Team of 50 engineers"
      source: "Jane Doe (Senior Engineer)"
      date: "2025-01-15"
      confidence: "firsthand_account"
      fact_type: "objective"
# ... rest of extracted facts ...
'''
client.save_insider_facts(
    company_name="Acme Corp",
    interview_date="2025-01-15",
    interviewee_name="Jane Doe",
    extracted_facts_yaml=yaml_facts,
    interviewee_role="Senior Engineer"
)
```

### Analyze Companies Needing Evaluation

```python
from wctf_core import WCTFClient

client = WCTFClient()

# Find companies with facts but no flags
needs_evaluation = [
    c['name'] for c in client.list_companies()
    if c['has_facts'] and not c['has_flags']
]

print(f"Companies needing evaluation: {', '.join(needs_evaluation)}")

# Generate gut-check summary for decision making
for company in needs_evaluation:
    result = client.gut_check(company)
    if result['success']:
        print(f"\\n{result['summary']}")
```

### Get Evaluation Summary for All Companies

```python
from wctf_core import WCTFClient

client = WCTFClient()

# Get overview of all evaluations
result = client.get_evaluation_summary()
if result['success']:
    print(result['summary_table'])
    print(f"\\nTotal companies: {result['company_count']}")
```

---
"""


def main():
    """Generate the SDK reference documentation."""
    output = []

    # Header
    output.append("# WCTF Core SDK Reference")
    output.append("")
    output.append(f"Auto-generated from wctf_core v0.2.0 on {date.today().isoformat()}")
    output.append("")
    output.append("## Overview")
    output.append("")
    output.append("The WCTF Core SDK provides a Python interface for managing company research data")
    output.append("for the \"Worth Climbing Together Framework\" job search framework.")
    output.append("")
    output.append("This SDK enables:")
    output.append("- Structured collection of company research facts")
    output.append("- Extraction of insights from insider interviews")
    output.append("- Evaluation of companies using green/red flags")
    output.append("- Decision making support for job search")
    output.append("")
    output.append("---")
    output.append("")

    # Quick Start
    output.append(generate_quickstart())

    # Client API
    output.append(generate_client_api_docs())

    # Data Models
    output.append(generate_models_docs())

    # Common Workflows
    output.append(generate_workflows())

    # Write to file
    docs_dir = Path(__file__).parent
    output_file = docs_dir / "SDK_REFERENCE.md"

    with open(output_file, "w") as f:
        f.write("\n".join(output))

    print(f"Documentation generated: {output_file}")
    print(f"Total lines: {len(output)}")


if __name__ == "__main__":
    main()
