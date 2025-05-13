# ATS_Analyser📄

**Intelligently analyze resumes against job descriptions with AI-powered insights!**

The ATS Resume Matcher is a Streamlit web application that helps you quickly evaluate how well a resume matches a given job description. It leverages Google's Gemini AI to parse resume sections, identify key skills and experiences, and provide an overall match score, making the initial screening process more efficient.

## 🌟 Key Features

* **AI-Powered Analysis:** Utilizes Google Gemini for nuanced understanding of resume content.
* **Automatic Resume Parsing:** Extracts text and structure from PDF and DOCX resume files.
* **Job Description Comparison:** Intelligently compares the parsed resume against any provided job description.
* **Match Score & Breakdown:** Displays a clear percentage match score and a detailed section-by-section breakdown of the resume (Contact Info, Skills, Experience, Education, etc.).
* **User-Friendly Interface:** Interactive and easy-to-use web application built with Streamlit.
* **Automatic Processing:** Analysis begins as soon as a resume is uploaded and a job description is provided.

## 🛠️ Technology Stack

This project is built with the following core technologies:

* **Python:** The primary programming language.
* **Streamlit:** For building the interactive web application.
* **Google Gemini API:** For the AI-driven resume analysis (`google-generativeai` library).
* **PDFPlumber (`pdfplumber`):** For PDF file parsing.
* **Docx2txt (`docx2txt`):** For DOCX file parsing.
* **Python-dotenv:** For managing environment variables (API keys).

## ⚙️ Getting Started: Setup and Installation

Follow these steps to get the ATS Resume Matcher running on your local machine:

**1. Prerequisites:**
    * Ensure you have [Python](https://www.python.org/downloads/) (version 3.8 or newer) installed.
    * Make sure [Git](https://git-scm.com/downloads) is installed for cloning the repository.

**2. Clone the Repository:**
    Open your terminal or command prompt and run:
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```
    *(Replace `<your-repository-url>` and `<repository-name>` with your actual repository details, e.g., `https://github.com/yourusername/ats-checker.git` and `ats-checker`)*

**3. Create and Activate a Virtual Environment (Highly Recommended):**
    This isolates project dependencies, preventing conflicts with other Python projects. From the project's root directory:
    ```bash
    python -m venv venv
    ```
    Activate the environment:
    * **Windows:** `venv\Scripts\activate`
    * **macOS/Linux:** `source venv/bin/activate`
    You should see `(venv)` at the beginning of your terminal prompt.

**4. Install Dependencies:**
    All required Python packages are listed in the `requirements.txt` file (which should be included in this repository). Install them using pip:
    ```bash
    pip install -r requirements.txt
    ```
    This command will download and install all the necessary libraries specified in the file.

**5. Configure the Gemini API Key:**
    This application requires a Google Gemini API key to function.
    * Create a new file named `.env` in the root directory of the project (i.e., alongside `app.py` and `requirements.txt`).
    * Add your Gemini API key to this `.env` file in the following format:
        ```env
        GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
        ```
    * **Important Security Note:** The `.gitignore` file included in this repository is set up to ignore `.env` files. This ensures your API key is not accidentally committed to your Git repository. **Never commit your `.env` file.**

## ▶️ Running the Application

Once you have completed the setup:

1.  Ensure your virtual environment is activated (you should see `(venv)` in your terminal prompt).
2.  Navigate to the project's root directory in your terminal.
3.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
    *(Assuming your main Python script is named `app.py`)*
4.  Streamlit will typically open the application automatically in your default web browser. If not, it will provide a local URL (usually `http://localhost:8501`) that you can open manually.

## 📖 How to Use

1.  **Upload Resume:** Use the file uploader widget on the left to select a resume file (supports PDF and DOCX formats).
2.  **Paste Job Description:** Copy the complete job description text into the text area on the right.
3.  **View Results:** The application will automatically begin processing once both inputs are valid.
    * The **Overall Match Score** will be displayed prominently at the top.
    * A **Detailed Analysis** section will show the resume content broken down into relevant categories (Contact Info, Skills, Experience, etc.) as understood by the AI.

## 🔧 Configuration Notes

* **API Key:** The `GEMINI_API_KEY` must be correctly set in the `.env` file for the AI analysis to work.
* **AI Model:** The application is currently configured to use `models/gemini-2.0-flash`. This can be modified within the Python script (`app.py`) if you need to use a different Gemini model version (ensure it's compatible and accessible with your API key).

---

*(Optional: You can add further sections like "Troubleshooting", "Contributing Guidelines", or "License Information" as your project develops.)*
