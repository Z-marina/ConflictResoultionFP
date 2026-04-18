"""
AI Conflict Resolution & Safety Reporting System
SI405 Applied AI — Course Project
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="SafeSpace | AI Conflict Resolution",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1100px; }

/* Brand header */
.brand-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #e8e4de;
}
.brand-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1a1a2e;
    margin: 0;
    line-height: 1;
}
.brand-sub {
    font-size: 0.8rem;
    color: #888;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 3px;
}

/* Tab pills */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #f5f3f0;
    padding: 6px;
    border-radius: 12px;
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    color: #666;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1a1a2e !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}

/* Cards */
.ss-card {
    background: white;
    border: 1px solid #e8e4de;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.ss-card-critical {
    border-left: 4px solid #e63946;
    background: #fff5f5;
}
.ss-card-high {
    border-left: 4px solid #f4a261;
    background: #fffbf5;
}
.ss-card-medium {
    border-left: 4px solid #f4d35e;
    background: #fffef5;
}
.ss-card-low {
    border-left: 4px solid #57cc99;
    background: #f5fff9;
}

/* Severity badge */
.sev-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.sev-low    { background: #d8f3dc; color: #1b4332; }
.sev-medium { background: #fff3b0; color: #7b5e00; }
.sev-high   { background: #ffe8cc; color: #7b3f00; }
.sev-critical { background: #ffd6d6; color: #7b0000; }

/* Section headers in advice */
.advice-section-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #888;
    margin: 1.2rem 0 0.5rem;
}

/* Stat boxes */
.stat-box {
    background: white;
    border: 1px solid #e8e4de;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.stat-num  { font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: #1a1a2e; line-height: 1; }
.stat-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
.stat-num-red { color: #e63946; }

/* Anonymous notice */
.anon-notice {
    background: #f0f7ff;
    border: 1px solid #c3d9f5;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    font-size: 0.85rem;
    color: #2d5986;
    margin-bottom: 1.2rem;
}

/* Crisis banner */
.crisis-banner {
    background: #e63946;
    color: white;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Eval table */
.eval-row-good  { background: #f0fff4; }
.eval-row-ok    { background: #fffff0; }
.eval-row-bad   { background: #fff0f0; }

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
    border: none;
    transition: all 0.15s;
}
.stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }

/* Text areas */
.stTextArea textarea {
    border-radius: 10px;
    border: 1px solid #ddd;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: 10px;
}

/* Divider */
hr { border: none; border-top: 1px solid #e8e4de; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

import json
from datetime import datetime
from pipeline import classify_report, get_deescalation_advice
from store import add_report, get_all_reports, get_stats
from models import UrgencyLevel

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
  <span style="font-size:2.2rem">🛡️</span>
  <div>
    <div class="brand-title">SafeSpace</div>
    <div class="brand-sub">AI Conflict Resolution &amp; Safety Reporting</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_student, tab_report, tab_educator, tab_eval = st.tabs([
    "💬 Get Advice", "📋 Report Anonymously", "🏫 Educator Dashboard", "📊 Evaluation"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — STUDENT ADVICE
# ══════════════════════════════════════════════════════════════════════════════
with tab_student:
    st.markdown("### What's going on?")
    st.caption("Describe the situation in your own words. Your advice is private and not saved.")

    col_input, col_tip = st.columns([3, 1])
    with col_input:
        conflict_text = st.text_area(
            "Describe the conflict",
            placeholder=(
                "e.g. There's a group of students who keep making fun of my friend online. "
                "It's getting worse and she's really upset..."
            ),
            height=160,
            label_visibility="collapsed",
        )
    with col_tip:
        st.markdown("""
<div class="ss-card" style="font-size:0.82rem; color:#666; height:160px; overflow:auto;">
<strong>💡 Tips for better advice</strong><br><br>
• Describe what happened<br>
• Who is involved?<br>
• How long has it been going on?<br>
• How does it make you feel?
</div>
""", unsafe_allow_html=True)

    get_btn = st.button("Get Advice →", type="primary", disabled=not conflict_text.strip())

    if get_btn and conflict_text.strip():
        # Crisis detection (simple keyword check before LLM call)
        crisis_keywords = ["kill myself", "end it all", "don't want to be here", "suicide", "hurt myself"]
        is_crisis = any(k in conflict_text.lower() for k in crisis_keywords)

        if is_crisis:
            st.markdown("""
