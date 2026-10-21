from study_helper import make_study_pack, save_as_pdf

print("🔮 ZA Study Helper - TRUE OFFLINE MODE (No Streamlit, No Wifi, No Data!)")
notes = input("\n📚 Paste your NOTES (press Enter when done):\n> ")
# For multi-line, we do simple version
print("\nPaste outcomes, then type DONE:")
lines = []
while True:
    l = input()
    if l.strip().upper() == "DONE":
        break
    lines.append(l)
objectives = "\n".join(lines)

pack = make_study_pack(notes, objectives)
print("\n" + "="*50)
print(pack)
print("="*50)

pdf = save_as_pdf(pack)
print(f"\n✅ PDF saved as {pdf} - Open it even when laptop dies!")