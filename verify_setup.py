# verify_setup.py
import sys

print(f"Python version: {sys.version}")
print()

packages = {
    "spacy":     "spacy",
    "nltk":      "nltk",
    "PyPDF2":    "PyPDF2",
    "pdfminer":  "pdfminer",
    "colorama":  "colorama",
}

all_ok = True
for name, module in packages.items():
    try:
        __import__(module)
        print(f"  [OK]      {name}")
    except ImportError:
        print(f"  [MISSING] {name}  <-- run: pip install {name}")
        all_ok = False

print()
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    print("  [OK]      spaCy model (en_core_web_sm)")
except OSError:
    print("  [MISSING] spaCy model  <-- run: python -m spacy download en_core_web_sm")
    all_ok = False

print()
if all_ok:
    print("=" * 45)
    print("  All good! Phase 1 complete.")
    print("  Ready to start Phase 2 - Resume Parser!")
    print("=" * 45)
else:
    print("Fix the missing items above, then re-run.")