import os
import re
import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx2txt
from dotenv import load_dotenv
import logging

# Suppress pdf-related warnings for a cleaner console output
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-2.0-flash"  # User-specified model, ensure it's accessible

# --- Helper Functions ---
def extract_text_from_file(uploaded_file):
    """Extracts text from PDF or DOCX files."""
    try:
        if uploaded_file.name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif uploaded_file.name.endswith(".docx"):
            return docx2txt.process(uploaded_file)
    except Exception as e:
        st.error(f"Error extracting text from {uploaded_file.name}: {e}")
    return ""

def analyze_resume_with_gemini(resume_text, jd_text, model_instance):
    """Analyzes resume against job description using the provided Gemini model instance."""
    prompt = f"""Analyze the following resume and compare it against the job description.

Resume:
---
{resume_text}
---

Job Description:
---
{jd_text}
---

Instructions for Output:
1.  Break down the resume into the following sections. If a section is not present in the resume, explicitly state "Not Found" or "None" for that section's content.
    - Contact Info
    - Skills (ensure this includes all technical and soft skills listed)
    - Experience
    - Education
    - Certifications (if any)
    - Achievements / Others (if any, combine these or list as "Achievements" or "Others" if only one type exists)

2.  Provide an overall match score as a percentage (e.g., Overall Match Score: 85%). This score should reflect how well the resume matches the job description.

3.  Format the output clearly:
    - Each section should start with its name (e.g., "Skills") on a new line.
    - List items within sections using hyphens (e.g., "- Skill 1"). Do not use asterisks.
    - Return ONLY the section-wise breakdown and the overall match score. Do not add any extra explanations, conversational text, or disclaimers.
    - Ensure each requested section header is present in your output, even if its content is "None".
"""
    try:
        response = model_instance.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}") # Display error directly in the app
        return f"Error during Gemini API call: {str(e)}" # Return error string for internal handling

# --- Main Streamlit App ---
st.set_page_config(page_title="ATS Resume Matcher", layout="wide")
st.title("📄 ATS Resume Matcher")
st.markdown("Upload a resume and paste a job description. Analysis will start automatically when both fields are populated.")

# Initialize Gemini Model (once)
try:
    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Error initializing Gemini model ({MODEL_NAME}): {e}")
    st.info("Please ensure the model name is correct and you have access.")
    st.stop()

for key, default_val in [("processed", False), ("result", ""), ("resume_filename", ""), ("last_jd", "")]:
    st.session_state.setdefault(key, default_val)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Upload Resume")
    resume_file = st.file_uploader("Formats: PDF, DOCX", type=["pdf", "docx"], key="resume_uploader")
with col2:
    st.subheader("Job Description")
    jd_text_input = st.text_area("Paste job description here", height=280, key="jd_input")

current_resume_name = resume_file.name if resume_file else None
resume_changed = current_resume_name and st.session_state.resume_filename != current_resume_name
jd_changed = st.session_state.last_jd != jd_text_input # True if text area content differs

if resume_changed or jd_changed:
    st.session_state.processed = False
    st.session_state.result = "" 
    if resume_changed: st.session_state.resume_filename = current_resume_name
    st.session_state.last_jd = jd_text_input # Update last_jd to track changes for the next run

# Core processing logic: runs automatically if inputs are ready and not yet processed
if not st.session_state.processed and resume_file and jd_text_input.strip():
    with st.spinner(f"Extracting text from {resume_file.name}..."):
        resume_text = extract_text_from_file(resume_file)
    
    if resume_text: 
        with st.spinner("🤖 Gemini is analyzing... This may take a moment."):
            st.session_state.result = analyze_resume_with_gemini(resume_text, jd_text_input, gemini_model)
        st.session_state.processed = True 
    elif resume_file: # Text extraction failed
        # Error for extraction failure is shown by extract_text_from_file
        st.session_state.processed = True # Mark as processed to avoid re-looping this error

# --- Result Display ---
if st.session_state.result:
    result_text = st.session_state.result
    is_api_error_string = result_text.startswith("Error during Gemini API call")

    if not is_api_error_string:
        score_match = re.search(r"Overall Match Score:\s*(\d+)%?", result_text, re.IGNORECASE)
        overall_score_value = score_match.group(1) if score_match else None

        if overall_score_value:
            try:
                score_int = int(overall_score_value)
                color = "green" if score_int >= 75 else "orange" if score_int >= 50 else "red"
                
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 20px; padding-top: 10px;">
                    <span style="font-size: 1.2em; font-weight: bold; display: block; margin-bottom: 5px;">Overall Match Score</span>
                    <span style="font-size: 3em; color: {color}; font-weight: bold;">{score_int}%</span>
                </div>
                """, unsafe_allow_html=True)
                st.progress(score_int / 100.0)
                st.markdown("---") 
            except ValueError:
                st.warning(f"Could not parse score from analysis: {overall_score_value}")
        else:
            st.warning("Overall Match Score not found in the analysis provided by the AI.")
    
    if is_api_error_string:
        # Error was already displayed by analyze_resume_with_gemini via st.error
        pass 
    else:
        st.success("Analysis Processed!") 

        st.subheader("📊 Detailed Analysis")
        sections_to_extract = ["Contact Info", "Skills", "Experience", "Education", "Certifications", "Achievements", "Others"]
        # Delimiters include section names and the score line to prevent score bleeding into the last section
        all_delimiters = sections_to_extract + ["Overall Match Score"]
        
        extracted_data_for_display = []
        seen_content_blocks = set()

        for section_name in sections_to_extract:
            # Regex: anchored to start of line, captures content until next known delimiter or end of string.
            # Critical for parsing Gemini's structured output.
            pattern = rf"^{re.escape(section_name)}[^\n]*\n(.*?)(?=\n(?:{'|'.join(re.escape(s) for s in all_delimiters)})[^\n]*\n|\Z)"
            match = re.search(pattern, result_text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                content = match.group(1).strip()
                is_placeholder = content.lower() in ["none", "not found", "n/a"]
                if content and not is_placeholder and content not in seen_content_blocks:
                    extracted_data_for_display.append({"Section": section_name, "Content": content.replace("\n", "<br>")})
                    seen_content_blocks.add(content) 
                elif content and is_placeholder: 
                    extracted_data_for_display.append({"Section": section_name, "Content": f"<i>{content}</i>"})
        
        if extracted_data_for_display:
            st.markdown("### Extracted Resume Sections")
            for item in extracted_data_for_display:
                is_empty_placeholder = item['Content'].lower().startswith("<i>") and item['Content'].lower().endswith("</i>")
                with st.expander(f"**{item['Section']}**", expanded=not is_empty_placeholder):
                    st.markdown(item['Content'], unsafe_allow_html=True)
        elif not is_api_error_string : 
            st.warning("No detailed sections could be extracted from the AI's analysis.")

# Handling for scenarios where processing was attempted but no result (e.g., text extraction failed earlier)
elif st.session_state.processed and not st.session_state.result:
    if not resume_file and jd_text_input.strip(): st.info("Please upload a Resume to begin analysis.")
    elif resume_file and not jd_text_input.strip(): st.info("Please paste the Job Description to begin analysis.")