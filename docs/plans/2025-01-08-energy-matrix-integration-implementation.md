# Energy Matrix Integration for WCTF v4.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate Scott Muc's Energy Matrix into WCTF to evaluate whether daily work will energize or drain you, answering "Will I have the energy to climb this mountain?"

**Architecture:** Stores personal profile (energy drains, generators, strengths) in `data/profile.yaml`, captures task implications during flag extraction with fine-grained characteristics, auto-calculates Energy Matrix quadrants (mutual/sparingly/burnout/help_mentoring), and synthesizes daily distribution with threshold checking (≥60% mutual, ≤20% burnout).

**Tech Stack:** Python 3.10+, Pydantic v2, PyYAML, pytest, MCP protocol

---

## Phase 1: Core Data Models

### Task 1.1: Profile Data Models

**Files:**
- Create: `active/projects/wctf/wctf_core/models/profile.py`
- Test: `active/projects/wctf/tests/test_profile_models.py`

**Step 1: Write the failing test for profile schema validation**

```python
"""Tests for profile data models."""

from datetime import date
import pytest
from wctf_core.models.profile import (
    Profile,
    EnergyDrain,
    EnergyGenerator,
    CoreStrength,
    GrowthArea,
)


def test_profile_basic_structure():
    """Test basic profile structure validates correctly."""
    profile = Profile(
        profile_version="1.0",
        last_updated=date(2025, 1, 8),
        energy_drains={
            "interpersonal_conflict": EnergyDrain(
                severity="severe",
                trigger="childhood_trauma",
                description="Conflicts in close working relationships",
            )
        },
        energy_generators={
            "visible_progress": EnergyGenerator(
                strength="core_need",
                description="Building things, shipping features",
            )
        },
        core_strengths=[
            CoreStrength(
                name="systems_thinking",
                level="expert",
                description="Designing complex interconnected systems",
            )
        ],
        growth_areas=[],
    )

    assert profile.profile_version == "1.0"
    assert "interpersonal_conflict" in profile.energy_drains
    assert profile.energy_drains["interpersonal_conflict"].severity == "severe"


def test_drain_severity_validation():
    """Test that drain severity only accepts valid values."""
    with pytest.raises(ValueError):
        EnergyDrain(
            severity="invalid",
            trigger="test",
            description="test",
        )


def test_generator_strength_validation():
    """Test that generator strength only accepts valid values."""
    with pytest.raises(ValueError):
        EnergyGenerator(
            strength="invalid",
            description="test",
        )


def test_strength_level_validation():
    """Test that strength level only accepts valid values."""
    with pytest.raises(ValueError):
        CoreStrength(
            name="test",
            level="invalid",
            description="test",
        )
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_profile_models.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_core.models.profile'"

**Step 3: Write minimal implementation**

Create `active/projects/wctf/wctf_core/models/profile.py`:

```python
"""Pydantic models for Energy Matrix profile data.

The profile captures your personal energy drains, generators, strengths,
and organizational coherence needs. It's stored in data/profile.yaml and
versioned in git to track self-knowledge evolution.
"""

from datetime import date as Date
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DrainSeverity(str, Enum):
    """Severity levels for energy drains."""
    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"


class GeneratorStrength(str, Enum):
    """Strength levels for energy generators."""
    CORE_NEED = "core_need"
    STRONG = "strong"
    MODERATE = "moderate"


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    EXPERT = "expert"
    PROFICIENT = "proficient"
    LEARNING = "learning"


class EnergyDrain(BaseModel):
    """An activity or situation that depletes your energy reserves."""

    severity: DrainSeverity = Field(..., description="How much this drains you")
    trigger: str = Field(..., description="What triggers this drain")
    description: str = Field(..., description="Description of this drain")


class EnergyGenerator(BaseModel):
    """An activity or situation that restores/amplifies your energy."""

    strength: GeneratorStrength = Field(..., description="How much this energizes you")
    description: str = Field(..., description="Description of this generator")


class CoreStrength(BaseModel):
    """An established area of expertise."""

    name: str = Field(..., description="Name of this strength")
    level: SkillLevel = Field(..., description="Your proficiency level")
    description: str = Field(..., description="Description of this strength")


class GrowthArea(BaseModel):
    """An area where you're actively learning."""

    name: str = Field(..., description="Name of this growth area")
    current_level: SkillLevel = Field(..., description="Your current level")
    energizing: bool = Field(..., description="Does learning this energize you?")
    description: str = Field(..., description="Description of this growth area")


class CommunicationPreferences(BaseModel):
    """Communication and decision-making preferences."""

    async_work_capability: str = Field(..., description="Preference for async work")
    timezone_flexibility: str = Field(..., description="Max timezone spread tolerance")
    decision_making_speed_needs: Dict[str, str] = Field(
        default_factory=dict,
        description="Decision speed needs in different contexts"
    )
    meeting_intensity_tolerance: Dict[str, int] = Field(
        default_factory=dict,
        description="Meeting load tolerance"
    )


class OrganizationalCoherenceNeed(BaseModel):
    """A pattern describing organizational coherence requirements."""

    pattern: str = Field(..., description="The organizational pattern")
    requires_one_of: List[str] = Field(
        default_factory=list,
        description="Must have at least one of these"
    )
    incompatible_with: List[str] = Field(
        default_factory=list,
        description="Cannot coexist with these"
    )
    impact_if_violated: str = Field(..., description="Impact when violated")
    description: str = Field(..., description="Description of this need")


class Profile(BaseModel):
    """Complete personal profile for Energy Matrix evaluation.

    This captures your energy drains, generators, strengths, and
    organizational needs. Git tracks version history.
    """

    profile_version: str = Field(..., description="Profile schema version")
    last_updated: Date = Field(..., description="Last update date")

    energy_drains: Dict[str, EnergyDrain] = Field(
        default_factory=dict,
        description="Things that deplete your energy"
    )
    energy_generators: Dict[str, EnergyGenerator] = Field(
        default_factory=dict,
        description="Things that restore/amplify energy"
    )
    core_strengths: List[CoreStrength] = Field(
        default_factory=list,
        description="Established areas of expertise"
    )
    growth_areas: List[GrowthArea] = Field(
        default_factory=list,
        description="Areas where you're actively learning"
    )
    communication_preferences: Optional[CommunicationPreferences] = Field(
        default=None,
        description="Communication and decision-making preferences"
    )
    organizational_coherence_needs: List[OrganizationalCoherenceNeed] = Field(
        default_factory=list,
        description="Organizational coherence requirements"
    )
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_profile_models.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/models/profile.py tests/test_profile_models.py
git commit -m "feat(energy-matrix): add profile data models

Add Pydantic models for Energy Matrix profile:
- EnergyDrain with severity levels
- EnergyGenerator with strength levels
- CoreStrength and GrowthArea with skill levels
- CommunicationPreferences
- OrganizationalCoherenceNeed
- Profile top-level model

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 1.2: Task Implications Models

**Files:**
- Modify: `active/projects/wctf/wctf_core/models.py` (add new models)
- Test: `active/projects/wctf/tests/test_models.py` (add new tests)

**Step 1: Write the failing test for task characteristics**

Add to `active/projects/wctf/tests/test_models.py`:

```python
def test_task_characteristics_basic_structure():
    """Test TaskCharacteristics model validates correctly."""
    from wctf_core.models import TaskCharacteristics

    chars = TaskCharacteristics(
        conflict_exposure="low",
        alignment_clarity="high",
        authority_ambiguity="low",
        progress_visibility="high",
        autonomy_level="high",
        decision_speed="fast",
        learning_required="low",
        collaboration_type="team",
        meeting_intensity="low",
        requires_sync_communication=False,
        timezone_spread="narrow",
    )

    assert chars.conflict_exposure == "low"
    assert chars.progress_visibility == "high"
    assert chars.requires_sync_communication is False


def test_task_implication_basic_structure():
    """Test TaskImplication model with characteristics."""
    from wctf_core.models import TaskImplication, TaskCharacteristics

    impl = TaskImplication(
        task="Design K8s operators for platform services",
        time_estimate_pct="20-30%",
        characteristics=TaskCharacteristics(
            conflict_exposure="low",
            alignment_clarity="high",
            authority_ambiguity="low",
            progress_visibility="high",
            autonomy_level="high",
            decision_speed="fast",
            learning_required="low",
            collaboration_type="team",
            meeting_intensity="low",
            requires_sync_communication=False,
            timezone_spread="narrow",
        ),
        notes="Platform work with clear scope",
    )

    assert impl.task == "Design K8s operators for platform services"
    assert impl.time_estimate_pct == "20-30%"
    assert impl.energy_matrix_quadrant is None  # Not calculated yet


def test_task_implication_with_strength_flags():
    """Test TaskImplication with core strength usage flags."""
    from wctf_core.models import TaskImplication, TaskCharacteristics

    impl = TaskImplication(
        task="Build automation tooling",
        time_estimate_pct="15%",
        characteristics=TaskCharacteristics(
            conflict_exposure="none",
            alignment_clarity="high",
            authority_ambiguity="low",
            progress_visibility="high",
            autonomy_level="high",
            decision_speed="fast",
            learning_required="none",
            collaboration_type="solo",
            meeting_intensity="low",
            requires_sync_communication=False,
            timezone_spread="co_located",
            uses_systems_thinking=True,
            uses_tool_building=True,
            uses_infrastructure_automation=True,
        ),
    )

    assert impl.characteristics.uses_tool_building is True
    assert impl.characteristics.uses_systems_thinking is True
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_models.py::test_task_characteristics_basic_structure -v`

Expected: FAIL with "ImportError: cannot import name 'TaskCharacteristics'"

**Step 3: Write minimal implementation**

Add to `active/projects/wctf/wctf_core/models.py` (after existing imports):

