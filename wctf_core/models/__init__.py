"""Models package for WCTF core."""

from wctf_core.models.company import (
    ConfidenceLevel,
    FactType,
    ImpactLevel,
    FlagSeverity,
    Fact,
    FactsCategory,
    CompanyFacts,
    InsiderFact,
    InsiderFactsCategory,
    InterviewMetadata,
    CompanyInsiderFacts,
    Flag,
    MountainElementGreenFlags,
    MountainElementRedFlags,
    MissingCriticalData,
    CompanyFlags,
)
from wctf_core.models.task import (
    ConflictLevel,
    ClarityLevel,
    DecisionSpeed,
    LearningRequired,
    CollaborationType,
    MeetingIntensity,
    TimezoneSpread,
    EnergyMatrixQuadrant,
    TaskCharacteristics,
    TaskImplication,
)
from wctf_core.models.orgmap import (
    Leadership,
    OrgMetrics,
    CoordinationSignals,
    InsiderConnection,
    RopeTeam,
    Peak,
)

# Rebuild models that have forward references to TaskImplication
Flag.model_rebuild()
MountainElementGreenFlags.model_rebuild()
MountainElementRedFlags.model_rebuild()
CompanyFlags.model_rebuild()

__all__ = [
    # Company models
    "ConfidenceLevel",
    "FactType",
    "ImpactLevel",
    "FlagSeverity",
    "Fact",
    "FactsCategory",
    "CompanyFacts",
    "InsiderFact",
    "InsiderFactsCategory",
    "InterviewMetadata",
    "CompanyInsiderFacts",
    "Flag",
    "MountainElementGreenFlags",
    "MountainElementRedFlags",
    "MissingCriticalData",
    "CompanyFlags",
    # Task models
    "ConflictLevel",
    "ClarityLevel",
    "DecisionSpeed",
    "LearningRequired",
    "CollaborationType",
    "MeetingIntensity",
    "TimezoneSpread",
    "EnergyMatrixQuadrant",
    "TaskCharacteristics",
    "TaskImplication",
    # Orgmap models
    "Leadership",
    "OrgMetrics",
    "CoordinationSignals",
    "InsiderConnection",
    "RopeTeam",
    "Peak",
]
