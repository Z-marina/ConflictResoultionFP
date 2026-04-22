# SafeSpace — AI Conflict Resolution & Safety Reporting
**SI405 Applied AI | Course Project**

---

## Setup

```bash
pip install -r requirements.txt
export LLM_BACKEND="ollama"
export LLM_MODEL="llama3.1:8b"
export ALLOW_FALLBACK="0"  # optional: fail loudly instead of hardcoded fallback
# Optional if Ollama is on a different host/port:
# export OLLAMA_BASE_URL="http://127.0.0.1:11434"

# Pull a local model once:
# ollama pull llama3.1:8b

# Optional Gemini path (paid API):
# export LLM_BACKEND="gemini"
# export GEMINI_API_KEY="..."

# Optional: only needed for LLM-as-judge evaluation
export ANTHROPIC_API_KEY="sk-..."
streamlit run app.py
```

---

## Architecture

```
conflict_system/
├── models.py        # Shared dataclasses & enums
├── pipeline.py      # LLM calls: advice generation + report classification
├── eval_data.py     # 25 scenarios + 10 labeled reports for evaluation
├── evaluation.py    # LLM-as-judge + classification accuracy framework
├── store.py         # In-memory report store (session-scoped)
└── app.py           # Streamlit UI (4 tabs)
```

### LLM Models Used
| Task | Model | Rationale |
|---|---|---|
| Advice generation | `gemini-2.0-flash` | Fast structured generation for student-facing responses |
| Report classification | `gemini-2.0-flash` | Fast structured extraction for anonymous reports |
| LLM-as-judge | `claude-opus-4-5` | Larger model for more reliable evaluation |

---

## Evaluation Design

### Metric 1: Advice Quality (target ≥ 3.5/5)
- **25 scenarios** across 8 categories: bullying, physical conflict, cyberbullying, verbal harassment, social exclusion, threats, weapons, edge cases
- **LLM-as-judge** (Opus-level model) scores each response on 5 criteria:
  - Clarity, Practicality, Empathy, Safety, Age-appropriateness
- **Human ratings** can be collected via the Evaluation tab and compared to LLM-judge scores
- **Correlation check**: Mean absolute difference between human and LLM scores validates judge reliability

### Metric 2: Classification Accuracy (target ≥ 80%)
- **10 labeled reports** with ground-truth conflict type and urgency level
- Accuracy computed separately for type and urgency
- Baseline comparison: keyword rule system vs. LLM classifier

### Scenario Diversity
Scenarios are stratified by:
- Category (8 types)
- Difficulty (low / medium / high / critical)
- Perspective (victim, bystander, perpetrator)
- Edge cases (vague input, mental health signals, external actors)

---

## Evaluation CLI

```bash
# Run both evaluations
python evaluation.py all

# Run only advice evaluation
python evaluation.py advice

# Run only classification evaluation
python evaluation.py classify
```

---

## Stretch Goal: MCP Messaging Integration

To connect SafeSpace to a messaging platform (WhatsApp, iMessage, Telegram) via MCP:

### Option A: Twilio WhatsApp MCP Server
```python
# In an MCP-compatible host, add a tool:
@mcp.tool()
async def handle_student_message(message: str) -> str:
    advice = get_deescalation_advice(message)
    return format_sms_advice(advice)  # condensed plain-text version
```

**Why this matters (per Prof. Jurgens' suggestion):**  
Texting feels natural and inconspicuous. A student in the middle of a tense situation is far more likely to text "help, this kid won't stop" than to open a browser and navigate to a portal.

### Condensed SMS Format
```python
def format_sms_advice(advice: DeescalationAdvice) -> str:
    steps = "\n".join(f"• {s}" for s in advice.immediate_steps[:3])
    return (
        f"[SafeSpace] Severity: {advice.severity.value.upper()}\n\n"
        f"{advice.summary}\n\n"
        f"Right now:\n{steps}\n\n"
        f"When to get help: {advice.when_to_involve_adult}\n\n"
        f"You can also submit this anonymously at [URL]"
    )
```

### Setup (Twilio)
```bash
pip install twilio mcp
# Configure webhook: POST /sms → handle_student_message()
```

---

## Safety Notes
- No student identity is ever stored
- Crisis keywords trigger immediate 988 hotline surfacing
- The system never makes disciplinary decisions — it summarizes and recommends
- All advice includes explicit adult-involvement guidance
