# WCTF Core SDK Reference

Auto-generated from wctf_core v0.2.0 on 2025-11-12

## Overview

The WCTF Core SDK provides a Python interface for managing company research data
for the "Worth Climbing Together Framework" job search framework.

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
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Number of facts saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available)

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


**`get_flags_extraction_prompt() -> Dict[str, Any]`**

Get prompt for extracting evaluation flags from research.

Returns a prompt for analyzing research facts and extracting green flags,
red flags, and missing critical data. The prompt expects research facts
to be provided in the conversation context.

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available) and extraction_prompt

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_flags_extraction_prompt()
>>> result['success']
True
>>> 'extraction_prompt' in result
True
```


**`save_flags(company_name: <class 'str'>, flags_yaml: <class 'str'>) -> Dict[str, Any]`**

Save extracted evaluation flags.

Takes YAML content with extracted flags and saves to company.flags.yaml.
Merges with existing flags if file already exists.

**Parameters:**
- company_name: Name of the company
- flags_yaml: Complete YAML content with extracted flags

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available)

**Example:**
```python
>>> client = WCTFClient()  # doctest: +SKIP
>>> flags_yaml = '''  # doctest: +SKIP
... company: "Stripe"
... evaluation_date: "2025-01-15"
... green_flags: {...}
... '''
>>> result = client.save_flags("Stripe", flags_yaml)  # doctest: +SKIP
```


**`add_flag(company_name: <class 'str'>, flag_type: <class 'str'>, mountain_element: <class 'str'>, kwargs) -> Dict[str, Any]`**

Manually add a flag to company evaluation.

**Parameters:**
- company_name: Name of the company
- flag_type: Type of flag - "green", "red", or "missing"
- mountain_element: Mountain element category
- **kwargs: Additional flag-specific fields (flag, impact, confidence, etc.)

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available)


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
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available) and extraction prompt


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
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available)


---

### Conversation & Decision

**`get_conversation_questions(company_name: <class 'str'>, stage: <class 'str'> = "opening", max_questions: <class 'int'> = 8) -> Dict[str, Any]`**

Get conversation guidance questions based on existing company data.

**Parameters:**
- company_name: Name of the company
- stage: Conversation stage - "opening", "follow_up", or "deep_dive"
- max_questions: Maximum number of questions to return

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available) and questions list


**`gut_check(company_name: <class 'str'>) -> Dict[str, Any]`**

Generate a gut-check summary for decision making.

Reads facts and flags, then formats an organized summary to help
with decision making.

**Parameters:**
- company_name: Name of the company

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available) and formatted summary


**`save_decision(company_name: <class 'str'>, mountain_worth_climbing: <class 'str'>, confidence: <class 'str'>, reasoning: Optional[str] = None) -> Dict[str, Any]`**

Save a gut decision to the company's flags file.

**Parameters:**
- company_name: Name of the company
- mountain_worth_climbing: "YES", "NO", or "MAYBE"
- confidence: "HIGH", "MEDIUM", or "LOW"
- reasoning: Optional reasoning text explaining the decision

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available)


**`get_evaluation_summary() -> Dict[str, Any]`**

Generate a summary table of all company evaluations.

Returns a formatted table showing all companies with their evaluation
status, decisions, and confidence levels.

**Returns:**
Dictionary with:
- success (bool): Whether operation completed successfully
- message (str): Human-readable confirmation
- company_name (str): Display name (e.g., "Toast, Inc.")
- company_slug (str): Filesystem slug (e.g., "toast-inc")
- file_path (str): Absolute path to saved file
- items_saved (int): Count of items saved
- operation (str): "created", "updated", or "merged"

On error:
- success (bool): False
- message (str): User-friendly error explanation
- error (str): Technical error details
- company_name (str): Display name (if available)
- company_slug (str): Filesystem slug (if available), company count, and summary table

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_evaluation_summary()
>>> result['success']
True
```


---

### Organizational Mapping

**`save_orgmap(company_name: <class 'str'>, orgmap_yaml: <class 'str'>) -> Dict`**

Save organizational map.

