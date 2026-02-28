#!/usr/bin/env python
"""Run Streamlit app."""
import subprocess
import sys
import os

project_root = r"C:\Users\haris\Downloads\PRB_PIPELINE\PRB_PIPELINES"
os.chdir(project_root)
sys.path.insert(0, project_root)

# Check if .env exists and has API key
env_file = os.path.join(project_root, ".env")
if os.path.exists(env_file):
    with open(env_file) as f:
        content = f.read()
        if "GROQ_API_KEY" in content:
            print("✓ GROQ_API_KEY found in .env")
        else:
            print("✗ Warning: GROQ_API_KEY not found in .env")

print(f"Starting Streamlit from: {project_root}")
print("Access the app at: http://localhost:8501")
print()

# Use full path to venv Python
venv_python = os.path.join(project_root, ".venv", "Scripts", "python.exe")

# Run streamlit with full paths
result = subprocess.run(
    [venv_python, "-m", "streamlit", "run", "app.py"],
    cwd=project_root
)
sys.exit(result.returncode)
