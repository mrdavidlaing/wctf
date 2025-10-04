# WCTF MCP Server - Product Requirements Document

## Executive Summary

Build an MCP (Model Context Protocol) server that helps a staff software engineer systematically evaluate job opportunities using the "Worth Climbing Together Framework". The server orchestrates research, conversation guidance, flag extraction, and decision synthesis through structured tools that integrate with Claude Desktop.

## Goals

1. **Reduce cognitive load** - Organize research data in familiar patterns
2. **Enable informed gut decisions** - Surface signals without mechanical scoring
3. **Maintain state** - Track evaluations across multiple conversations
4. **Leverage existing data** - Work with YAML files in `data/` directory
5. **Stay local** - All sensitive career data remains on user's machine

## Non-Goals

- Web interface or API server
- Automated decision-making or scoring algorithms
- Integration with job boards or ATS systems
- Multi-user support or cloud sync
- Mobile app or browser extension

## Technical Context

### Existing Repository Structure
```
wctf/
├── data/
│   ├── {company-name}/
│   │   ├── company.facts.yaml
│   │   └── company.flags.yaml
│   └── ...
└── README.md
```

### Target Environment
- **Runtime**: Python 3.11+
- **Integration**: Claude Desktop via MCP protocol
- **Data format**: YAML files
- **Distribution**: pip/uv installable package

## Core Concepts from WCTF Framework

### The Mountain Metaphor
Every job opportunity is evaluated as a mountain expedition with five elements:
1. **Mountain Range** (Macro Environment) - Can any team succeed here?
2. **Chosen Peak** (Strategic Alignment) - Is everyone climbing the same mountain?
3. **Rope Team Confidence** (Mutual Belief) - Does the team believe they can succeed?
4. **Daily Climb** (Work Reality) - Will the 99 days be energizing or draining?
5. **Story Worth Telling** (The Mom Test) - Would you be proud of this work?

### Two-Layer Investigation
- **Layer 1**: Macro environment (5 min automated research via web search)
- **Layer 2**: Team reality (ongoing conversations with insiders)

### Flag-Based Evaluation
- Collect **green flags** (positive signals) and **red flags** (concerning signals)
- No mechanical scoring - flags inform gut decisions
- Context matters - same fact can be different color in different situations

## MCP Tools Specification

### 1. Company Management

#### `list_companies`
**Purpose**: Show all companies currently being evaluated

**Input**: None

**Output**: List of company names from `data/` directory

**Example**:
```
Companies being evaluated:
- 1Password
- anthropic
- mechanical-orchard
- stripe
```

#### `get_company_facts`
**Purpose**: Retrieve structured facts from Layer 1 research

**Input**:
- `company` (string, required): Company name

**Output**: Contents of `data/{company}/company.facts.yaml` formatted as readable text

**Error handling**: If company doesn't exist, return helpful message suggesting `list_companies`

#### `get_company_flags`
**Purpose**: Retrieve extracted flags from conversations and research

**Input**:
- `company` (string, required): Company name

**Output**: Contents of `data/{company}/company.flags.yaml` formatted as readable text

**Error handling**: If flags file doesn't exist, return message indicating flags haven't been extracted yet

### 2. Research Tools

**Note**: Research follows a two-phase pattern where the MCP server provides prompts and Claude executes the research using its built-in web search capabilities.

#### `get_research_prompt`
**Purpose**: Generate the Layer 1 macro environment research prompt for a new company

**Input**:
- `company` (string, required): Company name

**Process**:
1. Load the Layer 1 research template
2. Generate structured research prompt with company name
3. Return prompt instructions for Claude to execute

**Output**: Research prompt with instructions covering:
- Financial health (profitability, runway, funding)
- Market position (competitors, market share, growth)
- Organizational stability (leadership, layoffs, culture)
- Technical culture (stack, engineering practices, blog content)

**Usage Flow**:
1. Call `get_research_prompt` to get instructions
2. Claude executes web searches using the prompt
3. Claude calls `save_research_results` with YAML output

**Template**: Uses "WCTF Layer 1 - LLM Research Prompt Templates.md"

