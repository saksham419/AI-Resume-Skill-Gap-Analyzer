# test_gap.py — full pipeline test: resume + JD + gap analysis

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modules.resume_parser import parse_resume
from modules.jd_analyzer   import analyze_jd
from modules.gap_analyzer  import analyze_gaps

RESUME_PATH = "samples/sample_resume.pdf"
JD_PATH     = "samples/sample_jd.txt"

# ── Load resume ──
resume = parse_resume(RESUME_PATH)
if not resume:
    sys.exit(1)

# ── Load JD ──
with open(JD_PATH, "r", encoding="utf-8") as f:
    jd_text = f.read()
jd = analyze_jd(jd_text)
if not jd:
    sys.exit(1)

# ── Run gap analysis ──
report = analyze_gaps(
    resume_skills    = resume["skills"],
    required_skills  = jd["required_skills"],
    preferred_skills = jd["preferred_skills"],
)

# ── Print full report ──
print("\n" + "="*55)
print(f"  MATCH SCORE :  {report['score']}%")
print("="*55)

print(f"\n  MATCHED REQUIRED  ({len(report['matched_required'])}/{report['total_required']})")
print("-"*55)
for m in report["matched_required"]:
    tag = "(exact)" if m["exact"] else f"(via '{m['matched_by']}')"
    print(f"  ✔  {m['skill']:<25} {tag}")

print(f"\n  MATCHED PREFERRED  ({len(report['matched_preferred'])}/{report['total_preferred']})")
print("-"*55)
for m in report["matched_preferred"]:
    tag = "(exact)" if m["exact"] else f"(via '{m['matched_by']}')"
    print(f"  ✔  {m['skill']:<25} {tag}")

print(f"\n  CRITICAL GAPS  ({len(report['critical_gaps'])})")
print("-"*55)
for g in report["critical_gaps"]:
    print(f"  ✘  {g['skill']}")
    print(f"     → {g['recommendation']}\n")

print(f"  MINOR GAPS  ({len(report['minor_gaps'])})")
print("-"*55)
for g in report["minor_gaps"]:
    print(f"  ◎  {g['skill']}")
    print(f"     → {g['recommendation']}\n")

print("="*55)