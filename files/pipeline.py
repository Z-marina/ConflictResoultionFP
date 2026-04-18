"""
Core LLM pipeline: advice generation + anonymous report classification.
"""

import json
import uuid
from datetime import datetime

from google import genai

from models import (
    AnonymousReport,
    ConflictType,
    DeescalationAdvice,
    ReportClassification,
    SeverityLevel,
    UrgencyLevel,
)

# ── Prompts ────────────────────────────────────────────────────────────────────

ADVICE_SYSTEM_PROMPT = """You are a compassionate conflict-resolution counselor specializing in
middle and high school environments. You use techniques from nonviolent communication (NVC),
trauma-informed care, and restorative practices.

Respond ONLY with a valid JSON object (no markdown fences, no preamble) matching this schema:

{
  "summary": "Neutral 1-2 sentence reframe of the situation",
  "root_causes": ["Likely underlying cause 1", "..."],
  "immediate_steps": ["Concrete action to take RIGHT NOW", "..."],
  "communication_tips": ["How to speak / listen effectively", "..."],
  "things_to_avoid": ["Action or phrase that will make things worse", "..."],
  "long_term_recommendations": ["Systemic or relational change for the future", "..."],
  "severity": "low | medium | high",
  "when_to_involve_adult": "Clear guidance on when a trusted adult must be brought in",
  "self_care_tip": "One brief, practical self-care suggestion for the student"
}

Rules:
- Be empathetic, age-appropriate, and non-judgmental.
- Never recommend violence or retaliation.
- Always include at least one pathway to involve a trusted adult.
- Aim for 3-5 items per list.
- Keep language accessible for a 12-18 year old."""

CLASSIFICATION_SYSTEM_PROMPT = """You are a school safety analyst. Your job is to read anonymous
student reports and extract structured information to help educators respond appropriately.

Respond ONLY with a valid JSON object (no markdown fences, no preamble) matching this schema:

{
  "conflict_type": "bullying | physical_conflict | cyberbullying | verbal_harassment | social_exclusion | threat | weapons | other",
  "urgency": "low | medium | high | critical",
  "location_inferred": "cafeteria / hallway / online / gym / etc. or null if unknown",
  "parties_involved": "e.g. 'student vs student', 'group vs individual', 'unknown'",
  "requires_immediate_action": true or false,
  "summary_for_educator": "2-3 sentence professional summary suitable for a school counselor",
  "recommended_staff_action": "Specific next step for school staff",
  "keywords_detected": ["list", "of", "notable", "terms"]
}

Urgency guide:
- critical: weapons, imminent physical danger, suicide/self-harm risk
- high: repeated bullying, credible threats, physical altercations
- medium: ongoing social conflict, cyberbullying, emotional distress
- low: minor disputes, rumors, venting"""

DEFAULT_MODEL = "gemini-2.0-flash"


def _generate_json(system_prompt: str, user_text: str, model: str, max_output_tokens: int) -> str:
    client = genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=user_text,
        config={
            "system_instruction": system_prompt,
            "temperature": 0.2,
            "max_output_tokens": max_output_tokens,
            "response_mime_type": "application/json",
        },
    )
    return response.text


# ── Advice generation ──────────────────────────────────────────────────────────

def get_deescalation_advice(
    conflict_description: str,
    *,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> DeescalationAdvice:
    """Return structured de-escalation advice for a conflict description."""
    text = _generate_json(
        ADVICE_SYSTEM_PROMPT,
        f"Conflict situation:\n\n{conflict_description}",
        model,
        max_tokens,
    )
    data = _parse_json(text, required_keys={
        "summary", "root_causes", "immediate_steps", "communication_tips",
        "things_to_avoid", "long_term_recommendations", "severity",
        "when_to_involve_adult", "self_care_tip",
    })
    return DeescalationAdvice(
        summary=data["summary"],
        root_causes=data["root_causes"],
        immediate_steps=data["immediate_steps"],
        communication_tips=data["communication_tips"],
        things_to_avoid=data["things_to_avoid"],
        long_term_recommendations=data["long_term_recommendations"],
        severity=SeverityLevel(data["severity"]),
        when_to_involve_adult=data["when_to_involve_adult"],
        self_care_tip=data["self_care_tip"],
    )


# ── Report classification ──────────────────────────────────────────────────────

def classify_report(
    report_text: str,
    *,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 512,
) -> AnonymousReport:
    """Classify an anonymous report and return a structured AnonymousReport."""
    text = _generate_json(
        CLASSIFICATION_SYSTEM_PROMPT,
        f"Anonymous student report:\n\n{report_text}",
        model,
        max_tokens,
    )
    data = _parse_json(text, required_keys={
        "conflict_type", "urgency", "location_inferred", "parties_involved",
        "requires_immediate_action", "summary_for_educator",
        "recommended_staff_action", "keywords_detected",
    })
    classification = ReportClassification(
        conflict_type=ConflictType(data["conflict_type"]),
        urgency=UrgencyLevel(data["urgency"]),
        location_inferred=data.get("location_inferred"),
        parties_involved=data["parties_involved"],
        requires_immediate_action=bool(data["requires_immediate_action"]),
        summary_for_educator=data["summary_for_educator"],
        recommended_staff_action=data["recommended_staff_action"],
        keywords_detected=data["keywords_detected"],
    )
    return AnonymousReport(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now(),
        raw_text=report_text,
        classification=classification,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_json(text: str, required_keys: set[str]) -> dict:
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned non-JSON:\n{text}") from e
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Response missing keys: {missing}")
    return data