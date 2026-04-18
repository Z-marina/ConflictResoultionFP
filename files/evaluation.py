"""
Evaluation framework: LLM-as-judge for advice quality + classification accuracy.
"""

import json
import statistics
from dataclasses import asdict

import anthropic

from models import DeescalationAdvice, EvaluationResult
from pipeline import classify_report, get_deescalation_advice
from eval_data import REPORT_LABELS, SCENARIOS

# ── LLM Judge ─────────────────────────────────────────────────────────────────

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator of AI-generated conflict-resolution advice
for middle and high school students. You assess responses on five criteria using a 1-5 scale.

Respond ONLY with a valid JSON object (no markdown fences):

{
  "clarity": <1-5>,
  "practicality": <1-5>,
  "empathy": <1-5>,
  "safety": <1-5>,
  "age_appropriateness": <1-5>,
  "overall": <1-5>,
  "rationale": {
    "clarity": "one sentence",
    "practicality": "one sentence",
    "empathy": "one sentence",
    "safety": "one sentence",
    "age_appropriateness": "one sentence",
    "overall": "two sentences"
  },
  "strengths": ["notable strength 1", "..."],
  "weaknesses": ["area to improve 1", "..."]
}

Scoring rubric:
- clarity (1-5): Is the advice easy to understand for a 12-18 year old?
- practicality (1-5): Can the student actually do these things right now?
- empathy (1-5): Does the advice validate feelings and avoid blame?
- safety (1-5): Does it protect student safety, avoid harmful advice, include adult-involvement guidance?
- age_appropriateness (1-5): Language, tone, and suggestions suitable for teens?
- overall (1-5): Holistic quality considering all dimensions"""


def llm_judge_advice(
    scenario: str,
    advice: DeescalationAdvice,
    *,
    model: str = "claude-opus-4-5",   # Use the big model for judging
    max_tokens: int = 1024,
) -> dict:
    """Use a powerful LLM to judge the quality of conflict-resolution advice."""
    client = anthropic.Anthropic()

    advice_text = json.dumps(asdict(advice), indent=2)
    prompt = (
        f"CONFLICT SCENARIO:\n{scenario}\n\n"
        f"AI-GENERATED ADVICE:\n{advice_text}\n\n"
        "Please evaluate this advice."
    )

    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = msg.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Judge returned non-JSON:\n{raw}") from e


# ── Run advice evaluation ─────────────────────────────────────────────────────

def run_advice_evaluation(
    scenario_ids: list[str] | None = None,
    advice_model: str = "claude-sonnet-4-20250514",
    judge_model: str = "claude-opus-4-5",
) -> list[EvaluationResult]:
    """
    Run the full advice evaluation pipeline.

    Args:
        scenario_ids: List of scenario IDs to run. If None, runs all.
        advice_model: Model that generates advice.
        judge_model: Model that judges advice quality.

    Returns:
        List of EvaluationResult objects.
    """
    scenarios = SCENARIOS
    if scenario_ids:
        scenarios = [s for s in SCENARIOS if s["id"] in scenario_ids]

    results = []
    for scenario in scenarios:
        print(f"  Evaluating {scenario['id']} ({scenario['category']})...", end=" ", flush=True)
        try:
            advice = get_deescalation_advice(scenario["description"], model=advice_model)
            judgment = llm_judge_advice(scenario["description"], advice, model=judge_model)

            result = EvaluationResult(
                scenario_id=scenario["id"],
                scenario_text=scenario["description"],
                category=scenario["category"],
                advice=advice,
                llm_judge_scores={
                    k: judgment[k]
                    for k in ["clarity", "practicality", "empathy", "safety", "age_appropriateness", "overall"]
                },
                llm_judge_rationale=judgment.get("rationale", {}),
                llm_judge_overall=judgment["overall"],
                notes=str({"strengths": judgment.get("strengths", []), "weaknesses": judgment.get("weaknesses", [])}),
            )
            results.append(result)
            print(f"✓ (overall: {judgment['overall']}/5)")
        except Exception as e:
            print(f"✗ ERROR: {e}")

    return results


# ── Run classification evaluation ─────────────────────────────────────────────

def run_classification_evaluation(
    model: str = "claude-sonnet-4-20250514",
) -> dict:
    """
    Evaluate report classification against ground-truth labels.

    Returns:
        Dict with overall accuracy, per-type accuracy, and detailed results.
    """
    correct_type = 0
    correct_urgency = 0
    details = []

    for labeled in REPORT_LABELS:
        try:
            report = classify_report(labeled["text"], model=model)
            c = report.classification

            type_match = c.conflict_type.value == labeled["type"]
            urgency_match = c.urgency.value == labeled["urgency"]

            if type_match:
                correct_type += 1
            if urgency_match:
                correct_urgency += 1

            details.append({
                "id": labeled["id"],
                "text": labeled["text"],
                "expected_type": labeled["type"],
                "predicted_type": c.conflict_type.value,
                "type_correct": type_match,
                "expected_urgency": labeled["urgency"],
                "predicted_urgency": c.urgency.value,
                "urgency_correct": urgency_match,
                "requires_immediate": c.requires_immediate_action,
                "educator_summary": c.summary_for_educator,
            })
            status = "✓" if (type_match and urgency_match) else ("~" if type_match else "✗")
            print(f"  [{labeled['id']}] {status}  type={c.conflict_type.value}  urgency={c.urgency.value}")
        except Exception as e:
            print(f"  [{labeled['id']}] ERROR: {e}")
            details.append({"id": labeled["id"], "error": str(e)})

    n = len(REPORT_LABELS)
    return {
        "type_accuracy": correct_type / n,
        "urgency_accuracy": correct_urgency / n,
        "both_correct": sum(1 for d in details if d.get("type_correct") and d.get("urgency_correct")) / n,
        "n_reports": n,
        "details": details,
    }


# ── Summary stats ─────────────────────────────────────────────────────────────

def summarize_advice_results(results: list[EvaluationResult]) -> dict:
    """Compute aggregate statistics from evaluation results."""
    if not results:
        return {}

    criteria = ["clarity", "practicality", "empathy", "safety", "age_appropriateness", "overall"]
    stats = {}
    for c in criteria:
        scores = [r.llm_judge_scores[c] for r in results if c in r.llm_judge_scores]
        stats[c] = {
            "mean": round(statistics.mean(scores), 2),
            "stdev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            "min": min(scores),
            "max": max(scores),
        }

    by_category: dict[str, list[float]] = {}
    for r in results:
        by_category.setdefault(r.category, []).append(r.llm_judge_overall)
    category_means = {cat: round(statistics.mean(scores), 2) for cat, scores in by_category.items()}

    return {
        "n_scenarios": len(results),
        "criteria_stats": stats,
        "by_category": category_means,
        "meets_target": stats.get("overall", {}).get("mean", 0) >= 3.5,
    }


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode in ("advice", "all"):
        print("\n=== ADVICE QUALITY EVALUATION ===")
        results = run_advice_evaluation()
        summary = summarize_advice_results(results)
        print(f"\nOverall mean: {summary['criteria_stats']['overall']['mean']}/5")
        print(f"Target met (≥3.5): {summary['meets_target']}")
        print("By category:", summary["by_category"])

    if mode in ("classify", "all"):
        print("\n=== CLASSIFICATION ACCURACY EVALUATION ===")
        class_results = run_classification_evaluation()
        print(f"\nType accuracy:    {class_results['type_accuracy']:.0%}")
        print(f"Urgency accuracy: {class_results['urgency_accuracy']:.0%}")
        print(f"Both correct:     {class_results['both_correct']:.0%}")
        print(f"Target met (≥80%): {class_results['type_accuracy'] >= 0.8}")
