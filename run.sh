#!/usr/bin/env bash
# HypoForge launcher: sets up a venv, installs deps, starts Streamlit.
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment…"
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "Installing dependencies…"
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env — add your GOOGLE_API_KEY for real analysis (free: https://aistudio.google.com/apikey)."
fi

echo "Launching HypoForge at http://localhost:8501 …"
streamlit run app.py
