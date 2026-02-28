PRB Pipeline – AI-Based Document Processing System
📌 Overview

PRB Pipeline is an AI-driven document processing application designed to ingest documents, extract meaningful information, and generate structured outputs using modern NLP and LLM-based techniques.
The project focuses on clean architecture, secure configuration handling, and scalable pipeline design.

🎯 Objectives

Process and analyze uploaded documents efficiently

Extract relevant textual information using AI models

Provide structured responses for downstream applications

Maintain clean, secure, and industry-standard project structure

🛠️ Tech Stack

Programming Language: Python 3.11

AI / NLP: LLM-based processing (Groq-compatible models)

Backend Utilities: Modular Python utilities

Configuration: Environment variables (.env)

Version Control: Git & GitHub

📂 Project Structure
PRB_PIPELINE/
│
├── app.py                  # Main application entry point
├── run_app.py              # Application runner
├── test_components.py      # Component-level testing
├── requirements.txt        # Project dependencies
├── .env.template           # Environment variable template
├── .gitignore              # Git ignore rules
│
├── src/
│   └── utils/
│       ├── chat_interface.py
│       ├── document_processor.py
│
└── README.md
⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/Harisha-s01/PRB_PIPELINE.git
cd PRB_PIPELINE
2️⃣ Create Virtual Environment
python -m venv .venv

Activate:

Windows

.venv\Scripts\activate

Linux / macOS

source .venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment Variables

Create a .env file using the template:

GROQ_API_KEY=your_api_key_here

⚠️ Never commit .env files to GitHub.

5️⃣ Run the Application
python run_app.py
