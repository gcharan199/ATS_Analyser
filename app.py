import os
import re
import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx2txt
from dotenv import load_dotenv
import logging

# Suppress pdf-related warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-2.0-flash"

# --- Helper Functions ---
def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif uploaded_file.name.endswith(".docx"):
            return docx2txt.process(uploaded_file)
        else:
            st.warning("Unsupported file format. Please upload a PDF or DOCX file.")
    except Exception as e:
        st.error(f"Error extracting text from {uploaded_file.name}: {e}")
    return ""

def analyze_resume_with_gemini(resume_text, model_instance):
    prompt = f"""Extract the following fields from the resume:

Resume:
---
{resume_text}
---

Instructions for Output:
1. Extract and return these fields as separate sections (even if not found, state 'Not Found' or 'None'):
    - Name
    - Contact
    - Email-ID
    - Skills (all technical and soft skills listed)
2. Format output clearly:
    - Each section should start with its name (e.g., "Name") on a new line.
    - List items within sections using hyphens (e.g., "- Skill 1"). Do not use asterisks.
    - Return ONLY the section-wise breakdown. Do not add any extra explanations, conversational text, or disclaimers.
    - Ensure each requested section header is present in your output, even if its content is "None".
"""
    try:
        response = model_instance.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return f"Error during Gemini API call: {str(e)}"

# --- Streamlit App ---
st.set_page_config(page_title="ATS Resume Extractor", layout="wide")
st.title("📄 ATS Resume Extractor")
st.markdown("Upload a resume. The app extracts Name, Contact, Email-ID, and Skills.")

# Load Gemini
try:
    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Error initializing Gemini model: {e}")
    st.stop()

# Initialize session state
for key, default_val in [("processed", False), ("result", ""), ("resume_filename", ""), ("excel_format", "")]:
    st.session_state.setdefault(key, default_val)

st.subheader("Upload Resume")
resume_file = st.file_uploader("Formats: PDF, DOCX", type=["pdf", "docx"], key="resume_uploader")

current_resume_name = resume_file.name if resume_file else None
resume_changed = current_resume_name and st.session_state.resume_filename != current_resume_name

if resume_changed:
    st.session_state.processed = False
    st.session_state.result = ""
    st.session_state.excel_format = ""
    st.session_state.resume_filename = current_resume_name

# Process and analyze
if not st.session_state.processed and resume_file:
    with st.spinner(f"Extracting text from {resume_file.name}..."):
        resume_text = extract_text_from_file(resume_file)
    if resume_text:
        with st.spinner("🤖 Gemini is analyzing..."):
            st.session_state.result = analyze_resume_with_gemini(resume_text, gemini_model)
        st.session_state.processed = True
    else:
        st.session_state.processed = True

# Extract fields and generate Excel format
if st.session_state.result:
    result_text = st.session_state.result
    if result_text.startswith("Error during Gemini API call"):
        st.error(result_text)
    else:
        fields = ["Name", "Contact", "Email-ID", "Skills"]
        extracted_fields = {}
        for field in fields:
            pattern = rf"^{re.escape(field)}[^\n]*\n(.*?)(?=\n(?:{'|'.join(re.escape(f) for f in fields)})[^\n]*\n|\Z)"
            match = re.search(pattern, result_text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                content = match.group(1).strip()
                extracted_fields[field] = content if content else "Not Found"
            else:
                extracted_fields[field] = "Not Found"

        # Create Excel-formatted line
        excel_headers = ["Name", "Contact No.", "Email-ID", "Skills"]
        cleaned_data = []
        for field in fields:
            value = extracted_fields.get(field, "Not Found")
            cleaned_value = value.replace('\n', ' ').replace('\r', ' ').strip()
            cleaned_value = re.sub(r'[-•*]\s*', '', cleaned_value)
            cleaned_data.append(cleaned_value)
        full_excel_format = "\t".join(cleaned_data)
        st.session_state.excel_format = full_excel_format

        # --- Show COPY TO EXCEL block here ---
        st.markdown("---")
        st.markdown("### 📋 Copy for Excel")

        st.components.v1.html(f"""
            <div style="font-family: Arial, sans-serif;">
              <textarea id="excelData" rows="4" style="width: 100%; padding: 10px; font-family: monospace; border: 1px solid #ccc; border-radius: 5px;">{full_excel_format}</textarea>
              <button onclick="copyToClipboard()" style="margin-top: 10px; background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                📋 Copy
              </button>
            </div>
            <script>
            function copyToClipboard() {{
                const textarea = document.getElementById("excelData");
                textarea.select();
                document.execCommand("copy");
                alert("✅ Data copied to clipboard!");
            }}
            </script>
        """, height=180)

        st.info("💡 Tip: Paste this into Excel. It will auto-fill Name, Contact No., Email-ID, and Skills.")

        # Show extracted fields
        st.markdown("---")
        st.subheader("📊 Extracted Fields")
        for field, value in extracted_fields.items():
            st.markdown(f"**{field}:**")
            st.code(value, language=None)

        with st.expander("📄 Full Extraction Output"):
            st.markdown(result_text)

elif st.session_state.processed and not st.session_state.result:
    if not resume_file:
        st.info("Please upload a resume to begin extraction.")
