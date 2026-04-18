"""
Shared data models for the AI Conflict Resolution & Safety Reporting System.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ConflictType(str, Enum):
    BULLYING = "bullying"
    PHYSICAL = "physical_conflict"
    CYBERBULLYING = "cyberbullying"
    VERBAL = "verbal_harassment"
    SOCIAL = "social_exclusion"
    THREAT = "threat"
    WEAPONS = "weapons"
    OTHER = "other"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class DeescalationAdvice:
    summary: str
    root_causes: list[str]
    immediate_steps: list[str]
    communication_tips: list[str]
    things_to_avoid: list[str]
    long_term_recommendations: list[str]
    severity: SeverityLevel
    when_to_involve_adult: str
    self_care_tip: str


@dataclass
class ReportClassification:
    conflict_type: ConflictType
    urgency: UrgencyLevel
    location_inferred: Optional[str]
    parties_involved: str          # e.g. "student vs student", "group vs individual"
    requires_immediate_action: bool
    summary_for_educator: str
    recommended_staff_action: str
    keywords_detected: list[str]


@dataclass
class AnonymousReport:
    id: str
    timestamp: datetime
    raw_text: str
    classification: Optional[ReportClassification] = None


@dataclass
class EvaluationResult:
    scenario_id: str
    scenario_text: str
    category: str
    advice: DeescalationAdvice
    llm_judge_scores: dict[str, float]   # criterion -> 1-5
    llm_judge_rationale: dict[str, str]
    llm_judge_overall: float
    human_score: Optional[float] = None
    notes: str = ""
