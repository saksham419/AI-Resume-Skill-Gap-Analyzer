# test_jd.py

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modules.jd_analyzer import analyze_jd

JD_PATH = "samples/sample_jd.txt"

if not os.path.exists(JD_PATH):
    print(f"[ERROR] No file at {JD_PATH}")
    print("  → Create samples/sample_jd.txt with a job description")
    sys.exit(1)

with open(JD_PATH, "r", encoding="utf-8") as f:
    jd_text = f.read()

result = analyze_jd(jd_text)

if result:
    print("\n" + "="*50)
    print("  REQUIRED SKILLS")
    print("="*50)
    for skill in result["required_skills"]:
        print(f"  ✔ {skill}")

    print(f"\n  PREFERRED SKILLS")
    print("="*50)
    for skill in result["preferred_skills"]:
        print(f"  ◎ {skill}")

    print(f"\n  Total required : {len(result['required_skills'])}")
    print(f"  Total preferred: {len(result['preferred_skills'])}")
    print("="*50)