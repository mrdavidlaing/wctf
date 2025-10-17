# CLAUDE.md

## Project Overview

**WCTF - Worth Climbing The Foothill** - A hybrid SDK and MCP server for managing company research data during job searches. Provides both a Python SDK (`wctf_core`) for direct programmatic access and an MCP server (`wctf_mcp`) for integration with Claude Desktop.

## Architecture

This project uses a **hybrid architecture** separating concerns:

- **`wctf_core`** - Core Python SDK with all business logic
  - High-level `WCTFClient` for easy SDK usage
  - Low-level operations modules for advanced use cases
  - Pure Python, no MCP dependencies

- **`wctf_mcp`** - Thin MCP wrapper
  - Delegates to `wctf_core` operations
  - Provides async MCP tool interfaces
  - Used by Claude Desktop

## Code Structure

```
.
├── wctf_core/                 # Core SDK library
│   ├── __init__.py           # Exports WCTFClient
│   ├── client.py             # High-level WCTFClient class
│   ├── models.py             # Pydantic data models
│   ├── operations/           # Core operations (business logic)
│   │   ├── company.py        # Company CRUD operations
│   │   ├── research.py       # Research workflows
│   │   ├── flags.py          # Flag operations
│   │   ├── insider.py        # Insider interview handling
│   │   ├── conversation.py   # Conversation guidance
│   │   └── decision.py       # Decision support
│   └── utils/                # Utility modules
│       ├── yaml_handler.py   # Safe YAML read/write
│       └── paths.py          # Data directory management
│
├── wctf_mcp/                  # MCP server wrapper
│   ├── __init__.py           # MCP package metadata
│   └── server.py             # MCP server (delegates to wctf_core)
│
├── docs/                      # Documentation
│   ├── generate_docs.py      # Auto-generate SDK_REFERENCE.md
│   └── SDK_REFERENCE.md      # Comprehensive SDK documentation
│
├── examples/                  # Example usage scripts
│   ├── list_companies.py     # List all companies
│   ├── research_company.py   # Get research prompt
│   ├── analyze_companies.py  # Analyze evaluation status
│   └── get_company_info.py   # Get detailed company info
│
├── tests/                     # Test suite (173 tests)
│   ├── test_company_tools.py # Company operations tests
│   ├── test_research_tool.py # Research workflow tests
│   ├── test_flags_tool.py    # Flag extraction tests
│   └── ...
│
├── data/                      # Company research data
│   ├── <company_name>/       # One directory per company
│   │   ├── company.facts.yaml   # Public research facts
│   │   ├── company.insider.yaml # Insider interview facts
│   │   └── company.flags.yaml   # Evaluation flags
│   └── ...
│
├── pyproject.toml            # Project configuration
├── README.md                 # Installation & setup docs
└── CLAUDE.md                 # This file (development docs)
```

## Using the SDK

### Direct SDK Usage (Recommended for Scripts)

```python
from wctf_core import WCTFClient

# Initialize client
client = WCTFClient()  # Uses ./data by default

# List companies
companies = client.list_companies()

# Get company facts
result = client.get_facts("Stripe")
if result['success']:
    facts = result['facts']

# Get research prompt
prompt = client.get_research_prompt("NewCompany")
print(prompt['research_prompt'])

# Save research results
yaml_content = '''...'''  # Your YAML content
client.save_facts("NewCompany", yaml_content)
```

See `docs/SDK_REFERENCE.md` for complete API documentation.

### Running Example Scripts

```bash
# List all companies
uv run python examples/list_companies.py

# Get research prompt
uv run python examples/research_company.py "Company Name"

# Analyze evaluation status
uv run python examples/analyze_companies.py

# Get detailed company info
uv run python examples/get_company_info.py "Company Name"
```

### Using via MCP (Claude Desktop)

The MCP server provides the same functionality via Claude Desktop integration.
See `README.md` for Claude Desktop configuration.

## Core Modules

### `wctf_core/client.py`

