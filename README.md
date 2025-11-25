# 🏥 AI Medical Assistant (Malaysia) - Embedded LLM Track

## Project Overview
This project is an AI-powered medical assistant tailored for **Klinik Desa (Rural Clinics)** and SMEs in Malaysia. It leverages **JamAI Base** to analyze medical imaging (CT Scans), automate documentation, and provide actionable referral advice based on the **Ministry of Health (MOH/KKM) Malaysia guidelines**.

### 🌟 Key Features
1.  **🧠 Tumor Detection (Vision)**: Analyzes CT Scans to identify potential masses, lesions, or tumors with high precision.
2.  **🇲🇾 Localized RAG (SOP Retrieval)**: Automatically queries the **Ministry of Health (MOH)** guidelines to determine the correct referral center (e.g., HKL, IKN).
3.  **📄 Automated Workflow**: Instantly generates and downloads an official **Referral Letter** (.txt) for patient transfer, saving doctors' time.
4.  **🗣️ Bilingual Support**: Generates diagnostic reports in both **English** and **Bahasa Melayu**.
5.  **🎙️ Voice Command**: Accepts doctor's verbal notes via audio processing (Manglish supported).

![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)

## ⚙️ System Architecture & Data Flow
1.  **Multimodal Ingestion**: Captures **CT Scans (Image)** and **Doctor's Voice Notes (Audio)** via the Streamlit frontend.

2.  **Context Injection Layer**: The audio is transcribed into text and **injected directly** into the Vision Model's prompt. This ensures the AI analyzes the image *while knowing* the patient's clinical history.

3.  **Visual Reasoning**: JamAI's Action Table analyzes the visual data for masses/lesions, cross-referencing with the injected doctor's context.

4.  **Automated RAG Retrieval**: Upon detecting a diagnosis, the system autonomously queries the `clinic_knowledge` table to retrieve the specific **MOH Referral SOPs**.

5.  **SOP-Aligned Synthesis**: The final output combines visual findings, diagnosis, and retrieved government protocols to generate an actionable **Referral Plan** and **Official Letter**.

## 🛠️ Tech Stack
* **Frontend**: Streamlit (Python)
* **Backend / LLM Ops**: JamAI Base (Action Tables + Knowledge Tables)
* **Models Used**:
    * Vision: ELLM Qwen3 VL (30B-A3B)
    * Audio: ELLM Qwen2 Audio (7B)
    * Reasoning: ELLM Qwen3 VL (30B-A3B)

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
* `app_ct.py`: Main application code (CT Scan + RAG + Letter Generation).
* `malaysia_referral_sop.txt`: Source document for RAG (MOH Guidelines).
* `requirements.txt`: Python dependencies.

---
*Submitted for Universiti Malaya Hackathon 2025 - PEKOM CODE FEST*