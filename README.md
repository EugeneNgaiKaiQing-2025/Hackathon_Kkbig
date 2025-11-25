# 🏥 AI Medical Assistant (Malaysia) - Embedded LLM Track

## Project Overview
This project is an AI-powered medical assistant designed for Malaysian clinics. It leverages **JamAI Base** to analyze medical imaging (CT Scans) and provide actionable referral advice based on the **Ministry of Health (MOH/KKM) Malaysia guidelines**.

### 🌟 Key Features
1.  **🧠 Tumor Detection (Vision)**: Analyzes CT Scans to identify potential masses or tumors.
2.  **🇲🇾 Localized RAG (SOP Retrieval)**: Automatically retrieves standard referral SOPs from MOH guidelines using JamAI's Knowledge Table.
3.  **🗣️ Bilingual Support**: Generates reports in both **English** and **Bahasa Melayu**.
4.  **🎙️ Voice Command**: Accepts doctor's verbal notes via audio processing.

## 🛠️ Tech Stack
* **Frontend**: Streamlit (Python)
* **Backend / LLM Ops**: JamAI Base (Action Tables + Knowledge Tables)
* **Models Used**:
    * Vision: Qwen-VL / Gemini 1.5 Pro
    * Audio: Whisper / Qwen-Audio
    * Reasoning: Llama 3 / GPT-4o

## 🚀 How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Credentials**
    * Open `app_ct.py`.
    * Replace `PROJECT_ID` and `PAT` with your JamAI Base credentials.

4.  **Run the App**
    ```bash
    streamlit run app_ct.py
    ```

## 📂 Project Structure
* `app_ct.py`: Main application code for CT Scan analysis.
* `malaysia_referral_sop.txt`: Source document for RAG (MOH Guidelines).
* `requirements.txt`: Python dependencies.

---
*Submitted for Universiti Malaya Hackathon 2025 - PEKOM CODE FEST*