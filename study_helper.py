import re
from fpdf import FPDF
import os

def clean_notes(text):
    text = re.sub(r'(?i)section \d+(\.\d+)*|page \d+|chapter \d+|figure \d+', '', text)
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 25]
    return '\n'.join(lines)

def make_study_pack(notes, objectives):
    notes_clean = clean_notes(notes)
    outcome_list = [o.strip() for o in re.split(r'\n+|;|•', objectives) if len(o.strip()) > 12]
    if not outcome_list:
        outcome_list = ["Main concepts", "Application", "Evaluation"]

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', notes_clean) if len(s.strip()) > 35]
    
    used_sentences = set()  # <--- THIS STOPS REPEATING
    pack = []
    pack.append(f"Source: {len(notes.split())} words | {len(sentences)} key points\n")
    pack.append("--- 1. LEARNING OUTCOMES ANSWERED (No repeats) ---\n")

    for i, outcome in enumerate(outcome_list[:8], 1):
        pack.append(f"{i}. OUTCOME: {outcome}")
        
        # Get unique keywords for this outcome only
        keywords = [w.lower() for w in re.findall(r'\b[a-z]{4,}\b', outcome.lower())]
        keywords = [k for k in keywords if k not in ['with','from','that','this','brief','synoptic','discussion','look','common','generic']]
        # Boost uniqueness: add outcome number bias
        start_idx = ((i-1) * 5) % max(1, len(sentences)-10)

        scored = []
        for idx, s in enumerate(sentences):
            if s in used_sentences:
                continue
            low = s.lower()
            score = sum(2 for k in keywords[:6] if k in low)
            # Prefer sentences not used, and near start_idx for variety
            score += 1 if abs(idx - start_idx) < 15 else 0
            if score > 0:
                scored.append((score, idx, s))
        
        scored.sort(key=lambda x: (-x[0], x[1]))
        chosen = []
        for _, _, s in scored[:6]:
            if s not in used_sentences:
                chosen.append(s)
                used_sentences.add(s)
            if len(chosen) >= 4:
                break
        
        # If still not enough, take unused sentences
        if len(chosen) < 4:
            for s in sentences[start_idx: start_idx+20]:
                if s not in used_sentences and len(chosen) < 4:
                    chosen.append(s)
                    used_sentences.add(s)

        for c in chosen[:4]:
            pack.append(f"   • {c[:380]}")
        pack.append("")

    pack.append("\n--- 2. KEY DEFINITIONS ---\n")
    definers = [s for s in sentences if ' is ' in s.lower() and len(s) < 250][:6]
    for d in definers:
        if d not in used_sentences:
            pack.append(f"• {d}")

    pack.append("\n--- 3. EXAM TEMPLATE ---\nINTRO: Define + importance.\nBODY: 4 points above with PEEL.\nCONCLUSION: Link back to outcome.\n")

    pack.append("\n--- 4. QUIZ (from YOUR outcomes) ---\n")
    for i, o in enumerate(outcome_list[:5], 1):
        pack.append(f"Q{i}: Explain: {o}?\n   A: Use points from outcome {i} above.\n")

    pack.append("\n--- 5. CLEANED NOTES ---\n")
    pack.append(notes_clean[:6000])
    return "\n".join(pack)

def save_as_pdf(text, filename="study_pack.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # --- Amethyst Colors ---
    AMETHYST_DARK = (107, 70, 193)   # #6B46C1
    AMETHYST_MID = (159, 122, 234)   # #9F7AEA  
    AMETHYST_LIGHT = (233, 216, 255) # #E9D8FF
    AMETHYST_BG = (250, 245, 255)    # #FAF5FF
    WHITE = (255, 255, 255)
    CHARCOAL = (45, 55, 72)

    pdf.add_page()
    # Background
    pdf.set_fill_color(*AMETHYST_BG)
    pdf.rect(0, 0, 210, 297, 'F')

    # Header bar
    pdf.set_fill_color(*AMETHYST_DARK)
    pdf.rect(0, 0, 210, 32, 'F')
    pdf.set_y(8)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 10, "  AMETHYST STUDY PACK", align='L', ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(*AMETHYST_LIGHT)
    pdf.cell(0, 5, "  Universal Offline Mode | V11 - No Repeats", align='L', ln=True)

    pdf.ln(15)
    pdf.set_text_color(*CHARCOAL)
    pdf.set_font("Arial", '', 10)

    # Process sections with amethyst headings
    for line in text.split('\n'):
        clean = line.encode('latin-1', 'ignore').decode('latin-1')
        if not clean.strip():
            pdf.ln(3)
            continue
        
        if "---" in clean or "LEARNING OUTCOMES" in clean or "KEY DEFINITIONS" in clean or "EXAM TEMPLATE" in clean or "QUIZ" in clean:
            pdf.ln(4)
            pdf.set_fill_color(*AMETHYST_MID)
            pdf.set_text_color(*WHITE)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, f"  {clean.replace('-','').strip()}", fill=True, ln=True)
            pdf.set_text_color(*CHARCOAL)
            pdf.set_font("Arial", '', 10)
            pdf.ln(2)
        elif clean.strip().startswith(tuple([f"{i}. OUTCOME" for i in range(1,10)])):
            pdf.set_fill_color(*AMETHYST_LIGHT)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 7, f" {clean[:120]}", fill=True, ln=True)
            pdf.set_font("Arial", '', 10)
        else:
            pdf.multi_cell(0, 5.5, clean)

    # Footer amethyst line
    pdf.set_y(-18)
    pdf.set_fill_color(*AMETHYST_DARK)
    pdf.rect(0, 285, 210, 12, 'F')
    pdf.set_text_color(*WHITE)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Made with amethyst energy - Good luck chomi!", align='C')

    path = os.path.join(os.getcwd(), filename)
    pdf.output(path)
    return path