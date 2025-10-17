# WCTF Core SDK Reference

Auto-generated from wctf_core v0.2.0 on 2025-10-17

## Overview

The WCTF Core SDK provides a Python interface for managing company research data
for the "Worth Climbing The Foothill" job search framework.

This SDK enables:
- Structured collection of company research facts
- Extraction of insights from insider interviews
- Evaluation of companies using green/red flags
- Decision making support for job search

---

## Quick Start

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

## WCTFClient Class

High-level client for all WCTF operations.

### Constructor

**`WCTFClient(data_dir: Union[pathlib._local.Path, str, NoneType] = None)`**

Initialize a WCTF client.

**Parameters:**
data_dir: Path to data directory. Defaults to ./data relative to
current working directory.

**Example:**
```python
>>> client = WCTFClient()  # Uses ./data
>>> client.data_dir  # doctest: +SKIP
PosixPath('...')
>>> client = WCTFClient("/custom/path")  # doctest: +SKIP
```

---

### Company Discovery

**`list_companies() -> List[Dict[str, Any]]`**

List all companies in the research database.

Returns a list of companies with metadata about available data files.
Useful for discovering what companies have been researched and what
information is available.

**Returns:**
List of dictionaries with company metadata:
- name (str): Company name
- has_facts (bool): Whether company.facts.yaml exists
- has_flags (bool): Whether company.flags.yaml exists

**Example:**
```python
>>> client = WCTFClient()
>>> companies = client.list_companies()
>>> isinstance(companies, list)
True
>>> all('name' in c for c in companies)
True
```

**See Also:**
- get_facts(): Retrieve facts for a specific company
- company_exists(): Check if a company directory exists


**`company_exists(company_name: <class 'str'>) -> <class 'bool'>`**

Check if a company directory exists.

**Parameters:**
- company_name: Name of the company to check

**Returns:**
True if company directory exists, False otherwise

**Example:**
```python
>>> client = WCTFClient()
>>> client.company_exists("NonExistentCompany123")
False
```


---

### Facts Operations

**`get_facts(company_name: <class 'str'>) -> Dict[str, Any]`**

Get research facts for a specific company.

Returns detailed factual information from company.facts.yaml including
financial health, market position, organizational stability, and technical culture.

**Parameters:**
- company_name: Name of the company (e.g., 'Stripe', 'Anthropic')

**Returns:**
Dictionary with:
- success (bool): Whether retrieval was successful
- facts (dict): Facts data if successful
- error (str): Error message if unsuccessful

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_facts("Stripe")  # doctest: +SKIP
>>> result['success']  # doctest: +SKIP
True
```


**`save_facts(company_name: <class 'str'>, yaml_content: <class 'str'>) -> Dict[str, Any]`**

Save research facts for a company.

Takes YAML content (as a string) and saves it to the appropriate
company directory. Merges with existing facts if file already exists.

**Parameters:**
- company_name: Name of the company
- yaml_content: Complete YAML content as a string

**Returns:**
Dictionary with:
- success (bool): Whether save was successful
- message (str): Result message
- facts_generated (int): Number of facts saved

**Example:**
```python
>>> client = WCTFClient()
>>> yaml_data = '''
... company: "TestCo"
... research_date: "2025-01-15"
... financial_health:
...   facts_found: []
...   missing_information: []
... market_position:
...   facts_found: []
...   missing_information: []
... organizational_stability:
...   facts_found: []
...   missing_information: []
... technical_culture:
...   facts_found: []
...   missing_information: []
... summary:
...   total_facts_found: 0
...   information_completeness: "low"
... '''  # doctest: +SKIP
>>> result = client.save_facts("TestCo", yaml_data)  # doctest: +SKIP
```


---

### Flags Operations

**`get_flags(company_name: <class 'str'>) -> Dict[str, Any]`**

Get evaluation flags for a specific company.

Returns evaluation data from company.flags.yaml including
green flags, red flags, missing critical data, and synthesis.

**Parameters:**
- company_name: Name of the company (e.g., 'Stripe', 'Anthropic')

**Returns:**
Dictionary with:
- success (bool): Whether retrieval was successful
- flags (dict): Flags data if successful
- error (str): Error message if unsuccessful

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_flags("Stripe")  # doctest: +SKIP
```


**`extract_flags(company_name: <class 'str'>, conversation_notes: <class 'str'>, extracted_flags_yaml: Optional[str] = None) -> Dict[str, Any]`**

Extract evaluation flags from conversation notes.

Works in two modes:
1. If extracted_flags_yaml is None: Returns a prompt for analysis
2. If extracted_flags_yaml is provided: Saves the extracted flags

**Parameters:**
- company_name: Name of the company being evaluated
- conversation_notes: Raw conversation notes to analyze
- extracted_flags_yaml: Optional YAML content with extracted flags