```python
class ConflictLevel(str, Enum):
    """Conflict exposure levels."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NONE = "none"


class ClarityLevel(str, Enum):
    """Clarity/ambiguity levels."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class DecisionSpeed(str, Enum):
    """Decision-making speed."""
    FAST = "fast"
    MODERATE = "moderate"
    SLOW = "slow"


class LearningRequired(str, Enum):
    """Learning requirement levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CollaborationType(str, Enum):
    """Types of collaboration."""
    SOLO = "solo"
    PAIRED = "paired"
    TEAM = "team"
    CROSS_TEAM = "cross_team"


class MeetingIntensity(str, Enum):
    """Meeting load intensity."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class TimezoneSpread(str, Enum):
    """Timezone spread of collaboration."""
    CO_LOCATED = "co_located"
    NARROW = "narrow"      # 0-6 hours
    MODERATE = "moderate"  # 6-12 hours
    WIDE = "wide"          # 12+ hours


class EnergyMatrixQuadrant(str, Enum):
    """Energy Matrix quadrants."""
    MUTUAL = "mutual"                    # Good at + energizes
    SPARINGLY = "sparingly"              # Good at + drains
    HELP_MENTORING = "help_mentoring"    # Not good at + energizes
    BURNOUT = "burnout"                  # Not good at + drains


class TaskCharacteristics(BaseModel):
    """Fine-grained characteristics of a task for Energy Matrix calculation.

    These characteristics are matched against your profile to determine
    which Energy Matrix quadrant the task falls into.
    """

    # Conflict & alignment
    conflict_exposure: ConflictLevel = Field(..., description="Exposure to interpersonal conflict")
    alignment_clarity: ClarityLevel = Field(..., description="Clarity of team alignment")
    authority_ambiguity: ClarityLevel = Field(..., description="Ambiguity in ownership/authority")

    # Progress & autonomy
    progress_visibility: ClarityLevel = Field(..., description="Visibility of forward progress")
    autonomy_level: ClarityLevel = Field(..., description="Level of autonomous decision-making")
    decision_speed: DecisionSpeed = Field(..., description="Speed of decision-making")

    # Skill alignment (matched against profile.core_strengths)
    learning_required: LearningRequired = Field(..., description="Amount of new learning required")
    uses_systems_thinking: bool = Field(default=False, description="Uses systems thinking strength")
    uses_tool_building: bool = Field(default=False, description="Uses tool building strength")
    uses_glue_work: bool = Field(default=False, description="Uses glue work strength")
    uses_infrastructure_automation: bool = Field(default=False, description="Uses infra automation strength")
    uses_decision_frameworks: bool = Field(default=False, description="Uses decision frameworks strength")

    # Work context
    collaboration_type: CollaborationType = Field(..., description="Type of collaboration")
    meeting_intensity: MeetingIntensity = Field(..., description="Meeting load intensity")
    requires_sync_communication: bool = Field(..., description="Requires synchronous communication")
    timezone_spread: TimezoneSpread = Field(..., description="Timezone spread of team")


class TaskImplication(BaseModel):
    """A task implication for a flag with Energy Matrix characteristics.

    Describes what you'll actually DO day-to-day because of a flag,
    with detailed characteristics for quadrant calculation.
    """

    task: str = Field(..., description="Description of the task")
    time_estimate_pct: str = Field(..., description="Estimated % of time (e.g., '20-30%')")
    energy_matrix_quadrant: Optional[EnergyMatrixQuadrant] = Field(
        default=None,
        description="Auto-calculated quadrant (mutual/sparingly/burnout/help_mentoring)"
    )
    characteristics: TaskCharacteristics = Field(..., description="Task characteristics for quadrant calculation")
    notes: Optional[str] = Field(default=None, description="Additional notes")
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_models.py::test_task_characteristics_basic_structure tests/test_models.py::test_task_implication_basic_structure tests/test_models.py::test_task_implication_with_strength_flags -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/models.py tests/test_models.py
git commit -m "feat(energy-matrix): add task characteristics models

Add TaskCharacteristics and TaskImplication models:
- Fine-grained task attributes (conflict, progress, autonomy, etc.)
- Strength usage flags (systems thinking, tool building, etc.)
- Energy Matrix quadrant field (auto-calculated later)
- Enums for all characteristic levels

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 1.3: Enhanced Flag Models

**Files:**
- Modify: `active/projects/wctf/wctf_core/models.py` (enhance existing Flag models)
- Test: `active/projects/wctf/tests/test_models.py` (add tests for enhanced flags)

**Step 1: Write the failing test for flags with task implications**

Add to `active/projects/wctf/tests/test_models.py`:

```python
def test_flag_with_task_implications():
    """Test Flag model with task implications."""
    from wctf_core.models import Flag, TaskImplication, TaskCharacteristics

    flag = Flag(
        flag="Modern tech stack: Kubernetes, Python, Go",
        impact="Matches infrastructure expertise",
        confidence="High - explicit in job description",
        task_implications=[
            TaskImplication(
                task="Design K8s operators",
                time_estimate_pct="20-30%",
                characteristics=TaskCharacteristics(
                    conflict_exposure="low",
                    alignment_clarity="high",
                    authority_ambiguity="low",
                    progress_visibility="high",
                    autonomy_level="high",
                    decision_speed="fast",
                    learning_required="low",
                    collaboration_type="team",
                    meeting_intensity="low",
                    requires_sync_communication=False,
                    timezone_spread="narrow",
                    uses_systems_thinking=True,
                    uses_tool_building=True,
                    uses_infrastructure_automation=True,
                ),
                notes="Platform work with clear scope",
            )
        ],
    )

    assert len(flag.task_implications) == 1
    assert flag.task_implications[0].task == "Design K8s operators"


def test_mountain_flags_with_profile_version():
    """Test MountainFlags model includes profile_version_used."""
    from wctf_core.models import MountainFlags
    from datetime import date

    flags = MountainFlags(
        company="TestCorp",
        evaluation_date=date(2025, 1, 8),
        evaluator_context="Test evaluation",
        profile_version_used="1.0",
        green_flags={
            "mountain_range": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "chosen_peak": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "rope_team_confidence": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "daily_climb": {
                "critical_matches": [],
                "strong_positives": [],
            },
            "story_worth_telling": {
                "critical_matches": [],
                "strong_positives": [],
            },
        },
        red_flags={
            "mountain_range": {"dealbreakers": [], "concerning": []},
            "chosen_peak": {"dealbreakers": [], "concerning": []},
            "rope_team_confidence": {"dealbreakers": [], "concerning": []},
            "daily_climb": {"dealbreakers": [], "concerning": []},
            "story_worth_telling": {"dealbreakers": [], "concerning": []},
        },
        missing_critical_data=[],
    )

    assert flags.profile_version_used == "1.0"
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_models.py::test_flag_with_task_implications -v`

Expected: FAIL - Flag model doesn't have task_implications field yet

**Step 3: Write minimal implementation**

Modify the `Flag` class in `active/projects/wctf/wctf_core/models.py`:

```python
class Flag(BaseModel):
    """A single evaluation flag (green or red).

    Flags are derived from facts through evaluation and include
    task implications for Energy Matrix analysis.
    """

    flag: str = Field(..., description="The flag statement")
    impact: str = Field(..., description="Why this matters")
    confidence: str = Field(..., description="Confidence in this flag")
    task_implications: List[TaskImplication] = Field(
        default_factory=list,
        description="Tasks you'll do because of this flag"
    )
```

Modify the `MountainFlags` class in `active/projects/wctf/wctf_core/models.py`:

```python
class MountainFlags(BaseModel):
    """Mountain climbing evaluation flags for a company.

    Organized by the five mountain elements, with task implications
    for Energy Matrix analysis.
    """

    company: str = Field(..., description="Company name")
    evaluation_date: Date = Field(..., description="Date of evaluation")
    evaluator_context: str = Field(..., description="Context about the evaluator")
    profile_version_used: Optional[str] = Field(
        default=None,
        description="Version of profile.yaml used for this evaluation"
    )

    green_flags: Dict[str, Dict[str, List[Flag]]] = Field(
        ...,
        description="Green flags organized by mountain element and severity"
    )
    red_flags: Dict[str, Dict[str, List[Flag]]] = Field(
        ...,
        description="Red flags organized by mountain element and severity"
    )
    missing_critical_data: List[str] = Field(
        default_factory=list,
        description="Critical information still needed"
    )
    synthesis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Overall evaluation synthesis including Energy Matrix analysis"
    )
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_models.py::test_flag_with_task_implications tests/test_models.py::test_mountain_flags_with_profile_version -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/models.py tests/test_models.py
git commit -m "feat(energy-matrix): enhance flag models with task implications

Modify Flag and MountainFlags models:
- Add task_implications field to Flag
- Add profile_version_used to MountainFlags
- Add synthesis field for Energy Matrix analysis

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Phase 2: Profile Management Tools

### Task 2.1: Profile Storage Operations

**Files:**
- Create: `active/projects/wctf/wctf_core/operations/profile.py`
- Test: `active/projects/wctf/tests/test_profile_operations.py`

**Step 1: Write the failing test for profile loading**

```python
"""Tests for profile operations."""

from datetime import date
from pathlib import Path
import pytest
import tempfile
import yaml

from wctf_core.operations.profile import get_profile, update_profile
from wctf_core.models.profile import Profile, EnergyDrain, EnergyGenerator, CoreStrength


@pytest.fixture
def temp_wctf_dir(tmp_path):
    """Create a temporary WCTF directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return tmp_path


def test_get_profile_loads_existing_profile(temp_wctf_dir, monkeypatch):
    """Test loading an existing profile."""
    # Setup: create a profile file
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {
            "interpersonal_conflict": {
                "severity": "severe",
                "trigger": "childhood_trauma",
                "description": "Conflicts drain energy",
            }
        },
        "energy_generators": {
            "visible_progress": {
                "strength": "core_need",
                "description": "Building things energizes",
            }
        },
        "core_strengths": [
            {
                "name": "systems_thinking",
                "level": "expert",
                "description": "Designing complex systems",
            }
        ],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    # Mock the WCTF_ROOT to use our temp directory
    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    result = get_profile()

    # Verify
    assert "profile_version" in result
    assert "1.0" in result
    assert "interpersonal_conflict" in result


def test_get_profile_returns_error_when_missing(temp_wctf_dir, monkeypatch):
    """Test error message when profile doesn't exist."""
    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    result = get_profile()

    assert "error" in result.lower() or "not found" in result.lower()


def test_update_profile_increments_version(temp_wctf_dir, monkeypatch):
    """Test that updating profile increments version."""
    # Setup: create initial profile
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {},
        "core_strengths": [],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute: update with new content
    updated_profile_yaml = """
profile_version: "1.0"
last_updated: "2025-01-08"
energy_drains:
  misalignment:
    severity: "severe"
    trigger: "blocks_progress"
    description: "Team moving in different directions"
energy_generators: {}
core_strengths: []
growth_areas: []
"""

    result = update_profile(updated_profile_yaml)

    # Verify: version should be incremented
    assert "1.1" in result

    # Verify: file was updated
    with open(profile_path) as f:
        saved_data = yaml.safe_load(f)

    assert saved_data["profile_version"] == "1.1"
    assert "misalignment" in saved_data["energy_drains"]
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_profile_operations.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_core.operations.profile'"

**Step 3: Write minimal implementation**

Create `active/projects/wctf/wctf_core/operations/profile.py`:

```python
"""Operations for profile management."""

