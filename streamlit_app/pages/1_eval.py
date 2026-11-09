import streamlit as st
import asyncio
import csv
import pandas as pd
from pathlib import Path
from services.eval_service import run_eval_set

st.set_page_config(page_title="Evaluation Suite - Plan B for my SIP", page_icon="📊", layout="wide")

st.info("📚 **Educational information only. Not investment advice.**")
st.title("📊 Evaluation Suite (/eval)")
st.caption("Benchmark Golden Dataset testing accuracy, safety guardrails, refusal rate, and ungrounded facts.")

DATA_FILE = Path(__file__).parent.parent / "data" / "golden_set.csv"

col_model, col_ver, col_cost, col_btn = st.columns([2, 1, 1, 1])
with col_model:
    model_name = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mock"], index=0)
with col_ver:
    prompt_ver = st.text_input("Prompt Version", value="v1.0")
with col_cost:
    cost_cap = st.number_input("Cost Cap ($)", value=1.00, step=0.1)
with col_btn:
    st.write("")
    st.write("")
    run_btn = st.button("▶ Run Eval", type="primary")

if run_btn:
    if not DATA_FILE.exists():
        st.error("golden_set.csv not found!")
    else:
        with open(DATA_FILE, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        with st.spinner(f"Evaluating {len(rows)} test cases against {model_name}..."):
            res = asyncio.run(run_eval_set(rows, model_name, prompt_ver, cost_cap))
            
            st.success("✅ Evaluation Complete!")
            
            # Key metrics in cards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Lever Exact Accuracy", f"{res['lever_accuracy_exact']*100:.1f}%")
            m2.metric("Situation Accuracy", f"{res['situation_type_accuracy']*100:.1f}%")
            m3.metric("Correct Refusal Rate", f"{res['correct_refusal_rate']*100:.1f}%")
            m4.metric("Faithfulness Rate", f"{res['card_faithfulness_rate']*100:.1f}%")
            
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Banned Words Violations", res['banned_word_violations'], delta="Target: 0", delta_color="inverse")
            s2.metric("Ungrounded Facts Rate", f"{res['ungrounded_fact_rate']*100:.1f}%", delta="Target: 0%", delta_color="inverse")
            s3.metric("Fallback Rate", f"{res['fallback_rate']*100:.1f}%")
            s4.metric("Est. Cost", f"${res['estimated_cost_usd']:.4f}")
            
            # Failures Table
            if res.get("failures"):
                st.subheader(f"Failures & Drift ({len(res['failures'])})")
                df_failures = pd.DataFrame(res["failures"])
                st.dataframe(df_failures, use_container_width=True)
            else:
                st.balloons()
                st.success("🎉 All test rows met benchmark requirements with 0 failures!")

st.divider()
st.subheader("📋 Golden Dataset Rows")
if DATA_FILE.exists():
    df_golden = pd.read_csv(DATA_FILE)
    st.dataframe(df_golden, use_container_width=True)