**Parameters:**
- company_name: Company name
- orgmap_yaml: YAML string with org structure

**Returns:**
Dict with success status and saved orgmap

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.save_orgmap("Chronosphere", orgmap_yaml)  # doctest: +SKIP
>>> result['success']
True
```


**`get_orgmap(company_name: <class 'str'>) -> Dict`**

Get organizational map.

**Parameters:**
- company_name: Company name

**Returns:**
Dict with orgmap data or error

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_orgmap("Chronosphere")  # doctest: +SKIP
>>> len(result['orgmap']['peaks'])
3
```


---

### Role Search

**`save_roles(company_name: <class 'str'>, roles_yaml: <class 'str'>) -> Dict`**

Save role search results.

**Parameters:**
- company_name: Company name
- roles_yaml: YAML string with roles

**Returns:**
Dict with success status and saved roles

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.save_roles("Apple", roles_yaml)  # doctest: +SKIP
>>> result['success']
True
```


**`get_roles(company_name: <class 'str'>) -> Dict`**

Get open roles.

**Parameters:**
- company_name: Company name

**Returns:**
Dict with roles data or error

**Example:**
```python
>>> client = WCTFClient()
>>> result = client.get_roles("Apple")  # doctest: +SKIP
>>> result['roles']['total_roles']
15
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
| `company` | `<class 'str'>` | Company display name |
| `company_slug` | `Optional[str]` | Slugified company name for filesystem (auto-generated if not provided) |
| `research_date` | `<class 'datetime.date'>` | Date when research was conducted |
| `financial_health` | `<class 'wctf_core.models.company.FactsCategory'>` | Financial health facts |
| `market_position` | `<class 'wctf_core.models.company.FactsCategory'>` | Market position facts |
| `organizational_stability` | `<class 'wctf_core.models.company.FactsCategory'>` | Organizational stability facts |
| `technical_culture` | `<class 'wctf_core.models.company.FactsCategory'>` | Technical culture facts |
| `summary` | `Dict[str, Any]` | Summary of all findings |

---

### CompanyInsiderFacts

Insider interview facts structure

Complete insider facts structure for a company.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` | Company display name |
| `company_slug` | `Optional[str]` | Slugified company name for filesystem (auto-generated if not provided) |
| `last_updated` | `<class 'datetime.date'>` | Date when last updated |
| `financial_health` | `<class 'wctf_core.models.company.InsiderFactsCategory'>` | Financial health facts |
| `market_position` | `<class 'wctf_core.models.company.InsiderFactsCategory'>` | Market position facts |
| `organizational_stability` | `<class 'wctf_core.models.company.InsiderFactsCategory'>` | Organizational stability facts |
| `technical_culture` | `<class 'wctf_core.models.company.InsiderFactsCategory'>` | Technical culture facts |
| `summary` | `Dict[str, Any]` | Summary including interview metadata |

---

### CompanyFlags

Evaluation flags structure

Complete flags structure for a company evaluation.

Uses double hierarchy: mountain elements (what aspect) -> severity (how important).
Includes task implications for Energy Matrix analysis.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` | Company display name |
| `company_slug` | `Optional[str]` | Slugified company name for filesystem (auto-generated if not provided) |
| `evaluation_date` | `<class 'datetime.date'>` | Date when evaluation was done |
| `evaluator_context` | `<class 'str'>` | Context of the evaluator |
| `profile_version_used` | `Optional[str]` | Version of profile.yaml used for this evaluation |
| `staff_engineer_alignment` | `Dict[str, str]` | Alignment with staff engineer criteria |
| `green_flags` | `Dict[str, wctf_core.models.company.MountainElementGreenFlags]` | Positive indicators organized by mountain element (mountain_range, chosen_peak, rope_team_confidence, daily_climb, story_worth_telling) |
| `red_flags` | `Dict[str, wctf_core.models.company.MountainElementRedFlags]` | Negative indicators organized by mountain element |
| `missing_critical_data` | `List[wctf_core.models.company.MissingCriticalData]` | Critical missing information |
| `synthesis` | `Optional[Dict[str, Any]]` | Overall synthesis and recommendation including Energy Matrix analysis |

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
| `facts_found` | `List[wctf_core.models.company.Fact]` | Facts found in this category |
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