#### `save_research_results`
**Purpose**: Save completed research results to company.facts.yaml

**Input**:
- `company` (string, required): Company name
- `yaml_content` (string, required): YAML-formatted research results

**Process**:
1. Create `data/{company}/` directory if it doesn't exist
2. Validate YAML structure
3. Save to `data/{company}/company.facts.yaml`

**Output**: Confirmation with count of facts saved

### 3. Conversation Guidance

#### `get_conversation_questions`
**Purpose**: Surface relevant questions for network conversations based on what's already known

**Input**:
- `company` (string, required): Company being researched
- `stage` (enum, required): "opening" | "follow_up" | "deep_dive"

**Process**:
1. Load existing facts and flags for context
2. Select questions from framework's Question Bank
3. Prioritize questions that fill information gaps
4. Return questions grouped by topic area

**Output**: Structured list of questions with context about why each matters

**Question categories**:
- Opening questions (the mountain question, team evolution)
- Cross-team decision making
- Daily work reality
- Strategic alignment

### 4. Flag Extraction

#### `extract_flags`
**Purpose**: Process conversation notes and extract green/red flags using Mountain Expedition framework

**Input**:
- `company` (string, required): Company being evaluated
- `notes` (string, required): Raw notes from conversation or research

**Process**:
1. Load existing flags if present
2. Apply "Mountain Expedition Flag Extraction Prompt" from framework
3. Extract facts, classify as green/red flags
4. Include confidence level (explicit_statement, implied, inferred)
5. Map to five mountain elements
6. Append new flags to existing collection
7. Save to `data/{company}/company.flags.yaml`

**Output**: Summary of newly extracted flags organized by mountain element

**Template**: Use "Improved Mountain Expedition Flag Extraction Prompt.md"

#### `add_manual_flag`
**Purpose**: Manually record a flag when user has specific insight

**Input**:
- `company` (string, required): Company name
- `flag_type` (enum, required): "green" | "red" | "missing"
- `mountain_element` (enum, required): "mountain_range" | "chosen_peak" | "rope_team_confidence" | "daily_climb" | "story_worth_telling"

**For green/red flags (required):**
- `severity` (enum):
  - Green: "critical_matches" | "strong_positives"
  - Red: "dealbreakers" | "concerning"
- `flag` (string): What was observed
- `impact` (string): Why this matters
- `confidence` (string): Confidence level with supporting evidence (e.g., "High - directly stated in blog post")

**For missing critical data:**
- `question` (string): What needs to be known
- `why_important` (string): Why it matters for the decision
- `how_to_find` (string): How to get this information

**Process**: Validate inputs and add flag to appropriate double hierarchy location in company.flags.yaml

**Output**: Confirmation message with flag location

### 5. Decision Synthesis

#### `gut_check`
**Purpose**: Present organized evidence summary to support gut decision-making

**Input**:
- `company` (string, required): Company to evaluate

**Process**:
1. Load all facts and flags from company data
2. Present organized summary with double hierarchy:
   - Per mountain element: green flags (critical_matches, strong_positives)
   - Per mountain element: red flags (dealbreakers, concerning)
   - Flag counts and visual indicators (✓✓✓, ✓✓, ✓, ⚠️, ⚠️⚠️)
3. Include synthesis section if present
4. Highlight missing critical information

**Output**: Formatted summary showing:
- Flag counts by mountain element and severity
- Existing synthesis (if present)
- Missing critical data gaps
- Does NOT make decisions - just presents data for user review

**Note**: After reviewing this output, use `save_gut_decision` to record your decision.

#### `save_gut_decision`
**Purpose**: Record the user's gut decision with reasoning

**Input**:
- `company` (string, required): Company name
- `mountain_worth_climbing` (enum, required): "YES" | "NO" | "MAYBE"
- `confidence` (enum, required): "HIGH" | "MEDIUM" | "LOW"
- `reasoning` (string, optional): User's explanation of the decision

**Process**: Add gut_decision section to company.flags.yaml synthesis with timestamp

**Output**: Confirmation with decision summary

**Note**: This tool only records decisions - it does not make them. The user must review the gut_check output and make their own decision.