High-level WCTFClient class with methods for:
- Company discovery: `list_companies()`, `company_exists()`
- Facts operations: `get_facts()`, `save_facts()`
- Flags operations: `get_flags()`, `extract_flags()`, `add_flag()`
- Research workflow: `get_research_prompt()`
- Insider interviews: `get_insider_extraction_prompt()`, `save_insider_facts()`
- Decision support: `gut_check()`, `save_decision()`, `get_evaluation_summary()`

### `wctf_core/models.py`

Pydantic models that validate the YAML schema for company data:

**Facts Models** (company.facts.yaml):
- `Fact` - Individual fact with source, date, and confidence level
- `FactsCategory` - Category of facts (financial_health, market_position, etc.)
- `CompanyFacts` - Complete facts structure for a company

**Flags Models** (company.flags.yaml):
- `GreenFlag` - Positive indicators about a company
- `RedFlag` - Negative indicators/concerns
- `MissingCriticalData` - Important information gaps
- `CompanyFlags` - Complete evaluation flags structure

**Enums**:
- `ConfidenceLevel` - `explicit_statement`, `implied`
- `ImpactLevel` - `EXCELLENT`, `GOOD`, `POOR`
- `FlagSeverity` - `YES`, `NO`, `MAYBE`

### `wctf_core/utils/yaml_handler.py`

Safe YAML file operations with error handling:

- `read_yaml(file_path)` - Read and parse YAML files
  - Returns empty dict for empty files
  - Raises `YAMLHandlerError` for missing/malformed files

- `write_yaml(file_path, data)` - Write data to YAML files
  - Creates parent directories automatically
  - Uses safe_dump with proper formatting
  - Raises `YAMLHandlerError` on write failures

### `wctf_core/utils/paths.py`

Path utilities for managing the data directory structure:

- `get_data_dir(base_path=None)` - Get the data directory path
- `get_company_dir(company_name, base_path=None)` - Get company directory
- `ensure_company_dir(company_name, base_path=None)` - Create company directory if needed
- `get_facts_path(company_name, base_path=None)` - Path to company.facts.yaml
- `get_flags_path(company_name, base_path=None)` - Path to company.flags.yaml
- `list_companies(base_path=None)` - List all companies in data directory

All functions accept optional `base_path` for testing or custom data locations.

### `wctf_mcp/server.py`

MCP server that wraps `wctf_core` operations. Provides async MCP tools for:
- Listing companies (`list_companies_tool`)
- Retrieving company facts (`get_company_facts_tool`)
- Retrieving company flags (`get_company_flags_tool`)
- Research workflow (`get_research_prompt_tool`, `save_research_results_tool`)
- Flag extraction (`extract_flags_tool`, `add_manual_flag_tool`)
- Insider interviews (`get_insider_extraction_prompt_tool`, `save_insider_facts_tool`)
- Conversation guidance (`get_conversation_questions_tool`)
- Decision support (`gut_check_tool`, `save_gut_decision_tool`, `get_evaluation_summary_tool`)

All MCP tools delegate to `wctf_core.operations` modules.

## Data Schema

### company.facts.yaml

```yaml
company: "CompanyName"
research_date: "YYYY-MM-DD"

financial_health:
  facts_found:
    - fact: "Descriptive statement"
      source: "Source citation"
      date: "YYYY-MM-DD"
      confidence: "explicit_statement" | "implied"
  missing_information:
    - "What's missing"

market_position: { ... }
organizational_stability: { ... }
technical_culture: { ... }

summary:
  total_facts_found: 42
  information_completeness: "high" | "medium" | "low"
  # ... additional summary fields
```

### company.flags.yaml

```yaml
company: "CompanyName"
evaluation_date: "YYYY-MM-DD"
evaluator_context: "Evaluator perspective"

senior_engineer_alignment:
  organizational_maturity: "EXCELLENT" | "GOOD" | "POOR"
  technical_culture: "EXCELLENT" | "GOOD" | "POOR"
  # ... more alignment criteria

green_flags:
  critical_matches:
    - flag: "Positive observation"
      impact: "Why this matters"
      confidence: "High/Medium/Low - evidence"
  strong_positives: [ ... ]

red_flags:
  dealbreakers: [ ... ]
  concerning: [ ... ]

missing_critical_data:
  - question: "What needs to be known?"
    why_important: "Why it matters"
    how_to_find: "How to get this info"

synthesis:
  mountain_worth_climbing: "YES" | "NO" | "MAYBE"
  sustainability_confidence: "HIGH" | "MEDIUM" | "LOW"
  # ... additional synthesis fields
```