<div class="crisis-banner">
⚠️ It sounds like you might be going through something really serious. 
Please reach out to a trusted adult or call/text <strong>988</strong> (Suicide & Crisis Lifeline) right now. 
You matter, and help is available.
</div>
""", unsafe_allow_html=True)

        with st.spinner("Thinking through your situation..."):
            try:
                advice = get_deescalation_advice(conflict_text)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        # Severity badge
        sev = advice.severity.value
        sev_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(sev, "⚪")
        st.markdown(f"""
<div class="ss-card">
  <span class="sev-badge sev-{sev}">{sev_icon} {sev.upper()} severity</span>
  <p style="margin-top:0.8rem; font-size:1.05rem; color:#333;">{advice.summary}</p>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        def render_list(title: str, items: list[str], icon: str = "•"):
            bullets = "".join(f"<li style='margin-bottom:6px'>{i}</li>" for i in items)
            st.markdown(f"""
<div class="ss-card">
  <div class="advice-section-title">{title}</div>
  <ul style="margin:0; padding-left:1.2rem; color:#333; font-size:0.92rem">{bullets}</ul>
</div>
""", unsafe_allow_html=True)

        with col1:
            render_list("⚡ What to do right now", advice.immediate_steps)
            render_list("💬 How to communicate", advice.communication_tips)
            render_list("🔍 Root causes", advice.root_causes)

        with col2:
            render_list("🚫 What to avoid", advice.things_to_avoid)
            render_list("🔭 Longer term", advice.long_term_recommendations)

            st.markdown(f"""
<div class="ss-card">
  <div class="advice-section-title">👩‍🏫 When to involve an adult</div>
  <p style="margin:0; font-size:0.92rem; color:#333">{advice.when_to_involve_adult}</p>
</div>
<div class="ss-card" style="background:#f0f7ff; border-color:#c3d9f5">
  <div class="advice-section-title">🧘 Self-care</div>
  <p style="margin:0; font-size:0.92rem; color:#2d5986">{advice.self_care_tip}</p>
</div>
""", unsafe_allow_html=True)

        # Offer to submit anonymous report
        st.markdown("---")
        if st.checkbox("Would you also like to submit this anonymously to school staff?"):
            st.info("Your identity is never stored. Only the situation details are shared.")
            if st.button("Submit anonymous report", type="secondary"):
                with st.spinner("Submitting..."):
                    report = classify_report(conflict_text)
                    add_report(report)
                st.success(f"✓ Report submitted anonymously (ID: #{report.id}). Thank you for helping keep your school safe.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANONYMOUS REPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab_report:
    st.markdown("### Submit an Anonymous Report")
    st.markdown("""
<div class="anon-notice">
🔒 <strong>Completely anonymous.</strong> We never collect your name, email, or any identifying information. 
You cannot be identified from this report.
</div>
""", unsafe_allow_html=True)

    report_text = st.text_area(
        "Describe what you saw or heard",
        placeholder=(
            "e.g. I saw a student threatening another student near the gym bathrooms. "
            "The student seemed scared and I heard mention of a weapon..."
        ),
        height=180,
        label_visibility="visible",
    )

    location_hint = st.selectbox(
        "Where did this happen? (optional)",
        ["Prefer not to say", "Cafeteria", "Hallway", "Classroom", "Bathroom", "Gym",
         "Outside / parking lot", "Online / social media", "Bus stop", "Other"],
    )

    urgency_self = st.radio(
        "How urgent do you think this is?",
        ["I'm not sure", "Not urgent — just wanted to flag it",
         "Somewhat urgent", "Very urgent — someone could get hurt"],
        horizontal=True,
    )

    submit_report_btn = st.button("Submit Report →", type="primary", disabled=not report_text.strip())

    if submit_report_btn and report_text.strip():
        combined = report_text
        if location_hint != "Prefer not to say":
            combined += f" [Location: {location_hint}]"

        with st.spinner("Processing report..."):
            try:
                report = classify_report(combined)
                add_report(report)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        c = report.classification
        urgency_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(c.urgency.value, "⚪")

        st.success(f"✓ Your report has been submitted. Reference ID: **#{report.id}**")
        st.markdown(f"""
<div class="ss-card ss-card-{c.urgency.value}">
  <span class="sev-badge sev-{c.urgency.value}">{urgency_color} {c.urgency.value.upper()} urgency</span>
  <p style="margin-top:0.6rem; font-size:0.9rem; color:#555">
    <strong>Type detected:</strong> {c.conflict_type.value.replace('_', ' ').title()}
  </p>
  {f'<div style="background:#e63946;color:white;border-radius:8px;padding:0.5rem 0.9rem;font-size:0.85rem;font-weight:600;margin-top:0.5rem">⚠️ This report has been flagged for IMMEDIATE staff attention.</div>' if c.requires_immediate_action else ''}
</div>
""", unsafe_allow_html=True)

        if c.urgency.value == "critical":
            st.warning("⚠️ If you or someone else is in immediate danger, please tell an adult right now or call 911.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EDUCATOR DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_educator:
    st.markdown("### Educator Dashboard")
    st.caption("Aggregated view of anonymous student reports. No identifying information is stored.")

    stats = get_stats()

    if stats["total"] == 0:
        st.info("No reports have been submitted yet. Reports from students will appear here.")
    else:
        # Stats row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{stats["total"]}</div><div class="stat-label">Total Reports</div></div>', unsafe_allow_html=True)
        with c2:
            crit = stats.get("critical", 0)
            st.markdown(f'<div class="stat-box"><div class="stat-num {"stat-num-red" if crit > 0 else ""}">{crit}</div><div class="stat-label">Need Immediate Action</div></div>', unsafe_allow_html=True)
        with c3:
            high = stats.get("by_urgency", {}).get("high", 0)
            st.markdown(f'<div class="stat-box"><div class="stat-num">{high}</div><div class="stat-label">High Urgency</div></div>', unsafe_allow_html=True)
        with c4:
            low_med = stats.get("by_urgency", {}).get("low", 0) + stats.get("by_urgency", {}).get("medium", 0)
            st.markdown(f'<div class="stat-box"><div class="stat-num">{low_med}</div><div class="stat-label">Low / Medium</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Breakdown charts
        col_type, col_urg = st.columns(2)
        with col_type:
            st.markdown("**Reports by Type**")
            by_type = stats.get("by_type", {})
            if by_type:
                for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
                    label = t.replace("_", " ").title()
                    pct = count / stats["total"]
                    st.markdown(f"`{label}` — {count}")
                    st.progress(pct)
        with col_urg:
            st.markdown("**Reports by Urgency**")
            by_urg = stats.get("by_urgency", {})
            order = ["critical", "high", "medium", "low"]
            colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            for u in order:
                count = by_urg.get(u, 0)
                if count > 0:
                    pct = count / stats["total"]
                    st.markdown(f"{colors[u]} `{u.title()}` — {count}")
                    st.progress(pct)

        st.markdown("---")
        st.markdown("**All Reports** (newest first)")

        all_reports = get_all_reports()
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_reports.sort(key=lambda r: urgency_order.get(r.classification.urgency.value if r.classification else "low", 3))

        for report in all_reports:
            c = report.classification
            if not c:
                continue
            urg = c.urgency.value
            urg_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(urg, "⚪")
            ts = report.timestamp.strftime("%b %d, %H:%M")

            with st.expander(f"{urg_icon} [{report.id}] {ts} — {c.conflict_type.value.replace('_',' ').title()} — {urg.upper()}"):
                st.markdown(f"**AI Summary:** {c.summary_for_educator}")
                st.markdown(f"**Recommended Action:** {c.recommended_staff_action}")
                cols = st.columns(3)
                cols[0].markdown(f"**Location:** {c.location_inferred or 'Unknown'}")
                cols[1].markdown(f"**Parties:** {c.parties_involved}")
                cols[2].markdown(f"**Immediate action needed:** {'Yes ⚠️' if c.requires_immediate_action else 'No'}")
                if c.keywords_detected:
                    st.markdown(f"**Keywords:** {', '.join(c.keywords_detected)}")
                st.caption(f"Raw report: {report.raw_text[:200]}{'...' if len(report.raw_text) > 200 else ''}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — EVALUATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.markdown("### System Evaluation")
    st.caption("LLM-as-judge evaluation of advice quality + classification accuracy. Uses claude-opus-4-5 as judge.")

    from eval_data import SCENARIOS, REPORT_LABELS

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 🧪 Advice Quality Evaluation")
        st.markdown(f"**{len(SCENARIOS)} scenarios** across {len(set(s['category'] for s in SCENARIOS))} categories. "
                    f"Target: ≥ 3.5 / 5 overall.")

        categories = sorted(set(s["category"] for s in SCENARIOS))
        selected_cats = st.multiselect("Filter by category", categories, default=categories, key="eval_cats")
        filtered = [s for s in SCENARIOS if s["category"] in selected_cats]
        st.info(f"{len(filtered)} scenarios selected.")

        run_advice_eval = st.button("▶ Run Advice Evaluation", type="primary", key="run_adv")

    with col_b:
        st.markdown("#### 🗂️ Classification Accuracy Evaluation")
        st.markdown(f"**{len(REPORT_LABELS)} labeled reports.** Target: ≥ 80% type accuracy.")
        st.markdown("Ground-truth labels cover all major conflict types and urgency levels.")
        run_class_eval = st.button("▶ Run Classification Evaluation", type="primary", key="run_cls")

    st.markdown("---")

    # ── Advice eval results ────────────────────────────────────────────────────
    if run_advice_eval:
        from evaluation import run_advice_evaluation, summarize_advice_results

        scenario_ids = [s["id"] for s in filtered]
        progress = st.progress(0, text="Running evaluations...")
        results_container = st.empty()

        all_results = []
        for i, sid in enumerate(scenario_ids):
            progress.progress((i + 1) / len(scenario_ids), text=f"Evaluating {sid}...")
            partial = run_advice_evaluation(scenario_ids=[sid])
            all_results.extend(partial)

        progress.empty()
        summary = summarize_advice_results(all_results)

        st.session_state["advice_results"] = all_results
        st.session_state["advice_summary"] = summary

    if "advice_summary" in st.session_state:
        summary = st.session_state["advice_summary"]
        results = st.session_state["advice_results"]

        overall = summary["criteria_stats"]["overall"]["mean"]
        meets = summary["meets_target"]
        badge = "✅ Target met" if meets else "❌ Below target"
        st.markdown(f"**Overall mean: {overall}/5 — {badge}**")

        # Criteria table
        criteria = ["clarity", "practicality", "empathy", "safety", "age_appropriateness", "overall"]
        criteria_data = {c: summary["criteria_stats"][c] for c in criteria if c in summary["criteria_stats"]}

        cols = st.columns(len(criteria))
        for col, (crit, vals) in zip(cols, criteria_data.items()):
            color = "#57cc99" if vals["mean"] >= 4 else ("#f4d35e" if vals["mean"] >= 3 else "#e63946")
            col.markdown(f"""
<div style="text-align:center; padding:0.8rem; border:1px solid #e8e4de; border-radius:10px;">
  <div style="font-size:1.5rem; font-weight:700; color:{color}">{vals['mean']}</div>
  <div style="font-size:0.7rem; color:#888; text-transform:uppercase">{crit.replace('_',' ')}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("**By Category:**")
        for cat, mean in sorted(summary["by_category"].items(), key=lambda x: -x[1]):
            color = "🟢" if mean >= 4 else ("🟡" if mean >= 3.5 else "🔴")
            st.markdown(f"  {color} `{cat}` — **{mean}**/5")

        st.markdown("**Individual Results:**")
        for r in results:
            ov = r.llm_judge_overall
            color = "eval-row-good" if ov >= 4 else ("eval-row-ok" if ov >= 3.5 else "eval-row-bad")
            icon = "✅" if ov >= 4 else ("🟡" if ov >= 3.5 else "❌")
            with st.expander(f"{icon} [{r.scenario_id}] {r.category} — {ov}/5"):
                st.markdown(f"**Scenario:** {r.scenario_text[:200]}...")
                score_cols = st.columns(5)
                for col, crit in zip(score_cols, ["clarity", "practicality", "empathy", "safety", "age_appropriateness"]):
                    col.metric(crit.split("_")[0].title(), f"{r.llm_judge_scores.get(crit, '?')}/5")
                if r.llm_judge_rationale.get("overall"):
                    st.caption(f"Judge: {r.llm_judge_rationale['overall']}")

    # ── Classification eval results ───────────────────────────────────────────
    if run_class_eval:
        from evaluation import run_classification_evaluation

        with st.spinner("Running classification evaluation..."):
            cls_results = run_classification_evaluation()

        st.session_state["cls_results"] = cls_results

    if "cls_results" in st.session_state:
        cr = st.session_state["cls_results"]

        type_acc = cr["type_accuracy"]
        urg_acc = cr["urgency_accuracy"]
        both = cr["both_correct"]

        c1, c2, c3 = st.columns(3)
        for col, label, val, target in [
            (c1, "Type Accuracy", type_acc, 0.80),
            (c2, "Urgency Accuracy", urg_acc, 0.80),
            (c3, "Both Correct", both, 0.70),
        ]:
            color = "#57cc99" if val >= target else "#e63946"
            badge = "✅" if val >= target else "❌"
            col.markdown(f"""
<div style="text-align:center; padding:1rem; border:1px solid #e8e4de; border-radius:10px;">
  <div style="font-size:1.8rem; font-weight:700; color:{color}">{val:.0%}</div>
  <div style="font-size:0.8rem; color:#888">{label} {badge}</div>
  <div style="font-size:0.7rem; color:#aaa">target ≥{target:.0%}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("**Detailed Results:**")
        for d in cr["details"]:
            if "error" in d:
                st.markdown(f"  ❌ `{d['id']}` — error")
                continue
            ok = d["type_correct"] and d["urgency_correct"]
            type_ok = d["type_correct"]
            icon = "✅" if ok else ("🟡" if type_ok else "❌")
            with st.expander(f"{icon} [{d['id']}] type={d['predicted_type']} (expected {d['expected_type']}) | urgency={d['predicted_urgency']} (expected {d['expected_urgency']})"):
                st.caption(f"Report: {d['text']}")
                st.markdown(f"**Educator summary:** {d.get('educator_summary', 'N/A')}")

    st.markdown("---")
    st.markdown("#### 📝 Add Human Rating")
    st.caption("Pair human ratings with LLM-judge scores to validate the judge's reliability.")
    with st.form("human_rating"):
        scenario_id = st.selectbox("Scenario ID", [s["id"] for s in SCENARIOS])
        human_score = st.slider("Your rating (1–5)", 1, 5, 4)
        notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Save Rating")
        if submitted:
            if "human_ratings" not in st.session_state:
                st.session_state["human_ratings"] = []
            st.session_state["human_ratings"].append({
                "scenario_id": scenario_id, "score": human_score, "notes": notes
            })
            st.success(f"✓ Rating saved for {scenario_id}: {human_score}/5")

    if "human_ratings" in st.session_state and st.session_state["human_ratings"]:
        ratings = st.session_state["human_ratings"]
        st.markdown(f"**{len(ratings)} human ratings collected.**")

        if "advice_results" in st.session_state:
            import statistics
            matched = []
            for hr in ratings:
                for ar in st.session_state["advice_results"]:
                    if ar.scenario_id == hr["scenario_id"]:
                        matched.append((hr["score"], ar.llm_judge_overall))
            if len(matched) >= 2:
                human_scores = [m[0] for m in matched]
                llm_scores = [m[1] for m in matched]
                mean_diff = statistics.mean(abs(h - l) for h, l in matched)
                st.markdown(f"**Mean absolute difference (human vs LLM judge):** {mean_diff:.2f} — "
                            f"{'✅ Good agreement' if mean_diff < 0.8 else '⚠️ Some disagreement, review manually'}")
