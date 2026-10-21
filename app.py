import streamlit as st
import requests
import time
from study_helper import save_as_pdf, make_study_pack

st.set_page_config(page_title="ZA Study Helper", layout="wide", page_icon="🔮")

st.markdown("""
<div style="background: linear-gradient(90deg,#7C3AED,#EC4899); padding:18px; border-radius:15px; text-align:center; color:white">
<h2>🔮 ZA Study Helper SA</h2>
<p>Paste notes → Get Summary + Quiz + PDF • Works for ANY subject</p>
</div><br>
""", unsafe_allow_html=True)

notes = st.text_area("📚 Your notes:", height=220, placeholder="Paste your chapter notes here...")
objectives = st.text_area("🎯 Learning Outcomes / Objectives:", height=140, placeholder="Paste from study guide: A synoptic discussion...")

# --- KEY LOGIC: Try secrets first, if not found show box ---
try:
    SECRET_KEY = st.secrets["GEMINI_API_KEY"]
except:
    SECRET_KEY = ""

if SECRET_KEY:
    gemini_key = SECRET_KEY
    st.success("✅ Gemini key loaded - friends don't need to paste!")
else:
    gemini_key = st.text_input("🔑 Gemini API Key (free from aistudio.google.com):", type="password")
    st.caption("Create key at: aistudio.google.com/app/apikey")

def ai_gemini_smart(notes, objectives, key):
    prompt = f"""You are a South African university tutor.
Clean messy notes. Create exam-ready study pack.

INSTRUCTIONS:
- Ignore junk like 'section 9.6', 'page 12'.
- For EACH learning outcome, give 4 detailed bullets that ANSWER it (not just topic list).
- Add: Key Definitions, Exam Answer Template (INTRO/Body/Conclusion), and 5 Quiz Qs with answers.

NOTES: {notes[:12000]}
OUTCOMES: {objectives}
"""
    # These models exist in 2026 - will auto-fallback if busy
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
    
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, timeout=90)
            
            if r.status_code == 200:
                try:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
                except:
                    continue
            elif r.status_code == 503:
                st.toast(f"⏳ {model} busy, trying {models[models.index(model)+1] if models.index(model)+1 < len(models) else 'offline'}...")
                time.sleep(1)
                continue
            else:
                # Show only last error
                if model == models[-1]:
                    st.error(f"Gemini Error {r.status_code}: {r.text[:400]}")
                continue
        except Exception as e:
            continue
    
    return None

if st.button("✨ Generate Study Pack", type="primary"):
    if not notes.strip() or not objectives.strip():
        st.warning("Paste both notes and outcomes first chomi!")
    elif not gemini_key or len(gemini_key) < 20:
        st.warning("Paste your Gemini key first - or add it to secrets.toml")
    else:
        with st.spinner("Gemini is thinking like your chomi now..."):
            pack = ai_gemini_smart(notes, objectives, gemini_key)
        
        if not pack:
            st.warning("Gemini overloaded (503) - using offline V9 mode for now. Try again in 1 min, it usually works!")
            pack = make_study_pack(notes, objectives)
        
        st.subheader("📖 Result")
        st.text_area("Study Pack", pack, height=700)
        
        try:
            pdf = save_as_pdf(pack)
            with open(pdf, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name="study_pack.pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")