import os
from datetime import date
from pathlib import Path
from typing import Dict, Any

import yaml

from wctf_core.models.profile import Profile
from wctf_core.utils.responses import success_response, error_response


def _get_profile_path() -> Path:
    """Get the path to profile.yaml."""
    wctf_root = os.getenv("WCTF_ROOT", os.getcwd())
    return Path(wctf_root) / "data" / "profile.yaml"


def get_profile() -> str:
    """Get current profile.yaml for reference during flag extraction.

    Returns the full profile including energy drains, generators, strengths,
    and organizational coherence needs.

    Returns:
        Formatted profile YAML as string, or error message if not found.
    """
    profile_path = _get_profile_path()

    if not profile_path.exists():
        return error_response(
            f"Profile not found at {profile_path}. "
            "Create data/profile.yaml to use Energy Matrix features."
        )

    try:
        with open(profile_path) as f:
            profile_data = yaml.safe_load(f)

        # Validate with Pydantic model
        profile = Profile(**profile_data)

        # Return as formatted YAML
        return success_response(
            f"Profile v{profile.profile_version} (updated {profile.last_updated})",
            yaml.dump(profile_data, default_flow_style=False, sort_keys=False)
        )

    except Exception as e:
        return error_response(f"Error loading profile: {e}")


def update_profile(updated_profile_yaml: str) -> str:
    """Update profile.yaml with new self-knowledge.

    Args:
        updated_profile_yaml: Complete profile YAML content

    Actions:
        - Increments profile_version (e.g., "1.0" -> "1.1")
        - Updates last_updated timestamp
        - Writes to data/profile.yaml

    Returns:
        Success message with new version, or error message.
    """
    profile_path = _get_profile_path()

    try:
        # Parse the updated profile
        updated_data = yaml.safe_load(updated_profile_yaml)

        # Validate with Pydantic
        profile = Profile(**updated_data)

        # Increment version (e.g., "1.0" -> "1.1")
        current_version = profile.profile_version
        if "." in current_version:
            major, minor = current_version.split(".")
            new_version = f"{major}.{int(minor) + 1}"
        else:
            new_version = f"{current_version}.1"

        # Update metadata
        updated_data["profile_version"] = new_version
        updated_data["last_updated"] = str(date.today())

        # Ensure parent directory exists
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(profile_path, "w") as f:
            yaml.dump(updated_data, f, default_flow_style=False, sort_keys=False)

        return success_response(
            f"Profile updated to v{new_version}",
            f"Saved to {profile_path}"
        )

    except Exception as e:
        return error_response(f"Error updating profile: {e}")
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_profile_operations.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/operations/profile.py tests/test_profile_operations.py
git commit -m "feat(energy-matrix): add profile storage operations

Add profile management operations:
- get_profile() - loads and validates profile.yaml
- update_profile() - increments version and saves
- Auto-increment version on update (1.0 -> 1.1)
- Updates last_updated timestamp

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 2.2: Profile MCP Tools

**Files:**
- Create: `active/projects/wctf/wctf_mcp/tools/profile_tools.py`
- Modify: `active/projects/wctf/wctf_mcp/server.py` (register tools)
- Test: `active/projects/wctf/tests/test_profile_tools.py`

**Step 1: Write the failing test for profile MCP tools**

```python
"""Tests for profile MCP tools."""

from datetime import date
from pathlib import Path
import pytest
import yaml

from wctf_mcp.tools.profile_tools import (
    get_profile_tool,
    update_profile_tool,
)


@pytest.fixture
def temp_wctf_dir(tmp_path):
    """Create a temporary WCTF directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return tmp_path


@pytest.mark.asyncio
async def test_get_profile_tool_returns_profile(temp_wctf_dir, monkeypatch):
    """Test get_profile_tool returns formatted profile."""
    # Setup
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {},
        "core_strengths": [],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    result = await get_profile_tool()

    # Verify
    assert len(result) == 1
    assert result[0].type == "text"
    assert "1.0" in result[0].text


@pytest.mark.asyncio
async def test_update_profile_tool_increments_version(temp_wctf_dir, monkeypatch):
    """Test update_profile_tool increments version."""
    # Setup
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {},
        "core_strengths": [],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    updated_yaml = yaml.dump(profile_data)
    result = await update_profile_tool(updated_yaml)

    # Verify
    assert len(result) == 1
    assert "1.1" in result[0].text
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_profile_tools.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_mcp.tools.profile_tools'"

**Step 3: Write minimal implementation**

Create `active/projects/wctf/wctf_mcp/tools/profile_tools.py`:

```python
"""MCP tools for Energy Matrix profile management."""

from mcp import types

from wctf_core.operations.profile import get_profile, update_profile


async def get_profile_tool() -> list[types.TextContent]:
    """Get current profile.yaml for reference during flag extraction.

    Returns the full profile including energy drains, generators, strengths,
    and organizational coherence needs.

    Returns:
        List containing single TextContent with profile YAML.
    """
    result = get_profile()
    return [types.TextContent(type="text", text=result)]


async def update_profile_tool(updated_profile_yaml: str) -> list[types.TextContent]:
    """Update profile.yaml with new self-knowledge.

    Args:
        updated_profile_yaml: Complete profile YAML content

    Actions:
        - Increments profile_version (e.g., "1.0" -> "1.1")
        - Updates last_updated timestamp
        - Writes to data/profile.yaml

    Returns:
        List containing single TextContent with success/error message.
    """
    result = update_profile(updated_profile_yaml)
    return [types.TextContent(type="text", text=result)]
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_profile_tools.py -v`

Expected: PASS (2 tests)

**Step 5: Register tools in MCP server**

Modify `active/projects/wctf/wctf_mcp/server.py` to add tool registration:

```python
# Add import at top
from wctf_mcp.tools.profile_tools import get_profile_tool, update_profile_tool

# Add tool registrations in the appropriate section
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""

    # ... existing tool handlers ...

    elif name == "get_profile":
        return await get_profile_tool()

    elif name == "update_profile":
        updated_profile_yaml = arguments.get("updated_profile_yaml", "")
        return await update_profile_tool(updated_profile_yaml)
```

**Step 6: Commit**

```bash
cd active/projects/wctf
git add wctf_mcp/tools/profile_tools.py wctf_mcp/server.py tests/test_profile_tools.py
git commit -m "feat(energy-matrix): add profile MCP tools

Add MCP tools for profile management:
- get_profile_tool - returns current profile
- update_profile_tool - updates with version increment
- Register tools in MCP server

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 2.3: Create Initial Profile

**Files:**
- Create: `active/projects/wctf/data/profile.yaml`

**Step 1: Create initial profile from design doc**

Create `active/projects/wctf/data/profile.yaml` with content from the design document:

```yaml
profile_version: "1.0"
last_updated: "2025-01-08"

# Energy drains (things that deplete your reserves)
energy_drains:
  interpersonal_conflict:
    severity: "severe"
    trigger: "childhood_trauma"
    description: "Conflicts in close working relationships cause severe energy drain"

  misalignment:
    severity: "severe"
    trigger: "blocks_progress"
    description: "Team moving in different directions, circular motion instead of forward progress"

  authority_ambiguity:
    severity: "moderate"
    trigger: "creates_latent_conflict"
    description: "Unclear ownership/authority creates hidden conflicts that drain energy"

  financial_anxiety:
    severity: "moderate"
    trigger: "survival_concerns"
    description: "Worrying about money leaks energy from progress work"

# Energy generators (things that restore/amplify your reserves)
energy_generators:
  visible_progress:
    strength: "core_need"
    description: "Building things, shipping features, seeing forward momentum"

  aligned_collaboration:
    strength: "strong"
    description: "Team moving together toward shared goal with clear direction"

  tool_building:
    strength: "core_need"
    description: "Creating systems and tools, flow state work"

  structured_processes:
    strength: "moderate"
    description: "Clear decision frameworks that prevent conflict"

# Core strengths (established expertise)
core_strengths:
  - name: "systems_thinking"
    level: "expert"
    description: "Designing and building complex interconnected systems"

  - name: "tool_building"
    level: "expert"
    description: "Creating automation, CLIs, infrastructure tooling"

  - name: "glue_work"
    level: "expert"
    description: "Bridging between teams, enabling others' progress"

  - name: "infrastructure_automation"
    level: "expert"
    description: "Platform engineering, SRE practices, release engineering"

  - name: "decision_frameworks"
    level: "proficient"
    description: "Building frameworks that prevent misalignment conflicts"

# Growth areas (actively learning)
growth_areas:
  - name: "multi_agent_orchestration"
    current_level: "learning"
    energizing: true
    description: "Coordinating multiple AI agents for complex workflows"

  - name: "ai_augmented_workflows"
    current_level: "proficient"
    energizing: true
    description: "Building human+AI collaboration systems"

# Communication & decision-making preferences
communication_preferences:
  async_work_capability: "strong"
  timezone_flexibility: "6_hours"
  decision_making_speed_needs:
    when_uncertain: "fast_alignment"
    when_clear: "autonomous"
  meeting_intensity_tolerance:
    max_pct: 30
    ideal_pct: 20

# Organizational coherence requirements
organizational_coherence_needs:
  - pattern: "uncertain_problem_space"
    requires_one_of:
      - "async_first_culture"
      - "co_located_team"
      - "fast_sync_decision_cadence"
    incompatible_with:
      - "wide_timezone_spread + sync_heavy_culture"
    impact_if_violated: "severe_drain"
    description: "Uncertain problems need tight feedback loops - either async-friendly OR co-located"
```

