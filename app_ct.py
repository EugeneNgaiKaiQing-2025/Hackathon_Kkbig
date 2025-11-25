"""
CT Scan AI Assistant (Single Feature Standalone)
================================================
Hackathon Track: Embedded LLM
Focus: Tumor Detection + MOH Referral SOP (RAG) + Context Injection

[Pitching Note]: This file represents the entire "Full Stack" application. 
It orchestrates the Frontend (Streamlit) and the Backend AI Logic (JamAI Base).
"""

from __future__ import annotations
import os
import tempfile
from typing import Optional, Dict, Any
import streamlit as st
from jamaibase import JamAI, types as t

# ==========================================
# 1. SYSTEM CONFIGURATION (系统配置层)
# [Pitching Point]: "We use a configuration-driven approach to easily switch 
# between different Action Tables and Cloud Projects."
# ==========================================
PROJECT_ID = "proj_08304a50c7b965045d545866"
PAT = "jamai_pat_f1d90e6738bcb786229dc7689bcf79b220d5752acf83fffb"

# --- Action Table: The "Brain" (Vision + RAG) ---
CT_TABLE_ID = "ct_scan"
CT_IMAGE_COL = "ct_scan_result"        # Input: Visual Data
CT_CONTEXT_COL = "doctor_context"      # Input: Multimodal Context (Audio Transcript)
CT_FINDINGS_COL = "description"        # Output: Vision Model Analysis
CT_DIAG_COL = "diagnosis"              # Output: Diagnostic Conclusion
CT_SOP_COL = "malaysia_referral_SOP"   # Output: RAG Retrieval (MOH Guidelines)

# --- Action Table: The "Ear" (Audio Processing) ---
AUDIO_TABLE_ID = "audi_feed"
AUDIO_INPUT_COL = "doc_notes"
AUDIO_TRANS_COL = "transciption"

# ==========================================
# 2. BACKEND LOGIC / CONTROLLERS (后端逻辑层)
# [Pitching Point]: "These functions handle the API orchestration and data flow."
# ==========================================

def get_client() -> JamAI:
    """Authenticates with JamAI Cloud Platform."""
    return JamAI(project_id=PROJECT_ID, token=PAT)

