import streamlit as st
import json
import os
from datetime import date, timedelta
from pathlib import Path

# Local imports
from config import settings
from services.masking_service import mask_digits
from services.llm_service import call_llm
from services.quality_gate import run_all_checks
from schemas.lever_coach_schema import LeverCoachLLMResponse
from schemas.plan_b_schema import PlanBLLMResponse

# ── App Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plan B for my SIP",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Knowledge Base & Prompts Loading ──────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
PROMPTS_DIR = Path(__file__).parent / "prompts"

@st.cache_data
def load_kb():
    kb_path = DATA_DIR / "knowledge_base.json"
    if kb_path.exists():
        with open(kb_path, encoding="utf-8") as f:
            return json.load(f)
    return {"facts": []}

@st.cache_data
def load_prompts():
    lc_prompt = (PROMPTS_DIR / "lever_coach_prompt.txt").read_text(encoding="utf-8")
    pb_prompt = (PROMPTS_DIR / "plan_b_prompt.txt").read_text(encoding="utf-8")
    return lc_prompt, pb_prompt

kb_data = load_kb()
facts_map = {f["id"]: f for f in kb_data.get("facts", [])}
lc_prompt_tmpl, pb_prompt_tmpl = load_prompts()

# ── Business Logic Helper Functions ───────────────────────────────────────────
def compute_edit_window(sip_day: int) -> str:
    today = date.today()
    try:
        sip_date = today.replace(day=sip_day)
    except ValueError:
        sip_date = (today.replace(day=1) + timedelta(days=32)).replace(day=sip_day)
    if sip_date <= today:
        m = today.month % 12 + 1
        y = today.year + (1 if m == 1 else 0)
        sip_date = date(y, m, sip_day)
    
    remaining = 2
    deadline = sip_date
    while remaining > 0:
        deadline -= timedelta(days=1)
        if deadline.weekday() < 5:  # Mon-Fri
            remaining -= 1
    return deadline.strftime("%d %b %Y")

# ── MANDATORY DISCLAIMER BANNER ───────────────────────────────────────────────
st.info("📚 **Educational information only. Not investment advice.** Never recommends any fund, stock, or amount.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌱 Plan B for my SIP")
    st.caption("Educational tool for first-time SIP investors on Groww.")
    st.markdown("---")
    st.markdown("**Core Rules:**")
    st.markdown("- Zero FOMO or fear tactics")
    st.markdown("- Automatic digit masking on PII")
    st.markdown("- Grounded strictly in Groww docs")
    st.markdown("---")
    st.page_link("pages/1_eval.py", label="Open Evaluation Suite (/eval) →", icon="📊")
    st.markdown("---")
    st.markdown("🔗 [Groww Help Desk](https://groww.in/help)")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Plan B for my SIP")
st.write("Understand which Groww adjustment feature fits your situation when a month gets tight.")

# ── ROUGH MONTH VIEW (Session State Persistence) ──────────────────────────────
if "saved_plan_b" in st.session_state and st.session_state["saved_plan_b"]:
    st.success(f"🌧️ **Rough month? Here is your saved Plan B:**\n\n> *\"{st.session_state['saved_plan_b']}\"*")
    if st.button("Clear saved Plan B", type="secondary"):
        del st.session_state["saved_plan_b"]
        st.rerun()

st.divider()

# ── SECTION 1: "My month feels tight" (Lever Coach) ────────────────────────────
st.subheader("1. My month feels tight")
st.write("Describe your situation in English or Hinglish (e.g. *salary 10 tarikh ko aati hai par SIP 5 ko kat jaata hai*).")

with st.form("lever_coach_form"):
    user_text = st.text_area(
        "What's happening this month?",
        placeholder="e.g. salary 10 tarikh ko aati hai par SIP 5 ko kat jaata hai or I have a big medical expense this month",
        height=100
    )
    col_date, col_btn = st.columns([1, 2])
    with col_date:
        sip_day = st.number_input("Your SIP Date (optional, 1-28)", min_value=1, max_value=28, value=None, step=1)
    
    st.caption("🔒 *Any sequence of 4+ digits is automatically masked for privacy before analysis.*")
    submitted = st.form_submit_button("Analyse Options →", type="primary")

