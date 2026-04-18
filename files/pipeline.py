"""
Core LLM pipeline: advice generation + anonymous report classification.
"""

import json
import os
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

_genai_client: genai.Client | None = None

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


def _get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        # The SDK also reads GEMINI_API_KEY from the environment by default.
        api_key = os.getenv("GEMINI_API_KEY")
        _genai_client = genai.Client(api_key=api_key) if api_key else genai.Client()
    return _genai_client


def _fallback_advice_json(user_text: str) -> str:
    text = user_text.lower()

    if "bully" in text or "bullied" in text or "picked on" in text:
        return json.dumps({
            "summary": "You may be experiencing bullying at school, which can be painful and isolating. This is not your fault, and you should not have to handle it alone.",
            "root_causes": [
                "A power imbalance between students",
                "Repeated harmful behavior meant to embarrass or target you",
                "Peer pressure or group behavior encouraging the bullying"
            ],
            "immediate_steps": [
                "Move toward a teacher, counselor, or other trusted adult if the bullying is happening in the moment",
                "Stay near supportive friends or adults instead of being alone with the person targeting you",
                "Write down what happened, who was involved, where it happened, and whether this has happened before",
                "Save texts, screenshots, or online messages if the bullying happened digitally",
                "Tell a trusted adult at school or home exactly what has been happening"
            ],
            "communication_tips": [
                "Say clearly: 'This has been happening more than once, and it is affecting me'",
                "Be specific about what was said or done instead of speaking only in general terms",
                "If you feel safe, use a short boundary statement like: 'Stop. This is not okay'",
                "When talking to an adult, explain how long it has been going on and how it is affecting your mood or school life"
            ],
            "things_to_avoid": [
                "Do not retaliate physically or threaten the other person",
                "Do not respond with insults online or in person",
                "Do not keep it secret if it is repeated or making you feel unsafe",
                "Do not delete evidence like screenshots or messages"
            ],
            "long_term_recommendations": [
                "Work with a counselor, dean, or teacher to create a plan for support and reporting",
                "Keep a record of repeated incidents if the behavior continues",
                "Spend more time with people who make you feel safe and supported",
                "Practice ways to ask for help early before things get worse"
            ],
            "severity": "medium",
            "when_to_involve_adult": "Bullying should be brought to a trusted adult, especially if it is repeated, public, threatening, or affecting your mental health.",
            "self_care_tip": "After reaching out for help, do one small calming activity like texting someone supportive, taking a walk, or listening to music you find comforting."
        })

    if "fight" in text or "argue" in text or "hit" in text:
        return json.dumps({
            "summary": "This situation sounds like it could escalate into a physical or intense verbal conflict. The priority is creating distance and preventing harm.",
            "root_causes": [
                "Emotional escalation in the moment",
                "Miscommunication or unresolved tension",
                "Pressure from other people watching or encouraging the conflict"
            ],
            "immediate_steps": [
                "Put physical space between yourself and the other person right away",
                "Go toward a teacher, security staff, coach, or other adult nearby",
                "Do not continue the argument in hallways, group chats, or after school",
                "Take a few slow breaths before saying anything else",
                "Leave the area if you feel unsafe"
            ],
            "communication_tips": [
                "Use short statements like: 'I do not want to fight' or 'I am walking away'",
                "Keep your voice calm and low",
                "Do not argue in front of a crowd if emotions are already high",
                "If you talk later, focus on what happened instead of blaming"
            ],
            "things_to_avoid": [
                "Do not shove, hit, or threaten the other person",
                "Do not let a crowd pressure you into staying in the conflict",
                "Do not post about it online while emotions are high",
                "Do not keep going back and forth once it starts escalating"
            ],
            "long_term_recommendations": [
                "Ask a counselor, teacher, or administrator to help mediate the conflict",
                "Think about what triggers usually lead to these arguments",
                "Avoid situations where the conflict is likely to restart without adult support",
                "Build a plan for what to do next time before things escalate"
            ],
            "severity": "high",
            "when_to_involve_adult": "An adult should be involved immediately if there are threats, physical contact, fear of violence, or pressure to fight.",
            "self_care_tip": "Once you are safe, give yourself time to calm down physically by sitting somewhere quiet and slowing your breathing."
        })

    if "rumor" in text or "gossip" in text or "talking about me" in text:
        return json.dumps({
            "summary": "This sounds like a social conflict involving rumors or gossip, which can damage trust and make school feel stressful.",
            "root_causes": [
                "Peer drama or exclusion",
                "Miscommunication spreading between people",
                "Social pressure to join gossip or take sides"
            ],
            "immediate_steps": [
                "Do not spread the rumor further, even to defend yourself emotionally",
                "Figure out whether there is one trusted person you need to speak to directly",
                "Talk to a counselor or trusted adult if the rumor is spreading widely or affecting your relationships",
                "Save messages or screenshots if the rumor is happening online",
                "Focus on the people who actually support you instead of trying to respond to everyone"
            ],
            "communication_tips": [
                "Use a calm statement like: 'I heard something was said about me, and I want to clear it up directly'",
                "Ask for facts instead of responding to secondhand claims",
                "Correct false information briefly without turning it into a larger argument",
                "If someone keeps stirring drama, end the conversation and seek support"
            ],
            "things_to_avoid": [
                "Do not start a new rumor in response",
                "Do not post an emotional public response unless safety requires it",
                "Do not confront a group all at once if emotions are already high",
                "Do not assume every person has bad intentions without checking facts"
            ],
            "long_term_recommendations": [
                "Strengthen relationships with people you trust instead of chasing approval from everyone",
                "Set boundaries with people who repeatedly spread drama",
                "Ask an adult for help if the rumor is harming your wellbeing or reputation at school",
                "Practice addressing issues earlier before they spread"
            ],
            "severity": "medium",
            "when_to_involve_adult": "Involve an adult if the rumor includes threats, sexual content, harassment, or is seriously affecting your mental health or school experience.",
            "self_care_tip": "Step away from social media for a bit and spend time with someone who makes you feel grounded and safe."
        })

    return json.dumps({
        "summary": "This seems like a stressful conflict that may need calm communication and support from trusted people.",
        "root_causes": [
            "Miscommunication",
            "Strong emotions",
            "Peer or social pressure"
        ],
        "immediate_steps": [
            "Pause before reacting",
            "Create some space if emotions are high",
            "Talk to a trusted friend, teacher, counselor, or parent",
            "Write down what happened if you need help explaining it later"
        ],
        "communication_tips": [
            "Speak calmly and clearly",
            "Use 'I feel' statements",
            "Focus on what happened instead of attacking the other person"
        ],
        "things_to_avoid": [
            "Escalating online",
            "Threatening or insulting the other person",
            "Trying to solve everything while very upset"
        ],
        "long_term_recommendations": [
            "Build a support system",
            "Set clear boundaries",
            "Ask for adult help if the problem continues"
        ],
        "severity": "medium",
        "when_to_involve_adult": "Involve a trusted adult if the conflict continues, feels unsafe, or starts affecting your emotional wellbeing.",
        "self_care_tip": "Do one calming activity after the conversation, like journaling, walking, or listening to music."
    })