**Returns:**
Dictionary with success status and either prompt or save confirmation


**`add_flag(company_name: <class 'str'>, flag_type: <class 'str'>, mountain_element: <class 'str'>, kwargs) -> Dict[str, Any]`**

Manually add a flag to company evaluation.

**Parameters:**
- company_name: Name of the company
- flag_type: Type of flag - "green", "red", or "missing"
- mountain_element: Mountain element category
- **kwargs: Additional flag-specific fields (flag, impact, confidence, etc.)

**Returns:**
Dictionary with success status and message


---

### Research Workflow

**`get_research_prompt(company_name: <class 'str'>) -> Dict[str, Any]`**

Get the research prompt for a company.

Returns a structured research prompt that can be used with
web search capabilities to gather company information.

**Parameters:**
- company_name: Name of the company to research

**Returns:**
Dictionary with:
- success (bool): Whether prompt was generated
- research_prompt (str): The formatted research prompt
- instructions (str): Instructions for conducting research

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_research_prompt("Stripe")
>>> result['success']
True
>>> 'research_prompt' in result
True
```


---

### Insider Interview

**`get_insider_extraction_prompt(company_name: <class 'str'>, interview_date: <class 'str'>, interviewee_name: <class 'str'>, interviewee_role: Optional[str] = None) -> Dict[str, Any]`**

Get prompt for extracting facts from insider interview transcript.

Returns a formatted prompt for analyzing interview transcripts and
extracting structured facts.

**Parameters:**
- company_name: Name of the company
- interview_date: Date of interview (YYYY-MM-DD)
- interviewee_name: Name of person interviewed
- interviewee_role: Optional role/title

**Returns:**
Dictionary with success status and extraction prompt


**`save_insider_facts(company_name: <class 'str'>, interview_date: <class 'str'>, interviewee_name: <class 'str'>, extracted_facts_yaml: <class 'str'>, interviewee_role: Optional[str] = None) -> Dict[str, Any]`**

Save extracted insider interview facts.

Takes YAML content with extracted facts and saves to company.insider.yaml.
Merges with existing insider facts if file already exists.

**Parameters:**
- company_name: Name of the company
- interview_date: Date of interview (YYYY-MM-DD)
- interviewee_name: Name of person interviewed
- extracted_facts_yaml: YAML content with extracted facts
- interviewee_role: Optional role/title

**Returns:**
Dictionary with success status and facts count


---

### Conversation & Decision

**`get_conversation_questions(company_name: <class 'str'>, stage: <class 'str'> = "opening", max_questions: <class 'int'> = 8) -> Dict[str, Any]`**

Get conversation guidance questions based on existing company data.

**Parameters:**
- company_name: Name of the company
- stage: Conversation stage - "opening", "follow_up", or "deep_dive"
- max_questions: Maximum number of questions to return

**Returns:**
Dictionary with success status and questions list


**`gut_check(company_name: <class 'str'>) -> Dict[str, Any]`**

Generate a gut-check summary for decision making.

Reads facts and flags, then formats an organized summary to help
with decision making.

**Parameters:**
- company_name: Name of the company

**Returns:**
Dictionary with success status and formatted summary


**`save_decision(company_name: <class 'str'>, mountain_worth_climbing: <class 'str'>, confidence: <class 'str'>, reasoning: Optional[str] = None) -> Dict[str, Any]`**

Save a gut decision to the company's flags file.

**Parameters:**
- company_name: Name of the company
- mountain_worth_climbing: "YES", "NO", or "MAYBE"
- confidence: "HIGH", "MEDIUM", or "LOW"
- reasoning: Optional reasoning text explaining the decision

**Returns:**
Dictionary with success status


**`get_evaluation_summary() -> Dict[str, Any]`**

Generate a summary table of all company evaluations.

Returns a formatted table showing all companies with their evaluation
status, decisions, and confidence levels.

**Returns:**
Dictionary with success status, company count, and summary table

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_evaluation_summary()
>>> result['success']
True
```


---

## Data Models

Pydantic models for validating company data structures.

### CompanyFacts

Public research facts structure

Complete facts structure for a company from public research.

Organizes research findings into four key categories with summary metadata.
Corresponds to company.facts.yaml file structure.

Categories:
- financial_health: Revenue, funding, profitability, runway
- market_position: Market share, competition, growth trends
- organizational_stability: Leadership, turnover, structure
- technical_culture: Engineering practices, tech stack, culture