**Step 2: Validate profile structure**

Run: `cd active/projects/wctf && python -c "import yaml; from wctf_core.models.profile import Profile; Profile(**yaml.safe_load(open('data/profile.yaml')))"`

Expected: No errors (profile validates)

**Step 3: Commit**

```bash
cd active/projects/wctf
git add data/profile.yaml
git commit -m "feat(energy-matrix): add initial profile

Create data/profile.yaml with personal energy profile:
- Energy drains (conflict, misalignment, ambiguity, financial anxiety)
- Energy generators (progress, collaboration, tool building)
- Core strengths (systems, tools, glue work, infra, frameworks)
- Growth areas (multi-agent orchestration, AI workflows)
- Communication preferences and org coherence needs

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Phase 3: Quadrant Calculation Engine

### Task 3.1: Quadrant Calculation Algorithm

**Files:**
- Create: `active/projects/wctf/wctf_core/energy_matrix/calculator.py`
- Test: `active/projects/wctf/tests/test_energy_calculator.py`

**Step 1: Write the failing test for quadrant calculation**

```python
"""Tests for Energy Matrix quadrant calculation."""

from datetime import date
import pytest

from wctf_core.models import TaskCharacteristics
from wctf_core.models.profile import (
    Profile,
    EnergyDrain,
    EnergyGenerator,
    CoreStrength,
    GrowthArea,
)
from wctf_core.energy_matrix.calculator import calculate_quadrant


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    return Profile(
        profile_version="1.0",
        last_updated=date(2025, 1, 8),
        energy_drains={
            "interpersonal_conflict": EnergyDrain(
                severity="severe",
                trigger="childhood_trauma",
                description="Conflicts drain energy",
            ),
            "misalignment": EnergyDrain(
                severity="severe",
                trigger="blocks_progress",
                description="Team misalignment drains energy",
            ),
        },
        energy_generators={
            "visible_progress": EnergyGenerator(
                strength="core_need",
                description="Progress energizes",
            ),
            "tool_building": EnergyGenerator(
                strength="core_need",
                description="Building tools energizes",
            ),
        },
        core_strengths=[
            CoreStrength(
                name="systems_thinking",
                level="expert",
                description="Expert at systems",
            ),
            CoreStrength(
                name="tool_building",
                level="expert",
                description="Expert at tools",
            ),
        ],
        growth_areas=[
            GrowthArea(
                name="ai_workflows",
                current_level="learning",
                energizing=True,
                description="Learning AI workflows",
            ),
        ],
    )


def test_mutual_quadrant_high_skill_high_energy(sample_profile):
    """Test task with high skill + high energy = mutual quadrant."""
    chars = TaskCharacteristics(
        # Low conflict, high progress = energizing
        conflict_exposure="low",
        alignment_clarity="high",
        authority_ambiguity="low",
        progress_visibility="high",
        autonomy_level="high",
        decision_speed="fast",
        # Uses core strengths = good at
        learning_required="low",
        uses_systems_thinking=True,
        uses_tool_building=True,
        # Good work context
        collaboration_type="team",
        meeting_intensity="low",
        requires_sync_communication=False,
        timezone_spread="narrow",
    )

    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "mutual"


def test_burnout_quadrant_low_skill_low_energy(sample_profile):
    """Test task with low skill + low energy = burnout quadrant."""
    chars = TaskCharacteristics(
        # High conflict, low progress = draining
        conflict_exposure="high",
        alignment_clarity="low",
        authority_ambiguity="high",
        progress_visibility="low",
        autonomy_level="low",
        decision_speed="slow",
        # Not using strengths = not good at
        learning_required="high",
        uses_systems_thinking=False,
        uses_tool_building=False,
        # Bad work context
        collaboration_type="cross_team",
        meeting_intensity="high",
        requires_sync_communication=True,
        timezone_spread="wide",
    )

    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "burnout"


def test_sparingly_quadrant_high_skill_low_energy(sample_profile):
    """Test task with high skill + low energy = sparingly quadrant."""
    chars = TaskCharacteristics(
        # High conflict = draining even if skilled
        conflict_exposure="high",
        alignment_clarity="low",
        authority_ambiguity="moderate",
        progress_visibility="moderate",
        autonomy_level="high",
        decision_speed="moderate",
        # Uses strengths = good at
        learning_required="low",
        uses_systems_thinking=True,
        uses_tool_building=False,
        # Mixed context
        collaboration_type="cross_team",
        meeting_intensity="moderate",
        requires_sync_communication=True,
        timezone_spread="moderate",
    )

    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "sparingly"


def test_help_mentoring_quadrant_low_skill_high_energy(sample_profile):
    """Test task with low skill + high energy = help_mentoring quadrant."""
    chars = TaskCharacteristics(
        # Low conflict, high progress = energizing
        conflict_exposure="low",
        alignment_clarity="high",
        authority_ambiguity="low",
        progress_visibility="high",
        autonomy_level="moderate",
        decision_speed="moderate",
        # High learning but energizing growth area = not good at yet but energizing
        learning_required="high",
        uses_systems_thinking=False,
        uses_tool_building=False,
        # Good context
        collaboration_type="team",
        meeting_intensity="low",
        requires_sync_communication=False,
        timezone_spread="narrow",
    )

    # Note: This would match a growth area if we had the matching logic
    quadrant = calculate_quadrant(chars, sample_profile)

    assert quadrant == "help_mentoring"
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_energy_calculator.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_core.energy_matrix'"

**Step 3: Write minimal implementation**

Create `active/projects/wctf/wctf_core/energy_matrix/__init__.py`:

```python
"""Energy Matrix calculation engine."""

from wctf_core.energy_matrix.calculator import calculate_quadrant

__all__ = ["calculate_quadrant"]
```

Create `active/projects/wctf/wctf_core/energy_matrix/calculator.py`:

```python
"""Energy Matrix quadrant calculation algorithm.

This module implements the core algorithm for calculating which Energy Matrix
quadrant a task falls into based on task characteristics and personal profile.
"""

from typing import Dict, Any

from wctf_core.models import TaskCharacteristics, EnergyMatrixQuadrant
from wctf_core.models.profile import Profile


# Tunable algorithm parameters
STRENGTH_THRESHOLD = 2  # Score needed to be "good at"
ENERGY_THRESHOLD = 0    # Score needed to be "energizing"

DRAIN_WEIGHTS = {
    "severe": -3,
    "moderate": -2,
    "mild": -1,
}

GENERATOR_WEIGHTS = {
    "core_need": 3,
    "strong": 2,
    "moderate": 1,
}

STRENGTH_WEIGHTS = {
    "expert": 2,
    "proficient": 1,
    "learning": 0,
}


def _matches_drain(chars: TaskCharacteristics, drain_name: str) -> bool:
    """Check if task characteristics trigger a specific energy drain."""
    if drain_name == "interpersonal_conflict":
        return chars.conflict_exposure in ["high", "moderate"]
    elif drain_name == "misalignment":
        return chars.alignment_clarity in ["low"]
    elif drain_name == "authority_ambiguity":
        return chars.authority_ambiguity in ["high", "moderate"]
    elif drain_name == "financial_anxiety":
        # Financial anxiety is context-dependent, not task-dependent
        return False

    return False


def _matches_generator(chars: TaskCharacteristics, gen_name: str) -> bool:
    """Check if task characteristics activate an energy generator."""
    if gen_name == "visible_progress":
        return chars.progress_visibility in ["high"]
    elif gen_name == "aligned_collaboration":
        return (
            chars.alignment_clarity == "high"
            and chars.collaboration_type in ["team", "paired"]
        )
    elif gen_name == "tool_building":
        return chars.uses_tool_building
    elif gen_name == "structured_processes":
        return chars.decision_speed == "fast" and chars.autonomy_level == "high"

    return False


def _calculate_strength_score(chars: TaskCharacteristics, profile: Profile) -> int:
    """Calculate strength score (how "good at" you are)."""
    score = 0

    # Check core strengths usage
    for strength in profile.core_strengths:
        # Map strength names to characteristic flags
        uses_strength = False
        if strength.name == "systems_thinking":
            uses_strength = chars.uses_systems_thinking
        elif strength.name == "tool_building":
            uses_strength = chars.uses_tool_building
        elif strength.name == "glue_work":
            uses_strength = chars.uses_glue_work
        elif strength.name == "infrastructure_automation":
            uses_strength = chars.uses_infrastructure_automation
        elif strength.name == "decision_frameworks":
            uses_strength = chars.uses_decision_frameworks

        if uses_strength:
            score += STRENGTH_WEIGHTS.get(strength.level, 0)

    # Penalty for high learning requirement
    learning_penalties = {
        "high": -2,
        "moderate": -1,
        "low": 0,
        "none": 0,
    }
    score += learning_penalties.get(chars.learning_required, 0)

    # Bonus for energizing growth areas
    # (Simplified: if high learning but other signals positive, might be growth area)
    for growth_area in profile.growth_areas:
        if growth_area.energizing and chars.learning_required in ["moderate", "high"]:
            # Give a small bonus if learning is required but context is positive
            if chars.progress_visibility == "high" and chars.conflict_exposure == "low":
                score += 1
                break

    return score


def _calculate_energy_score(chars: TaskCharacteristics, profile: Profile) -> int:
    """Calculate energy score (how energizing vs draining)."""
    score = 0

    # Check energy drains
    for drain_name, drain in profile.energy_drains.items():
        if _matches_drain(chars, drain_name):
            score += DRAIN_WEIGHTS.get(drain.severity, 0)

    # Check energy generators
    for gen_name, generator in profile.energy_generators.items():
        if _matches_generator(chars, gen_name):
            score += GENERATOR_WEIGHTS.get(generator.strength, 0)

    # Check organizational coherence (ambient drain)
    for coherence_need in profile.organizational_coherence_needs:
        # Simplified: check for wide timezone + sync communication mismatch
        if coherence_need.pattern == "uncertain_problem_space":
            if (chars.timezone_spread == "wide" and
                chars.requires_sync_communication and
                coherence_need.impact_if_violated == "severe_drain"):
                score -= 2

    return score


def calculate_quadrant(
    chars: TaskCharacteristics,
    profile: Profile,
) -> str:
    """Calculate Energy Matrix quadrant from task characteristics and profile.

    Args:
        chars: Task characteristics
        profile: Personal profile with drains, generators, and strengths

    Returns:
        Quadrant name: "mutual" | "sparingly" | "burnout" | "help_mentoring"
    """
    strength_score = _calculate_strength_score(chars, profile)
    energy_score = _calculate_energy_score(chars, profile)

    good_at = strength_score >= STRENGTH_THRESHOLD
    energizes = energy_score > ENERGY_THRESHOLD

    # Map to quadrant
    if good_at and energizes:
        return EnergyMatrixQuadrant.MUTUAL.value
    elif good_at and not energizes:
        return EnergyMatrixQuadrant.SPARINGLY.value
    elif not good_at and energizes:
        return EnergyMatrixQuadrant.HELP_MENTORING.value
    else:
        return EnergyMatrixQuadrant.BURNOUT.value
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_energy_calculator.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/energy_matrix/ tests/test_energy_calculator.py
git commit -m "feat(energy-matrix): add quadrant calculation engine

Implement Energy Matrix quadrant calculation:
- calculate_quadrant() main algorithm
- Strength score calculation (skills + learning penalty)
- Energy score calculation (drains + generators)
- Tunable threshold parameters
- Helper functions for matching drains/generators

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Phase 4: Synthesis Generation

### Task 4.1: Energy Distribution Aggregation

**Files:**
- Create: `active/projects/wctf/wctf_core/energy_matrix/synthesis.py`
- Test: `active/projects/wctf/tests/test_energy_synthesis.py`

**Step 1: Write the failing test for synthesis generation**

```python
"""Tests for Energy Matrix synthesis generation."""

