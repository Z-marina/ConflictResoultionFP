
import json
import streamlit as st
from dataclasses import dataclass
import anthropic

# --- dataclass, SYSTEM_PROMPT, get_deescalation_advice() unchanged ---

def display_advice(advice: DeescalationAdvice) -> None:
    """Render advice in the Streamlit UI."""
    severity_colors = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    icon = severity_colors.get(advice.severity, "⚪")

    st.subheader(f"{icon} Severity: {advice.severity.upper()}")
    st.write(f"**Summary:** {advice.summary}")

    sections = [
        ("🔍 Root Causes",               advice.root_causes),
        ("⚡ Immediate Steps",            advice.immediate_steps),
        ("💬 Communication Tips",         advice.communication_tips),
        ("🚫 Things to Avoid",            advice.things_to_avoid),
        ("🔭 Long-term Recommendations",  advice.long_term_recommendations),
    ]
    for title, items in sections:
        st.markdown(f"**{title}**")
        for item in items:
            st.markdown(f"- {item}")

# --- Streamlit UI ---
st.title("AI Conflict Resolution System")

conflict_input = st.text_area("Describe the conflict:", height=150)

if st.button("Analyze") and conflict_input.strip():
    with st.spinner("Analyzing..."):
        advice = get_deescalation_advice(conflict_input)
    display_advice(advice)