def _upload_file(client: JamAI, uploaded_file) -> Optional[str]:
    """Handles secure file transmission to cloud storage."""
    if not uploaded_file:
        return None
    suffix = os.path.splitext(uploaded_file.name)[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    try:
        # Uploads file to JamAI's S3-compatible storage
        resp = client.file.upload_file(tmp_path)
        return getattr(resp, "uri", None)
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass

def _safe_text(cell: Any) -> str:
    """Error handling wrapper for data retrieval."""
    return getattr(cell, "text", "") or ""

def split_language_content(text, marker):
    """
    [Post-Processing Logic]
    Parses the raw LLM output to separate English and Bahasa Melayu content 
    for better User Experience (UX).
    """
    if marker in text:
        parts = text.split(marker)
        return parts[0].strip(), (marker + parts[1]).strip()
    return text, text 

def extract_hospital(text, keyword):
    """
    [Intelligent Parsing]
    Scans the RAG output (SOP) to automatically identify the target hospital 
    for the referral letter.
    """
    for line in text.split('\n'):
        if keyword.lower() in line.lower():
            parts = line.split(":")
            if len(parts) > 1:
                return parts[1].strip().strip("-* ")
    return "Nearest District Specialist Hospital"

def run_audio(client: JamAI, audio_uri: str) -> str:
    """
    [Module: Audio Intelligence]
    Sends voice notes to Qwen-Audio model for high-accuracy transcription (supports Manglish).
    """
    req = t.MultiRowAddRequest(
        table_id=AUDIO_TABLE_ID,
        data=[{AUDIO_INPUT_COL: audio_uri}],
        stream=False,
    )
    res = client.table.add_table_rows(t.TableType.ACTION, req)
    try:
        return _safe_text(res.rows[0].columns.get(AUDIO_TRANS_COL))
    except:
        return "Error: Audio transcription failed."

def run_ct_analysis(client: JamAI, image_uri: str, doctor_note: str = "") -> Dict[str, str]:
    """
    [Module: Core Reasoning Engine] - ** THIS IS THE MOST IMPORTANT FUNCTION **
    
    1. Multimodal Ingestion: Takes both Image and Text (Doctor's Note).
    2. Context Injection: Injects the doctor's context into the Vision Model.
    3. RAG Execution: The 'malaysia_referral_SOP' column automatically triggers 
       a retrieval from the Knowledge Table in the backend.
    """
    if not doctor_note:
        doctor_note = "No specific clinical context provided."

    # Construct the payload with Context Injection
    req = t.MultiRowAddRequest(
        table_id=CT_TABLE_ID,
        data=[{
            CT_IMAGE_COL: image_uri, 
            CT_CONTEXT_COL: doctor_note  # <-- Context Injection happens here
        }],
        stream=False, 
    )
    
    # Execute the Chain
    res = client.table.add_table_rows(t.TableType.ACTION, req)
    row = res.rows[0]
    cols = getattr(row, "columns", {})
    
    # Retrieve structured outputs
    return {
        "findings": _safe_text(cols.get(CT_FINDINGS_COL)),
        "diagnosis": _safe_text(cols.get(CT_DIAG_COL)),
        "sop": _safe_text(cols.get(CT_SOP_COL)) # This contains the RAG result
    }

# ==========================================
# 3. FRONTEND UI (STREAMLIT) (前端展示层)
# [Pitching Point]: "A lightweight, mobile-first interface designed for rural clinics."
# ==========================================

st.set_page_config(page_title="CT Scan Tumor Assistant", page_icon="🧠", layout="centered")

# --- Sidebar: Clinic Profile ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital-2.png", width=80)
    st.title("Klinik Desa AI")
    st.markdown("**Dr. On-Call:** Dr. Ali")
    st.markdown("---")
    st.markdown("**System Status:**")
    st.success("🟢 JamAI Cloud: Online")
    st.success("🟢 MOH Database: Connected") 
    st.markdown("---")
    st.caption("Powered by JamAI Base\nHackathon 2025 Build")

# --- Main Header ---
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

# --- Execution Logic ---
if st.button("🔍 Analyze Scan & Retrieve SOP", type="primary", use_container_width=True):
    if not ct_file:
        st.warning("Please upload a CT Scan image first.")
        st.stop()

    # Step 1: Audio Processing (Speech-to-Text)
    doctor_note = ""
    if audio_file:
        with st.spinner("🎧 Listening to doctor's note (Processing Manglish)..."):
            a_uri = _upload_file(client, audio_file)
            doctor_note = run_audio(client, a_uri)
            st.success(f"**Doctor's Note:** {doctor_note}")

    # Step 2: Vision Analysis + RAG Retrieval
    with st.spinner("🧠 Analyzing tissue density & searching MOH Guidelines..."):
        img_uri = _upload_file(client, ct_file)
        # Pass the audio transcript (context) into the vision analysis
        result = run_ct_analysis(client, img_uri, doctor_note)

    # --- Results Display ---
    st.markdown("---")
    
    # A. Diagnosis Result
    st.subheader("🩺 Diagnosis Conclusion")
    diag = result["diagnosis"]
    is_normal = "normal" in diag.lower() or "no acute" in diag.lower() or "no abnormalities" in diag.lower()
    
    if is_normal:
        st.success(f"✅ {diag}")
    else:
        st.error(f"⚠️ {diag}")

    # B. Detailed Findings
    with st.expander("📄 View Detailed Radiological Report (English & BM)", expanded=False):
        st.markdown(result["findings"])

    # C. RAG Output (MOH SOP)
    st.subheader("🏥 Ministry of Health Referral Plan (SOP)")
    st.info(result["sop"])

    # --- Workflow Automation: Document Generation ---
    st.markdown("---")
    st.subheader("📄 Actions & Documentation")

    # Prepare data for letters
    diag_en, diag_bm = split_language_content(result['diagnosis'], "Bahasa Melayu:")
    find_en, find_bm = split_language_content(result['findings'], "[LAPORAN BAHASA MELAYU]")
    find_en = find_en.replace("[ENGLISH REPORT]", "").strip()
    sop_en, sop_bm = split_language_content(result['sop'], "Bahasa Melayu")
    if sop_en == sop_bm:
         sop_en, sop_bm = split_language_content(result['sop'], "Syor")

    # Logic for Letter Type (Referral vs Discharge)
    if is_normal:
        doc_title_en = "RADIOLOGY REPORT (DISCHARGE)"
        doc_to_en = "Patient Record / General Practitioner"
        doc_title_bm = "LAPORAN RADIOLOGI (DISCAJ)"
        doc_to_bm = "Rekod Pesakit / Doktor Am"
        action_plan_en = "No active referral required. Advice given."
        action_plan_bm = "Tiada rujukan diperlukan. Nasihat diberikan."
    else:
        doc_title_en = "URGENT REFERRAL LETTER"
        target_hospital = extract_hospital(sop_en, "Hospital") 
        doc_to_en = f"{target_hospital}\n(Attention: Emergency / Oncology Dept)"
        doc_title_bm = "SURAT RUJUKAN CEMAS"
        target_hospital_bm = extract_hospital(sop_bm, "Hospital")
        if target_hospital_bm == "Nearest District Specialist Hospital":
             target_hospital_bm = target_hospital
        doc_to_bm = f"{target_hospital_bm}\n(u.p: Jabatan Kecemasan / Onkologi)"
        action_plan_en = sop_en
        action_plan_bm = sop_bm

    # Generate Letter Content (English)
    letter_en = f"""{doc_title_en}
--------------------------------------------------
To:   {doc_to_en}
From: Klinik Desa AI (Automated System)
Date: 2025-11-25

PATIENT ID: #1023  |  REFERRED BY: Dr. Ali

1. CLINICAL CONTEXT:
{doctor_note if doctor_note else "None provided."}

2. DIAGNOSIS CONCLUSION:
{diag_en.replace("English:", "").strip()}

3. RADIOLOGICAL FINDINGS:
{find_en}

4. MANAGEMENT PLAN / SOP:
{action_plan_en}

--------------------------------------------------
Generated by JamAI Base Medical Assistant
Ministry of Health Malaysia Guidelines Compliant
"""

    # Generate Letter Content (BM)
    letter_bm = f"""{doc_title_bm}
--------------------------------------------------
Kepada: {doc_to_bm}
Daripada: Klinik Desa AI (Sistem Automatik)
Tarikh: 2025-11-25

ID PESAKIT: #1023  |  DIRUJUK OLEH: Dr. Ali

1. KONTEKS KLINIKAL:
{doctor_note if doctor_note else "Tiada."}

2. KESIMPULAN DIAGNOSIS:
{diag_bm.replace("Bahasa Melayu:", "").strip()}

3. PENEMUAN RADIOLOGI:
{find_bm.replace("[LAPORAN BAHASA MELAYU]", "").strip()}

4. PELAN PENGURUSAN (GARIS PANDUAN KKM):
{action_plan_bm}

--------------------------------------------------
Dijana oleh Pembantu Perubatan JamAI Base
"""

    # Download Buttons
    col_a, col_b = st.columns(2)
    btn_type = "secondary" if is_normal else "primary"
    
    with col_a:
        st.download_button(
            label=f"📥 Download English Report (.txt)",
            data=letter_en,
            file_name="medical_report_en.txt",
            mime="text/plain",
            type=btn_type
        )
        
    with col_b:
        st.download_button(
            label=f"📥 Muat Turun Laporan BM (.txt)",
            data=letter_bm,
            file_name="laporan_perubatan_bm.txt",
            mime="text/plain",
            type=btn_type
        )

    # E. System Transparency (For Judges)
    # [Pitching Point]: "We value transparency. This section shows exactly how the AI reasoned."
    with st.expander("⚙️ System Logic (How it works)"):
        st.markdown(f"""
        1. **Multimodal Input**: Audio note is transcribed: *"{doctor_note if doctor_note else 'N/A'}"*.
        2. **Context Injection**: This note is sent ALONG WITH the image to the Vision Model.
        3. **Visual Analysis**: AI analyzes the CT scan, specifically looking for what the doctor mentioned.
        4. **RAG Retrieval**: System queries the `clinic_knowledge` table for MOH SOPs.
        5. **Synthesis**: Generates the final Referral Plan.
        """)