### company.insider.yaml

```yaml
company: "CompanyName"
last_updated: "YYYY-MM-DD"

financial_health:
  facts_found:
    - fact: "Descriptive statement"
      source: "Interviewee Name (Role)"
      date: "YYYY-MM-DD"
      confidence: "firsthand_account"
      fact_type: "objective" | "subjective"
      context: "Optional additional context"
  missing_information:
    - "Information not discussed"

market_position: { ... }
organizational_stability: { ... }
technical_culture: { ... }

summary:
  total_facts_found: 42
  information_completeness: "high" | "medium" | "low"
  most_recent_interview: "YYYY-MM-DD"
  oldest_interview: "YYYY-MM-DD"
  total_interviews: 1
  interviewees:
    - name: "Interviewee Name"
      role: "Role/Title"
      interview_date: "YYYY-MM-DD"
```

## MCP Tool Workflows

The MCP server provides two main workflows for collecting company data:

### Research Workflow (Public Data)

For collecting public information about companies (press releases, articles, financial reports):

1. **Get the prompt**: Call `get_research_prompt_tool(company_name)`
   - Returns a detailed prompt for researching the company
   - Use this prompt to guide your research

2. **Conduct research**: Use the prompt to research the company via web search, articles, etc.

3. **Save results**: Call `save_research_results_tool(company_name, extracted_facts_yaml)`
   - Takes the YAML-formatted facts you extracted
   - Saves to `data/{company_name}/company.facts.yaml`
   - Merges with existing facts if file already exists
   - Deduplicates exact matches (same fact, source, date)

### Insider Interview Workflow (Firsthand Accounts)

For collecting information from insider interviews with current/former employees:

1. **Get the extraction prompt**: Call `get_insider_extraction_prompt_tool(company_name, interview_date, interviewee_name, interviewee_role)`
   - Assumes the interview transcript is already in the conversation context
   - Returns a specialized prompt for extracting facts from the transcript
   - Guides classification of facts as objective vs subjective

2. **Analyze the transcript**: Use the extraction prompt to analyze the transcript in your conversation context
   - Extract concrete facts (revenue, team size, policies)
   - Capture cultural observations and opinions
   - Note comparisons to other companies

3. **Save extracted facts**: Call `save_insider_facts_tool(company_name, interview_date, interviewee_name, extracted_facts_yaml, interviewee_role)`
   - Takes only the extracted YAML
   - Saves to `data/{company_name}/company.insider.yaml`
   - Merges with existing insider facts if file already exists
   - Deduplicates exact matches (same fact, source, date)
   - Updates summary metadata (interview count, date ranges, interviewees)

**Key differences from research workflow:**
- Two separate tools instead of mode-switching
- Transcript stays in conversation context (not passed to tools)
- Facts classified as objective vs subjective
- Separate file (`company.insider.yaml`) for firsthand accounts
- Tracks interviewee metadata in summary section

## Running Tests

### Using UV (Recommended)

UV is configured as the dependency manager for this project.

**Install dependencies:**
```bash
uv sync --all-extras
```

**Run all tests:**
```bash
uv run pytest
```

**Run tests with verbose output:**
```bash
uv run pytest -v
```

**Run specific test file:**
```bash
uv run pytest tests/test_models.py
uv run pytest tests/test_yaml_handler.py
uv run pytest tests/test_paths.py
```

**Run specific test class or function:**
```bash
uv run pytest tests/test_models.py::TestFactModel
uv run pytest tests/test_models.py::TestFactModel::test_valid_fact
```

**Run tests with coverage:**
```bash
uv run pytest --cov=wctf_mcp --cov-report=html
```

### Test Suite Overview