from datetime import date
import pytest

from wctf_core.models import (
    MountainFlags,
    Flag,
    TaskImplication,
    TaskCharacteristics,
)
from wctf_core.models.profile import Profile, EnergyDrain, EnergyGenerator, CoreStrength
from wctf_core.energy_matrix.synthesis import generate_energy_synthesis


@pytest.fixture
def sample_profile():
    """Create a sample profile."""
    return Profile(
        profile_version="1.0",
        last_updated=date(2025, 1, 8),
        energy_drains={
            "interpersonal_conflict": EnergyDrain(
                severity="severe",
                trigger="test",
                description="test",
            ),
        },
        energy_generators={
            "visible_progress": EnergyGenerator(
                strength="core_need",
                description="test",
            ),
        },
        core_strengths=[
            CoreStrength(
                name="systems_thinking",
                level="expert",
                description="test",
            ),
        ],
        growth_areas=[],
    )


@pytest.fixture
def sample_flags_with_quadrants():
    """Create sample flags with calculated quadrants."""
    return MountainFlags(
        company="TestCorp",
        evaluation_date=date(2025, 1, 8),
        evaluator_context="Test",
        profile_version_used="1.0",
        green_flags={
            "mountain_range": {
                "critical_matches": [
                    Flag(
                        flag="Good tech stack",
                        impact="High",
                        confidence="High",
                        task_implications=[
                            TaskImplication(
                                task="Build systems",
                                time_estimate_pct="30%",
                                energy_matrix_quadrant="mutual",
                                characteristics=TaskCharacteristics(
                                    conflict_exposure="low",
                                    alignment_clarity="high",
                                    authority_ambiguity="low",
                                    progress_visibility="high",
                                    autonomy_level="high",
                                    decision_speed="fast",
                                    learning_required="low",
                                    collaboration_type="team",
                                    meeting_intensity="low",
                                    requires_sync_communication=False,
                                    timezone_spread="narrow",
                                ),
                            ),
                        ],
                    ),
                ],
                "strong_positives": [],
            },
            "chosen_peak": {"critical_matches": [], "strong_positives": []},
            "rope_team_confidence": {"critical_matches": [], "strong_positives": []},
            "daily_climb": {"critical_matches": [], "strong_positives": []},
            "story_worth_telling": {"critical_matches": [], "strong_positives": []},
        },
        red_flags={
            "mountain_range": {
                "dealbreakers": [
                    Flag(
                        flag="Lots of conflict",
                        impact="High",
                        confidence="High",
                        task_implications=[
                            TaskImplication(
                                task="Navigate conflicts",
                                time_estimate_pct="40%",
                                energy_matrix_quadrant="burnout",
                                characteristics=TaskCharacteristics(
                                    conflict_exposure="high",
                                    alignment_clarity="low",
                                    authority_ambiguity="high",
                                    progress_visibility="low",
                                    autonomy_level="low",
                                    decision_speed="slow",
                                    learning_required="moderate",
                                    collaboration_type="cross_team",
                                    meeting_intensity="high",
                                    requires_sync_communication=True,
                                    timezone_spread="wide",
                                ),
                            ),
                        ],
                    ),
                ],
                "concerning": [],
            },
            "chosen_peak": {"dealbreakers": [], "concerning": []},
            "rope_team_confidence": {"dealbreakers": [], "concerning": []},
            "daily_climb": {"dealbreakers": [], "concerning": []},
            "story_worth_telling": {"dealbreakers": [], "concerning": []},
        },
        missing_critical_data=[],
    )


def test_generate_energy_synthesis_calculates_distribution(sample_flags_with_quadrants, sample_profile):
    """Test that synthesis calculates quadrant distribution."""
    synthesis = generate_energy_synthesis(sample_flags_with_quadrants, sample_profile)

    assert "energy_matrix_analysis" in synthesis
    assert "predicted_daily_distribution" in synthesis["energy_matrix_analysis"]

    dist = synthesis["energy_matrix_analysis"]["predicted_daily_distribution"]
    assert "mutual_green_flags" in dist
    assert "burnout_red_flags" in dist

    # Should have 30% mutual and 40% burnout based on time estimates
    assert dist["mutual_green_flags"]["percentage"] == 30
    assert dist["burnout_red_flags"]["percentage"] == 40


def test_generate_energy_synthesis_checks_thresholds(sample_flags_with_quadrants, sample_profile):
    """Test that synthesis checks sustainability thresholds."""
    synthesis = generate_energy_synthesis(sample_flags_with_quadrants, sample_profile)

    thresholds = synthesis["energy_matrix_analysis"]["threshold_analysis"]

    # 30% mutual < 60% required
    assert thresholds["meets_green_minimum"] is False

    # 40% burnout > 20% allowed
    assert thresholds["exceeds_red_maximum"] is True


def test_generate_energy_synthesis_sets_sustainability_rating(sample_flags_with_quadrants, sample_profile):
    """Test that synthesis sets energy_sustainability rating."""
    synthesis = generate_energy_synthesis(sample_flags_with_quadrants, sample_profile)

    # With 40% burnout and 30% mutual, should be LOW
    assert synthesis["energy_matrix_analysis"]["energy_sustainability"] == "LOW"
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_energy_synthesis.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'wctf_core.energy_matrix.synthesis'"

**Step 3: Write minimal implementation**

Create `active/projects/wctf/wctf_core/energy_matrix/synthesis.py`:

```python
"""Energy Matrix synthesis generation.

This module aggregates task implications across all flags to generate
the overall Energy Matrix analysis in the synthesis section.
"""

from typing import Dict, Any, List
import re

from wctf_core.models import MountainFlags, Flag, TaskImplication
from wctf_core.models.profile import Profile


def _parse_time_estimate(time_estimate_pct: str) -> int:
    """Parse time estimate percentage string.

    Handles formats like:
    - "30%" -> 30
    - "20-30%" -> 25 (midpoint)
    - "15-20%" -> 17.5 -> 17 (rounded)
    """
    # Extract numbers
    numbers = re.findall(r'\d+', time_estimate_pct)
    if not numbers:
        return 0

    # If range, take midpoint
    if len(numbers) == 2:
        return (int(numbers[0]) + int(numbers[1])) // 2

    return int(numbers[0])


def _aggregate_quadrant_distribution(flags: MountainFlags) -> Dict[str, Dict[str, Any]]:
    """Aggregate task implications by quadrant."""
    distribution = {
        "mutual_green_flags": {"percentage": 0, "tasks_count": 0},
        "sparingly_yellow_flags": {"percentage": 0, "tasks_count": 0},
        "burnout_red_flags": {"percentage": 0, "tasks_count": 0},
        "help_mentoring_yellow_flags": {"percentage": 0, "tasks_count": 0},
    }

    # Collect all task implications
    all_implications: List[TaskImplication] = []

    for mountain_element in flags.green_flags.values():
        for severity_list in mountain_element.values():
            for flag in severity_list:
                all_implications.extend(flag.task_implications)

    for mountain_element in flags.red_flags.values():
        for severity_list in mountain_element.values():
            for flag in severity_list:
                all_implications.extend(flag.task_implications)

    # Aggregate by quadrant
    for impl in all_implications:
        if impl.energy_matrix_quadrant is None:
            continue

        time_pct = _parse_time_estimate(impl.time_estimate_pct)

        if impl.energy_matrix_quadrant == "mutual":
            distribution["mutual_green_flags"]["percentage"] += time_pct
            distribution["mutual_green_flags"]["tasks_count"] += 1
        elif impl.energy_matrix_quadrant == "sparingly":
            distribution["sparingly_yellow_flags"]["percentage"] += time_pct
            distribution["sparingly_yellow_flags"]["tasks_count"] += 1
        elif impl.energy_matrix_quadrant == "burnout":
            distribution["burnout_red_flags"]["percentage"] += time_pct
            distribution["burnout_red_flags"]["tasks_count"] += 1
        elif impl.energy_matrix_quadrant == "help_mentoring":
            distribution["help_mentoring_yellow_flags"]["percentage"] += time_pct
            distribution["help_mentoring_yellow_flags"]["tasks_count"] += 1

    return distribution


def _check_thresholds(distribution: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
    """Check sustainability thresholds."""
    mutual_pct = distribution["mutual_green_flags"]["percentage"]
    burnout_pct = distribution["burnout_red_flags"]["percentage"]
    sparingly_pct = distribution["sparingly_yellow_flags"]["percentage"]
    help_mentoring_pct = distribution["help_mentoring_yellow_flags"]["percentage"]

    return {
        "meets_green_minimum": mutual_pct >= 60,
        "exceeds_red_maximum": burnout_pct > 20,
        "exceeds_yellow_maximum": (sparingly_pct + help_mentoring_pct) > 30,
    }


def _calculate_sustainability_rating(
    distribution: Dict[str, Dict[str, Any]],
    thresholds: Dict[str, bool],
) -> str:
    """Calculate overall energy sustainability rating."""
    mutual_pct = distribution["mutual_green_flags"]["percentage"]
    burnout_pct = distribution["burnout_red_flags"]["percentage"]

    # LOW: exceeds burnout threshold OR far below mutual threshold
    if thresholds["exceeds_red_maximum"] or mutual_pct < 40:
        return "LOW"

    # MEDIUM: meets minimums but not ideal
    if thresholds["meets_green_minimum"] and not thresholds["exceeds_red_maximum"]:
        if thresholds["exceeds_yellow_maximum"]:
            return "MEDIUM"
        return "HIGH"

    return "MEDIUM"


def generate_energy_synthesis(flags: MountainFlags, profile: Profile) -> Dict[str, Any]:
    """Generate Energy Matrix analysis for synthesis section.

    Args:
        flags: Company flags with calculated task quadrants
        profile: Personal profile

    Returns:
        Dictionary with energy_matrix_analysis to add to synthesis
    """
    distribution = _aggregate_quadrant_distribution(flags)
    thresholds = _check_thresholds(distribution)
    sustainability = _calculate_sustainability_rating(distribution, thresholds)

    # Generate key insights
    key_insights = []
    total_draining = (
        distribution["sparingly_yellow_flags"]["percentage"]
        + distribution["burnout_red_flags"]["percentage"]
    )
    if total_draining >= 50:
        key_insights.append(
            f"{total_draining}% of work in draining quadrants (sparingly + burnout)"
        )

    if distribution["burnout_red_flags"]["percentage"] > 20:
        key_insights.append(
            f"{distribution['burnout_red_flags']['percentage']}% burnout quadrant work exceeds 20% threshold"
        )

    if distribution["mutual_green_flags"]["percentage"] < 60:
        key_insights.append(
            f"Insufficient mutual quadrant work ({distribution['mutual_green_flags']['percentage']}% vs 60% needed)"
        )

    # Generate decision factors
    decision_factors = []
    if thresholds["exceeds_red_maximum"]:
        decision_factors.append(
            f"REJECT: {distribution['burnout_red_flags']['percentage']}% burnout quadrant exceeds 20% threshold"
        )

    if not thresholds["meets_green_minimum"]:
        decision_factors.append(
            f"RED: Only {distribution['mutual_green_flags']['percentage']}% mutual quadrant (need ≥60%)"
        )

    return {
        "energy_matrix_analysis": {
            "profile_version_used": profile.profile_version,
            "predicted_daily_distribution": distribution,
            "threshold_analysis": thresholds,
            "energy_sustainability": sustainability,
            "key_insights": key_insights,
            "decision_factors": decision_factors,
        }
    }
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_energy_synthesis.py -v`

