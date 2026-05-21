# test_parser.py  — run this to test the parser with a sample resume

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.resume_parser import parse_resume

# ── change this path to your actual resume PDF ──
RESUME_PATH = "samples/sample_resume.pdf"

if not os.path.exists(RESUME_PATH):
    print(f"[ERROR] No file found at: {RESUME_PATH}")
    print("  → Put any PDF resume inside the samples/ folder")
    print("  → Rename it to sample_resume.pdf")
    print("  → Then run this file again")
    sys.exit(1)

result = parse_resume(RESUME_PATH)

if result:
    print("\n" + "="*50)
    print("  EXTRACTED SKILLS")
    print("="*50)
    for skill in result["skills"]:
        print(f"  • {skill}")

    print(f"\n  Total: {len(result['skills'])} skills found")
    print("="*50)

    print("\n  SECTION PREVIEW")
    print("="*50)
    for section, content in result["sections"].items():
        if content.strip():
            preview = content.strip()[:120].replace("\n", " ")
            print(f"  [{section.upper()}] {preview}...")
            