**Example:**
```python
>>> from datetime import date
>>> facts = CompanyFacts(
...     company="Stripe",
...     research_date=date(2025, 1, 15),
...     financial_health=FactsCategory(facts_found=[], missing_information=[]),
...     market_position=FactsCategory(facts_found=[], missing_information=[]),
...     organizational_stability=FactsCategory(facts_found=[], missing_information=[]),
...     technical_culture=FactsCategory(facts_found=[], missing_information=[]),
...     summary={"total_facts_found": 0, "information_completeness": "low"}
... )
>>> facts.company
'Stripe'
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` | Company name |
| `research_date` | `<class 'datetime.date'>` | Date when research was conducted |
| `financial_health` | `<class 'wctf_core.models.FactsCategory'>` | Financial health facts |
| `market_position` | `<class 'wctf_core.models.FactsCategory'>` | Market position facts |
| `organizational_stability` | `<class 'wctf_core.models.FactsCategory'>` | Organizational stability facts |
| `technical_culture` | `<class 'wctf_core.models.FactsCategory'>` | Technical culture facts |
| `summary` | `Dict[str, Any]` | Summary of all findings |

---

### CompanyInsiderFacts

Insider interview facts structure

Complete insider facts structure for a company.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` | Company name |
| `last_updated` | `<class 'datetime.date'>` | Date when last updated |
| `financial_health` | `<class 'wctf_core.models.InsiderFactsCategory'>` | Financial health facts |
| `market_position` | `<class 'wctf_core.models.InsiderFactsCategory'>` | Market position facts |
| `organizational_stability` | `<class 'wctf_core.models.InsiderFactsCategory'>` | Organizational stability facts |
| `technical_culture` | `<class 'wctf_core.models.InsiderFactsCategory'>` | Technical culture facts |
| `summary` | `Dict[str, Any]` | Summary including interview metadata |

---

### CompanyFlags

Evaluation flags structure

Complete flags structure for a company evaluation.

Uses double hierarchy: mountain elements (what aspect) -> severity (how important).

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` | Company name |
| `evaluation_date` | `<class 'datetime.date'>` | Date when evaluation was done |
| `evaluator_context` | `<class 'str'>` | Context of the evaluator |
| `senior_engineer_alignment` | `Dict[str, str]` | Alignment with senior engineer criteria |
| `green_flags` | `Dict[str, wctf_core.models.MountainElementGreenFlags]` | Positive indicators organized by mountain element (mountain_range, chosen_peak, rope_team_confidence, daily_climb, story_worth_telling) |
| `red_flags` | `Dict[str, wctf_core.models.MountainElementRedFlags]` | Negative indicators organized by mountain element |
| `missing_critical_data` | `List[wctf_core.models.MissingCriticalData]` | Critical missing information |
| `synthesis` | `Dict[str, Any]` | Overall synthesis and recommendation |

---

### Fact

Single fact from public research

A single fact about a company from public research.

Facts are concrete, verifiable statements about a company with
citations and confidence levels.

**Example:**
```python
>>> from datetime import date
>>> fact = Fact(
...     fact="Raised $200M Series C in Q2 2024",
...     source="TechCrunch, Company blog",
...     date=date(2024, 6, 15),
...     confidence=ConfidenceLevel.EXPLICIT_STATEMENT
... )
>>> fact.fact
'Raised $200M Series C in Q2 2024'
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `fact` | `<class 'str'>` | The factual statement |
| `source` | `<class 'str'>` | Source of the fact |
| `date` | `<class 'datetime.date'>` | Date of the fact |
| `confidence` | `<enum 'ConfidenceLevel'>` | Confidence level in this fact |

---

### InsiderFact

Single fact from insider interview

A single fact from an insider interview.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `fact` | `<class 'str'>` | The factual statement |
| `source` | `<class 'str'>` | Source with name and role (e.g., 'John Doe (Senior Engineer)') |
| `date` | `<class 'datetime.date'>` | Date of the interview |
| `confidence` | `<enum 'ConfidenceLevel'>` | Confidence level (should be firsthand_account) |
| `fact_type` | `<enum 'FactType'>` | Type of fact: objective or subjective |
| `context` | `Optional[str]` | Additional context for the fact |

---

### FactsCategory

Category of facts

A category of facts with found and missing information.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `facts_found` | `List[wctf_core.models.Fact]` | Facts found in this category |
| `missing_information` | `List[str]` | Information not found |

---

### ConfidenceLevel

Confidence level enum

Confidence levels for facts.

Indicates how directly the fact was stated or observed:
- EXPLICIT_STATEMENT: Directly stated in source
- IMPLIED: Can be reasonably inferred from source
- FIRSTHAND_ACCOUNT: From direct participant/observer (insider interviews)

---

### FactType

Fact type enum (objective/subjective)

Types of facts from insider interviews.

---

## Common Workflows

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
        print(f"\n{result['summary']}")
```

### Get Evaluation Summary for All Companies

```python
from wctf_core import WCTFClient

client = WCTFClient()

# Get overview of all evaluations
result = client.get_evaluation_summary()
if result['success']:
    print(result['summary_table'])
    print(f"\nTotal companies: {result['company_count']}")
```

---