def _fallback_classification_json(report_text: str) -> str:
    text = report_text.lower()

    conflict_type = "other"
    urgency = "low"
    location = None
    parties = "unknown"
    immediate = False
    summary = "Student submitted an anonymous report describing a conflict situation."
    staff_action = "Review the report and follow up if additional context becomes available."
    keywords = []

    if "online" in text or "instagram" in text or "snapchat" in text or "group chat" in text:
        location = "online"
        keywords.append("online")

    if "hallway" in text:
        location = "hallway"
        keywords.append("hallway")
    elif "cafeteria" in text:
        location = "cafeteria"
        keywords.append("cafeteria")
    elif "gym" in text:
        location = "gym"
        keywords.append("gym")

    if "bully" in text or "bullied" in text:
        conflict_type = "bullying"
        urgency = "high"
        immediate = False
        summary = "Report describes repeated bullying behavior affecting a student."
        staff_action = "Counseling staff should document the incident, check on the targeted student, and investigate for repeated behavior."
        keywords.extend(["bullying", "repeated behavior"])

    elif "fight" in text or "hit" in text or "punch" in text:
        conflict_type = "physical_conflict"
        urgency = "high"
        immediate = True
        summary = "Report indicates a physical conflict or risk of physical altercation between students."
        staff_action = "Staff should intervene immediately, separate students if needed, and assess safety."
        keywords.extend(["fight", "physical conflict"])

    elif "rumor" in text or "gossip" in text:
        conflict_type = "social_exclusion"
        urgency = "medium"
        immediate = False
        summary = "Report describes rumor-spreading or social conflict affecting peer relationships."
        staff_action = "A counselor or administrator should review the social conflict and support affected students."
        keywords.extend(["rumor", "gossip"])

    elif "threat" in text or "hurt" in text:
        conflict_type = "threat"
        urgency = "high"
        immediate = True
        summary = "Report includes language suggesting threats or potential harm."
        staff_action = "Staff should assess the immediacy of the threat and intervene as soon as possible."
        keywords.extend(["threat", "harm"])

    elif "weapon" in text or "gun" in text or "knife" in text:
        conflict_type = "weapons"
        urgency = "critical"
        immediate = True
        summary = "Report suggests possible weapon-related safety risk."
        staff_action = "Contact school safety personnel and administrators immediately according to school policy."
        keywords.extend(["weapon"])

    if "group" in text:
        parties = "group vs individual"
    elif "friend" in text or "student" in text:
        parties = "student vs student"

    return json.dumps({
        "conflict_type": conflict_type,
        "urgency": urgency,
        "location_inferred": location,
        "parties_involved": parties,
        "requires_immediate_action": immediate,
        "summary_for_educator": summary,
        "recommended_staff_action": staff_action,
        "keywords_detected": keywords
    })


def _generate_json(system_prompt: str, user_text: str, model: str, max_output_tokens: int) -> str:
    try:
        client = _get_genai_client()
        response = client.models.generate_content(
            model=model,
            contents=f"{system_prompt}\n\n{user_text}",
            config={
                "temperature": 0.2,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": "application/json",
            },
        )
        return response.text or ""
    except Exception:
        if "conflict_type" in system_prompt and "urgency" in system_prompt:
            return _fallback_classification_json(user_text)
        return _fallback_advice_json(user_text)


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