if submitted and user_text.strip():
    masked_text, occurred = mask_digits(user_text)
    if occurred:
        st.warning(f"🛡️ **Digits Masked for Privacy:** `{masked_text}`")
    
    prompt = lc_prompt_tmpl.format(
        knowledge_base_json=json.dumps(kb_data),
        skip_rules_verified=str(settings.skip_rules_verified).lower(),
        user_input=masked_text
    )
    
    with st.spinner("Analyzing with Groq Llama-3.3..."):
        try:
            raw_response = call_llm(prompt, masked_text)
            validated = LeverCoachLLMResponse.model_validate(raw_response)
            quality = run_all_checks(validated.model_dump(), masked_text)
            
            # Quality Gate Check
            if not quality["checked"]:
                st.error("⚠️ **Verification Check:** We could not verify this against documented Groww facts.")
                st.info("I'm not sure about this one. The official place to check is [Groww Help](https://groww.in/help).")
            elif validated.situation_type in ("advice_request", "out_of_scope"):
                st.warning("ℹ️ **Educational Scope Only:** This tool does not provide fund choices, investment advice, or cancellation actions.")
                st.write("For official queries, please visit the [Groww Help Centre](https://groww.in/help).")
                st.caption("✅ Correct Refusal")
            else:
                st.success("✅ **Checked** — Grounded in official Groww Help facts.")
                st.markdown(f"**Explanation:** {validated.explanation}")
                st.caption(f"*Evidence detected:* \"{validated.evidence_quote}\"")
                
                # Show Levers
                st.markdown("### Matching Groww Adjustment Options:")
                levers = [l.value for l in validated.levers if l.value != "none_applicable"]
                if levers:
                    cols = st.columns(len(levers))
                    for idx, lever in enumerate(levers):
                        with cols[idx]:
                            if lever == "change_date":
                                st.markdown("#### 📅 Change SIP Date")
                                fact = facts_map.get("K1", {})
                                for step in fact.get("steps", []):
                                    st.write(f"- {step}")
                                st.markdown(f"[Groww Help Guide ↗]({fact.get('source_url')})")
                            elif lever == "change_amount":
                                st.markdown("#### 💰 Change SIP Amount")
                                fact = facts_map.get("K1", {})
                                for step in fact.get("steps", []):
                                    st.write(f"- {step}")
                                st.markdown(f"[Groww Help Guide ↗]({fact.get('source_url')})")
                            elif lever == "skip_one":
                                st.markdown("#### ⏭️ Skip One Instalment")
                                fact = facts_map.get("K3", {})
                                for step in fact.get("steps", []):
                                    st.write(f"- {step}")
                                st.markdown(f"[Groww Help Guide ↗]({fact.get('source_url')})")
                
                # Edit Window Calculator
                if sip_day:
                    deadline_str = compute_edit_window(int(sip_day))
                    st.info(f"ℹ️ **Edit Window Timing:** Changes made after about **{deadline_str}** may apply only from the following instalment. Your confirmation screen shows exact timing.")

        except Exception as e:
            st.error(f"Analysis error: {e}")
            st.info("Official documentation is always available at [Groww Help](https://groww.in/help).")

st.divider()

# ── SECTION 2: "My Plan B" (Plan B Card) ───────────────────────────────────────
st.subheader("2. My Plan B")
st.write("Write a one-line commitment in your own words: *\"If a month gets tight, I will...\"*")

with st.form("plan_b_form"):
    plan_input = st.text_input("If a month gets tight, I will...", placeholder="e.g. change my SIP date to after the 15th")
    pb_submitted = st.form_submit_button("Generate Plan B Card →", type="primary")

if pb_submitted and plan_input.strip():
    pb_prompt = pb_prompt_tmpl.format(
        plan_text=plan_input,
        confirmed_lever="none provided"
    )
    with st.spinner("Generating card..."):
        try:
            raw_pb = call_llm(pb_prompt, plan_input)
            validated_pb = PlanBLLMResponse.model_validate(raw_pb)
            issues = validated_pb.issues or []
            
            if "cancel_intent" in issues:
                st.warning("⚠️ **Notice:** You mentioned cancelling or stopping. Cancellation steps are not covered in this tool. Please check [Groww Help](https://groww.in/help).")
            elif "unsupported_feature" in issues:
                st.warning("⚠️ **Unsupported Feature:** Groww does not have a multi-month pause feature. The documented option is **skipping one instalment**.")
                if st.button("Use 'Skip One Instalment' instead?"):
                    st.session_state["saved_plan_b"] = "If a month gets tight, I will skip one instalment using Edit SIP in Groww."
                    st.success("Plan B saved!")
                    st.rerun()
            else:
                card_text = validated_pb.card_text
                st.markdown(f"""
                <div style="background-color: #E8F8F5; border-left: 5px solid #00D09C; padding: 15px; border-radius: 8px;">
                    <h4 style="margin:0; color: #117A65;">📋 Your Plan B</h4>
                    <p style="font-size: 1.1em; font-style: italic; margin-top: 8px;">"{card_text}"</p>
                </div>
                """, unsafe_allow_html=True)
                st.session_state["temp_card"] = card_text
        except Exception as e:
            st.error(f"Error generating card: {e}")

if "temp_card" in st.session_state:
    if st.button("Approve & Save to This Device"):
        st.session_state["saved_plan_b"] = st.session_state["temp_card"]
        del st.session_state["temp_card"]
        st.success("✅ Card saved on this device!")
        st.rerun()

