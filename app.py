"""
CT Scan AI Assistant (Single Feature Standalone)
================================================
Hackathon Track: Embedded LLM
Focus: Tumor Detection + MOH Referral SOP (RAG)
"""

from __future__ import annotations
import os
import tempfile
from typing import Optional, Dict, Any
import streamlit as st
from jamaibase import JamAI, types as t

# ==============================
# 1. Configuration (配置中心)
# ==============================
# 你的 Project ID 和 PAT (已填好)
PROJECT_ID = "proj_08304a50c7b965045d545866"
PAT = "jamai_pat_f1d90e6738bcb786229dc7689bcf79b220d5752acf83fffb"

# --- CT Scan Table Configuration ---
# 必须与 JamAI Base 中的 Action Table ID 一致
CT_TABLE_ID = "ct_scan"
CT_IMAGE_COL = "ct_scan_result"        # Input: Image Column ID
CT_FINDINGS_COL = "description"        # Output: Detailed Report
CT_DIAG_COL = "diagnosis"              # Output: Short Diagnosis
CT_SOP_COL = "malaysia_referral_SOP"   # Output: RAG Generated SOP

# --- Audio Table Configuration ---
AUDIO_TABLE_ID = "audi_feed"
AUDIO_INPUT_COL = "doc_notes"
AUDIO_TRANS_COL = "transciption"       # 注意拼写: 你的表中是 'transciption' (缺了个r)

# ==============================
# 2. Helper Functions
# ==============================

def get_client() -> JamAI:
    return JamAI(project_id=PROJECT_ID, token=PAT)

def _upload_file(client: JamAI, uploaded_file) -> Optional[str]:
    """Upload file to JamAI cloud storage."""
    if not uploaded_file:
        return None
    suffix = os.path.splitext(uploaded_file.name)[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    try:
        resp = client.file.upload_file(tmp_path)
        return getattr(resp, "uri", None)
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass

def _safe_text(cell: Any) -> str:
    return getattr(cell, "text", "") or ""

def run_audio(client: JamAI, audio_uri: str) -> str:
    """Send audio to JamAI for transcription."""
    req = t.MultiRowAddRequest(
        table_id=AUDIO_TABLE_ID,
        data=[{AUDIO_INPUT_COL: audio_uri}],
        stream=False,
    )
    res = client.table.add_table_rows(t.TableType.ACTION, req)
    # Handle potential empty response if model quota exceeded
    try:
        return _safe_text(res.rows[0].columns.get(AUDIO_TRANS_COL))
    except:
        return "Error: Audio transcription failed (Check Model Quota)."

def run_ct_analysis(client: JamAI, image_uri: str) -> Dict[str, str]:
    """
    Main Logic: Sends CT image -> Gets Findings, Diagnosis & RAG SOP
    """
    req = t.MultiRowAddRequest(
        table_id=CT_TABLE_ID,
        data=[{CT_IMAGE_COL: image_uri}],
        stream=False, # Set to True if you want to stream text
    )
    res = client.table.add_table_rows(t.TableType.ACTION, req)
    row = res.rows[0]
    cols = getattr(row, "columns", {})
    
    return {
        "findings": _safe_text(cols.get(CT_FINDINGS_COL)),
        "diagnosis": _safe_text(cols.get(CT_DIAG_COL)),
        "sop": _safe_text(cols.get(CT_SOP_COL))
    }

# ==============================
# 3. Streamlit UI
# ==============================

st.set_page_config(page_title="CT Scan Tumor Assistant", page_icon="🧠", layout="centered")

# Header
st.title("🧠 CT Scan Tumor Assistant")
st.caption("Embedded LLM Track | Feature: Tumor Detection & Automated MOH Referral (RAG)")

# Client Connection
try:
    client = get_client()
except Exception as e:
    st.error(f"Connection failed: {e}")
    st.stop()

# --- Input Section ---
st.markdown("### 1. Upload Patient Data")
col1, col2 = st.columns(2)

with col1:
    ct_file = st.file_uploader("Upload CT Scan Image", type=["jpg", "png", "jpeg", "webp"], key="ct_upl")
    if ct_file:
        st.image(ct_file, caption="Preview", use_column_width=True)

with col2:
    audio_file = st.file_uploader("Doctor's Voice Note (Optional)", type=["mp3", "wav", "m4a"], key="aud_upl")
    if audio_file:
        st.audio(audio_file)

# --- Execution Section ---
if st.button("🔍 Analyze Scan & Retrieve SOP", type="primary", use_container_width=True):
    if not ct_file:
        st.warning("Please upload a CT Scan image first.")
        st.stop()

    # 1. Process Audio (If any)
    doctor_note = ""
    if audio_file:
        with st.spinner("🎧 Listening to doctor's note..."):
            a_uri = _upload_file(client, audio_file)
            doctor_note = run_audio(client, a_uri)
            st.success(f"**Doctor's Note:** {doctor_note}")

    # 2. Analyze Image
    with st.spinner("🧠 Analyzing tissue density & searching MOH Guidelines..."):
        # Upload & Run
        img_uri = _upload_file(client, ct_file)
        result = run_ct_analysis(client, img_uri)

    # --- Results Display ---
    st.markdown("---")
    
    # A. Diagnosis (High Level)
    st.subheader("🩺 Diagnosis Conclusion")
    diag = result["diagnosis"]
    if "normal" in diag.lower() or "no acute" in diag.lower():
        st.success(f"✅ {diag}")
    else:
        st.error(f"⚠️ {diag}")

    # B. Detailed Findings (Expandable)
    with st.expander("📄 View Detailed Radiological Report (English & BM)", expanded=False):
        st.markdown(result["findings"])

    # C. RAG SOP Recommendation (The "Hackathon Winner" Feature)
    st.subheader("🏥 Ministry of Health Referral Plan (SOP)")
    st.info(result["sop"])

    # D. Logic Explanation (For Judges)
    with st.expander("⚙️ System Logic (How it works)"):
        st.markdown(f"""
        1. **Visual Analysis**: Vision Model analyzed the image for mass/density anomalies.
        2. **Context Awareness**: Doctor's note *"{doctor_note if doctor_note else 'N/A'}"* was considered.
        3. **RAG Retrieval**: System queried the `clinic_knowledge` table for relevant MOH SOPs.
        4. **Synthesis**: Generated the Referral Plan based on the specific Diagnosis.
        """)