#### `get_evaluation_summary`
**Purpose**: Get current state of all evaluations

**Input**: None

**Output**: Table showing all companies with:
- Last research date
- Flag counts (green/red)
- Missing data indicators
- Decision status if recorded

## Data Schema Specifications

### company.facts.yaml Structure
```yaml
company: "string"
research_date: "YYYY-MM-DD"

financial_health:
  facts_found:
    - fact: "string"
      source: "string"
      date: "YYYY-MM-DD"
      confidence: "explicit_statement" | "implied" | "inferred"
  missing_information:
    - "string"

market_position:
  facts_found: [...]
  missing_information: [...]

organizational_stability:
  facts_found: [...]
  missing_information: [...]

technical_culture:
  facts_found: [...]
  missing_information: [...]

summary:
  total_facts_found: integer
  information_completeness: "high" | "medium" | "low"
  most_recent_data_point: "YYYY-MM-DD"
  oldest_data_point: "YYYY-MM-DD"
```

### company.flags.yaml Structure

**Double Hierarchy Design**: Flags are organized by **mountain element** (what aspect) → **severity** (how important) → flags

```yaml
company: "string"
evaluation_date: "YYYY-MM-DD"
evaluator_context: "string"  # e.g., "25yr staff engineer, sustainable excellence focus"

senior_engineer_alignment:
  organizational_maturity: "EXCELLENT" | "GOOD" | "POOR"
  technical_culture: "EXCELLENT" | "GOOD" | "POOR"
  decision_making: "EXCELLENT" | "GOOD" | "POOR"
  work_sustainability: "EXCELLENT" | "GOOD" | "POOR"
  growth_trajectory: "EXCELLENT" | "GOOD" | "POOR"

green_flags:
  mountain_range:  # Financial & Market Foundation
    critical_matches:  # Exactly what you're looking for
      - flag: "string"
        impact: "string"
        confidence: "string"  # e.g., "High - directly stated"
    strong_positives:  # Generally good signals
      - flag: "string"
        impact: "string"
        confidence: "string"

  chosen_peak:  # Technical Culture & Work Quality
    critical_matches: [...]
    strong_positives: [...]

  rope_team_confidence:  # Leadership & Organization
    critical_matches: [...]
    strong_positives: [...]

  daily_climb:  # Day-to-Day Experience
    critical_matches: [...]
    strong_positives: [...]

  story_worth_telling:  # Growth & Legacy
    critical_matches: [...]
    strong_positives: [...]

red_flags:
  mountain_range:
    dealbreakers:  # Would eliminate this option
      - flag: "string"
        impact: "string"
        confidence: "string"
    concerning:  # Worth investigating further
      - flag: "string"
        impact: "string"
        confidence: "string"

  chosen_peak:
    dealbreakers: [...]
    concerning: [...]

  rope_team_confidence:
    dealbreakers: [...]
    concerning: [...]

  daily_climb:
    dealbreakers: [...]
    concerning: [...]

  story_worth_telling:
    dealbreakers: [...]
    concerning: [...]

missing_critical_data:
  - question: "string"
    why_important: "string"
    how_to_find: "string"
    mountain_element: "mountain_range" | "chosen_peak" | "rope_team_confidence" | "daily_climb" | "story_worth_telling"

synthesis:
  mountain_worth_climbing: "YES" | "NO" | "MAYBE"
  sustainability_confidence: "HIGH" | "MEDIUM" | "LOW"
  primary_strengths: ["string"]
  primary_risks: ["string"]
  confidence_level: "HIGH" | "MEDIUM" | "LOW"
  next_investigation: "string"

gut_decision:  # Optional - added by save_gut_decision tool
  recorded_date: "YYYY-MM-DD"
  mountain_worth_climbing: "YES" | "NO" | "MAYBE"
  confidence: "HIGH" | "MEDIUM" | "LOW"
  reasoning: "string"  # Optional user explanation
```

## Implementation Requirements

