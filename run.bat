@echo off
echo 🔮 ZA Study Helper - Loadshedding Mode...
echo.
python -m pip install streamlit fpdf2 requests python-dotenv -q
echo Starting app... Works WITHOUT wifi!
echo.
python -m streamlit run app.py
pause