Expected: PASS (3 tests)

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/energy_matrix/synthesis.py tests/test_energy_synthesis.py
git commit -m "feat(energy-matrix): add synthesis generation

Implement Energy Matrix synthesis generation:
- Aggregate task implications by quadrant
- Calculate percentage distribution
- Check sustainability thresholds (60% mutual, 20% burnout)
- Generate key insights and decision factors
- Calculate overall sustainability rating (HIGH/MEDIUM/LOW)

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Phase 5: Workflow Integration

### Task 5.1: Auto-Calculate Quadrants in save_flags

**Files:**
- Modify: `active/projects/wctf/wctf_core/operations/flags.py`
- Test: `active/projects/wctf/tests/test_flag_operations.py`

**Step 1: Write the failing test for auto-calculation**

Add to existing `active/projects/wctf/tests/test_flag_operations.py` (or create if needed):

```python
def test_save_flags_auto_calculates_quadrants(temp_wctf_dir, monkeypatch):
    """Test that save_flags auto-calculates Energy Matrix quadrants."""
    # Setup profile
    profile_path = temp_wctf_dir / "data" / "profile.yaml"
    profile_path.parent.mkdir(parents=True, exist_ok=True)

    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {},
        "energy_generators": {
            "visible_progress": {
                "strength": "core_need",
                "description": "test",
            },
        },
        "core_strengths": [
            {
                "name": "systems_thinking",
                "level": "expert",
                "description": "test",
            },
        ],
        "growth_areas": [],
    }

    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Create flags with task implications (no quadrant set)
    flags_yaml = """
company: "TestCorp"
evaluation_date: "2025-01-08"
evaluator_context: "Test"
profile_version_used: "1.0"
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Good tech"
        impact: "High"
        confidence: "High"
        task_implications:
          - task: "Build stuff"
            time_estimate_pct: "30%"
            characteristics:
              conflict_exposure: "low"
              alignment_clarity: "high"
              authority_ambiguity: "low"
              progress_visibility: "high"
              autonomy_level: "high"
              decision_speed: "fast"
              learning_required: "low"
              uses_systems_thinking: true
              collaboration_type: "team"
              meeting_intensity: "low"
              requires_sync_communication: false
              timezone_spread: "narrow"
    strong_positives: []
  chosen_peak:
    critical_matches: []
    strong_positives: []
  rope_team_confidence:
    critical_matches: []
    strong_positives: []
  daily_climb:
    critical_matches: []
    strong_positives: []
  story_worth_telling:
    critical_matches: []
    strong_positives: []
red_flags:
  mountain_range:
    dealbreakers: []
    concerning: []
  chosen_peak:
    dealbreakers: []
    concerning: []
  rope_team_confidence:
    dealbreakers: []
    concerning: []
  daily_climb:
    dealbreakers: []
    concerning: []
  story_worth_telling:
    dealbreakers: []
    concerning: []
missing_critical_data: []
"""

    # Import function
    from wctf_core.operations.flags import save_flags

    # Execute
    result = save_flags("TestCorp", flags_yaml)

    # Verify
    assert "success" in result.lower() or "saved" in result.lower()

    # Load saved file and check quadrant was calculated
    flags_path = temp_wctf_dir / "data" / "TestCorp" / "testcorp.flags.yaml"
    with open(flags_path) as f:
        saved_data = yaml.safe_load(f)

    task_impl = saved_data["green_flags"]["mountain_range"]["critical_matches"][0]["task_implications"][0]
    assert task_impl["energy_matrix_quadrant"] == "mutual"
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_flag_operations.py::test_save_flags_auto_calculates_quadrants -v`

Expected: FAIL - quadrant not calculated yet

**Step 3: Modify save_flags to auto-calculate quadrants**

In `active/projects/wctf/wctf_core/operations/flags.py`, add imports and modify the save function:

```python
# Add these imports at the top
from wctf_core.models.profile import Profile
from wctf_core.energy_matrix.calculator import calculate_quadrant
from wctf_core.energy_matrix.synthesis import generate_energy_synthesis
from wctf_core.operations.profile import get_profile


def save_flags(company_name: str, flags_yaml: str) -> str:
    """Save flags with auto-calculated Energy Matrix quadrants and synthesis.

    Enhanced behavior:
    - Validates task_implications structure
    - Auto-calculates energy_matrix_quadrant for each task
    - Generates energy_matrix_analysis in synthesis section
    - Checks thresholds and sets energy_sustainability

    Args:
        company_name: Company name
        flags_yaml: Flags YAML content

    Returns:
        Success/error message
    """
    try:
        # Parse flags YAML
        flags_data = yaml.safe_load(flags_yaml)

        # Validate structure
        # ... existing validation code ...

        # Load profile if present
        profile = None
        if flags_data.get("profile_version_used"):
            profile_result = get_profile()
            if "error" not in profile_result.lower():
                # Parse profile from result (strip success message)
                profile_yaml = profile_result.split("\n", 2)[2] if "\n" in profile_result else profile_result
                profile_data = yaml.safe_load(profile_yaml)
                profile = Profile(**profile_data)

        # Auto-calculate quadrants for all task implications
        if profile:
            for flag_color in ["green_flags", "red_flags"]:
                for mountain_element in flags_data.get(flag_color, {}).values():
                    for severity_list in mountain_element.values():
                        for flag in severity_list:
                            for impl in flag.get("task_implications", []):
                                # Calculate quadrant
                                from wctf_core.models import TaskCharacteristics
                                chars = TaskCharacteristics(**impl["characteristics"])
                                quadrant = calculate_quadrant(chars, profile)
                                impl["energy_matrix_quadrant"] = quadrant

        # Generate synthesis if profile present
        if profile:
            from wctf_core.models import MountainFlags
            flags_model = MountainFlags(**flags_data)
            synthesis = generate_energy_synthesis(flags_model, profile)

            # Merge with existing synthesis if present
            if "synthesis" not in flags_data:
                flags_data["synthesis"] = {}
            flags_data["synthesis"].update(synthesis)

        # Save to file
        # ... existing save code ...

        return success_response(
            f"Flags saved for {company_name}",
            f"Saved to {flags_path}" +
            (f"\nEnergy Matrix: {flags_data.get('synthesis', {}).get('energy_matrix_analysis', {}).get('energy_sustainability', 'N/A')}" if profile else "")
        )

    except Exception as e:
        return error_response(f"Error saving flags: {e}")
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_flag_operations.py::test_save_flags_auto_calculates_quadrants -v`

Expected: PASS

**Step 5: Commit**

```bash
cd active/projects/wctf
git add wctf_core/operations/flags.py tests/test_flag_operations.py
git commit -m "feat(energy-matrix): auto-calculate quadrants in save_flags

Enhance save_flags operation:
- Load profile if profile_version_used present
- Auto-calculate energy_matrix_quadrant for all task implications
- Generate energy_matrix_analysis in synthesis
- Include sustainability rating in success message

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 5.2: Enhance Flag Extraction Prompt

**Files:**
- Modify: `active/projects/wctf/wctf_core/prompts/mountain_flags.md`
- Test: Manual verification

**Step 1: Add Energy Matrix guidance to extraction prompt**

Modify `active/projects/wctf/wctf_core/prompts/mountain_flags.md` to include task implications guidance:

```markdown
# Mountain Flags Extraction Guide

