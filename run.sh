#!/bin/bash
echo "🔮 ZA Study Helper - Loadshedding Mode..."
pip3 install streamlit fpdf2 requests python-dotenv -q
echo "Starting app... Works WITHOUT wifi!"
streamlit run app.py