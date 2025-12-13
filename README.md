# 📄 AI CV Extractor & Resume Parser

An intelligent, all-in-one resume parsing tool designed to streamline the recruitment process. This application allows users to bulk upload resumes (PDF, DOCX, Images), automatically extracts key information using AI, matches candidates against Job Descriptions (JD), and exports the data for analysis.

## ✨ Key Features

  * **📂 Bulk Processing:** Drag & drop multiple resumes at once.
  * **🧠 AI Extraction:** Intelligently parses names, emails, skills, and experience from unstructured layouts.
  * **📄 Multi-Format Support:** Handles `.pdf`, `.docx`, `.doc`, `.jpg`, and `.png` files.
  * **🎯 Smart JD Matching:** Paste a Job Description to get a relevance score (0-100%) for every candidate.
  * **📊 Data Export:** Download extracted data as structured **JSON** or **CSV** for Excel/Google Sheets.
  * **🎨 Modern UI:** Fully responsive design with **Dark Mode** support and smooth animations.
  * **🔒 Local Session:** Files are cleared automatically upon session reset.

## 🛠️ Tech Stack

**Frontend:**

  * **HTML5 & Vanilla JavaScript:** Lightweight, fast, and no build steps required.
  * **Tailwind CSS:** For rapid, responsive, and beautiful styling.
  * **Chart.js:** For data visualization (prepared in codebase).

**Backend (Suggested/Implied):**

  * **Python:** (Flask or FastAPI recommended)
  * **OCR Engine:** (e.g., Tesseract or Azure Document Intelligence) for image-based CVs.
  * **LLM Integration:** (e.g., OpenAI/Gemini) for entity extraction and scoring.

## 🚀 Installation & Setup

### Prerequisites

  * Python 3.8+
  * A modern web browser

### 1\. Clone the Repository

```bash
git clone https://github.com/yourusername/cv-extractor.git
cd cv-extractor
```

### 2\. Backend Setup

*(Assuming you are using a Python virtual environment)*

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3\. Running the App

Start the Python backend server:

```bash
python app.py
```

*The app should now be running at `http://localhost:5000` (or your configured port).*

## 📖 Usage Guide

1.  **Upload:** Drag and drop your folder of resumes onto the "Browse Files" area on the Home screen.
2.  **Process:** Go to the **Dashboard** tab, select the files you want to parse, and click **Process Files**.
3.  **Track:** Watch the real-time progress bar as the AI processes each file.
4.  **Match:** Switch to the **Outputs** tab. Paste a Job Description (e.g., *"Looking for a Python developer with AWS experience"*) into the Job Matcher box and click **Score Candidates**.
5.  **Export:** View the JSON data or click **CSV** to download a spreadsheet of the results.

## 🔌 API Reference

The frontend interacts with the following backend endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/upload` | `POST` | Uploads a file and initiates an async processing task. |
| `/status/<task_id>` | `GET` | Polls the status of the specific file processing task. |
| `/match-jd` | `POST` | Accepts parsed resumes + JD text; returns match scores. |
| `/download-csv` | `POST` | Converts the JSON result set into a CSV file download. |
| `/reset` | `POST` | Clears the session and temporary server files. |

## 🤝 Contributing

Contributions are welcome\!

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