... [existing content] ...

## Energy Matrix Integration

For each flag, identify **task implications** - what you'll actually DO day-to-day because of this fact.

### Task Implication Structure

For each flag, add `task_implications` with:

```yaml
task_implications:
  - task: "Clear description of what you'll do"
    time_estimate_pct: "15-20%"  # Or single value like "10%"
    characteristics:
      # Conflict & alignment
      conflict_exposure: "high" | "moderate" | "low" | "none"
      alignment_clarity: "high" | "moderate" | "low"
      authority_ambiguity: "high" | "moderate" | "low"

      # Progress & autonomy
      progress_visibility: "high" | "moderate" | "low"
      autonomy_level: "high" | "moderate" | "low"
      decision_speed: "fast" | "moderate" | "slow"

      # Skill alignment (check profile.yaml for your strengths)
      learning_required: "none" | "low" | "moderate" | "high"
      uses_systems_thinking: true | false
      uses_tool_building: true | false
      uses_glue_work: true | false
      uses_infrastructure_automation: true | false
      uses_decision_frameworks: true | false

      # Work context
      collaboration_type: "solo" | "paired" | "team" | "cross_team"
      meeting_intensity: "low" | "moderate" | "high"
      requires_sync_communication: true | false
      timezone_spread: "co_located" | "narrow" | "moderate" | "wide"

    notes: "Optional notes about this task"
```

### Reference Profile

Use the `get_profile` tool to see your personal energy drains, generators, and strengths.
Match task characteristics against your profile to ensure accurate quadrant calculation.

### Example

```yaml
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Modern tech stack: Kubernetes, Python, Go"
        impact: "Matches infrastructure expertise"
        confidence: "High - explicit in job description"
        task_implications:
          - task: "Design K8s operators for platform services"
            time_estimate_pct: "20-30%"
            characteristics:
              conflict_exposure: "low"
              alignment_clarity: "high"
              authority_ambiguity: "low"
              progress_visibility: "high"
              autonomy_level: "high"
              decision_speed: "fast"
              uses_systems_thinking: true
              uses_tool_building: true
              uses_infrastructure_automation: true
              learning_required: "low"
              collaboration_type: "team"
              meeting_intensity: "low"
              requires_sync_communication: false
              timezone_spread: "narrow"
            notes: "Platform work with clear scope, autonomous execution"
```

The system will auto-calculate the Energy Matrix quadrant (mutual/sparingly/burnout/help_mentoring)
when you save the flags.
```

**Step 2: Verify prompt loads correctly**

Run: `cd active/projects/wctf && python -c "from wctf_core.operations.flags import _load_extraction_prompt; print(_load_extraction_prompt()[:100])"`

Expected: Prompt loads and includes "Energy Matrix" section

**Step 3: Commit**

```bash
cd active/projects/wctf
git add wctf_core/prompts/mountain_flags.md
git commit -m "feat(energy-matrix): enhance flag extraction prompt

Add Energy Matrix guidance to extraction prompt:
- Task implications structure and fields
- Characteristics checklist with all dimensions
- Reference to get_profile tool
- Example task implication with all fields
- Auto-calculation note

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 5.3: Energy Summary Tool

**Files:**
- Modify: `active/projects/wctf/wctf_mcp/tools/profile_tools.py` (add new tool)
- Modify: `active/projects/wctf/wctf_mcp/server.py` (register tool)
- Test: `active/projects/wctf/tests/test_profile_tools.py`

**Step 1: Write the failing test for energy summary tool**

Add to `active/projects/wctf/tests/test_profile_tools.py`:

```python
@pytest.mark.asyncio
async def test_get_energy_summary_tool_returns_analysis(temp_wctf_dir, monkeypatch):
    """Test get_energy_summary_tool returns just the energy analysis."""
    # Setup company with energy analysis
    company_dir = temp_wctf_dir / "data" / "TestCorp"
    company_dir.mkdir(parents=True)

    flags_data = {
        "company": "TestCorp",
        "evaluation_date": "2025-01-08",
        "synthesis": {
            "energy_matrix_analysis": {
                "energy_sustainability": "MEDIUM",
                "predicted_daily_distribution": {
                    "mutual_green_flags": {"percentage": 50, "tasks_count": 3},
                },
            },
        },
    }

    with open(company_dir / "testcorp.flags.yaml", "w") as f:
        yaml.dump(flags_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(temp_wctf_dir))

    # Execute
    from wctf_mcp.tools.profile_tools import get_energy_summary_tool
    result = await get_energy_summary_tool("TestCorp")

    # Verify
    assert len(result) == 1
    assert "MEDIUM" in result[0].text
    assert "50" in result[0].text  # Should show percentage
```

**Step 2: Run test to verify it fails**

Run: `cd active/projects/wctf && pytest tests/test_profile_tools.py::test_get_energy_summary_tool_returns_analysis -v`

Expected: FAIL - function doesn't exist yet

**Step 3: Implement energy summary tool**

Add to `active/projects/wctf/wctf_mcp/tools/profile_tools.py`:

```python
import yaml
from pathlib import Path
import os

from wctf_core.utils.paths import get_flags_path
from wctf_core.utils.responses import error_response, success_response


async def get_energy_summary_tool(company_name: str) -> list[types.TextContent]:
    """Get just the energy_matrix_analysis from synthesis.

    Quick view of energy distribution without full flags.

    Args:
        company_name: Company to analyze

    Returns:
        List containing single TextContent with energy analysis.
    """
    try:
        flags_path = get_flags_path(company_name)

        if not flags_path.exists():
            result = error_response(
                f"No flags found for {company_name}",
                f"Run flag extraction first"
            )
            return [types.TextContent(type="text", text=result)]

        with open(flags_path) as f:
            flags_data = yaml.safe_load(f)

        synthesis = flags_data.get("synthesis", {})
        energy_analysis = synthesis.get("energy_matrix_analysis")

        if not energy_analysis:
            result = error_response(
                f"No Energy Matrix analysis for {company_name}",
                "Flags may not have profile_version_used set"
            )
            return [types.TextContent(type="text", text=result)]

        # Format energy analysis
        result = success_response(
            f"Energy Matrix Analysis for {company_name}",
            yaml.dump({"energy_matrix_analysis": energy_analysis}, default_flow_style=False)
        )

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        result = error_response(f"Error getting energy summary: {e}")
        return [types.TextContent(type="text", text=result)]
```

**Step 4: Run test to verify it passes**

Run: `cd active/projects/wctf && pytest tests/test_profile_tools.py::test_get_energy_summary_tool_returns_analysis -v`

Expected: PASS

**Step 5: Register tool in MCP server**

Add to `active/projects/wctf/wctf_mcp/server.py`:

```python
# Update import
from wctf_mcp.tools.profile_tools import (
    get_profile_tool,
    update_profile_tool,
    get_energy_summary_tool,
)

# Add tool handler
elif name == "get_energy_summary":
    company_name = arguments.get("company_name", "")
    return await get_energy_summary_tool(company_name)
```

**Step 6: Commit**

```bash
cd active/projects/wctf
git add wctf_mcp/tools/profile_tools.py wctf_mcp/server.py tests/test_profile_tools.py
git commit -m "feat(energy-matrix): add energy summary MCP tool

Add get_energy_summary_tool:
- Quick view of energy_matrix_analysis
- Returns just the synthesis section
- Useful for checking sustainability without full flags

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Phase 6: Testing & Validation

### Task 6.1: Integration Test with Sample Company

**Files:**
- Create: `active/projects/wctf/tests/test_energy_integration.py`

**Step 1: Write integration test**

```python
"""Integration tests for complete Energy Matrix workflow."""

from datetime import date
import pytest
import yaml

from wctf_core.operations.profile import get_profile, update_profile
from wctf_core.operations.flags import save_flags
from wctf_core.operations.company import get_company_flags


@pytest.fixture
def setup_wctf_with_profile(tmp_path, monkeypatch):
    """Setup WCTF directory with profile."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create profile
    profile_data = {
        "profile_version": "1.0",
        "last_updated": "2025-01-08",
        "energy_drains": {
            "interpersonal_conflict": {
                "severity": "severe",
                "trigger": "childhood_trauma",
                "description": "Conflicts drain energy",
            },
        },
        "energy_generators": {
            "visible_progress": {
                "strength": "core_need",
                "description": "Progress energizes",
            },
        },
        "core_strengths": [
            {
                "name": "systems_thinking",
                "level": "expert",
                "description": "Expert systems thinker",
            },
        ],
        "growth_areas": [],
    }

    profile_path = data_dir / "profile.yaml"
    with open(profile_path, "w") as f:
        yaml.dump(profile_data, f)

    monkeypatch.setenv("WCTF_ROOT", str(tmp_path))

    return tmp_path


def test_complete_energy_workflow(setup_wctf_with_profile):
    """Test complete workflow: profile -> flags with tasks -> synthesis."""

    # Step 1: Get profile
    profile_result = get_profile()
    assert "1.0" in profile_result
    assert "systems_thinking" in profile_result

    # Step 2: Save flags with task implications
    flags_yaml = """
company: "AppleDublin"
evaluation_date: "2025-01-08"
evaluator_context: "Test evaluation"
profile_version_used: "1.0"
green_flags:
  mountain_range:
    critical_matches:
      - flag: "Modern tech stack"
        impact: "Matches expertise"
        confidence: "High"
        task_implications:
          - task: "Build K8s operators"
            time_estimate_pct: "20%"
            characteristics:
              conflict_exposure: "low"
              alignment_clarity: "high"
              authority_ambiguity: "low"
              progress_visibility: "high"
              autonomy_level: "high"
              decision_speed: "fast"
              uses_systems_thinking: true
              learning_required: "low"
              collaboration_type: "team"
              meeting_intensity: "low"
              requires_sync_communication: false
              timezone_spread: "narrow"
    strong_positives: []
  chosen_peak:
    critical_matches: []
    strong_positives: []
  rope_team_confidence:
    critical_matches: []
    strong_positives: []
  daily_climb:
    critical_matches: []
    strong_positives: []
  story_worth_telling:
    critical_matches: []
    strong_positives: []