### Package Structure
```
wctf_mcp/
├── __init__.py
├── server.py              # Main MCP server setup
├── tools/
│   ├── __init__.py
│   ├── company.py         # list, get_facts, get_flags
│   ├── research.py        # start_company_research
│   ├── conversation.py    # get_conversation_questions
│   ├── flags.py           # extract_flags, add_manual_flag
│   └── decision.py        # gut_check, save_decision, get_summary
├── models.py              # Pydantic models for validation
├── prompts/
│   ├── layer1_research.md
│   └── mountain_flags.md
└── utils/
    ├── yaml_handler.py    # Safe YAML read/write
    └── paths.py           # Data directory management
```

### Dependencies
```toml
[project]
dependencies = [
    "mcp>=0.9.0",           # MCP SDK
    "pyyaml>=6.0",          # YAML parsing
    "pydantic>=2.0",        # Data validation
]

# Note: Web search is provided by Claude Desktop's built-in capabilities,
# not a Python dependency. The MCP server provides prompts, Claude executes searches.
```

### Configuration for Claude Desktop

**Transport**: The server uses `streamable-http` transport for remote MCP connections, rather than stdio-based local connections.

Users will configure Claude Desktop to connect to the running server. Start the server with:
```bash
# Install the package
pip install -e .

# Run the server (starts on default port with streamable-http transport)
wctf-server
```

The server can also be configured via environment variables:
```bash
# Optional: Set custom data directory
export WCTF_DATA_DIR="/path/to/wctf/data"

# Start server
wctf-server
```

**Note**: Configuration details for connecting Claude Desktop to an HTTP-based MCP server may vary. Consult the MCP documentation for current streamable-http setup instructions.

## Error Handling

### Graceful Degradation
- If company doesn't exist, suggest `list_companies`
- If YAML is malformed, show error but don't crash
- If web search fails during research, save partial results
- If missing required fields, use sensible defaults

### User-Friendly Messages
- No stack traces in tool outputs
- Clear next steps when things go wrong
- Suggest specific tools to fix issues

## Testing Strategy

### Unit Tests
- YAML read/write operations
- Flag extraction logic
- Data validation with Pydantic

### Integration Tests
- Tool invocation through MCP protocol
- File system operations in test directory
- End-to-end: research → flags → decision

### Manual Testing Checklist
1. Start fresh company research
2. Extract flags from sample notes
3. Record gut decision
4. Get evaluation summary
5. Verify YAML files are human-readable

## Success Criteria

### Functional
- ✅ Can research new company in <5 minutes
- ✅ Conversation questions adapt to existing knowledge
- ✅ Flag extraction captures 90%+ of signals from notes
- ✅ All data persists correctly in YAML
- ✅ Tools respond in <2 seconds for local operations

### User Experience
- ✅ Natural conversation flow in Claude Desktop
- ✅ No manual YAML editing required (but still possible)
- ✅ Clear guidance on next steps
- ✅ Trustworthy - never loses or corrupts data

### Technical
- ✅ Works on macOS, Linux, Windows
- ✅ Python 3.11+ compatible
- ✅ No external API dependencies (except during research)
- ✅ Clean shutdown on Ctrl-C

## Future Enhancements (Out of Scope for v1)

- Import Glassdoor/LinkedIn data via browser extension
- Automatic follow-up reminders for stale evaluations
- Export evaluations to markdown reports
- Comparison view across multiple opportunities
- Network graph of connections at companies
- Integration with calendar for conversation scheduling

## Appendix: Key Framework Documents

The following documents should be embedded as prompt templates:
1. "WCTF Layer 1 - LLM Research Prompt Templates.md"
2. "Improved Mountain Expedition Flag Extraction Prompt.md"
3. "Job Evaluation System v3.0 - Data-Informed Gut Decision Framework.md" (for question bank)

## Development Phases

### Phase 1: MVP (This PRD)
- Basic tool implementation
- File operations working
- Manual testing successful

### Phase 2: Polish
- Comprehensive error handling
- Better output formatting
- Documentation and examples

### Phase 3: Community
- Open source release
- Installation guide
- Video walkthrough

---

**Document Version**: 1.0  
**Target Completion**: 1 week from project start  
**Primary User**: Staff software engineer with 25 years experience  
**Success Metric**: User chooses to use this over manual note-taking