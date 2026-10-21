import streamlit as st
import requests
import time
from study_helper import save_as_pdf, make_study_pack

st.set_page_config(page_title="ZA Study Helper", layout="wide", page_icon="🔮")

st.markdown("""
<div style="background: linear-gradient(90deg,#7C3AED,#EC4899); padding:18px; border-radius:15px; text-align:center; color:white">
<h2>🔮 ZA Study Helper SA</h2>
<p>Paste notes → Get Summary + Quiz + PDF • Works OFFLINE during load-shedding!</p>
</div><br>
""", unsafe_allow_html=True)

notes = st.text_area("📚 Your notes:", height=220, placeholder="Paste your chapter notes here...")
objectives = st.text_area("🎯 Learning Outcomes / Objectives:", height=140, placeholder="Paste from study guide...")

# --- KEY LOGIC: Optional key ---
try:
    SECRET_KEY = st.secrets["GEMINI_API_KEY"]
except:
    SECRET_KEY = ""

if SECRET_KEY:
    gemini_key = SECRET_KEY
    st.success("✅ Online Mode: Gemini loaded!")
    mode = "online"
else:
    gemini_key = st.text_input("🔑 Gemini API Key (OPTIONAL - leave empty for OFFLINE mode):", type="password")
    st.caption("Offline mode works with NO key & NO wifi! Online is just better. Key: aistudio.google.com/app/apikey")
    mode = "optional"

def ai_gemini_smart(notes, objectives, key):
    prompt = f"""You are a South African university tutor. Clean messy notes. Create exam-ready study pack.
    INSTRUCTIONS: For EACH learning outcome, give 4 detailed bullets that ANSWER it. Add: Definitions, Exam Template, 5 Quiz Qs.
    NOTES: {notes[:12000]} OUTCOMES: {objectives}"""
    models = ["gemini-1.5-flash","gemini-1.5-flash-8b","gemini-flash-latest","gemini-pro-latest"]
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=data, timeout=90)
            if r.status_code == 200:
                try: return r.json()["candidates"][0]["content"]["parts"][0]["text"]
                except: continue
        except: continue
    return None

if st.button("✨ Generate Study Pack", type="primary"):
    if not notes.strip() or not objectives.strip():
        st.warning("Paste both notes and outcomes first chomi!")
    else:
        pack = None
        # Try online if key exists
        if gemini_key and len(gemini_key) > 20:
            with st.spinner("Trying Gemini (online)..."):
                pack = ai_gemini_smart(notes, objectives, gemini_key)
        
        # If no pack, use OFFLINE mode - WORKS WITHOUT WIFI!
        if not pack:
            if gemini_key:
                st.toast("Gemini busy, switching to OFFLINE V11...")
            else:
                st.info("🔋 OFFLINE Mode Activated - Perfect for load-shedding! No data needed!")
            pack = make_study_pack(notes, objectives)
        
        st.subheader("📖 Result")
        st.text_area("Study Pack", pack, height=700)
        try:
            pdf = save_as_pdf(pack)
            with open(pdf, "rb") as f:
                st.download_button("📄 Download PDF (save for load-shedding)", f, file_name="study_pack.pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")