red_flags:
  mountain_range:
    dealbreakers:
      - flag: "Siloed teams with conflicts"
        impact: "High conflict exposure"
        confidence: "High"
        task_implications:
          - task: "Navigate cross-silo conflicts"
            time_estimate_pct: "40%"
            characteristics:
              conflict_exposure: "high"
              alignment_clarity: "low"
              authority_ambiguity: "high"
              progress_visibility: "low"
              autonomy_level: "low"
              decision_speed: "slow"
              uses_systems_thinking: false
              learning_required: "moderate"
              collaboration_type: "cross_team"
              meeting_intensity: "high"
              requires_sync_communication: true
              timezone_spread: "moderate"
    concerning: []
  chosen_peak:
    dealbreakers: []
    concerning: []
  rope_team_confidence:
    dealbreakers: []
    concerning: []
  daily_climb:
    dealbreakers: []
    concerning: []
  story_worth_telling:
    dealbreakers: []
    concerning: []
missing_critical_data: []
"""

    save_result = save_flags("AppleDublin", flags_yaml)
    assert "success" in save_result.lower() or "saved" in save_result.lower()

    # Step 3: Get flags back and verify synthesis
    flags_result = get_company_flags("AppleDublin")
    assert "energy_matrix_analysis" in flags_result
    assert "mutual" in flags_result  # Should have mutual quadrant task
    assert "burnout" in flags_result  # Should have burnout quadrant task
    assert "LOW" in flags_result or "MEDIUM" in flags_result  # Sustainability rating

    # Verify specific values
    flags_data = yaml.safe_load(flags_result.split("---")[1])  # Get YAML part
    synthesis = flags_data["synthesis"]["energy_matrix_analysis"]

    # Should have 20% mutual and 40% burnout
    assert synthesis["predicted_daily_distribution"]["mutual_green_flags"]["percentage"] == 20
    assert synthesis["predicted_daily_distribution"]["burnout_red_flags"]["percentage"] == 40

    # Should fail thresholds
    assert synthesis["threshold_analysis"]["meets_green_minimum"] is False
    assert synthesis["threshold_analysis"]["exceeds_red_maximum"] is True

    # Should have LOW sustainability
    assert synthesis["energy_sustainability"] == "LOW"
```

**Step 2: Run integration test**

Run: `cd active/projects/wctf && pytest tests/test_energy_integration.py -v`

Expected: PASS

**Step 3: Commit**

```bash
cd active/projects/wctf
git add tests/test_energy_integration.py
git commit -m "test(energy-matrix): add integration test

Add complete Energy Matrix integration test:
- Load profile
- Save flags with task implications
- Verify quadrant auto-calculation
- Verify synthesis generation
- Check threshold analysis
- Validate sustainability rating

Tests the full workflow end-to-end.

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Phase 7: Documentation

### Task 7.1: Update Framework Documentation

**Files:**
- Modify: `active/projects/wctf/WCTF_FRAMEWORK.md`

**Step 1: Add Energy Matrix section to framework doc**

Add new section to `active/projects/wctf/WCTF_FRAMEWORK.md`:

```markdown
## Energy Matrix Integration (v4.0)

### Overview

The Energy Matrix evaluates whether daily work will energize or drain you, answering "Will I have the energy to climb this mountain?"

**Key insight:** A role with 70% draining tasks (even with great compensation and mission) leads to burnout. Accept only roles with ≥60% energizing work that leverages your strengths.

### The Four Quadrants

```
                           Good at
        ┌──────────────────┬──────────────────┐
        │   SPARINGLY      │     MUTUAL       │
Drains  │   (Top Left)     │   (Top Right)    │
Energy  │  Skilled but     │  SWEET SPOT      │
        │  draining work   │  Energizing AND  │
        │  (limit this)    │  leveraging      │
        │                  │  strengths       │
        ├──────────────────┼──────────────────┤
        │   BURNOUT        │  HELP/MENTORING  │
Brings  │   (Bottom Left)  │  (Bottom Right)  │
Energy  │  Weak AND        │  Energizing but  │
        │  draining        │  still learning  │
        │  (eliminate)     │  (growth area)   │
        └──────────────────┴──────────────────┘
                          Bad at
```

### Profile Storage

Your personal profile lives in `data/profile.yaml` and includes:

- **Energy drains:** Activities that deplete you (conflict, misalignment, etc.)
- **Energy generators:** Activities that restore energy (progress, tool building, etc.)
- **Core strengths:** Established expertise (systems thinking, infrastructure, etc.)
- **Growth areas:** Skills you're actively learning (multi-agent orchestration, etc.)
- **Communication preferences:** Async capability, timezone tolerance, meeting load
- **Organizational coherence needs:** Systemic patterns that enable/drain energy

The profile is versioned in git to track self-knowledge evolution.

### Task Implications

Each flag now includes `task_implications` describing what you'll DO day-to-day:

```yaml
task_implications:
  - task: "Design K8s operators for platform services"
    time_estimate_pct: "20-30%"
    energy_matrix_quadrant: "mutual"  # Auto-calculated
    characteristics:
      conflict_exposure: "low"
      progress_visibility: "high"
      uses_systems_thinking: true
      uses_infrastructure_automation: true
      # ... 20+ characteristics
```

Characteristics are matched against your profile to auto-calculate the quadrant.

### Synthesis

The synthesis section includes Energy Matrix analysis:

```yaml
energy_matrix_analysis:
  predicted_daily_distribution:
    mutual_green_flags: {percentage: 20, tasks_count: 3}
    burnout_red_flags: {percentage: 40, tasks_count: 6}
    # ...

  threshold_analysis:
    meets_green_minimum: false  # Need ≥60% mutual
    exceeds_red_maximum: true   # Allow ≤20% burnout

  energy_sustainability: "LOW"  # HIGH/MEDIUM/LOW

  decision_factors:
    - "REJECT: 40% burnout quadrant exceeds 20% threshold"
    - "RED: Only 20% mutual quadrant (need ≥60%)"
```

### Sustainability Thresholds

- **≥60% Mutual (green):** Energizing work using your strengths
- **≤20% Burnout (red):** Draining work you're not good at
- **≤30% Sparingly + Help/Mentoring (yellow):** Combined

Exceeding thresholds triggers reject recommendation.

### MCP Tools

Three new tools support Energy Matrix:

- **get_profile:** Returns current profile for reference during flag extraction
- **update_profile:** Updates profile with version increment (1.0 → 1.1)
- **get_energy_summary:** Quick view of energy_matrix_analysis for a company

### Workflow

1. **Get profile:** Reference your drains, generators, and strengths
2. **Extract flags:** Include task_implications with detailed characteristics
3. **Save flags:** System auto-calculates quadrants and generates synthesis
4. **Review synthesis:** Check energy_sustainability and threshold violations
5. **Make decision:** Accept only roles with sustainable energy distribution
```

**Step 2: Commit**

```bash
cd active/projects/wctf
git add WCTF_FRAMEWORK.md
git commit -m "docs(energy-matrix): add Energy Matrix section to framework

Document Energy Matrix integration:
- Four quadrants explanation
- Profile storage structure
- Task implications format
- Synthesis analysis
- Sustainability thresholds
- MCP tools
- Workflow integration

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

### Task 7.2: Update README

**Files:**
- Modify: `active/projects/wctf/README.md`

**Step 1: Add v4.0 changelog to README**

Add to changelog section in `active/projects/wctf/README.md`:

```markdown
## Version 4.0 - Energy Matrix Integration

**Released:** 2025-01-08

### New Features

- **Energy Matrix Integration:** Evaluates whether daily work will energize or drain you
- **Profile Storage:** Personal profile in `data/profile.yaml` with energy drains, generators, and strengths
- **Task Implications:** Each flag now includes tasks you'll do with 20+ characteristics
- **Auto-Quadrant Calculation:** System automatically calculates which quadrant each task falls into
- **Sustainability Thresholds:** Checks if role meets ≥60% mutual, ≤20% burnout requirements
- **Energy Synthesis:** Aggregates task distribution and generates accept/reject signals

### New MCP Tools

- `get_profile` - Get current profile for reference
- `update_profile` - Update profile with version increment
- `get_energy_summary` - Quick energy analysis view

### Breaking Changes

- `MountainFlags` model now includes `profile_version_used` field
- `Flag` model now includes `task_implications` field
- Synthesis section now includes `energy_matrix_analysis`

### Migration Guide

Existing flags files will continue to work. To use Energy Matrix features:

1. Create `data/profile.yaml` (see design doc for template)
2. Add `profile_version_used: "1.0"` to new flags files
3. Include `task_implications` with characteristics for each flag
4. System will auto-calculate quadrants and synthesis

### What's Next (v4.1)

- Tune algorithm thresholds based on real evaluations
- Add organizational coherence pattern detection
- Support for re-evaluating companies with updated profile
- Calibration tools for time estimate accuracy
```

**Step 2: Commit**

```bash
cd active/projects/wctf
git add README.md
git commit -m "docs(energy-matrix): add v4.0 changelog to README

Document v4.0 release:
- Energy Matrix features
- New MCP tools
- Breaking changes
- Migration guide
- Future roadmap

Generated with Claude Code via Happy
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Happy <yesreply@happy.engineering>"
```

---

## Summary

This implementation plan covers all 7 phases of the Energy Matrix integration:

1. **Phase 1:** Core data models (Profile, TaskCharacteristics, enhanced Flags)
2. **Phase 2:** Profile management (storage operations, MCP tools, initial profile)
3. **Phase 3:** Quadrant calculation engine (algorithm with tunable parameters)
4. **Phase 4:** Synthesis generation (distribution aggregation, threshold checking)
5. **Phase 5:** Workflow integration (auto-calculation, enhanced prompts, tools)
6. **Phase 6:** Testing & validation (integration tests with sample company)
7. **Phase 7:** Documentation (framework docs, README, changelog)

Each task follows TDD:
1. Write failing test
2. Run test (verify failure)
3. Write minimal implementation
4. Run test (verify pass)
5. Commit with conventional message

The plan assumes zero context about WCTF and provides:
- Exact file paths for all changes
- Complete code examples (not placeholders)
- Exact test commands with expected output
- Clear commit messages with co-authorship

**Total estimated time:** 8-12 hours for experienced developer

---

**Plan complete and saved to `docs/plans/2025-01-08-energy-matrix-integration.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