**174 tests total** covering all modules including:
- Pydantic models (`test_models.py`)
- YAML operations (`test_yaml_handler.py`)
- Path utilities (`test_paths.py`)
- Company tools (`test_company_tools.py`)
- Research tools (`test_research_tool.py`)
- Insider interview tools (`test_insider_tool.py`)
- Flag extraction tools (`test_flag_tools.py`)
- Conversation tools (`test_conversation_tool.py`)
- Decision tools (`test_decision_tools.py`)

All tests use pytest fixtures and temporary directories to avoid affecting real data.

## Development Workflow

### Making Changes

1. **Make changes** to code in `wctf_core/` (core SDK) or `wctf_mcp/` (MCP wrapper)
2. **Update docstrings** with examples and doctests if adding new methods
3. **Run tests** to verify: `uv run pytest`
4. **Check coverage**: `uv run pytest --cov=wctf_core`
5. **Add new tests** in `tests/` for new functionality
6. **Regenerate documentation**: `uv run python docs/generate_docs.py`

### SDK Documentation

The SDK documentation (`docs/SDK_REFERENCE.md`) is auto-generated from:
- Docstrings in `wctf_core/client.py`
- Pydantic Field descriptions in `wctf_core/models.py`
- The `docs/generate_docs.py` script

**To update documentation:**
```bash
# After modifying docstrings or models
uv run python docs/generate_docs.py
```

**Best practices:**
- Use Google-style docstrings with Args, Returns, Example sections
- Include doctests in Examples (e.g., `>>> client = WCTFClient()`)
- Add Pydantic Field descriptions for all model fields
- Keep examples focused and practical

### Using the SDK in Agent Scripts

When Claude Code (or other agents) want to use WCTF functionality, they should:

1. **Read the SDK documentation** (`docs/SDK_REFERENCE.md`)
2. **Write a throwaway Python script** that imports `wctf_core`
3. **Execute the script** via `uv run python script.py`

Example agent workflow:
```python
#!/usr/bin/env python3
"""Find companies that need evaluation."""
from wctf_core import WCTFClient

client = WCTFClient()
companies = [c for c in client.list_companies() if c['has_facts'] and not c['has_flags']]
print(f"Need evaluation: {', '.join(c['name'] for c in companies)}")
```

Benefits of this approach:
- Flexible composition of operations
- Standard Python programming model
- Better error handling
- Stateful workflows possible
- Can use loops, conditions, etc.

## Dependencies

**Core dependencies:**
- `mcp>=0.9.0` - Model Context Protocol SDK
- `pyyaml>=6.0` - YAML parsing and writing
- `pydantic>=2.0` - Data validation and models

**Dev dependencies:**
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reporting

## Architecture Benefits

The hybrid SDK + MCP approach provides:

1. **Flexibility**: Agents can write custom workflows combining multiple operations
2. **Composability**: Standard Python programming vs limited MCP tool chaining
3. **Better Error Handling**: Scripts can implement custom retry and validation logic
4. **Stateful Operations**: Scripts can maintain state across operations
5. **Discoverability**: MCP tools for simple queries, SDK for complex workflows
6. **Documentation**: Auto-generated SDK docs from docstrings ensure accuracy

## Notes

- All path utilities accept optional `base_path` parameter for flexibility in testing
- YAML handler uses safe_load/safe_dump for security
- Models use Pydantic v2 syntax (ConfigDict recommended over class Config)
- Test suite uses pytest with fixtures for isolation

## Debugging

### Claude Desktop Logs

MCP server logs are written to:
```
/mnt/c/Users/DavidLaing/AppData/Roaming/Claude/logs/mcp-server-wctf.log
```

Useful commands:
```bash
# View recent log entries
tail -n 100 "/mnt/c/Users/DavidLaing/AppData/Roaming/Claude/logs/mcp-server-wctf.log"

# Follow logs in real-time
tail -f "/mnt/c/Users/DavidLaing/AppData/Roaming/Claude/logs/mcp-server-wctf.log"

# Search for errors
grep -i "error\|fail\|exception" "/mnt/c/Users/DavidLaing/AppData/Roaming/Claude/logs/mcp-server-wctf.log" | tail -20

# Search for specific tool usage
grep -i "extract_insider" "/mnt/c/Users/DavidLaing/AppData/Roaming/Claude/logs/mcp-server-wctf.log" -A 10
```
