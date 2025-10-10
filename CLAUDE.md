# CLAUDE.md

## Project Overview

**WCTF MCP Server** - A Model Context Protocol (MCP) server for managing "Worth Climbing The Foothill" company research data. This server provides structured access to company facts and evaluation flags for engineers researching potential employers.

## Code Structure

```
.
├── wctf_mcp/                  # Main package
│   ├── __init__.py           # Package initialization
│   ├── models.py             # Pydantic data models
│   ├── server.py             # MCP server (stub - to be implemented)
│   └── utils/                # Utility modules
│       ├── __init__.py
│       ├── yaml_handler.py   # Safe YAML read/write operations
│       └── paths.py          # Data directory management
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_models.py        # Tests for Pydantic models
│   ├── test_yaml_handler.py  # Tests for YAML operations
│   └── test_paths.py         # Tests for path utilities
│
├── data/                      # Company research data
│   ├── <company_name>/       # One directory per company
│   │   ├── company.facts.yaml  # Factual research data
│   │   └── company.flags.yaml  # Evaluation flags
│   └── ...
│
├── pyproject.toml            # Project configuration and dependencies
└── README.md                 # Project documentation
```

## Core Modules

### `wctf_mcp/models.py`

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

### `wctf_mcp/utils/yaml_handler.py`

Safe YAML file operations with error handling:

- `read_yaml(file_path)` - Read and parse YAML files
  - Returns empty dict for empty files
  - Raises `YAMLHandlerError` for missing/malformed files

- `write_yaml(file_path, data)` - Write data to YAML files
  - Creates parent directories automatically
  - Uses safe_dump with proper formatting
  - Raises `YAMLHandlerError` on write failures

### `wctf_mcp/utils/paths.py`

Path utilities for managing the data directory structure:

- `get_data_dir(base_path=None)` - Get the data directory path
- `get_company_dir(company_name, base_path=None)` - Get company directory
- `ensure_company_dir(company_name, base_path=None)` - Create company directory if needed
- `get_facts_path(company_name, base_path=None)` - Path to company.facts.yaml
- `get_flags_path(company_name, base_path=None)` - Path to company.flags.yaml
- `list_companies(base_path=None)` - List all companies in data directory

All functions accept optional `base_path` for testing or custom data locations.

### `wctf_mcp/server.py`

MCP server stub (to be implemented). Will provide tools for:
- Listing companies
- Retrieving company facts
- Retrieving company flags
- Searching companies by criteria

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

1. **Make changes** to code in `wctf_mcp/`
2. **Run tests** to verify: `uv run pytest`
3. **Check coverage**: `uv run pytest --cov=wctf_mcp`
4. **Add new tests** in `tests/` for new functionality

## Dependencies

**Core dependencies:**
- `mcp>=0.9.0` - Model Context Protocol SDK
- `pyyaml>=6.0` - YAML parsing and writing
- `pydantic>=2.0` - Data validation and models

**Dev dependencies:**
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reporting

## Next Steps

The foundation is complete. Future tasks will implement:
1. MCP server with read tools (list, get facts/flags)
2. MCP server with write tools (create/update companies)
3. Search and filter capabilities
4. CLI interface for manual data management

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