### CompanyOrgMap

Organizational map structure

Complete organizational map.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` |  |
| `company_slug` | `<class 'str'>` |  |
| `last_updated` | `<class 'str'>` | YYYY-MM-DD format |
| `mapping_metadata` | `Dict` | sources, confidence, notes |
| `peaks` | `List[wctf_core.models.orgmap.Peak]` |  |

---

### Peak

VP-level organizational unit

VP-level organization.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `peak_id` | `<class 'str'>` | Unique identifier, e.g., 'apple_cloud_services' |
| `peak_name` | `<class 'str'>` |  |
| `leadership` | `<class 'wctf_core.models.orgmap.Leadership'>` |  |
| `mission` | `<class 'str'>` |  |
| `org_metrics` | `<class 'wctf_core.models.orgmap.OrgMetrics'>` |  |
| `tech_focus` | `Dict[str, List[str]]` | primary and secondary tech areas |
| `coordination_signals` | `<class 'wctf_core.models.orgmap.CoordinationSignals'>` |  |
| `insider_connections` | `List[wctf_core.models.orgmap.InsiderConnection]` |  |
| `rope_teams` | `List[wctf_core.models.orgmap.RopeTeam]` |  |

---

### RopeTeam

Director-level team within a Peak

Director-level team cluster.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `team_id` | `<class 'str'>` | Unique identifier, e.g., 'apple_k8s_platform' |
| `team_name` | `<class 'str'>` |  |
| `leadership` | `<class 'wctf_core.models.orgmap.Leadership'>` |  |
| `mission` | `<class 'str'>` |  |
| `estimated_size` | `<class 'str'>` | e.g., '40-50 engineers' |
| `tech_focus` | `List[str]` | Primary technologies |
| `public_presence` | `List[str]` | Talks, blog posts |
| `insider_info` | `Optional[Dict]` | Contact and notes |

---

### CompanyRoles

Role search results structure

All roles for company.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `company` | `<class 'str'>` |  |
| `company_slug` | `<class 'str'>` |  |
| `last_updated` | `<class 'str'>` | YYYY-MM-DD format |
| `search_metadata` | `Dict` | sources, last_search_date |
| `peaks` | `List[wctf_core.models.orgmap.PeakRoles]` |  |
| `unmapped_roles` | `List[wctf_core.models.orgmap.Role]` | Roles not linked to orgmap |

---

### Role

Single open role with WCTF analysis

Job role posting.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `role_id` | `<class 'str'>` | Unique identifier, e.g., 'apple_202511_senior_swe_k8s' |
| `title` | `<class 'str'>` |  |
| `url` | `<class 'str'>` |  |
| `posted_date` | `<class 'str'>` | YYYY-MM-DD format |
| `location` | `<class 'str'>` |  |
| `rope_team_id` | `Optional[str]` | References company.orgmap.yaml |
| `rope_team_name` | `Optional[str]` |  |
| `seniority` | `Literal['senior_ic', 'staff_plus', 'management']` |  |
| `description` | `<class 'str'>` |  |
| `requirements` | `List[str]` |  |
| `salary_range` | `Optional[str]` |  |
| `wctf_analysis` | `<class 'wctf_core.models.orgmap.WCTFAnalysis'>` |  |

---

### WCTFAnalysis

WCTF framework analysis of a role

WCTF framework analysis of role.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `analyzed_date` | `Optional[str]` | YYYY-MM-DD when analyzed |
| `coordination_style` | `Optional[Literal['alpine', 'expedition', 'established', 'orienteering', 'trail_crew']]` |  |
| `terrain_match` | `Optional[Literal['good_fit', 'workable', 'mismatched']]` |  |
| `mountain_clarity` | `Optional[Literal['clear', 'unclear', 'conflicting']]` |  |
| `energy_matrix` | `Dict` | Predicted quadrants and tasks |
| `alignment_signals` | `Dict` | Green/red flags |

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
